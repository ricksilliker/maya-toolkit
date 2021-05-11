"""The UI components of the Maya extension of dragonfly.
"""
# built-ins
import os
import sys
import logging
import glob

# third party
import maya.cmds as cmds
import maya.utils
from Qt import QtWidgets, QtCore, QtGui

# internal
import qt_utils.core
import py_tasker.tasks

import modules
import node
import meta_types
import core


LOG = logging.getLogger(__name__)
DEFAULT_BLUEPRINT_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'default_blueprint.yaml')
TREE_TASK_TYPE = QtWidgets.QTreeWidgetItem.UserType + 1
TREE_GROUP_TYPE = QtWidgets.QTreeWidgetItem.UserType + 2


def show(dockable=False):
    """Shows the PyQt UI for dragonfly-maya.

    Returns:
        QtWidgets.QWidget: The DragonflyWidget object
    """
    app = qt_utils.core.fetch_maya_window()
    app_dimensions = app.geometry()

    for child in app.findChildren(QtWidgets.QWidget):
        if child.objectName() == 'DragonflyWidget':
            child.deleteLater()

    win = DragonflyWidget(parent=app)

    if dockable:
        win = qt_utils.core.dock_with_dockControl(win)
    else:
        win.resize(300, 650)
        win.show()

    return win


class DragonflyWidget(QtWidgets.QWidget):
    """Main UI widget."""
    plus_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'plus_icon.png')
    refresh_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'refresh_icon.png')

    def __init__(self, parent=None):
        super(DragonflyWidget, self).__init__(parent=parent)

        self.is_built = False

        self.menu = QtWidgets.QMenuBar()
        new_bp_action = QtWidgets.QAction('New Blueprint', self)
        save_bp_action = QtWidgets.QAction('Save Blueprint', self)
        open_bp_action = QtWidgets.QAction('Open Blueprint..', self)
        open_bp_template_action = QtWidgets.QAction('Open Blueprint Template..', self)
        append_bp_action = QtWidgets.QAction('Append Blueprint..', self)
        reload_tasks_action = QtWidgets.QAction('Reload Tasks', self)
        file_menu = self.menu.addMenu('File')
        file_menu.addAction(new_bp_action)
        file_menu.addAction(save_bp_action)
        file_menu.addAction(open_bp_action)
        file_menu.addAction(open_bp_template_action)
        file_menu.addAction(append_bp_action)
        file_menu.addAction(reload_tasks_action)

        build_action = QtWidgets.QAction('Build', self)
        debug_action = QtWidgets.QAction('Debug', self)
        revert_action = QtWidgets.QAction('Revert', self)
        run_menu = self.menu.addMenu('Run')
        run_menu.addAction(build_action)
        run_menu.addAction(debug_action)
        run_menu.addAction(revert_action)

        name_conventions_action = QtWidgets.QAction('Name Conventions', self)
        file_structure_action = QtWidgets.QAction('File Structure', self)
        help_menu = self.menu.addMenu('Help')
        help_menu.addAction(name_conventions_action)
        help_menu.addAction(file_structure_action)

        separator = qt_utils.core.QHLine()

        self.manage_page = ManagePageWidget(self)
        self.built_page = BuiltPageWidget(self)

        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.addTab(self.manage_page, 'Rig')
        self.tabs_widget.addTab(self.built_page, 'Console')

        self.run_build_button = QtWidgets.QPushButton('BUILD  TASKS')
        self.run_build_button.setStyleSheet("font: bold; background-color: grey; font-size: 11pt;")

        # top layout
        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.setAlignment(QtCore.Qt.AlignTop)
        sub_layout.setSpacing(3)
        sub_layout.setContentsMargins(2, 2, 2, 2)
        sub_layout.addWidget(self.tabs_widget)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.menu)
        main_layout.addWidget(separator)

        main_layout.addLayout(sub_layout)
        main_layout.addWidget(self.run_build_button)

        # default settings
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        self.setObjectName('DragonflyWidget')
        self.setWindowTitle('Dragonfly')
        self.setWindowFlags(qt_utils.core.get_os_window_type())

        # signals
        new_bp_action.triggered.connect(self.manage_page.create_default_blueprint)
        save_bp_action.triggered.connect(self.manage_page.save_blueprint)
        open_bp_action.triggered.connect(self.manage_page.import_blueprint)
        open_bp_template_action.triggered.connect(lambda x=True: self.manage_page.import_blueprint(template=x))
        append_bp_action.triggered.connect(lambda x=False: self.manage_page.import_blueprint(clear=x))
        reload_tasks_action.triggered.connect(self.reload_tasks)

        build_action.triggered.connect(self.build_rig)
        debug_action.triggered.connect(lambda debug=True: self.build_rig(debug))
        revert_action.triggered.connect(self.open_rig)
        self.run_build_button.clicked.connect(self.build_rig)

        self.tabs_widget.currentChanged.connect(self.tabChange)

        #self.run_build_button.setEnabled(True)

    def tabChange(self, i):
        if i:
            self.run_build_button.setEnabled(False)
        else:
            self.run_build_button.setEnabled(True)
        """
        QtWidgets.QMessageBox.information(self,
                                      "Tab Index Changed!",
                                      "Current Tab Index: %d" % i)
        """

    def reload_tasks(self):
        def _reload_ui(dimensions):
            ui = show()
            ui.setGeometry(dimensions)
            ui.manage_page.open_relative_blueprint()

        self.manage_page.save_blueprint(force=True)
        old_geometry = self.geometry()
        self.close()
        core.setup()
        maya.utils.executeDeferred(_reload_ui, dimensions=old_geometry)

    def build_rig(self, debug=False):
        scene_path = cmds.file(q=True, sn=True)

        if not scene_path:
            QtWidgets.QMessageBox().critical(self, 'Scene Not Saved', 'Cannot build, file has not been saved')
            return

        self.tabs_widget.setCurrentIndex(1)

        if debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        self.built_page.log_browser.clear()

        ui_handler = QtLogger(self.built_page.log_browser, level=log_level)
        core.LOG.addHandler(ui_handler)

        try:
            bp = self.manage_page.create_blueprint_from_ui()
            core.build_maya_blueprint(bp, debug)
            self.is_built = True
        except Exception as e:
            LOG.error('Something went wrong')

        self.built_page.log_browser.append('\n')
        scene_link = '<a href="maya://scene/{}"><font color="orange">Click To Open Blueprint</font></href>'.format(scene_path)
        self.built_page.log_browser.append(scene_link)

        core.LOG.removeHandler(ui_handler)

        self.run_build_button.setEnabled(False)

    def open_rig(self):
        self.tabs_widget.setCurrentIndex(0)
        bp_file = core.open_maya_blueprint()
        if bp_file:
            self.manage_page.import_blueprint(bp_file)

        self.is_built = False

        self.run_build_button.setEnabled(True)


