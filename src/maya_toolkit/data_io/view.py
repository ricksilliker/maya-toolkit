
import os
import logging
import subprocess

from Qt import QtWidgets, QtCore, QtGui

import qt_utils.core
reload(qt_utils.core)

import core
reload(core)

import skinCluster_io
reload(skinCluster_io)

import blendShape_io
reload(blendShape_io)

import curve_io
reload(curve_io)

import attribute_io
reload(attribute_io)

import maya.cmds as cmds
import maya.mel as mel

global skin_per_file

LOG = logging.getLogger(__name__)
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')


STYLESHEET = '''
QPushButton {
    background: #555;
    border: 0px solid #333;
    font-size: 12pt;
    font-weight: 600;
    color: lightgrey;
}

QPushButton:hover {
    color: white;
    background: #666;
}
QTextEdit#OutputWin {font: 24pt Courier; color: lightgrey; font-size: 10pt;}
QPushButton#QueryButton { color: lightgrey; font-size: 14pt; font-family: "FontAwesome"; }
QPushButton#EditFileButton { color: lightgrey; font-size: 14pt; font-family: "FontAwesome"; }
QPushButton#RefreshFileButton { color: lightgrey; font-size: 14pt; font-family: "FontAwesome"; }
QPushButton#BrowseFileButton { color: lightgrey; font-size: 14pt; font-family: "FontAwesome"; }
'''


def show(dockable=False, currentTab=0):
    """Shows the PyQt UI for Data IO

    Returns:
        QtWidgets.QWidget: The DataIOMainWidget object
    """
    app = qt_utils.core.fetch_maya_window()
    win = DataIOMainWidget(parent=app, currentTab=currentTab)

    if dockable:
        qt_utils.core.dock_widget_2016(win)
    else:
        win.show()
        win.resize(542, 200)

    return win


