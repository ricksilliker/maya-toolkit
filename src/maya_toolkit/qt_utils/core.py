import os
import sys
import logging

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from Qt import QtWidgets, QtCore, QtGui, __binding__

if __binding__ == 'PySide2':
    from shiboken2 import wrapInstance
else:
    from shiboken import wrapInstance

LOG = logging.getLogger(__name__)


def fetch_maya_window():
    """Get the Maya app window as a PySide/PySide2 QWidget.

    Returns:
        QtWidgets.QWidget: The Maya main window object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()

    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def fetch_maya_statusline_toolbox():
    status_line = mel.eval('$tmp = $gStatusLineForm')
    pointer = omui.MQtUtil_findControl(status_line)
    status_line = wrapInstance(long(pointer), QtWidgets.QWidget)
    toolbox = status_line.children()[1].children()[2]

    return toolbox


def dock_with_dockControl(widget):
    """Create a docked widget for Maya 2016.5 and lower.

    Args:
        widget: QWidget to parent to dock control

    Returns:
        str: Name of the new dock control
    """
    dock_name = '{0}Dock'.format(widget.objectName())

    try:
        cmds.deleteUI(dock_name)
    except RuntimeError as e:
        LOG.exception(e)

    panel = cmds.paneLayout(configuration='single')
    cmds.control(widget.objectName(), e=True, p=panel)
    cmds.evalDeferred(lambda *args: cmds.dockControl(dock_name, r=True, vis=True, closeCommand=widget.close,
                                                     area='right', content=panel, label=widget.windowTitle(), width=550))

    return dock_name


def dock_with_workspaceControl(widget):
    dock_name = '{0}Dock'.format(widget.objectName())
    if cmds.workspaceControl(dock_name, ex=True):
        cmds.deleteUI(dock_name)

    cmds.workspaceControl(dock_name, label=widget.windowTitle(), closeCommand=widget.close)
    control_widget = omui.MQtUtil.findControl(dock_name)
    control_wrap = wrapInstance(long(control_widget), QtWidgets.QWidget)
    control_wrap.layout().addWidget(widget)

    return control_wrap


def dock_widget(widget):
    if cmds.about(api=True) < 2017:
        dock_with_dockControl(widget)
    else:
        dock_with_workspaceControl(widget)


def wrap_widget(widget, *args, **kwargs):
    """A safe way to parent a widget to a Maya window.

    This allows you to skip finding Maya's main window and resolves window flag compatibility issues across OSs.

    Args:
        widget(QtWidgets.QWidget): A Qt widget to parent to a Maya window
        *args: Arguments for cmds.window command
        **kwargs: Keyword arguments for cmds.window command

    Returns:
        QtWidgets.QWidget: The new window as a QWidget.
    """
    maya_main = fetch_maya_window()

    win = cmds.window(*args, **kwargs)
    win = maya_main.findChild(QtWidgets.QWidget, win)
    win.setObjectName(widget.objectName())
    win.setGeometry(widget.geometry())
    win.resize(widget.size())

    lay = win.layout()
    if not lay:
        lay = QtWidgets.QVBoxLayout(win)
    lay.addWidget(widget)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)

    title = widget.windowTitle()
    if title:
        win.setWindowTitle(title)

    icon = widget.windowIcon()
    if icon:
        win.setWindowIcon(icon)

    return win


def get_os_window_type():
    if sys.platform == 'darwin':
        window_type = QtCore.Qt.Tool
    else:
        window_type = QtCore.Qt.Window

    return window_type


class QAbstractGroup(QtWidgets.QGroupBox):
    def __init__(self, groupName, parent=None):
        super(QAbstractGroup, self).__init__(title=groupName, parent=parent)
        self.setCheckable(True)
        self.toggled.connect(self.toggleChildren)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.main_layout.setSpacing(3)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.main_layout)

    def toggleChildren(self, state):
        if state:
            for x in self.findChildren(QtWidgets.QWidget):
                x.setVisible(True)
        else:
            for x in self.findChildren(QtWidgets.QWidget):
                x.setVisible(False)


class QHLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(QHLine, self).__init__(parent=parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(QVLine, self).__init__(parent=parent)
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QFilePath(QtWidgets.QWidget):
    def __init__(self, title, dialog=None, parent=None):
        super(QFilePath, self).__init__(parent=parent)

        self._dialog = dialog
        self._use_directory = False
        self._use_file = False

        self.label = QtWidgets.QLabel(title)
        self.field = QtWidgets.QLineEdit('')
        self.button = QtWidgets.QPushButton('...')

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.label, 0)
        layout.addWidget(self.field, 1)
        layout.addWidget(self.button, 0)

        self.setLayout(layout)

        self.field.setReadOnly(True)
        self.field.setPlaceholderText('Save Directory')
        self.button.setFixedWidth(22)
        self.button.setFixedHeight(18)
        self.button.clicked.connect(self.show_dialog)

    @property
    def use_directory(self):
        return self._use_directory

    @use_directory.setter
    def use_directory(self, value):
        self._use_directory = bool(value)

    @property
    def use_file(self):
        return self._use_file

    @use_file.setter
    def use_file(self, value):
        self._use_file = bool(value)

    @property
    def current_dir(self):
        current_value = self.field.text()
        if os.path.exists(current_value):
            return self.field.text()
        elif os.path.isfile(current_value):
            return os.path.dirname(current_value)
        else:
            return os.path.dirname(cmds.file(query=True, sceneName=True))

    def show_dialog(self):
        if self._dialog is not None:
            self._dialog.show()
            return

        dialog = QtWidgets.QFileDialog(self)

        if self.use_directory:
            result = dialog.getExistingDirectory(self, 'Choose Directory', self.current_dir)
        elif self.use_file:
            result = dialog.getOpenFileName(self, 'Choose File', self.current_dir)
        else:
            result = dialog.getOpenFileName(self, 'Choose File', self.current_dir)

        if result:
            self.field.setText(result)


class QFileList(QtWidgets.QListWidget):
    filepath_role = QtCore.Qt.UserRole + 1

    def __init__(self, parent=None):
        super(QFileList, self).__init__(parent=parent)

        self._directory = None
        self._filetype = list()

    def set_filetype(self, value):
        self._filetype = value

    def set_directory(self, value):
        self._directory = value

    def update_list(self, directory):
        self.clear()
        self.set_directory(directory)

        for dirpath, dirname, filenames in os.walk(directory):
            for filename in filenames:
                for ext in self._filetype:
                    if ext in filename:
                        self.append_file_item(os.path.join(dirpath, filename))

    def append_file_item(self, filepath):
        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.DisplayRole, os.path.basename(filepath))
        item.setData(self.filepath_role, filepath)
        self.addItem(item)


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smartSpacing(
                QtWidgets.QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smartSpacing(
                QtWidgets.QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

    def expandingDirections(self):
        return QtCore.Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QtCore.QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect, testonly):
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(+left, +top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        lineheight = 0
        for item in self._items:
            widget = item.widget()
            hspace = self.horizontalSpacing()
            if hspace == -1:
                hspace = widget.style().layoutSpacing(
                    QtWidgets.QSizePolicy.PushButton,
                    QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            vspace = self.verticalSpacing()
            if vspace == -1:
                vspace = widget.style().layoutSpacing(
                    QtWidgets.QSizePolicy.PushButton,
                    QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + hspace
            if nextX - hspace > effective.right() and lineheight > 0:
                x = effective.x()
                y = y + lineheight + vspace
                nextX = x + item.sizeHint().width() + hspace
                lineheight = 0
            if not testonly:
                item.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineheight = max(lineheight, item.sizeHint().height())
        return y + lineheight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()