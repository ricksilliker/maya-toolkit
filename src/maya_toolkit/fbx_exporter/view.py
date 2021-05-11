# built-ins
import os
import sys
import logging
import json
import time

# third party
import maya.cmds as cmds
import maya.mel as mel
from Qt import QtWidgets, QtCore, QtGui

# internal
import qt_utils.core
import clips
import core
reload(core)
reload(qt_utils.core)


LOG = logging.getLogger(__name__)

TIME_ROLE = QtCore.Qt.UserRole + 1
NAME_ROLE = QtCore.Qt.UserRole + 2
WINDOW_TYPE = qt_utils.core.get_os_window_type()
ICON_DIR = os.path.join(os.path.dirname(__file__), 'resources', 'img')

FBX_TITLE_VERSION = "FBX Exporter 1.4"


def show(dockable=False):
    """Shows the PyQt UI for dragonfly-maya.

    Returns:
        QtWidgets.QWidget: The DragonflyWidget object
    """
    app = qt_utils.core.fetch_maya_window()
    win = ExporterWidget(parent=app)

    if dockable:
        qt_utils.core.dock_with_dockControl(win)
    else:
        win.show()

    with open(os.path.join(os.path.dirname(__file__), 'resources', 'stylesheet.css')) as f:
        css = f.read()
        win.setStyleSheet(css)

    win.load_clips()

    return win


class ExporterWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ExporterWidget, self).__init__(parent=parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.settings_widget = SettingsWidget()
        self.add_clip_button = QtWidgets.QPushButton('Add New Clip')
        self.clips_widget = ClipsWidget()
        self.rigs_widget = RigsWidget()
        self.export_button = QtWidgets.QPushButton('Export FBX')
        self.refresh_button = QtWidgets.QPushButton('Refresh')

        output_frame = QGroupFrame('Output')
        output_frame.add_widget(self.settings_widget)

        clips_frame = QGroupFrame('Animation Clips')
        clips_frame.add_widget(self.add_clip_button)
        clips_frame.add_widget(self.clips_widget)

        rigs_frame = QGroupFrame('Rigs')
        rigs_frame.add_widget(self.rigs_widget)

        main_layout.addWidget(output_frame)
        main_layout.addWidget(clips_frame)
        main_layout.addWidget(rigs_frame)
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.refresh_button)

        # defaults
        self.setObjectName('FBXExporter')
        self.setWindowTitle(FBX_TITLE_VERSION)
        self.setWindowFlags(WINDOW_TYPE)

        self.add_clip_button.setToolTip('Add New Clip')
        self.export_button.setToolTip('Export Clips')
        self.refresh_button.setToolTip('Refresh UI')

        self.fbx_node = core.get_node()

        # signals
        self.export_button.clicked.connect(self.run_export)
        self.add_clip_button.clicked.connect(self.clips_widget.add_new_clip)
        self.refresh_button.clicked.connect(self.refresh_ui)

    def refresh_ui(self):
        LOG.info('Refreshing FBX Exporter UI')
        self.close()
        show()

    # override
    def closeEvent(self, event):
        ui_settings = self.settings_widget.value()
        rig_settings = self.rigs_widget.value()
        core.save_ui_settings(ui_settings)
        core.save_rig_settings(rig_settings)

        super(ExporterWidget, self).closeEvent(event)

    # override
    def showEvent(self, event):
        ui_settings = core.load_ui_settings()
        rig_settings = core.load_rig_settings()

        if not ui_settings:
            self.settings_widget.set_defaults()
        else:
            self.settings_widget.set_value(ui_settings)
            self.rigs_widget.set_rigs(rig_settings)

        super(ExporterWidget, self).showEvent(event)

    # override
    def sizeHint(self):
        return QtCore.QSize(375, 650)

    def load_clips(self):
        clip_data = cmds.getAttr('FBXExporterNode.clips')
        _clips = json.loads(clip_data)
        for clip in _clips:
            clip_item = ClipItemWidget(clip_data=clip, parent=self.clips_widget)
            self.clips_widget.layout().addWidget(clip_item)

    def run_export(self):
        """Do file checks and validation before actual export call"""

        file_check = False
        write_check = False
        rig_export_check = False
        final_check = False
        abort_export = False

        #==============================================
        # Save setting to FBXExporterNode before continuing
        kw = dict()
        kw['user_filename'] = self.settings_widget.filename_line.text()
        kw['nodes'] = self.rigs_widget.get_rigs()
        kw['clip_data'] = clips.get_clips('FBXExporterNode')
        kw['only_selection'] = False
        kw['output_path'] = self.settings_widget.path_widget.field.text()
        kw.update(self.settings_widget.value())
        core.save_ui_settings(kw)

        #==============================================
        # File check, save file?, can the file be saved?, continue anyway?
        do_file_save = False
        if cmds.file(q=True, modified=True):
            results = QtWidgets.QMessageBox().question(self, 'Save File', 'Unsaved changes, save the file?')
            if results == QtWidgets.QMessageBox.Yes:
                try:
                    #cmds.file(save=True, force=True, prompt=False)
                    do_file_save = True
                    LOG.info('Saved scene changes')
                    file_check = True
                except:
                    LOG.warning('Unable to save file, make sure file is checked out of Perforce')
                    results = QtWidgets.QMessageBox().question(self, 'Continue', 'Cannot save file, continue?')
                    if results == QtWidgets.QMessageBox.Yes:
                        file_check = True
                    else:
                        file_check = False
                        abort_export = True
            else:
                LOG.warning('File not saved, continuing with FBX export')
                file_check = True
                abort_export = False
        else:
            file_check = True

        #==============================================
        # File writable check
        if not abort_export:
            non_write_files = check_file_write()
            if non_write_files:
                LOG.info("Some FBX files exist and are not writable!")
                results = QtWidgets.QMessageBox().question(self, 'Continue?', 'Some FBX files exist but are not writable, continue?')
                if results == QtWidgets.QMessageBox.Yes:
                    write_check = True
                else:
                    LOG.warning("FBX Export operation aborted!")
                    write_check = False
                    abort_export = True
            else:
                write_check = True

        #==============================================
        # Rig export check, if no anim clips are specfied, check if user intends to export an fbx rig or not
        if not abort_export:
            if not kw['clip_data']:
                results = QtWidgets.QMessageBox().question(self, 'Export Rig FBX', 'No clips specfied, export as rig?')
                if results == QtWidgets.QMessageBox.Yes:
                    rig_export_check = True
                else:
                    rig_export_check = False
            else:
                rig_export_check = True

        #==============================================

        LOG.info('file_check = {}'.format(file_check))
        LOG.info('write_check = {}'.format(write_check))
        LOG.info('rig_export_check = {}'.format(rig_export_check))

        #==============================================
        # Final check so user can abort
        if not abort_export:
            quit_msg = "Continue with FBX Export?"
            reply = QtWidgets.QMessageBox.question(self, 'Continue with FBX Export?',
                                                   quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                LOG.info("FBX Export operation started...")
                # Run FBX Export after all checks
                if file_check and write_check and rig_export_check:
                    if do_file_save:
                        cmds.file(save=True, force=True, prompt=False)
                    start_time = time.time()
                    core.export_rigs(**kw)
                    elapsed_time = time.time() - start_time

                    LOG.info("FBX Export successfully completed in {} seconds".format(str(round(elapsed_time, 1))))
                    results = QtWidgets.QMessageBox().information(self, 'Export Completed', 'FBX Export Completed')
                    if results == QtWidgets.QMessageBox.Yes:
                        return True
                else:
                    LOG.warning("FBX Export operation aborted!")

        # FBX export cancelled by user
        else:
            LOG.warning("FBX Export operation aborted!")



class ClipsWidget(QtWidgets.QWidget):
    column_labels = ['Delete', 'Clip Name', 'Start', 'End', 'Set', 'Play', 'On/Off']

    def __init__(self, parent=None):
        super(ClipsWidget, self).__init__(parent=parent)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(3)

    def add_new_clip(self):
        clips.add_clip('FBXExporterNode')
        cw = ClipItemWidget(clip_data=list(), parent=self)
        self.layout().addWidget(cw)
        cw.start_frame_spinbox.setValue(cmds.playbackOptions(q=True, min=True))
        cw.end_frame_spinbox.setValue(cmds.playbackOptions(q=True, max=True))


class ClipItemWidget(QtWidgets.QWidget):
    delete_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'delete_icon.png'))
    frame_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'frame_icon.png'))
    play_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'play_icon.png'))
    pause_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'pause_icon.png'))

    def __init__(self, clip_data, parent=None):
        super(ClipItemWidget, self).__init__(parent=parent)

        self.timeline_settings = dict()

        # delete clip button
        self.delete_clip_button = QtWidgets.QPushButton(self.delete_icon, '')
        self.delete_clip_button.setToolTip('Delete')
        self.delete_clip_button.setIconSize(QtCore.QSize(15, 15))
        self.delete_clip_button.setFlat(True)

        # clip name field
        self.clip_name_line = QtWidgets.QLineEdit()
        self.clip_name_line.setMinimumHeight(25)
        self.clip_name_line.setPlaceholderText('Clip Name')
        self.clip_name_line.setToolTip('Clip Name')

        # start frame field
        self.start_frame_spinbox = QtWidgets.QSpinBox()
        self.start_frame_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_frame_spinbox.setMinimum(-1000)
        self.start_frame_spinbox.setMaximum(10000)
        self.start_frame_spinbox.setToolTip('Start Frame')

        # end frame field
        self.end_frame_spinbox = QtWidgets.QSpinBox()
        self.end_frame_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.end_frame_spinbox.setMinimum(-1000)
        self.end_frame_spinbox.setMaximum(10000)
        self.end_frame_spinbox.setToolTip('End Frame')

        # set clip button
        self.set_clip_button = QtWidgets.QPushButton(self.frame_icon, '')
        self.set_clip_button.setIconSize(QtCore.QSize(15, 15))
        self.set_clip_button.setFlat(True)
        self.set_clip_button.setToolTip('Set Clip as Active Time')

        # play clip button
        self.play_clip_button = QtWidgets.QPushButton(self.play_icon, '')
        self.play_clip_button.setIconSize(QtCore.QSize(15, 15))
        self.play_clip_button.setFlat(True)
        self.play_clip_button.setToolTip('Play Clip')

        # toggle clip
        self.toggle_clip_checkbox = QtWidgets.QCheckBox('')
        self.toggle_clip_checkbox.setChecked(True)
        self.toggle_clip_checkbox.setToolTip('Toggle Export On/Off')

        if clip_data:
            self.clip_name_line.setText(clip_data[0])
            self.start_frame_spinbox.setValue(clip_data[1])
            self.end_frame_spinbox.setValue(clip_data[2])
            self.toggle_clip_checkbox.setChecked(clip_data[3])

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.toggle_clip_checkbox, 0)
        main_layout.addWidget(self.clip_name_line, 1)
        main_layout.addWidget(self.start_frame_spinbox, 0)
        main_layout.addWidget(self.end_frame_spinbox, 0)
        main_layout.addWidget(self.set_clip_button, 0)
        main_layout.addWidget(self.play_clip_button, 0)
        main_layout.addWidget(self.delete_clip_button, 0)

        # signals
        self.set_clip_button.clicked.connect(self.set_timeline)
        self.play_clip_button.clicked.connect(self.play_timeline)
        self.delete_clip_button.clicked.connect(self.delete_clip)

        self.clip_name_line.textChanged.connect(self.name_changed)
        self.start_frame_spinbox.valueChanged.connect(self.start_changed)
        self.end_frame_spinbox.valueChanged.connect(self.end_changed)
        self.toggle_clip_checkbox.stateChanged.connect(self.toggle_changed)

    def clip_index(self):
        return self.parentWidget().layout().indexOf(self)

    def name_changed(self, value):
        data = clips.get_clips('FBXExporterNode')
        data[self.clip_index()].pop(0)
        data[self.clip_index()].insert(0, value)
        clips.set_clips('FBXExporterNode', *data)

    def start_changed(self, value):
        data = clips.get_clips('FBXExporterNode')
        clip = data[self.clip_index()]
        clip.pop(1)
        clip.insert(1, value)
        clips.set_clips('FBXExporterNode', *data)

    def end_changed(self, value):
        data = clips.get_clips('FBXExporterNode')
        clip = data[self.clip_index()]
        clip.pop(2)
        clip.insert(2, value)
        clips.set_clips('FBXExporterNode', *data)

    def toggle_changed(self, value):
        if value == QtCore.Qt.Unchecked:
            value = False
        else:
            value = True
        data = clips.get_clips('FBXExporterNode')
        clip = data[self.clip_index()]
        clip.pop(3)
        clip.insert(3, value)
        clips.set_clips('FBXExporterNode', *data)

    def delete_clip(self):
        clips.delete_clip('FBXExporterNode', self.clip_index())
        parent_layout = self.parentWidget().layout()
        widget_index = parent_layout.indexOf(self)
        parent_layout.takeAt(widget_index)
        self.deleteLater()

    def set_timeline(self):
        start_frame = self.start_frame_spinbox.value()
        end_frame = self.end_frame_spinbox.value()
        cmds.playbackOptions(min=start_frame, max=end_frame)

    def play_timeline(self):
        if not cmds.play(q=True, state=True):
            self.timeline_settings = core.get_current_playback_settings()
            self.set_timeline()
            cmds.play(forward=True)
            self.play_clip_button.setIcon(self.pause_icon)
        else:
            cmds.play(state=False)
            cmds.playbackOptions(**self.timeline_settings)
            self.play_clip_button.setIcon(self.play_icon)