class DataIOMainWidget(QtWidgets.QWidget):
    """Main UI widget."""
    def __init__(self, parent=None, currentTab=1):
        super(DataIOMainWidget, self).__init__(parent=parent)

        #global skin_per_file

        # Stylesheet and  fonts
        self.setStyleSheet(STYLESHEET)
        add_fonts(FONT_PATH)

        main_layout = QtWidgets.QVBoxLayout()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)

        # Main menu bar and menus
        self.menu = QtWidgets.QMenuBar()

        # Settings menu...
        #rel_paths_action = QtWidgets.QAction('Use relative paths...', self)
        file_menu = self.menu.addMenu('Settings')
        #file_menu.addAction(rel_paths_action)

        # Utils menu...
        utils_menu = self.menu.addMenu('Utils')
        project_submenu = QtWidgets.QMenu('Project')
        utils_menu.addMenu(project_submenu)

        file_explore_action = QtWidgets.QAction('Explore to current directory...', self)
        set_project_action = QtWidgets.QAction('Set Maya project...', self)
        project_submenu.addAction(file_explore_action)
        project_submenu.addAction(set_project_action)

        skin_submenu = QtWidgets.QMenu('Skin Cluster')
        utils_menu.addMenu(skin_submenu)
        skin_xfer_action = QtWidgets.QAction('Transfer skin from source to target...', self)
        skin_submenu.addAction(skin_xfer_action)

        curves_submenu = QtWidgets.QMenu('Curves')
        utils_menu.addMenu(curves_submenu)
        curve_shape_rename_action = QtWidgets.QAction('Rename curve control shapes...', self)
        curves_submenu.addAction(curve_shape_rename_action)

        help_menu = self.menu.addMenu('Help')

        main_layout.addWidget(self.menu)

        separator = qt_utils.core.QHLine()
        main_layout.addWidget(separator)

        # ROWS - For each area of UI - Tabs, file path, import/export buttons, log window
        row_tabs = QtWidgets.QHBoxLayout()
        main_layout.layout().addLayout(row_tabs)

        row_file = QtWidgets.QHBoxLayout()
        main_layout.layout().addLayout(row_file)

        row_buttons = QtWidgets.QHBoxLayout()
        main_layout.layout().addLayout(row_buttons)

        row_logger = QtWidgets.QHBoxLayout()
        main_layout.layout().addLayout(row_logger)

        # CREATE TABS
        self.skinCluster_tab = SkinClusterWidget(self)
        self.blendShape_tab = BlendShapesWidget(self)
        self.controlCurves_tab = ControlCurvesWidget(self)
        self.attrs_tab = AttrsWidget(self)
        self.setDrivenKey_tab = SetDrivenKeyWidget(self)
        self.shapes_tab = ShapesWidget(self)

        # ADD TABS
        self.tabs_widget = QtWidgets.QTabWidget()
        self.tabs_widget.addTab(self.skinCluster_tab, 'Skin Cluster')
        self.tabs_widget.addTab(self.blendShape_tab, 'Blendshapes')
        self.tabs_widget.addTab(self.controlCurves_tab, 'Control Curves')
        self.tabs_widget.addTab(self.attrs_tab, 'Attributes')
        self.tabs_widget.addTab(self.setDrivenKey_tab, 'Set Driven Key')
        self.tabs_widget.addTab(self.shapes_tab, 'SHAPES')
        self.tabs_widget.setFixedHeight(120)
        row_tabs.addWidget(self.tabs_widget)

        # FILE PATH Section
        self.QueryButton = QtWidgets.QPushButton(u'\uf128')
        self.QueryButton.setObjectName("QueryButton")
        self.QueryButton.setFixedHeight(35)
        self.QueryButton.setFixedWidth(35)

        self.EditFileButton = QtWidgets.QPushButton(u'\uf044')
        self.EditFileButton.setObjectName("EditFileButton")
        self.EditFileButton.setFixedHeight(35)
        self.EditFileButton.setFixedWidth(35)
        
        self.FilePathLine = QtWidgets.QLineEdit()
        self.FilePathLine.setObjectName("FilePathLine")
        self.FilePathLine.setFixedHeight(35)

        filepath_font = self.FilePathLine.font()
        filepath_font.setPointSize(11)
        self.FilePathLine.setFont(filepath_font)

        self.RefreshFileButton = QtWidgets.QPushButton(u'\uf01e')
        self.RefreshFileButton.setObjectName("RefreshFileButton")
        self.RefreshFileButton.setFixedHeight(35)
        self.RefreshFileButton.setFixedWidth(35)

        self.BrowseFileButton = QtWidgets.QPushButton(u'\uf07c')
        self.BrowseFileButton.setObjectName("BrowseFileButton")
        self.BrowseFileButton.setFixedHeight(35)
        self.BrowseFileButton.setFixedWidth(35)
        self.BrowseFileButton.clicked.connect(self.file_browser)

        row_file.addWidget(self.QueryButton)
        row_file.addWidget(self.EditFileButton)
        row_file.addWidget(self.FilePathLine)
        row_file.addWidget(self.RefreshFileButton)
        row_file.addWidget(self.BrowseFileButton)

        # IMPORT / EXPORT BUTTON Section
        self.importBTN = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.importBTN.setFont(font)
        self.importBTN.setObjectName("importSkinWeightsBTN")
        self.importBTN.setText("IMPORT")
        self.importBTN.setFixedHeight(35)

        self.exportBTN = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.exportBTN.setFont(font)
        self.exportBTN.setObjectName("exportBTN")
        self.exportBTN.setText("EXPORT")
        self.exportBTN.setFixedHeight(35)

        row_buttons.addWidget(self.importBTN)
        row_buttons.addWidget(self.exportBTN)

        # OUTPUT LOG Section
        self.OutputWin = QtWidgets.QTextEdit()
        self.OutputWin.setObjectName("OutputWin")
        self.OutputWin.setReadOnly(True)
        self.OutputWin.setFixedHeight(150)
        vbox.addWidget(self.OutputWin)
        main_layout.addLayout(vbox)

        # SETTINGS
        self.setAcceptDrops(True)
        self.setLayout(main_layout)
        self.setObjectName('DataIOWidget')
        self.setWindowTitle('Data IO')
        self.setWindowFlags(qt_utils.core.get_os_window_type())
        self.output = 'Data IO initialized...\n'

        # SIGNALS
        self.tabs_widget.currentChanged.connect(self.tab_selector)
        self.RefreshFileButton.clicked.connect(self.refreshFilename)
        self.importBTN.clicked.connect(self.tab_import)
        self.exportBTN.clicked.connect(self.tab_export)
        self.QueryButton.clicked.connect(self.tab_query)
        self.EditFileButton.clicked.connect(self.edit_file)

        file_explore_action.triggered.connect(self.file_explorer)
        skin_xfer_action.triggered.connect(self.call_skin_xfer)
        curve_shape_rename_action.triggered.connect(self.call_curve_shape_rename)

        # HELP/TIPS - This is not working right now
        self.BrowseFileButton.setToolTip('Browse to existing file')
        self.RefreshFileButton.setToolTip('Refreshes file field based on current selection')
        self.QueryButton.setToolTip('Prints information about skinCluster on selected objects in scene')
        self.EditFileButton.setToolTip('Opens current file in text editor for editing')
        self.importBTN.setToolTip('Imports data from file in file field')
        self.exportBTN.setToolTip('Exports data to file in file field')

        self.refreshUI()
        self.tabs_widget.setCurrentIndex(currentTab)
        self.tab_selector(currentTab)

    def refreshUI(self):
        self.OutputWin.setText(self.output)

    def refreshFilename(self):
        current_tab = self.tabs_widget.currentIndex()
        self.tab_selector(current_tab)
        LOG.info("Refreshing file name")

    def file_browser(self, file_filter="Json files (*.json)"):
        sel_file = cmds.fileDialog2(fileFilter=file_filter, dialogStyle=2, fm=1)
        rel_path = return_relative_path(sel_file[0])
        self.FilePathLine.setText(rel_path)

    def file_explorer(self):
        current_file_path = self.FilePathLine.text()
        full_file_path = resolve_file_path(os.path.dirname(current_file_path))
        subprocess.Popen(r'explorer "{}"'.format(full_file_path.replace("/", "\\")))
        LOG.info('Exploring to {}'.format(full_file_path))

    def call_skin_xfer(self):
        skinCluster_io.quickTransferSkinCluster()
        LOG.info('Transferred skin clusters...')

    def call_curve_shape_rename(self):
        curve_io.rename_curve_shapes()
        LOG.info('Renamed curve control shapes...')

    def tab_selector(self, selected_index):
        """Updates tab data when tabs selected"""
        selected = cmds.ls(selection=True)

        # Skin Cluster Tab
        if selected_index == 0:
            LOG.info("Skin Cluster tab selected...")
            file_type = self.skinCluster_tab.file_type
            subdir = self.skinCluster_tab.subdir
            self.FilePathLine.setText(return_default_file_path(subdir=subdir, extension=file_type))

        # Blendshape Tab
        elif selected_index == 1:
            LOG.info("Blendshape tab selected...")
            subdir = self.blendShape_tab.subdir
            self.blendShape_tab.bshp_imp_widgetB.clear()

            if selected:
                bs = blendShape_io.return_blendshape_from_mesh(mesh_name=selected[0])
                if bs:
                    file_name = "{}{}__{}.json".format(subdir, selected[0], bs[0])
                    self.FilePathLine.setText(file_name)
                    self.blendShape_tab.bshp_imp_widgetB.addItems(bs)
            else:
                self.FilePathLine.setText(subdir)
                self.blendShape_tab.bshp_imp_widgetB.addItems(['Please select mesh with blendShape and hit reload button...'])

        # Control Curve Tab
        elif selected_index == 2:
            LOG.info("Control Curve tab selected...")
            file_type = self.controlCurves_tab.file_type
            subdir = self.controlCurves_tab.subdir
            file_name = "{}control{}".format(subdir, file_type)
            self.FilePathLine.setText(file_name)

        # Attributes Tab
        elif selected_index == 3:
            LOG.info("Attributes tab selected...")
            file_type = self.attrs_tab.file_type
            subdir = self.attrs_tab.subdir
            file_name = "{}node{}".format(subdir, file_type)
            self.FilePathLine.setText(file_name)

        # Set Driven Key Tab
        elif selected_index == 4:
            LOG.info("Set Driven Key tab selected...")
            file_type = self.setDrivenKey_tab.file_type
            subdir = self.setDrivenKey_tab.subdir
            file_name = "{}node{}".format(subdir, file_type)
            self.FilePathLine.setText(file_name)

        # SHAPES Tab
        elif selected_index == 5:
            LOG.info("SHAPES tab selected...")
            subdir = self.shapes_tab.subdir
            self.FilePathLine.setText(subdir)

        self.refreshUI()

    def tab_export(self):
        """Calls proper data export function based on current tab"""
        currentTab = self.tabs_widget.currentIndex()
        selected = cmds.ls(selection=True)

        if selected:
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)

            if currentTab == 0:
                LOG.info("Exporting skin cluster data...")
                global skin_per_file
                #global skin_use_long_names
                self.output = ""
                self.refreshUI()
                self.output += skinCluster_io.call_exportSkinWeight(full_file_path, selected, per_file=skin_per_file)
                self.refreshUI()

            elif currentTab == 1:
                LOG.info("Exporting blendShape data...")
                bs_node = self.blendShape_tab.bshp_imp_widgetB.currentText()
                self.output = ""
                self.refreshUI()
                self.output += blendShape_io.call_export_blendshape(full_file_path, selected[0], blendshape_node=bs_node)
                self.refreshUI()

            elif currentTab == 2:
                LOG.info("Exporting control curve data...")
                self.output = ""
                self.refreshUI()
                self.output += curve_io.call_export_control_curves(full_file_path)
                self.refreshUI()

            elif currentTab == 3:
                LOG.info("Exporting attribute data...")
                global selected_attrs
                global locked_attrs
                self.output = ""
                self.refreshUI()
                self.output += attribute_io.call_export_attributes(full_file_path, selected_attrs=selected_attrs, locked_channels=locked_attrs)
                self.refreshUI()

            elif currentTab == 4:
                LOG.info("Exporting set driven keyframe data...")
                self.output = ""
                self.refreshUI()
                self.refreshUI()

            elif currentTab == 5:
                LOG.info("Exporting SHAPES data...")
                self.output = ""
                self.refreshUI()
                #self.output +=
                mel.eval("SHAPES;")
                mel.eval("shapesMain_getMeshSelection 0;")
                mel.eval("shapesUI_buildExportUI 1;")
                self.refreshUI()
        else:
            LOG.error("Nothing selected to export!")

    def tab_import(self):
        """Calls proper data import function based on current tab"""
        global selected_only

        currentTab = self.tabs_widget.currentIndex()

        if currentTab == 0:
            LOG.info("Importing skin cluster data...")
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)
            skinCluster_io.importSkinWeight(full_file_path, [], selected=selected_only)

        elif currentTab == 1:
            LOG.info("Importing blendShape data...")
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)
            blendShape_io.import_blendshape(full_file_path)

        elif currentTab == 2:
            LOG.info("Importing control curve data...")
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)
            curve_io.import_control_curves(full_file_path)

        elif currentTab == 3:
            LOG.info("Importing attribute data...")
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)
            attribute_io.import_attributes(full_file_path)

        elif currentTab == 4:
            LOG.info("Importing Set Driven Keyframe data...")
            current_file_path = self.FilePathLine.text()
            full_file_path = resolve_file_path(current_file_path)

        elif currentTab == 5:
            LOG.info("Importing SHAPES blendshape data...")
            #current_file_path = self.FilePathLine.text()
            #full_file_path = resolve_file_path(current_file_path)
            mel.eval("SHAPES;")
            mel.eval('shapesUtil_importFromCustomPath "D:/dev/reef/SourceArt/Characters/RainbowParrot/Rig/work/RainbowParrot/data/SHAPES/setup";')

    def tab_query(self):
        """Calls proper data query function based on current tab"""
        currentTab = self.tabs_widget.currentIndex()

        selected = cmds.ls(selection=True)

        if selected:
            if currentTab == 0:
                LOG.info("Querying skinCluster data...")
                self.output = ""
                for item in selected:
                    print "Working on: {}".format(item)
                    self.output += skinCluster_io.query_skin_cluster(item)
                self.refreshUI()

            elif currentTab == 1:
                LOG.info("Querying blendShape data...")

            elif currentTab == 2:
                LOG.info("Querying control curve data...")

            elif currentTab == 3:
                LOG.info("Querying attribute data...")

            elif currentTab == 4:
                LOG.info("Querying set driven key data...")

            elif currentTab == 5:
                LOG.info("SHAPES data...")

    def edit_file(self):
        """Opens current file in Notepad (for now)"""
        current_file = resolve_file_path(self.FilePathLine.text())
        if os.path.isfile(current_file):
            try:
                LOG.info("Opening file: {}".format(current_file))
                subprocess.Popen([
                    r'C:\Program Files (x86)\Notepad++\notepad++.exe',
                    current_file
                ])
            except:
                raise Exception ("Cannot open {}".format(current_file))
        else:
            LOG.warning("File does not exist: {}".format(current_file))


