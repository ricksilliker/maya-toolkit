import re

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from Qt import QtWidgets, __binding__

if __binding__ == 'PySide2':
    import shiboken2 as shiboken
else:
    import shiboken


def maya_main_window():
    """Get the Maya app window as a PyQt widget.

    Returns:
        QtWidgets.QWidget: The Maya main window object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()

    return shiboken.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def create_maya_window(widget, *args, **kwargs):
    """A safe way to parent a widget to a Maya window.

    Args:
        widget(QtWidgets.QWidget): A Qt widget to parent to a Maya window

    Returns:
        The new Maya window Qt object.
    """
    win = cmds.window(*args, **kwargs)
    mayaMain = maya_main_window()
    win = mayaMain.findChild(QtWidgets.QWidget, win)
    win.setObjectName('Maya{0}'.format(widget.objectName()))
    win.setGeometry(widget.geometry())
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
    win.resize(widget.size())

    return win


def dock_widget(widget, dock_name, **kwargs):
    dock_path = '{0}Dock'.format(dock_name)

    dock_name = ' '.join(re.findall('[A-Z][a-z]*', dock_name))

    if cmds.dockControl(dock_path, q=True, ex=True):
        cmds.deleteUI(dock_path)

    kw = dict(r=True, area='right', vis=True, width=350)
    kw.update(kwargs)

    panel = cmds.paneLayout(configuration='single')
    cmds.control(widget.objectName(), e=True, p=panel)
    dock = cmds.dockControl(dock_path, closeCommand=widget.close, content=panel, label=dock_name, **kw)
    dock_ptr = omui.MQtUtil.findControl(dock)

    return shiboken.wrapInstance(long(dock_ptr), QtWidgets.QWidget)