class RigsWidget(QtWidgets.QListWidget):
    rig_path_role = QtCore.Qt.UserRole + 1
    rig_enabled_bg = QtGui.QBrush(QtGui.QColor('#666666'))
    rig_disabled_bg = QtGui.QBrush(QtGui.QColor('#FF3333'))

    def __init__(self, parent=None):
        super(RigsWidget, self).__init__(parent=parent)
        self.add_rigs()
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSpacing(2)

        self.itemChanged.connect(self.update_item_color)

    def update_item_color(self, item):
        if item.checkState() == QtCore.Qt.Unchecked:
            item.setBackground(self.rig_disabled_bg)
        else:
            item.setBackground(self.rig_enabled_bg)

    def add_rig_item(self, rig_path):
        rig_item = QtWidgets.QListWidgetItem()
        rig_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        rig_item.setCheckState(QtCore.Qt.Checked)
        rig_item.setData(self.rig_path_role, rig_path)
        rig_item.setData(QtCore.Qt.DisplayRole, rig_path)
        rig_item.setBackground(self.rig_enabled_bg)
        rig_item.setTextAlignment(QtCore.Qt.AlignCenter)
        rig_item.setSizeHint(QtCore.QSize(50, 30))

        return rig_item

    def add_rigs(self):
        for rig_path in core.get_rigs():
            item = self.add_rig_item(rig_path)
            self.addItem(item)

    def get_rigs(self):
        checked_rigs = list()
        for index in range(self.count()):
            item = self.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                rig_path = item.data(self.rig_path_role)
                checked_rigs.append(rig_path)
        LOG.debug(checked_rigs)
        return checked_rigs

    def get_rig_states(self):
        rig_dict = dict()
        for index in range(self.count()):
            item = self.item(index)
            active_state = 'False'
            if item.checkState() == QtCore.Qt.Checked:
                active_state = 'True'
            rig_path = item.data(self.rig_path_role)
            rig_dict[rig_path] = [index, active_state]
        LOG.debug(rig_dict)
        return rig_dict

    def value(self):
        result = self.get_rig_states()
        return result

    def set_rigs(self, rig_settings):

        for rig, index_state in rig_settings.iteritems():
            index = index_state[0]
            state = str(index_state[1])
            item = self.item(index)
            try:
                if state == 'True':
                    item.setCheckState(QtCore.Qt.Checked)
                    item.setBackground(self.rig_enabled_bg)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setBackground(self.rig_disabled_bg)
            except:
                LOG.warning('{} no longer exists in scene, skipping...'.format(rig))
        return True