class ShapesWidget(QtWidgets.QWidget):
    """SHAPES tab widget"""

    def __init__(self, parent=None):
        super(ShapesWidget, self).__init__(parent=parent)

        # DATA TYPE INFO
        self.file_type = ""
        self.subdir = 'data/SHAPES/setup/'

        # HELP TEXT
        self.shps_help_text = "Use to import or export SHAPES data to/from a file."
        self.shps_VertLayout = QtWidgets.QVBoxLayout(self)
        self.shps_widget_help = QtWidgets.QLabel(self.shps_help_text)
        shps_help_font = QtGui.QFont()
        shps_help_font.setBold(True)
        self.shps_widget_help.setFont(shps_help_font)
        self.shps_VertLayout.addWidget(self.shps_widget_help)
        self.shps_widget_help.setFixedHeight(15)
        self.shps_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.shps_hbox = QtWidgets.QHBoxLayout()
        self.shps_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.shps_VertLayout.addLayout(self.shps_hbox)

        self.shps_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.shps_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.shps_hbox.addLayout(self.shps_import_VertLayout)
        self.shps_hbox.addLayout(self.shps_export_VertLayout)
        self.shps_import_VertLayout.setSpacing(20)
        self.shps_export_VertLayout.setSpacing(20)
        self.shps_hbox.addStretch(1)
        self.shps_import_VertLayout.addStretch(1)
        self.shps_export_VertLayout.addStretch(1)

        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.shps_imp_widgetA = QtWidgets.QLabel("Select mesh with blendshape and hit import/export buttons below to open SHAPES option window...")
        self.shps_imp_widgetB = QtWidgets.QLabel("(requires SHAPES installed on current machine)")
        self.shps_imp_widgetC = QtWidgets.QLabel()
        self.shps_imp_widgetD = QtWidgets.QLabel()

        self.shps_exp_widgetA = QtWidgets.QLabel()
        self.shps_exp_widgetB = QtWidgets.QLabel()
        self.shps_exp_widgetC = QtWidgets.QLabel()
        self.shps_exp_widgetD = QtWidgets.QLabel()

        self.shps_import_VertLayout.addWidget(self.shps_imp_widgetA)
        self.shps_import_VertLayout.addWidget(self.shps_imp_widgetB)
        self.shps_import_VertLayout.addWidget(self.shps_imp_widgetC)
        self.shps_import_VertLayout.addWidget(self.shps_imp_widgetD)

        self.shps_export_VertLayout.addWidget(self.shps_exp_widgetA)
        self.shps_export_VertLayout.addWidget(self.shps_exp_widgetB)
        self.shps_export_VertLayout.addWidget(self.shps_exp_widgetC)
        self.shps_export_VertLayout.addWidget(self.shps_exp_widgetD)

        self.shps_imp_widgetA.setFixedHeight(20)
        self.shps_imp_widgetB.setFixedHeight(20)
        self.shps_imp_widgetC.setFixedHeight(20)
        self.shps_imp_widgetD.setFixedHeight(20)

        self.shps_exp_widgetA.setFixedHeight(20)
        self.shps_exp_widgetB.setFixedHeight(20)
        self.shps_exp_widgetC.setFixedHeight(20)
        self.shps_exp_widgetD.setFixedHeight(20)
        
        