class QtLogger(logging.Handler):
    def __init__(self, log_widget, level=logging.NOTSET):
        super(QtLogger, self).__init__(level=level)
        self.log_widget = log_widget

    def emit(self, record):
        msg = self.format(record)

        msg = '<font face="Courier">{}</font>'.format(msg)

        if record.levelno == logging.INFO:
            msg = '<font color="green">[INFO]: {}</font>'.format(msg)
        elif record.levelno == logging.DEBUG:
            msg = '<font color="green">[DEBUG]: {}</font>'.format(msg)
        elif record.levelno == logging.WARNING:
            msg = '<font color="yellow">[WARNING]: {}</font>'.format(msg)
        elif record.levelno == logging.ERROR:
            msg = '<font color="red">[ERROR]: {}</font>'.format(msg)

        self.log_widget.append(msg)


class MayaUrlReceiver(QtCore.QObject):
    @QtCore.Slot(QtCore.QUrl)
    def receive(self, url):
        if url.host() == 'scene':
            self.open_scene(url.path())

    def open_scene(self, path):
        LOG.debug('Opening Maya Scene: {}'.format(path))
        cmds.file(path, o=True, f=True)


mayaReceiver = MayaUrlReceiver()
QtGui.QDesktopServices.setUrlHandler('maya', mayaReceiver, 'receive')


class BuiltPageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BuiltPageWidget, self).__init__(parent=parent)

        self.log_browser = QtWidgets.QTextBrowser()

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(3, 3, 3, 3)

        main_layout.addWidget(self.log_browser)

        self.setLayout(main_layout)

        self.log_browser.setOpenExternalLinks(True)
        self.log_browser.setReadOnly(True)