class SettingsWidget(QtWidgets.QWidget):
    default_settings = dict(
        ExportDirectory=core.get_scene_directory(),
        ExportFileName='CH_{asset}_{clip}_Anim',
        ExportMeshes=False,
        ExportPreset=0,
        SnapToOrigin=False,
        DeleteStaticChannels=True,
        FBXExportSkins=False,
        FBXExportShapes=True,
        FBXExportFileVersion=0,
        FBXExportInAscii=0
    )

    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent=parent)

        # export preset options
        self.export_presets_menu = QtWidgets.QComboBox()
        self.export_presets_menu.addItems(['Export Preset: ANIMATION', 'Export Preset: RIG'])

        # how to handle gathering export objects
        self.export_type_menu = QtWidgets.QComboBox()
        #self.export_type_menu.addItems(['Export Type: ASSET', 'Export Type: SELECTED'])
        self.export_type_menu.addItems(['Export Type: ASSET'])

        # output directory and file info
        self.path_widget = qt_utils.core.QFilePath('Output Folder')
        self.path_widget.use_directory = True
        self.filename_line = QtWidgets.QLineEdit('')
        self.filename_line.setPlaceholderText('File Name')

        # whether to export geometry or not
        self.export_mesh_checkbox = QtWidgets.QCheckBox('Meshes')

        # whether to export skin or not
        self.export_skinclusters_checkbox = QtWidgets.QCheckBox('Skinclusters')

        # whether to export blendshapes/morphs or not
        self.export_blendshapes_checkbox = QtWidgets.QCheckBox('Blendshapes')

        # snap will move the root object back to the origin before export
        self.snap_checkbox = QtWidgets.QCheckBox('Snap Root to Origin')

        # this will filter out keyframes that hold redundant values across time
        self.static_checkbox = QtWidgets.QCheckBox('Delete Static Channels')

        # pick the FBX version
        self.fbx_version_label = QtWidgets.QLabel()
        self.fbx_version_label.setText('FBX Version')
        self.fbx_version_menu = QtWidgets.QComboBox()
        fbx_versions_uivl = mel.eval('FBXExportFileVersion -uivl;')
        self.fbx_version_menu.addItems(fbx_versions_uivl)

        # pick the fbx data type binary or ascii data
        self.fbx_type_label = QtWidgets.QLabel()
        self.fbx_type_label.setText('FBX Type')
        self.fbx_type_menu = QtWidgets.QComboBox()
        self.fbx_type_menu.addItems(['Binary', 'ASCII'])

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(3)

        main_layout.addWidget(self.filename_line)
        main_layout.addWidget(self.export_presets_menu)
        main_layout.addWidget(self.export_type_menu)
        main_layout.addWidget(self.path_widget)
        main_layout.addWidget(self.filename_line)

        main_layout.addWidget(self.export_mesh_checkbox)
        main_layout.addWidget(self.export_skinclusters_checkbox)
        main_layout.addWidget(self.export_blendshapes_checkbox)
        main_layout.addWidget(self.snap_checkbox)
        main_layout.addWidget(self.static_checkbox)

        fbx_version_hbox = QtWidgets.QHBoxLayout()
        fbx_version_hbox.setAlignment(QtCore.Qt.AlignLeft)
        fbx_version_hbox.addWidget(self.fbx_version_label)
        fbx_version_hbox.addWidget(self.fbx_version_menu)

        fbx_type_hbox = QtWidgets.QHBoxLayout()
        fbx_type_hbox.setAlignment(QtCore.Qt.AlignLeft)
        fbx_type_hbox.addWidget(self.fbx_type_label)
        fbx_type_hbox.addWidget(self.fbx_type_menu)

        main_layout.addLayout(fbx_version_hbox)
        main_layout.addLayout(fbx_type_hbox)

        # signals
        self.export_presets_menu.currentIndexChanged.connect(self.change_preset)
        self.export_mesh_checkbox.stateChanged.connect(self.value)

    def value(self):
        result = dict()
        result.update(self.default_settings)

        result['ExportDirectory'] = self.path_widget.field.text()
        result['ExportFileName'] = self.filename_line.text()
        result['ExportMeshes'] = self.export_mesh_checkbox.isChecked()
        result['ExportPreset'] = self.export_presets_menu.currentIndex()
        result['SnapToOrigin'] = self.snap_checkbox.isChecked()
        result['DeleteStaticChannels'] = self.static_checkbox.isChecked()
        result['FBXExportSkins'] = self.export_skinclusters_checkbox.isChecked()
        result['FBXExportShapes'] = self.export_blendshapes_checkbox.isChecked()
        result['FBXExportFileVersion'] = self.fbx_version_menu.currentIndex()
        result['FBXExportInAscii'] = self.fbx_type_menu.currentIndex()

        return result

    def set_value(self, settings):
        self.export_presets_menu.setCurrentIndex(settings.get('ExportPreset', 0))  # this needs to be first or else
        self.path_widget.field.setText(settings.get('ExportDirectory', ''))
        self.filename_line.setText(settings.get('ExportFileName', ''))
        self.export_mesh_checkbox.setChecked(settings.get('ExportMeshes', False))
        self.snap_checkbox.setChecked(settings.get('SnapToOrigin', False))
        self.static_checkbox.setChecked(settings.get('DeleteStaticChannels', False))
        self.export_skinclusters_checkbox.setChecked(settings.get('FBXExportSkins', False))
        self.export_blendshapes_checkbox.setChecked(settings.get('FBXExportShapes', False))
        self.fbx_version_menu.setCurrentIndex(settings.get('FBXExportFileVersion', 0))
        self.fbx_type_menu.setCurrentIndex(settings.get('FBXExportInAscii', 0))

    def change_preset(self):
        selected_preset = self.export_presets_menu.currentIndex()
        if selected_preset == 0:
            self.export_mesh_checkbox.setChecked(QtCore.Qt.Unchecked)
            self.export_skinclusters_checkbox.setChecked(QtCore.Qt.Unchecked)
            self.export_blendshapes_checkbox.setChecked(QtCore.Qt.Checked)
            self.snap_checkbox.setChecked(QtCore.Qt.Unchecked)
            #self.static_checkbox.setChecked(QtCore.Qt.Unchecked)
            self.static_checkbox.setChecked(False)
            self.filename_line.setText('{asset}_{clip}_Anim.fbx')
            LOG.debug("Animation Export preset: Used to export animated skeleton clips to FBX file.")

        elif selected_preset == 1:
            self.export_mesh_checkbox.setChecked(QtCore.Qt.Checked)
            self.export_skinclusters_checkbox.setChecked(QtCore.Qt.Checked)
            self.export_blendshapes_checkbox.setChecked(QtCore.Qt.Checked)
            self.snap_checkbox.setChecked(QtCore.Qt.Unchecked)
            #self.static_checkbox.setChecked(QtCore.Qt.Unchecked)
            self.static_checkbox.setChecked(False)
            self.filename_line.setText('{asset}_Rig.fbx')
            LOG.debug("Rig Export preset: Used to export non-animated skeleton with deformers FBX file.")

    def set_defaults(self):
        self.path_widget.field.setText(core.get_scene_directory())
        self.export_mesh_checkbox.setChecked(QtCore.Qt.Unchecked)
        self.export_skinclusters_checkbox.setChecked(QtCore.Qt.Unchecked)
        self.export_blendshapes_checkbox.setChecked(QtCore.Qt.Checked)
        #self.static_checkbox.setChecked(QtCore.Qt.Checked)
        self.static_checkbox.setChecked(False)
        self.filename_line.setText('{asset}_{clip}_Anim.fbx')
        LOG.debug("Animation Export preset: Used to export animated skeleton clips to FBX file.")

    def get_output_folder(self):

        result = dict()
        result['ExportDirectory'] = self.path_widget.field.text()
        result['ExportFileName'] = self.filename_line.text()
        return result