class ControlCurvesWidget(QtWidgets.QWidget):
    """Control Curve tab widget"""
    def __init__(self, parent=None):
        super(ControlCurvesWidget, self).__init__(parent=parent)

        # DATA TYPE INFO
        self.file_type = "_curves.json"
        self.subdir = 'data/'

        # HELP TEXT
        self.curve_help_text = "Use to import or export control curve data to/from a file."
        self.curve_VertLayout = QtWidgets.QVBoxLayout(self)
        self.curve_widget_help = QtWidgets.QLabel(self.curve_help_text)
        curve_help_font = QtGui.QFont()
        curve_help_font.setBold(True)
        self.curve_widget_help.setFont(curve_help_font)
        self.curve_VertLayout.addWidget(self.curve_widget_help)
        self.curve_widget_help.setFixedHeight(15)
        self.curve_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.curve_hbox = QtWidgets.QHBoxLayout()
        self.curve_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.curve_VertLayout.addLayout(self.curve_hbox)

        self.curve_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.curve_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.curve_hbox.addLayout(self.curve_import_VertLayout)
        self.curve_hbox.addLayout(self.curve_export_VertLayout)
        self.curve_import_VertLayout.setSpacing(20)
        self.curve_export_VertLayout.setSpacing(20)
        self.curve_hbox.addStretch(1)
        self.curve_import_VertLayout.addStretch(1)
        self.curve_export_VertLayout.addStretch(1)
        
        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.curve_imp_widgetA = QtWidgets.QLabel()
        self.curve_imp_widgetB = QtWidgets.QLabel()
        self.curve_imp_widgetC = QtWidgets.QLabel()
        self.curve_imp_widgetD = QtWidgets.QLabel()

        self.curve_exp_widgetA = QtWidgets.QLabel()
        self.curve_exp_widgetB = QtWidgets.QLabel()
        self.curve_exp_widgetC = QtWidgets.QLabel()
        self.curve_exp_widgetD = QtWidgets.QLabel()

        self.curve_imp_widgetA.setFixedHeight(20)
        self.curve_imp_widgetB.setFixedHeight(20)
        self.curve_imp_widgetC.setFixedHeight(20)
        self.curve_imp_widgetD.setFixedHeight(20)

        self.curve_exp_widgetA.setFixedHeight(20)
        self.curve_exp_widgetB.setFixedHeight(20)
        self.curve_exp_widgetC.setFixedHeight(20)
        self.curve_exp_widgetD.setFixedHeight(20)