class ManagePageWidget(QtWidgets.QWidget):
    """Rig page tab widget.

    Manage the tasks in the Blueprint that build the rig.
    """
    def __init__(self, parent=None):
        super(ManagePageWidget, self).__init__(parent=parent)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # rig outliner
        self.add_groups_button = QtWidgets.QPushButton('Add Group')
        self.add_tasks_button = QtWidgets.QPushButton('Add Task')

        layout.addWidget(self.add_groups_button, 0, 0, 2, 2)
        layout.addWidget(self.add_tasks_button, 0, 2, 2, 2)
        layout.setRowMinimumHeight(6, 5)

        self.rig_tree = RigTreeWidget(self)

        # main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(3, 3, 3, 3)

        main_layout.addLayout(layout)
        main_layout.addWidget(self.rig_tree)

        self.setLayout(main_layout)

        # event filters
        self.rig_tree.viewport().installEventFilter(self)

        # signals
        self.add_tasks_button.clicked.connect(self.open_task_dialog)
        self.add_groups_button.clicked.connect(self.open_group_dialog)
        self.rig_tree.customContextMenuRequested.connect(self.show_popup)
        self.rig_tree.itemDoubleClicked.connect(self.double_click_tree)

    def eventFilter(self, object, event):
        if object is self.rig_tree.viewport():
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if self.rig_tree.itemAt(event.pos()) is None:
                    self.rig_tree.clearSelection()

        return super(ManagePageWidget, self).eventFilter(object, event)

    def create_blueprint_from_ui(self):
        # create new blueprint to export
        LOG.debug('Creating Blueprint Builder...')
        blueprint = core.Blueprint()

        # add tasks to blueprint
        for item in self.rig_tree.get_task_items():
            blueprint.append_task(item.task_spec)

        return blueprint

    def create_default_blueprint(self):
        self.rig_tree.clear()
        self.import_blueprint(DEFAULT_BLUEPRINT_PATH)

    def save_blueprint(self, force=False):
        sceneName = cmds.file(q=True, sn=True)
        if not sceneName:
            raise ValueError('Unable to save blueprint because the file has not been saved.')

        blueprint_file_path = sceneName.split('.')[0] + '_blueprint.yaml'

        if not force:
            if os.path.isfile(blueprint_file_path):
                result = QtWidgets.QMessageBox().warning(self, 'Overwrite Blueprint',
                                                         'A blueprint already exists for this file, do you want to overwrite it?',
                                                         buttons=QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
                if result != QtWidgets.QMessageBox.Save:
                    LOG.debug('Not saving blueprint, it already exists')
                    return

        # export blueprint
        blueprint = self.create_blueprint_from_ui()
        core.export_blueprint(blueprint, blueprint_file_path)

        LOG.info('Saved Blueprint: {0}'.format(blueprint_file_path))

        return blueprint_file_path

    def open_relative_blueprint(self):
        sceneName = cmds.file(q=True, sn=True)
        if sceneName:
            bp_file = sceneName.split('.')[0] + '_blueprint.yaml'
            self.import_blueprint(bp_file)

    def import_blueprint(self, blueprint_file=None, template=False, clear=True):
        if blueprint_file is None:
            sceneName = cmds.file(q=True, sn=True)
            current_scene_directory = os.path.dirname(sceneName)
            if template:
                current_scene_directory = os.path.join(os.path.dirname(__file__), 'templates')

            result = QtWidgets.QFileDialog().getOpenFileName(self, 'Import Blueprint', current_scene_directory)

            if not result[0] and not result[0].endswith('.yaml'):
                LOG.debug('Can not import, no file was selected and/or the file is not a yaml file')
                return

            blueprint_file = result[0]

        bp = core.import_blueprint(blueprint_file)

        # clear list widgets lists
        # task list
        if clear:
            self.rig_tree.clear()

        # create tasks for blueprint, and add widgets to build list
        for task_data in bp['tasks']:
            task_spec = core.MayaTaskSpec(py_tasker.tasks.TASK_CACHE[task_data['task']], **task_data)

            task_item = TreeTaskWidget(task_spec)
            task_item.set_enabled(task_data['enabled'])
            task_item.set_debug(task_data['debug'])

            group_item = self.rig_tree.get_group_item(task_data['group'])
            if task_data['group'] is None:
                self.rig_tree.addTopLevelItem(task_item)
            elif group_item is None:
                self.rig_tree.add_group(task_data['group'], [task_item])
            else:
                group_item.add_task_item(task_item)

        # Open maya template file if it exists
        if template:
            filename = blueprint_file.split('.')[0]
            maya_file = glob.glob('{}*.m*'.format(filename))
            if maya_file:
                cmds.file(maya_file[0], o=True, force=True, pmt=False)
                LOG.info('Opened Maya File Template: {0}'.format(maya_file[0]))
            else:
                LOG.info('No Maya File Template found...')

        LOG.info('Imported Blueprint: {0}'.format(blueprint_file))

    def open_task_dialog(self):
        dialog = AddTaskDialog()

        main_window = self.parentWidget()
        dialog.move(main_window.width()+main_window.x(), main_window.y())
        dialog.resize(350, 350)

        dialog.task_list.itemDoubleClicked.connect(dialog.accept)
        dialog.accepted.connect(lambda x=dialog: self.add_task_spec(x))
        dialog.exec_()

    def open_group_dialog(self):
        self.rig_tree.add_group('NewGroup')

    def update_group_name(self, item, column):
        if item.type() == TREE_GROUP_TYPE and column == 0:
            value = item.data(column, QtCore.Qt.DisplayRole)
            item.set_name(value)

    def add_task_spec(self, dialog):
        task_item = dialog.task_list.currentItem()
        task_type = task_item.data(QtCore.Qt.DisplayRole)
        self.rig_tree.add_task(task_type)

    def update_task_spec(self, task_spec, widget_map):
        for k in task_spec.params().keys():
            task_spec[k] = widget_map[k].data

        LOG.debug('{0} data updated'.format(task_spec.name))

    def show_popup(self):
        selected_item = self.rig_tree.currentItem()
        LOG.debug('Item popup for {0}'.format(selected_item.task_spec.name))

        if selected_item.type() == TREE_TASK_TYPE:
            self.show_task_popup()
        elif selected_item.type() == TREE_GROUP_TYPE:
            self.show_group_popup()
        else:
            return

    def show_task_popup(self):
        menu = QtWidgets.QMenu(self)
        enabled_action = menu.addAction('Toggle On/Off')
        menu.addSeparator()
        edit_action = menu.addAction('Edit Selected Task')
        setup_action = menu.addAction('Run Task Setup')
        menu.addSeparator()
        duplicate_action = menu.addAction('Duplicate')
        duplicate_mirror_action = menu.addAction('Duplicate and Mirror')
        menu.addSeparator()
        move_up_action = menu.addAction('Move Up')
        move_down_action = menu.addAction('Move Down')
        menu.addSeparator()
        delete_action = menu.addAction('Delete')
        menu.addSeparator()
        selected_action = menu.exec_(QtGui.QCursor().pos())
        selected_item = self.rig_tree.currentItem()

        if selected_action == enabled_action:
            selected_item.set_enabled(not(selected_item.is_enabled()))

        elif selected_action == edit_action:
            self.open_edit_task_dialog(selected_item)

        elif selected_action == setup_action:
            selected_item.task_spec.setUp()

        elif selected_action == delete_action:
            self.rig_tree.delete_item()

        elif selected_action == move_up_action:
            self.rig_tree.move_up_item()

        elif selected_action == move_down_action:
            self.rig_tree.move_down_item()

        elif selected_action == duplicate_action:
            self.rig_tree.duplicate_task()

        elif selected_action == duplicate_mirror_action:
            self.rig_tree.duplicate_mirror_task()

    def show_group_popup(self):
        menu = QtWidgets.QMenu(self)
        rename_action = menu.addAction('Rename Group')
        menu.addSeparator()
        duplicate_action = menu.addAction('Duplicate')
        mirror_action = menu.addAction('Duplicate and Mirror')
        menu.addSeparator()
        move_up_action = menu.addAction('Move Up')
        move_down_action = menu.addAction('Move Down')
        menu.addSeparator()
        delete_action = menu.addAction('Delete')
        menu.addSeparator()
        selected_action = menu.exec_(QtGui.QCursor().pos())
        selected_item = self.rig_tree.currentItem()

        if selected_action == rename_action:
            self.open_edit_group_dialog(selected_item)

        elif selected_action == duplicate_action:
            self.rig_tree.duplicate_group()

        elif selected_action == mirror_action:
            self.rig_tree.duplicate_mirror_group()

        elif selected_action == move_up_action:
            self.rig_tree.move_up_item()

        elif selected_action == move_down_action:
            self.rig_tree.move_down_item()

        elif selected_action == delete_action:
            self.rig_tree.delete_item()

    def double_click_tree(self, item):
        if item.type() == TREE_TASK_TYPE:
            self.open_edit_task_dialog(item)
        elif item.type() == TREE_GROUP_TYPE:
            self.open_edit_group_dialog(item)
        else:
            return False

    def open_edit_group_dialog(self, item):
        name, accepted = QtWidgets.QInputDialog.getText(self, 'Rename Group', item.name())
        if accepted and name:
            while name in [x.name() for x in self.rig_tree.get_group_items()]:
                name = '{oldName}Copy'.format(oldName=name)
            item.set_name(name)

    def open_edit_task_dialog(self, item):
        edit_task_dialog = EditTaskDialog(self)
        edit_task_dialog.task_header.update_from_task(item)
        edit_task_dialog.set_task_widget(item.get_form())
        edit_task_dialog.set_task_info(item.task_spec.task().task_type, item.task_spec.task().config['version'])
        edit_task_dialog.accepted.connect(lambda x=item.task_spec, y=edit_task_dialog.get_data(): self.update_task_spec(x, y))

        edit_task_dialog.resize(350, 450)
        main_window = self.parentWidget()
        edit_task_dialog.move(main_window.width()+main_window.x(), main_window.y())
        edit_task_dialog.show()

        return edit_task_dialog


class AddTaskDialog(QtWidgets.QDialog):
    """A dialog that lists the available tasks to add to a Blueprint.

    A user selects a task from the list, and adds it with the OK button.
    """
    def __init__(self, parent=None):
        super(AddTaskDialog, self).__init__(parent=parent)

        self.task_list = QtWidgets.QListWidget()
        self.task_info = QtWidgets.QTextEdit()
        task_layout = QtWidgets.QHBoxLayout()
        task_layout.addWidget(self.task_list)
        task_layout.addWidget(self.task_info)

        self.ok_button = QtWidgets.QPushButton('OK')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        submit_layout = QtWidgets.QHBoxLayout()
        submit_layout.addWidget(self.ok_button)
        submit_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(task_layout)
        main_layout.addLayout(submit_layout)
        self.setLayout(main_layout)

        self.setWindowTitle('Select a Task')
        self.task_info.setReadOnly(True)

        self.task_list.itemClicked.connect(self.update_task_info)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        for task_name in sorted(py_tasker.tasks.TASK_CACHE.keys()):
            task_list_item = QtWidgets.QListWidgetItem(task_name)
            self.task_list.addItem(task_list_item)

    def update_task_info(self, item):
        task_name = item.data(QtCore.Qt.DisplayRole)
        self.task_info.setText(py_tasker.tasks.TASK_CACHE[task_name].config['description'])


class EditTaskDialog(QtWidgets.QDialog):
    """A dialog to edit TaskSpec Parameter values."""
    DATA_WIDGETS = dict()

    def __init__(self, parent=None):
        super(EditTaskDialog, self).__init__(parent=parent)

        self.task_header = TaskHeaderWidget()
        self.task_settings = QtWidgets.QWidget()
        self.task_settings_layout = QtWidgets.QVBoxLayout()
        self.task_settings.setLayout(self.task_settings_layout)
        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.task_settings)
        self.task_info_label = QtWidgets.QLabel('')

        self.ok_button = QtWidgets.QPushButton('OK')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        submit_layout = QtWidgets.QHBoxLayout()
        submit_layout.addWidget(self.ok_button)
        submit_layout.addWidget(self.cancel_button)

        # top layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self.task_header)
        main_layout.addWidget(self.scroll)
        main_layout.addWidget(self.task_info_label)
        main_layout.addLayout(submit_layout)

        self.setLayout(main_layout)

        self.setWindowModality(QtCore.Qt.NonModal)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Edit Selected Task')

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    @classmethod
    def data_type_widget(cls, widget):
        cls.DATA_WIDGETS[widget.VALUE_TYPE] = widget

        return widget

    def set_task_widget(self, task_widget):
        self.task_settings_layout.addWidget(task_widget)

    def set_task_info(self, plugin_type, version_number):
        label = '<font color=#666666>Plugin Type: {0}  Version: {1}</font>'
        self.task_info_label.setText(label.format(plugin_type, version_number))

    def get_data(self):
        return self.task_settings_layout.itemAt(0).widget().widgetMap