class QGroupFrame(QtWidgets.QWidget):
    panel_opened_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'panel_opened_icon.png'))
    panel_closed_icon = QtGui.QIcon(os.path.join(ICON_DIR, 'panel_closed_icon.png'))

    def __init__(self, title, parent=None):
        super(QGroupFrame, self).__init__(parent=parent)

        self.title_button = QtWidgets.QPushButton(self.panel_opened_icon, title)
        self.children_frame = QtWidgets.QFrame()
        self.children_layout = QtWidgets.QVBoxLayout()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        main_layout.addWidget(self.title_button)
        main_layout.addWidget(self.children_frame)
        self.children_frame.setLayout(self.children_layout)

        # default settings
        self.title_button.setIconSize(QtCore.QSize(5, 5))
        self.children_frame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Foreground, QtGui.QColor('#333'))
        palette.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QColor(60, 60, 60))
        self.children_frame.setAutoFillBackground(True)
        self.children_frame.setPalette(palette)
        self.title_button.setStyleSheet('text-align: left;background: #555;border: 0px;padding: 3px;')

        # signals
        self.title_button.clicked.connect(self.show_and_hide)

    def show_and_hide(self):
        if self.children_frame.isVisible():
            self.children_frame.hide()
            self.title_button.setIcon(self.panel_closed_icon)
        else:
            self.children_frame.show()
            self.title_button.setIcon(self.panel_opened_icon)

    def add_widget(self, widget):
        self.children_frame.layout().addWidget(widget)