class AttrsWidget(QtWidgets.QWidget):
    """Skin Cluster tab widget"""
    def __init__(self, parent=None):
        super(AttrsWidget, self).__init__(parent=parent)

        global selected_attrs
        global locked_attrs

        # DATA TYPE INFO
        self.file_type = "_attrs.json"
        self.subdir = 'data/'

        # HELP TEXT
        self.attr_help_text = "Use to import or export attribute data to/from a file."
        self.attr_VertLayout = QtWidgets.QVBoxLayout(self)
        self.attr_widget_help = QtWidgets.QLabel(self.attr_help_text)
        attr_help_font = QtGui.QFont()
        attr_help_font.setBold(True)
        self.attr_widget_help.setFont(attr_help_font)
        self.attr_VertLayout.addWidget(self.attr_widget_help)
        self.attr_widget_help.setFixedHeight(15)
        self.attr_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.attr_hbox = QtWidgets.QHBoxLayout()
        self.attr_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.attr_VertLayout.addLayout(self.attr_hbox)

        self.attr_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.attr_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.attr_hbox.addLayout(self.attr_import_VertLayout)
        self.attr_hbox.addLayout(self.attr_export_VertLayout)
        self.attr_import_VertLayout.setSpacing(20)
        self.attr_export_VertLayout.setSpacing(20)
        self.attr_hbox.addStretch(1)
        self.attr_import_VertLayout.addStretch(1)
        self.attr_export_VertLayout.addStretch(1)

        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.attr_imp_widgetA = QtWidgets.QLabel()
        self.attr_imp_widgetB = QtWidgets.QLabel()
        self.attr_imp_widgetC = QtWidgets.QLabel()
        self.attr_imp_widgetD = QtWidgets.QLabel()

        self.attr_exp_widgetA = QtWidgets.QCheckBox('Export selected channels only')
        self.attr_exp_widgetB = QtWidgets.QCheckBox('Export locked channels')
        self.attr_exp_widgetC = QtWidgets.QLabel()
        self.attr_exp_widgetD = QtWidgets.QLabel()

        self.attr_imp_widgetA.setFixedHeight(20)
        self.attr_imp_widgetB.setFixedHeight(20)
        self.attr_imp_widgetC.setFixedHeight(20)
        self.attr_imp_widgetD.setFixedHeight(20)

        self.attr_exp_widgetA.setFixedHeight(20)
        self.attr_exp_widgetB.setFixedHeight(20)
        self.attr_exp_widgetC.setFixedHeight(20)
        self.attr_exp_widgetD.setFixedHeight(20)

        self.attr_import_VertLayout.addWidget(self.attr_imp_widgetA)
        self.attr_import_VertLayout.addWidget(self.attr_imp_widgetB)
        self.attr_import_VertLayout.addWidget(self.attr_imp_widgetC)
        self.attr_import_VertLayout.addWidget(self.attr_imp_widgetD)

        self.attr_export_VertLayout.addWidget(self.attr_exp_widgetA)
        self.attr_export_VertLayout.addWidget(self.attr_exp_widgetB)
        self.attr_export_VertLayout.addWidget(self.attr_exp_widgetC)
        self.attr_export_VertLayout.addWidget(self.attr_exp_widgetD)

        # SETTINGS
        self.attr_exp_widgetA.setChecked(False)
        self.attr_exp_widgetB.setChecked(False)
        selected_attrs = False
        locked_attrs = False

        # SIGNALS AND CONNECTIONS
        self.attr_exp_widgetA.stateChanged.connect(self.selected_attrs_changed)
        self.attr_exp_widgetB.stateChanged.connect(self.locked_attrs_changed)

    def selected_attrs_changed(self, int):
        global selected_attrs
        selected_attrs = self.attr_exp_widgetA.isChecked()

    def locked_attrs_changed(self, int):
        global locked_attrs
        locked_attrs = self.attr_exp_widgetB.isChecked()