class TaskHeaderWidget(QtWidgets.QWidget):
    options_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'options_icon.png')
    debug_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'debug_icon.png')

    def __init__(self, parent=None):
        super(TaskHeaderWidget, self).__init__(parent=parent)

        self.task_item = None

        self.name_field = QtWidgets.QLineEdit()
        self.debug_button = QtWidgets.QPushButton(QtGui.QIcon(self.debug_icon_path), '')
        self.options_button = QtWidgets.QPushButton(QtGui.QIcon(self.options_icon_path), '')

        # top layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.name_field)
        main_layout.addWidget(self.debug_button)
        main_layout.addWidget(self.options_button)

        self.setLayout(main_layout)
        self.setObjectName('TaskSettingsHeaderWidget')

        # default settings
        self.debug_button.setToolTip('Toggle between Task debug and info logger levels')
        self.options_button.setToolTip('Show Task options')

        # signals
        self.name_field.textChanged.connect(self.update_task_name)
        self.options_button.clicked.connect(self.show_options_menu)
        self.debug_button.clicked.connect(self.toggle_task_debug)

    def update_task_name(self):
        self.task_item.setData(0, QtCore.Qt.DisplayRole, self.name_field.text())
        self.task_item.task_spec.name = self.name_field.text()

    def update_from_task(self, task_item):
        self.task_item = task_item
        self.name_field.setText(task_item.task_spec.name)
        self.update_debug_icon(task_item.task_spec.debug)

    def update_icon(self, icon_path, value):
        pixmap = QtGui.QPixmap(icon_path)
        mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)
        if value:
            pixmap.fill((QtGui.QColor(0, 200, 150)))
        else:
            pixmap.fill((QtGui.QColor(0, 0, 0)))
        pixmap.setMask(mask)

        return QtGui.QIcon(pixmap)

    def toggle_task_debug(self):
        value = self.task_item.task_spec.debug
        self.update_debug_icon(not(value))
        self.task_item.task_spec.debug = not(value)

    def update_debug_icon(self, value):
        icon = self.update_icon(self.debug_icon_path, value)
        self.debug_button.setIcon(icon)

    def show_options_menu(self):
        menu = QtWidgets.QMenu(self)
        toggle_action = menu.addAction('Toggle On/Off')
        run_setup_action = menu.addAction('Run Task SetUp')
        result = menu.exec_(QtGui.QCursor().pos())

        if result == toggle_action:
            value = self.selected_task_item.is_enabled()
            self.task_item.set_enabled(not(value))
        elif result == run_setup_action:
            self.task_item.task_spec.setUp()


def getTaskInput(task_item):
    """Gets a TaskSpec and configures a layout with the appropriate widgets for each Parameter of a TaskSpec."""
    layout = QtWidgets.QGridLayout()
    layout.setAlignment(QtCore.Qt.AlignTop)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(4)

    widgetMap = dict()

    row = 0

    for param_name, param_value in task_item.params().items():
        label = QtWidgets.QLabel(param_name)
        label.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(label, row, 0)

        value_type = task_item.task().params[param_name].paramType
        widgetType = EditTaskDialog.DATA_WIDGETS.get(value_type, 'unknown')
        kw = dict()
        kw['choices'] = task_item.task().params[param_name].choices()
        kw['children'] = task_item.task().params[param_name].children()
        widget = widgetType(param_value, **kw)
        widget.setToolTip(task_item.task().params[param_name].description)

        layout.addWidget(widget, row, 1)
        widgetMap[param_name] = widget
        row += 1

    return layout, widgetMap