def check_file_write():
    """Determines if FBX files to export exist and are writable"""
    fbx_node = 'FBXExporterNode'

    if cmds.objExists(fbx_node):
        rigs = core.get_rigs()
        #rig_settings = core.load_rig_settings()

        settings = core.load_ui_settings()
        export_dir = settings["ExportDirectory"]
        export_name = settings["ExportFileName"]
        export_clips = clips.get_clips(fbx_node)

        fbx_export_files = list()

        for rig in rigs:
            LOG.info("Rig: {}".format(rig))

            rep_export_name = ""
            if "{asset}" in export_name:
                asset = core.get_asset(core.get_rig_mobject(rig))
                rep_export_name = export_name.replace("{asset}", asset)
            else:
                rep_export_name = export_name

            if export_clips:
                for clip in export_clips:
                    clip_name = clip[0]

                    if "{clip}" in rep_export_name:
                        clip_name = rep_export_name.replace("{clip}", clip[0])
                    fbx_export_files.append('{}/{}'.format(export_dir, clip_name))

        if fbx_export_files:
            fbx_error_files = list()
            for fbx_file in fbx_export_files:
                if os.path.isfile(fbx_file):
                    if not os.access(fbx_file, os.W_OK):
                        LOG.error("FILE WRITE ERROR: {} exists and is not writable!  Check Perforce".format(fbx_file))
                        fbx_error_files.append(fbx_file)
            return fbx_error_files