class SetDrivenKeyWidget(QtWidgets.QWidget):
    """Skin Cluster tab widget"""
    def __init__(self, parent=None):
        super(SetDrivenKeyWidget, self).__init__(parent=parent)

        # DATA TYPE INFO
        self.file_type = "_sdk.json"
        self.subdir = 'data/'

        # HELP TEXT
        self.sdk_help_text = "Use to import or export set driven keyframe data to/from a file."
        self.sdk_VertLayout = QtWidgets.QVBoxLayout(self)
        self.sdk_widget_help = QtWidgets.QLabel(self.sdk_help_text)
        sdk_help_font = QtGui.QFont()
        sdk_help_font.setBold(True)
        self.sdk_widget_help.setFont(sdk_help_font)
        self.sdk_VertLayout.addWidget(self.sdk_widget_help)
        self.sdk_widget_help.setFixedHeight(15)
        self.sdk_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.sdk_hbox = QtWidgets.QHBoxLayout()
        self.sdk_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.sdk_VertLayout.addLayout(self.sdk_hbox)

        self.sdk_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.sdk_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.sdk_hbox.addLayout(self.sdk_import_VertLayout)
        self.sdk_hbox.addLayout(self.sdk_export_VertLayout)
        self.sdk_import_VertLayout.setSpacing(20)
        self.sdk_export_VertLayout.setSpacing(20)
        self.sdk_hbox.addStretch(1)
        self.sdk_import_VertLayout.addStretch(1)
        self.sdk_export_VertLayout.addStretch(1)

        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.sdk_imp_widgetA = QtWidgets.QLabel()
        self.sdk_imp_widgetB = QtWidgets.QLabel()
        self.sdk_imp_widgetC = QtWidgets.QLabel()
        self.sdk_imp_widgetD = QtWidgets.QLabel()

        self.sdk_exp_widgetA = QtWidgets.QLabel()
        self.sdk_exp_widgetB = QtWidgets.QLabel()
        self.sdk_exp_widgetC = QtWidgets.QLabel()
        self.sdk_exp_widgetD = QtWidgets.QLabel()

        self.sdk_imp_widgetA.setFixedHeight(20)
        self.sdk_imp_widgetB.setFixedHeight(20)
        self.sdk_imp_widgetC.setFixedHeight(20)
        self.sdk_imp_widgetD.setFixedHeight(20)

        self.sdk_exp_widgetA.setFixedHeight(20)
        self.sdk_exp_widgetB.setFixedHeight(20)
        self.sdk_exp_widgetC.setFixedHeight(20)
        self.sdk_exp_widgetD.setFixedHeight(20)
        
        
class SkinClusterWidget(QtWidgets.QWidget):
    """Skin Cluster tab widget"""
    def __init__(self, parent=None):
        super(SkinClusterWidget, self).__init__(parent=parent)

        global skin_per_file
        global selected_only

        # DATA TYPE INFO
        self.file_type = "_skin.json"
        self.subdir = 'data/'

        # HELP TEXT
        self.skin_help_text = "Use to import or export set driven keyframe data to/from a file."
        self.skin_VertLayout = QtWidgets.QVBoxLayout(self)
        self.skin_widget_help = QtWidgets.QLabel(self.skin_help_text)
        skin_help_font = QtGui.QFont()
        skin_help_font.setBold(True)
        self.skin_widget_help.setFont(skin_help_font)
        self.skin_VertLayout.addWidget(self.skin_widget_help)
        self.skin_widget_help.setFixedHeight(15)
        self.skin_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.skin_hbox = QtWidgets.QHBoxLayout()
        self.skin_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.skin_VertLayout.addLayout(self.skin_hbox)

        self.skin_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.skin_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.skin_hbox.addLayout(self.skin_import_VertLayout)
        self.skin_hbox.addLayout(self.skin_export_VertLayout)
        self.skin_import_VertLayout.setSpacing(20)
        self.skin_export_VertLayout.setSpacing(20)
        self.skin_hbox.addStretch(1)
        self.skin_import_VertLayout.addStretch(1)
        self.skin_export_VertLayout.addStretch(1)

        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.skin_imp_widgetA = QtWidgets.QCheckBox('Import onto selected objects only')
        self.skin_imp_widgetB = QtWidgets.QLabel()
        self.skin_imp_widgetC = QtWidgets.QLabel()
        self.skin_imp_widgetD = QtWidgets.QLabel()

        self.skin_exp_widgetA = QtWidgets.QCheckBox('Export skin file per mesh')
        #self.skin_exp_widgetB = QtWidgets.QCheckBox('Export using influence long names')
        self.skin_exp_widgetB = QtWidgets.QLabel()
        self.skin_exp_widgetC = QtWidgets.QLabel()
        self.skin_exp_widgetD = QtWidgets.QLabel()

        self.skin_imp_widgetA.setFixedHeight(20)
        self.skin_imp_widgetB.setFixedHeight(20)
        self.skin_imp_widgetC.setFixedHeight(20)
        self.skin_imp_widgetD.setFixedHeight(20)

        self.skin_exp_widgetA.setFixedHeight(20)
        self.skin_exp_widgetB.setFixedHeight(20)
        self.skin_exp_widgetC.setFixedHeight(20)
        self.skin_exp_widgetD.setFixedHeight(20)

        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetA)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetB)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetC)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetD)

        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetA)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetB)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetC)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetD)

        # SETTINGS
        self.skin_exp_widgetA.setChecked(True)
        skin_per_file = True
        selected_only = False

        # SIGNALS AND CONNECTIONS
        self.skin_exp_widgetA.stateChanged.connect(self.per_file_state_changed)
        #self.skin_exp_widgetB.stateChanged.connect(self.use_long_names_state_changed)
        self.skin_imp_widgetA.stateChanged.connect(self.import_selected_only)

    def per_file_state_changed(self, int):
        global skin_per_file
        skin_per_file = self.skin_exp_widgetA.isChecked()

    def use_long_names_state_changed(self, int):
        global skin_use_long_names
        skin_use_long_names = self.skin_exp_widgetB.isChecked()

    def import_selected_only(self, int):
        selected_only = self.skin_imp_widgetA.isChecked()
        
        