class RigTreeWidget(QtWidgets.QTreeWidget):
    """Widget for the rig build tree on the rig page tab."""
    def __init__(self, parent=None):
        super(RigTreeWidget, self).__init__(parent=parent)

        self.setHeaderLabel('Rig Build')
        self.header().hide()

        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Return, QtCore.Qt.Key_Backspace]:
            self.delete_item()
            event.accept()
        elif event.key() == QtCore.Qt.Key_E:
            self.parentWidget().open_edit_task_dialog(self.currentItem())
        elif event.key() == QtCore.Qt.Key_D:
            if self.currentItem().type() == TREE_GROUP_TYPE:
                self.duplicate_group()
            else:
                self.duplicate_task()
        elif event.key() == QtCore.Qt.Key_M:
            if self.currentItem().type() == TREE_GROUP_TYPE:
                self.duplicate_mirror_group()
            else:
                self.duplicate_mirror_task()
        elif event.key() == QtCore.Qt.Key_T:
            if self.currentItem().type() == TREE_GROUP_TYPE:
                for item in self.currentItem().get_task_items():
                    item.set_enabled(not (item.is_enabled()))
            else:
                self.currentItem().set_enabled(not (self.currentItem().is_enabled()))

        super(RigTreeWidget, self).keyPressEvent(event)

    def dropEvent(self, event):
        children = self.selectedItems()
        parents = [x.parent() for x in children]

        if any([True if x.type() == TREE_GROUP_TYPE else False for x in children]):
            target_item = self.itemAt(event.pos())
            if target_item and target_item.type() == TREE_GROUP_TYPE:
                event.setDropAction(QtCore.Qt.IgnoreAction)
                return

        super(RigTreeWidget, self).dropEvent(event)

        for child in children:
            if child.type() == TREE_GROUP_TYPE:
                continue
            parent_item = child.parent()
            if parent_item:
                parent_item.set_name(parent_item.name())
                child.set_group(parent_item.name())
            else:
                child.set_group(None)

        for parent in parents:
            if parent:
                parent.set_name(parent.name())

    def add_group(self, name, task_items=None):
        while name in [x.name() for x in self.get_group_items()]:
            name = '{oldName}Copy'.format(oldName=name)

        grp = TreeGroupWidget(name)
        self.addTopLevelItem(grp)
        if task_items:
            for item in task_items:
                grp.add_task_item(item)

    def add_task(self, task_type):
        task_obj = py_tasker.tasks.TASK_CACHE[task_type]
        task_spec = core.MayaTaskSpec(task_obj, task_obj.config['title'])
        task_item = TreeTaskWidget(task_spec)
        self.addTopLevelItem(task_item)

    def get_group_item(self, name):
        groups = {x.name(): x for x in self.get_group_items()}

        return groups.get(name, None)

    def get_group_items(self):
        result = list()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if item.type() == TREE_GROUP_TYPE:
                result.append(item)

        return result

    def get_task_items(self):
        result = list()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if item.type() == TREE_TASK_TYPE:
                result.append(item)
            elif item.type() == TREE_GROUP_TYPE:
                result.extend(item.get_task_items())
            else:
                continue

        return result

    def duplicate_group(self, item=None):
        if not item:
            item = self.currentItem()

        name = item.name()
        while name in [x.name() for x in self.get_group_items()]:
            name = '{oldName}Copy'.format(oldName=name)
        duplicated_item = TreeGroupWidget(name)

        self.addTopLevelItem(duplicated_item)

        for task_item in item.get_task_items():
            self.duplicate_task(task_item, duplicated_item)

        duplicated_item.set_name(duplicated_item.name())

    def duplicate_mirror_group(self, item=None):
        if not item:
            item = self.currentItem()

        name = core.MayaTaskSpec.mirror_name(item.name())
        while name in [x.name() for x in self.get_group_items()]:
            name = '{oldName}Copy'.format(oldName=name)
        duplicated_item = TreeGroupWidget(name)

        self.addTopLevelItem(duplicated_item)

        for task_item in item.get_task_items():
            self.duplicate_mirror_task(task_item, duplicated_item)

        duplicated_item.set_name(duplicated_item.name())

    def duplicate_task(self, item=None, parent_item=None):
        if not item:
            item = self.currentItem()

        if not parent_item:
            parent_item = item.parent()

        duplicated_spec = core.MayaTaskSpec.duplicate_spec(item.task_spec)
        duplicated_item = TreeTaskWidget(duplicated_spec)

        if parent_item:
            parent_item.addChild(duplicated_item)
            parent_item.set_name(parent_item.name())
            duplicated_item.set_group(parent_item.name())
        else:
            self.addTopLevelItem(duplicated_item)
            duplicated_item.set_group(None)

    def duplicate_mirror_task(self, item=None, parent_item=None):
        if not item:
            item = self.currentItem()

        if not parent_item:
            parent_item = item.parent()

        mirrored_spec = core.MayaTaskSpec.mirror_spec(item.task_spec)
        mirrored_item = TreeTaskWidget(mirrored_spec)

        if parent_item:
            parent_item.addChild(mirrored_item)
        else:
            self.addTopLevelItem(mirrored_item)

    def delete_item(self, item=None):
        if not item:
            item = self.currentItem()

        parent_item = item.parent()
        # remove item widget based on where it is parented
        if parent_item:
            item_index = parent_item.indexOfChild(item)
            item = item.parent().takeChild(item_index)
        else:
            item = self.takeTopLevelItem(self.currentIndex().row())
        # now delete the widget item instance
        del item

    def move_up_item(self, item=None):
        if not item:
            item = self.currentItem()

        parent_item = item.parent()
        # move the item widget up 1 row, does not move up past groups first index
        if parent_item:
            item_index = parent_item.indexOfChild(item)
            item = parent_item.takeChild(item_index)
            new_index = max(item_index - 1, 0)
            parent_item.insertChild(new_index, item)
        else:
            item_index = self.currentIndex().row()
            item = self.takeTopLevelItem(item_index)
            new_index = max(item_index - 1, 0)
            self.insertTopLevelItem(new_index, item)
        # set selected item back to old item, that is in new position
        self.setCurrentItem(item)

    def move_down_item(self, item=None):
        if not item:
            item = self.currentItem()

        parent_item = item.parent()
        # move the item widget down 1 row, does not move down past groups last index
        if parent_item:
            item_index = parent_item.indexOfChild(item)
            item = parent_item.takeChild(item_index)
            new_index = min(item_index + 1, parent_item.childCount())
            parent_item.insertChild(new_index, item)
        else:
            item_index = self.currentIndex().row()
            item = self.takeTopLevelItem(item_index)
            new_index = min(item_index + 1, self.topLevelItemCount())
            self.insertTopLevelItem(new_index, item)
        # set selected item back to old item, that is in new position
        self.setCurrentItem(item)