class BlendShapesWidget(QtWidgets.QWidget):
    """BlendShape tab widget"""
    def __init__(self, parent=None):
        super(BlendShapesWidget, self).__init__(parent=parent)

        # DATA TYPE INFO
        self.file_type = ".json"
        self.subdir = 'data/blendshapes/'

        # HELP TEXT
        self.bshp_help_text = "Use to import or export blendShape deformer and weight data to/from a file."
        self.bshp_VertLayout = QtWidgets.QVBoxLayout(self)
        self.bshp_widget_help = QtWidgets.QLabel(self.bshp_help_text)
        bshp_help_font = QtGui.QFont()
        bshp_help_font.setBold(True)
        self.bshp_widget_help.setFont(bshp_help_font)
        self.bshp_VertLayout.addWidget(self.bshp_widget_help)
        self.bshp_widget_help.setFixedHeight(15)
        self.bshp_widget_help.setFixedHeight(15)

        # OPTIONS LAYOUT
        self.bshp_hbox = QtWidgets.QHBoxLayout()
        self.bshp_hbox.setAlignment(QtCore.Qt.AlignLeft)
        self.bshp_VertLayout.addLayout(self.bshp_hbox)
        self.bshp_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.bshp_hbox.addLayout(self.bshp_import_VertLayout)
        self.bshp_import_VertLayout.setSpacing(20)

        # OPTIONS - IMPORT/EXPORT CHECKBOXES
        self.bshp_imp_widgetA = QtWidgets.QLabel('Select blendshape node to export from selected mesh')
        self.bshp_imp_widgetB = QtWidgets.QComboBox()
        self.bshp_imp_widgetC = QtWidgets.QLabel()
        self.bshp_imp_widgetD = QtWidgets.QLabel()

        self.bshp_widget_help.setFixedHeight(15)
        self.bshp_imp_widgetA.setFixedHeight(20)
        self.bshp_imp_widgetB.setFixedHeight(20)
        self.bshp_imp_widgetC.setFixedHeight(20)
        self.bshp_imp_widgetD.setFixedHeight(20)

        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetA)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetB)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetC)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetD)

'''
class SkinClusterWidget(QtWidgets.QWidget):
    """Skin Cluster tab widget"""
    def __init__(self, parent=None):
        super(SkinClusterWidget, self).__init__(parent=parent)
        global skin_per_file

        # DATA TYPE INFO
        self.file_type = "_skin.json"
        self.subdir = 'deform/skinClusters/'

        # SKIN HELP TEXT
        self.skin_help_text = "Use to import or export skinCluster deformer and weight data to/from a file."
        self.skin_VertLayout = QtWidgets.QVBoxLayout(self)
        self.skin_widget_help = QtWidgets.QLabel(self.skin_help_text)
        skin_help_font = QtGui.QFont()
        skin_help_font.setBold(True)
        self.skin_widget_help.setFont(skin_help_font)
        self.skin_VertLayout.addWidget(self.skin_widget_help)

        # IMPORT/EXPORT CHECKBOX OPTIONS
        self.skin_imp_widgetA = QtWidgets.QCheckBox('Import onto selected objects only')
        self.skin_imp_widgetB = QtWidgets.QLabel()
        self.skin_imp_widgetC = QtWidgets.QLabel()
        self.skin_imp_widgetD = QtWidgets.QLabel()

        self.skin_exp_widgetA = QtWidgets.QCheckBox('Export skin file per mesh')
        self.skin_exp_widgetB = QtWidgets.QCheckBox('Export using influence long names')
        self.skin_exp_widgetC = QtWidgets.QLabel()
        self.skin_exp_widgetD = QtWidgets.QLabel()

        self.skin_exp_widgetA.setChecked(True)
        skin_per_file = True

        # OPTIONS CHECKBOX LAYOUT
        self.skin_hbox = QtWidgets.QHBoxLayout()
        self.skin_hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.skin_VertLayout.addLayout(self.skin_hbox)

        self.skin_import_VertLayout = QtWidgets.QVBoxLayout(self)
        self.skin_export_VertLayout = QtWidgets.QVBoxLayout(self)

        self.skin_hbox.addLayout(self.skin_import_VertLayout)
        self.skin_hbox.addLayout(self.skin_export_VertLayout)
        self.skin_import_VertLayout.setSpacing(20)
        self.skin_export_VertLayout.setSpacing(20)
        self.skin_hbox.addStretch(1)
        self.skin_import_VertLayout.addStretch(1)
        self.skin_export_VertLayout.addStretch(1)

        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetA)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetB)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetC)
        self.skin_import_VertLayout.addWidget(self.skin_imp_widgetD)

        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetA)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetB)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetC)
        self.skin_export_VertLayout.addWidget(self.skin_exp_widgetD)

        # Size and layout
        self.skin_widget_help.setFixedHeight(15)
        self.skin_widget_help.setFixedHeight(15)

        self.skin_imp_widgetA.setFixedHeight(20)
        self.skin_imp_widgetB.setFixedHeight(20)
        self.skin_imp_widgetC.setFixedHeight(20)
        self.skin_imp_widgetD.setFixedHeight(20)

        self.skin_exp_widgetA.setFixedHeight(20)
        self.skin_exp_widgetB.setFixedHeight(20)
        self.skin_exp_widgetC.setFixedHeight(20)
        self.skin_exp_widgetD.setFixedHeight(20)

        self.skin_exp_widgetA.stateChanged.connect(self.per_file_state_changed)
        self.skin_exp_widgetB.stateChanged.connect(self.use_long_names_state_changed)

        global selected_only
        selected_only = False
        self.skin_imp_widgetA.stateChanged.connect(self.import_selected_only)

    def per_file_state_changed(self, int):
        global skin_per_file
        skin_per_file = self.skin_exp_widgetA.isChecked()

    def use_long_names_state_changed(self, int):
        global skin_use_long_names
        skin_use_long_names = self.skin_exp_widgetB.isChecked()

    def import_selected_only(self, int):
        #global selected_only
        selected_only = self.skin_imp_widgetA.isChecked()


class BlendShapesWidget(QtWidgets.QWidget):
    """BlendShapes tab widget"""
    def __init__(self, parent=None):
        super(BlendShapesWidget, self).__init__(parent=parent)

        self.file_type = ".json"
        self.subdir = 'deform/blendshapes/'

        self.bshp_help_text = "Use to import or export blendShape deformer and weight data to/from a file."

        self.bshp_VertLayout = QtWidgets.QVBoxLayout(self)
        self.bshp_widget_help = QtWidgets.QLabel(self.bshp_help_text)

        bshp_help_font = QtGui.QFont()
        bshp_help_font.setBold(True)
        self.bshp_widget_help.setFont(bshp_help_font)
        self.bshp_VertLayout.addWidget(self.bshp_widget_help)

        # Import export checkbox options
        self.bshp_imp_widgetA = QtWidgets.QLabel('Select blendshape node to export from selected mesh')
        self.bshp_imp_widgetB = QtWidgets.QComboBox()
        self.bshp_imp_widgetC = QtWidgets.QLabel()
        self.bshp_imp_widgetD = QtWidgets.QLabel()

        # Horizontal layout for import and export setting columns
        self.bshp_hbox = QtWidgets.QHBoxLayout()
        self.bshp_hbox.setAlignment(QtCore.Qt.AlignLeft)
        self.bshp_VertLayout.addLayout(self.bshp_hbox)

        self.bshp_import_VertLayout = QtWidgets.QVBoxLayout(self)

        self.bshp_hbox.addLayout(self.bshp_import_VertLayout)
        self.bshp_import_VertLayout.setSpacing(20)

        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetA)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetB)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetC)
        self.bshp_import_VertLayout.addWidget(self.bshp_imp_widgetD)

        # Size and layout
        self.bshp_widget_help.setFixedHeight(15)
        self.bshp_imp_widgetA.setFixedHeight(20)
        self.bshp_imp_widgetB.setFixedHeight(20)
        self.bshp_imp_widgetC.setFixedHeight(20)
        self.bshp_imp_widgetD.setFixedHeight(20)
        
'''


def file_browser(file_filter=""):
    cmds.fileDialog2(selectFileFilter=file_filter, dialogStyle=2, fm=1)


def add_fonts(font_directory):
    """Add extra fonts to QApplication.

    Args:
        font_directory (string): Path where fonts live

    Returns:
        bool: True if successful, False if not.
    """
    valid_types = ['ttf', 'otf']
    fonts = QtGui.QFontDatabase()
    for thing in os.listdir(font_directory):
        thing_path = os.path.join(font_directory, thing)
        if os.path.isfile(thing_path):
            if thing.split('.')[1] in valid_types:
                fonts.addApplicationFont(thing_path)


def return_default_file_path(subdir="", extension="", relative=True):
    """Returns file path for data file export"""
    proj_path = cmds.workspace(q=True, rd=True)
    obj_sel = cmds.ls(selection=True)
    #if not obj_sel:  obj_sel = ["{}_filename".format(extension)]
    if not obj_sel:
        return subdir
    if relative:
        return "{}{}{}".format(subdir, obj_sel[0], extension)
    else:
        return "{}{}{}{}".format(proj_path, subdir, obj_sel[0], extension)


def resolve_file_path(file_path):
    """Returns full path from full or relative input file path

    resolve_file_path('deform/skinClusters/Ch_YellowButterfly_LOD0_SM_skin.json')
    """
    if file_path:
        if os.path.exists(file_path):
            return file_path
        elif os.path.exists(os.path.dirname(file_path)):
            return file_path
        else:
            proj_path = cmds.workspace(q=True, rd=True)
            return "{}{}".format(proj_path, file_path)
    else:
        LOG.error('No file path specified!')


def return_relative_path(full_path):
    """Returns relative path of input path based on current Maya project"""
    root_dir = cmds.workspace(q=True, rd=True)
    rel_path = os.path.relpath(full_path, root_dir)
    return rel_path.replace('\\','/')


def isMesh(mesh):
    """Check if the specified object is a polygon mesh or transform parent of a mesh

    Args:
        mesh: Object to query
    Returns:
        True/False
    """
    # Check Object Exists
    if not cmds.objExists(mesh): return False

    # Check Shape
    if 'transform' in cmds.nodeType(mesh, i=True):
        meshShape = cmds.ls(cmds.listRelatives(mesh, s=True, ni=True, pa=True) or [], type='mesh')
        if not meshShape: return False
        mesh = meshShape[0]

    # Check Mesh
    if cmds.objectType(mesh) != 'mesh': return False

    # Return Result
    return True