class TreeGroupWidget(QtWidgets.QTreeWidgetItem):
    """Widget that represents a build group in RigTreeWidget instance."""
    display_name_format = '{name} ({taskCount})'

    def __init__(self, name, parent=None):
        super(TreeGroupWidget, self).__init__(parent=parent, type=TREE_GROUP_TYPE)

        self._name = name

        self.setData(0, QtCore.Qt.DisplayRole, self.display_name_format.format(name=self._name, taskCount=0))
        self.setForeground(0, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setSizeHint(0, QtCore.QSize(50, 30))

    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        self.setData(0, QtCore.Qt.DisplayRole, self.display_name_format.format(name=self._name, taskCount=self.childCount()))
        for task_item in self.get_task_items():
            task_item.set_group(self._name)

    def add_task_item(self, item):
        if item.type() == TREE_TASK_TYPE:
            self.addChild(item)
            self.setData(0, QtCore.Qt.DisplayRole, self.display_name_format.format(name=self._name, taskCount=self.childCount()))

    def insert_task_item(self, index, item):
        if item.type() == TREE_TASK_TYPE:
            self.insertChild(index, item)
            self.setData(0, QtCore.Qt.DisplayRole, self.display_name_format.format(name=self._name, taskCount=self.childCount()))

    def get_task_items(self):
        return [self.child(index) for index in range(self.childCount())]


class TreeTaskWidget(QtWidgets.QTreeWidgetItem):
    """Widget that represents a task spec in RigTreeWidget instance."""
    enabled_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'enabled_icon.png')
    disabled_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'img', 'disabled_icon.png')

    task_status_role = QtCore.Qt.UserRole + 1
    task_debug_role = QtCore.Qt.UserRole + 2

    def __init__(self, task_spec, parent=None):
        super(TreeTaskWidget, self).__init__(parent=parent, type=TREE_TASK_TYPE)

        self.task_spec = task_spec

        self.setData(0, QtCore.Qt.DisplayRole, self.task_spec.name)
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)

        self.set_enabled(True)
        self.set_debug(False)

    def get_form(self):
        form_widget = QtWidgets.QWidget()
        form_layout, widget_map = getTaskInput(self.task_spec)
        form_widget.setLayout(form_layout)
        form_widget.widgetMap = widget_map
        return form_widget

    def set_group(self, group_name):
        self.task_spec.group = group_name

    def set_enabled(self, value):
        if value is False:
            self.set_off_style()
        else:
            self.set_on_style()

        self.setData(0, self.task_status_role, value)
        self.task_spec.enabled = value

    def is_enabled(self):
        return self.data(0, self.task_status_role)

    def set_debug(self, value):
        self.setData(0, self.task_debug_role, value)
        self.task_spec.debug = value

    def is_debug(self):
        return self.data(0, self.task_debug_role)

    def set_off_style(self):
        self.setForeground(0, QtGui.QBrush(QtGui.QColor(150, 150, 150)))
        self.setSizeHint(0, QtCore.QSize(50, 15))
        self.setFont(0, self.item_font())

    def set_on_style(self):
        self.setForeground(0, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setSizeHint(0, QtCore.QSize(50, 20))
        self.setFont(0, self.item_font())

    def enabled_icon(self):
        pixmap = QtGui.QPixmap(self.enabled_icon_path)
        mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)
        pixmap.fill((QtGui.QColor(0, 250, 150)))
        pixmap.setMask(mask)

        return QtGui.QIcon(pixmap)

    def disabled_icon(self):
        pixmap = QtGui.QPixmap(self.disabled_icon_path)
        pixmap = pixmap.copy(0, 0, 5, 5)
        mask = pixmap.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)
        pixmap.fill((QtGui.QColor(250, 0, 150)))
        pixmap.setMask(mask)

        return QtGui.QIcon(pixmap)

    def item_font(self):
        font = QtGui.QFont()
        font.setFamily('sans-serif')
        font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 110)

        return font


@EditTaskDialog.data_type_widget
class BoolParameterWidget(QtWidgets.QCheckBox):
    """Widget to store and display Parameters for boolean data with a QCheckBox."""
    VALUE_TYPE = 'bool'

    def __init__(self, current_value, **kwargs):
        super(BoolParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = False

        self.data = current_value

        self.setChecked(self.data)

        self.stateChanged.connect(self.setData)

    def setData(self, state):
        self.data = bool(state)


@EditTaskDialog.data_type_widget
class FloatParameterWidget(QtWidgets.QDoubleSpinBox):
    """Widget to store and display Parameters for float data with a QDoubleSpinBox."""
    VALUE_TYPE = 'float'

    def __init__(self, current_value, **kwargs):
        super(FloatParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = 0.0

        self.data = current_value

        self.setValue(self.data)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setMinimum(0.0)
        self.setMaximum(99.0)
        self.setDecimals(3)

        self.valueChanged.connect(self.setData)

    def setData(self, value):
        self.data = value


@EditTaskDialog.data_type_widget
class IntParameterWidget(QtWidgets.QSpinBox):
    """Widget to store and display Parameters for integer data with a QSpinBox."""
    VALUE_TYPE = 'int'

    def __init__(self, current_value, **kwargs):
        super(IntParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = 0

        self.data = current_value

        self.setValue(self.data)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setMinimum(0)
        self.setMaximum(99)

        self.valueChanged.connect(self.setData)

    def setData(self, value):
        self.data = value


@EditTaskDialog.data_type_widget
class StringParameterWidget(QtWidgets.QLineEdit):
    """Widget to store and display Parameters for string data with a QLineEdit."""
    VALUE_TYPE = 'string'

    def __init__(self, current_value, **kwargs):
        super(StringParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = ''

        self.data = current_value

        self.setText(self.data)

        self.textChanged.connect(self.setData)

    def setData(self, value):
        self.data = value


@EditTaskDialog.data_type_widget
class PythonParameterWidget(QtWidgets.QWidget):
    """Widget to store and display Parameters for python code with a cmdScrollFieldExecuter wrapped in a QTextEdit."""
    VALUE_TYPE = 'python'

    def __init__(self, current_value, **kwargs):
        super(PythonParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = ''

        self.data = current_value

        self.widget = QtWidgets.QTextEdit()
        self.widget.setText(self.data)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)
        self.setLayout(layout)

        # signals
        self.widget.textChanged.connect(self.setData)

    def setData(self):
        self.data = self.widget.toPlainText()


@EditTaskDialog.data_type_widget
class FilePathParameterWidget(QtWidgets.QWidget):
    """Widget to store and display file path Parameters using a QLineEdit and QPushButton to search for a path."""
    VALUE_TYPE = 'file_path'

    def __init__(self, current_value, **kwargs):
        super(FilePathParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = ''

        self.data = current_value

        self.widget = QtWidgets.QLineEdit(self.data)
        self.button = QtWidgets.QPushButton('...')

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.widget, 1)
        layout.addWidget(self.button, 0)

        self.setLayout(layout)

        self.button.setFixedWidth(27)

        self.widget.textChanged.connect(self.setData)
        self.button.clicked.connect(self.showFileSystemDialog)

    def setData(self, value):
        self.data = value

    def showFileSystemDialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.exec_()
        if dialog.selectedFiles():
            self.widget.setText(dialog.selectedFiles()[0])


@EditTaskDialog.data_type_widget
class EnumParameterWidget(QtWidgets.QWidget):
    """Widget to store and display enum type Parameters in a QComboBox format."""
    VALUE_TYPE = 'enum'

    def __init__(self, current_value, **kwargs):
        super(EnumParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = 0

        self.data = current_value

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QtWidgets.QComboBox()
        choices = kwargs.get('choices', [])
        sorted_choices = sorted(choices.iterkeys(), key=lambda k: choices[k])
        self.widget.addItems(sorted_choices)
        self.widget.setCurrentIndex(self.data)
        layout.addWidget(self.widget, 1)

        self.setLayout(layout)

        self.widget.currentIndexChanged.connect(self.setData)

    def setData(self, value):
        self.data = value


@EditTaskDialog.data_type_widget
class UnknownParameterWidget(QtWidgets.QLineEdit):
    """Widget to store and display Parameters that's value can not be solved or queried."""
    VALUE_TYPE = 'unknown'

    def __init__(self, current_value, **kwargs):
        super(UnknownParameterWidget, self).__init__(parent=None)

        self.data = current_value

        self.setText(str(current_value))
        self.setReadOnly(True)


@EditTaskDialog.data_type_widget
class CompoundParameterWidget(QtWidgets.QWidget):
    """Widget to store and display multi type Parameters that have multiple data types."""
    VALUE_TYPE = 'compound'

    def __init__(self, current_value, **kwargs):
        super(CompoundParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = []

        self._data = current_value
        self.children = kwargs.get('children', dict())

        add_element_button = QtWidgets.QPushButton('Add Element')

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(2)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_layout.addWidget(add_element_button, 1)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.main_layout)
        self.main_layout.addLayout(header_layout)

        self.element_layout = None
        self.show_elements()

        # signals
        add_element_button.clicked.connect(self.append_child)

    @property
    def data(self):
        result = list()

        for num, elem in enumerate(self._data):
            elem_result = dict()
            elem_widget = self.element_layout.itemAt(num).widget()
            param_layout = elem_widget.findChild(QtWidgets.QGridLayout, 'ChildParamLayout')

            for row in range(param_layout.rowCount()):
                k = param_layout.itemAtPosition(row, 0).widget().text()
                v = param_layout.itemAtPosition(row, 1).widget().data
                elem_result[k] = v
            result.append(elem_result)

        return result

    def clear_elements(self):
        if self.element_layout is not None:
            while self.element_layout.count():
                item = self.element_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            del self.element_layout
            self.element_layout = None

    def show_elements(self):
        self.clear_elements()

        self.element_layout = QtWidgets.QVBoxLayout()
        self.element_layout.setContentsMargins(0, 0, 0, 0)
        self.element_layout.setSpacing(2)
        self.element_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.addLayout(self.element_layout)

        self.set_children()

    def add_child(self, child_index=0, current_value=None):
        widget = QtWidgets.QWidget()
        widget_layout = QtWidgets.QVBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(0)
        widget.setLayout(widget_layout)

        element_label = QtWidgets.QLabel('<b>Element [{}]</b>'.format(child_index))
        child_remove_button = QtWidgets.QPushButton('x')
        child_remove_button.setFixedWidth(27)
        child_remove_button.clicked.connect(lambda x=child_index: self.remove_child(x))

        child_header_layout = QtWidgets.QHBoxLayout()
        child_header_layout.setAlignment(QtCore.Qt.AlignLeft)
        child_header_layout.setContentsMargins(0, 0, 0, 0)
        child_header_layout.setSpacing(5)
        child_header_layout.addWidget(element_label, 0)
        child_header_layout.addWidget(child_remove_button, 0)
        widget_layout.addLayout(child_header_layout)

        child_param_layout = QtWidgets.QGridLayout()
        child_param_layout.setObjectName('ChildParamLayout')
        child_param_layout.setContentsMargins(2, 2, 2, 2)
        child_param_layout.setSpacing(4)
        child_param_layout.setAlignment(QtCore.Qt.AlignTop)
        widget_layout.addLayout(child_param_layout)

        row = 0
        for param_name, param_obj in self.children.items():
            val = current_value.get(param_name, param_obj.defaultValue)
            widgetType = EditTaskDialog.DATA_WIDGETS.get(param_obj.paramType, 'unknown')
            kw = dict()
            if param_obj.paramType == 'enum':
                kw['choices'] = param_obj.choices()

            child_label = QtWidgets.QLabel(param_name)
            child_label.setAlignment(QtCore.Qt.AlignRight)
            child_widget = widgetType(val, **kw)
            child_widget.setToolTip(param_obj.description)

            child_param_layout.addWidget(child_label, row, 0)
            child_param_layout.addWidget(child_widget, row, 1)

            row += 1

        self.element_layout.addWidget(widget)

        return widget

    def append_child(self):
        new_data = self.data
        new_data.append({k: v.defaultValue for k, v in self.children.items()})
        self._data = new_data
        self.show_elements()

    def remove_child(self, child_index):
        self._data.pop(child_index)
        self.show_elements()

    def numElements(self):
        return len(self._data)

    def set_children(self):
        for n, elem in enumerate(self._data):
            self.add_child(n, elem)


@EditTaskDialog.data_type_widget
class NodeListParameterWidget(QtWidgets.QWidget):
    """Widget to store and display node names Parameter in a QListWidget with QPushButtons to add, remove,
    and clear the list.
    """
    listChanged = QtCore.Signal()

    VALUE_TYPE = 'nodeList'

    ID_ROLE = QtCore.Qt.UserRole + 1
    NAME_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, current_value, **kwargs):
        super(NodeListParameterWidget, self).__init__(parent=None)

        if current_value is None:
            current_value = []

        self.data = current_value

        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QtWidgets.QListWidget()

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumHeight(100)

        self.add_button = QtWidgets.QPushButton('+')
        self.remove_button = QtWidgets.QPushButton('-')
        self.clear_button = QtWidgets.QPushButton('x')

        layout.addWidget(self.widget, 0, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self.add_button, 0, 1, QtCore.Qt.AlignTop)
        layout.addWidget(self.remove_button, 0, 2, QtCore.Qt.AlignTop)
        layout.addWidget(self.clear_button, 0, 3, QtCore.Qt.AlignTop)

        self.setLayout(layout)

        if current_value:
            for node in current_value:
                node_item = QtWidgets.QListWidgetItem(node.name())
                node_item.setData(self.ID_ROLE, node.uuid())
                self.widget.addItem(node_item)

        # default settings
        self.widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.add_button.setFixedWidth(27)
        self.remove_button.setFixedWidth(27)
        self.clear_button.setFixedWidth(27)
        self.add_button.setToolTip('Add the selected nodes to this Parameter')
        self.remove_button.setToolTip('Remove the selected nodes from the Parameter')
        self.clear_button.setToolTip('Remove all nodes from the Parameter')

        # signals
        self.listChanged.connect(self.setData)
        self.widget.itemSelectionChanged.connect(self.select_node)
        self.add_button.clicked.connect(self.add_to_list)
        self.remove_button.clicked.connect(self.remove_from_list)
        self.clear_button.clicked.connect(self.clear_list)

    def select_node(self):
        node_ids = [x.data(self.ID_ROLE) for x in self.widget.selectedItems()]
        cmds.select(cmds.ls(node_ids), r=True)

    def add_to_list(self):
        selection = list()
        existing_uuids = [self.widget.item(x).data(self.ID_ROLE) for x in range(self.widget.count())]

        for sel in cmds.ls(sl=True, uuid=True):
            if sel in existing_uuids:
                continue
            selection.append(sel)

        for selected in selection:
            node_name = cmds.ls(selected)[0]
            node_item = QtWidgets.QListWidgetItem(node_name)
            node_item.setData(self.ID_ROLE, selected)
            self.widget.addItem(node_item)

        self.listChanged.emit()

    def remove_from_list(self):
        for x in self.widget.selectedItems():
            row = self.widget.row(x)
            item = self.widget.takeItem(row)
            del item
            self.listChanged.emit()

    def clear_list(self):
        self.widget.clear()
        self.listChanged.emit()

    def setData(self):
        new_node_list = [self.widget.item(x).data(self.ID_ROLE) for x in range(self.widget.count())]
        self.data = [node.dfNode(x) for x in new_node_list]


@EditTaskDialog.data_type_widget
class NodeParameterWidget(QtWidgets.QWidget):
    """Widget to store and display a node name Parameter in a QLineEdit with QPushButtons to add and clear the field."""

    VALUE_TYPE = 'node'

    def __init__(self, current_value, **kwargs):
        super(NodeParameterWidget, self).__init__(parent=None)

        self.data = current_value

        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton('+')
        self.clear_button = QtWidgets.QPushButton('x')

        layout.addWidget(self.widget, 0, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self.add_button, 0, 1, QtCore.Qt.AlignTop)
        layout.addWidget(self.clear_button, 0, 2, QtCore.Qt.AlignTop)

        self.setLayout(layout)

        if current_value is not None:
            self.widget.setText(current_value.name())

        # default settings
        self.widget.setReadOnly(True)
        self.add_button.setFixedWidth(27)
        self.clear_button.setFixedWidth(27)
        self.add_button.setToolTip('Set this Parameter to the selected node')
        self.clear_button.setToolTip('Clear this Parameter')

        # signals
        self.add_button.clicked.connect(self.add_to_list)
        self.clear_button.clicked.connect(self.clear_list)

    def add_to_list(self):
        dfnode = node.dfNode.fromSelection()[0]
        self.widget.setText(dfnode.name())
        self.data = dfnode

    def clear_list(self):
        self.widget.clear()
        self.data = None


class PropertiesWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PropertiesWidget, self).__init__(parent=parent)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(3, 5, 3, 10)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        self.header = QtWidgets.QWidget()
        self.panel_count_spinbox = QtWidgets.QSpinBox()
        self.panel_lock_button = QtWidgets.QPushButton('lock')
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.header.setLayout(header_layout)

        self.panels = QtWidgets.QWidget()

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.panels)

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.scroll)