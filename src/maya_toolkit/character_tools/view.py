import logging

from Qt import QtWidgets, QtCore, QtGui

import qt_utils.core
import core

LOG = logging.getLogger(__name__)
WINDOW_TYPE = qt_utils.core.get_os_window_type()


def show(dockable=False):
    """Shows main widget.

    Args:
        dockable: Whether to dock the widget to Maya's right side panel

    Returns:
        QtWidgets.QWidget: Main UI widget
    """
    app = qt_utils.core.fetch_maya_window()
    win = CharacterToolsWidget(parent=app)

    if dockable:
        qt_utils.core.dock_with_dockControl(win)
    else:
        win.show()
        win.move(app.geometry().center().x(), 100)
        win.resize(350, 625)

    return win


class CharacterToolsWidget(QtWidgets.QWidget):
    """Main widget."""
    def __init__(self, parent=None):
        """Generate default UI elements.
        Args:
            parent: Parent QWidget object
        """
        super(CharacterToolsWidget, self).__init__(parent=parent)

        spaces_widget = SpacesWidget()
        spaces_group = qt_utils.core.QAbstractGroup('Space Switching')
        spaces_group.main_layout.addWidget(spaces_widget)
        separator0 = qt_utils.core.QHLine()

        keys_widget = KeysWidget()
        keys_group = qt_utils.core.QAbstractGroup('Keys')
        keys_group.main_layout.addWidget(keys_widget)
        separator1 = qt_utils.core.QHLine()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        main_layout.addWidget(spaces_group)
        main_layout.addWidget(separator0)

        main_layout.addWidget(keys_group)
        main_layout.addWidget(separator1)

        self.setObjectName('CharacterTools')
        self.setWindowTitle('Character Tools')
        self.setWindowFlags(WINDOW_TYPE)

        self.spaces_callback_id = core.add_selection_callback(spaces_widget.callback)

    def closeEvent(self, event):
        """Customized close event, removes Maya callbacks."""
        core.remove_callbacks([self.spaces_callback_id])
        super(CharacterToolsWidget, self).closeEvent(event)


class SpacesWidget(QtWidgets.QWidget):
    """Elements for space switching."""
    def __init__(self, parent=None):
        """Generate default UI elements.
        Args:
            parent: Parent QWidget object
        """
        super(SpacesWidget, self).__init__(parent=parent)

        self.space_names = list()
        self.selection = list()

        self.spaces_layout = QtWidgets.QVBoxLayout()
        self.spaces_layout.setAlignment(QtCore.Qt.AlignTop)
        self.spaces_layout.setContentsMargins(0, 0, 0, 0)
        self.spaces_layout.setSpacing(3)
        self.setLayout(self.spaces_layout)

        self.update_available_spaces()

    def callback(self, clientData=None):
        """Wrapper for updating UI on object selection by user."""
        self.update_available_spaces()

    def update_available_spaces(self):
        """Updates UI space button elements."""
        self.clear_spaces()

        self.selection = core.get_selection()
        self.space_names = core.get_common_spaces(self.selection)
        self.add_space_buttons(self.space_names)

    def add_space_buttons(self, names):
        """Add all the space buttons for the selected object.

        Args:
            names: Names of spaces
        """
        for name in names:
            btn = QtWidgets.QPushButton(name)
            btn.clicked.connect(lambda x=name: self.change_space(x))

            self.spaces_layout.addWidget(btn)

    def change_space(self, space_name):
        """Slot for updating space switch on the selected objects.

        Args:
            space_name: Name to give the UI element that corresponds to the space name.
        """
        core.set_space(self.selection, space_name)

    def clear_spaces(self):
        """Clears UI space button elements."""
        for i in reversed(range(self.spaces_layout.count())):
            self.spaces_layout.itemAt(i).widget().deleteLater()


class KeysWidget(QtWidgets.QWidget):
    """Elements for keying.

    Attributes:
        clipboard: stores latest cut/copy key data
    """
    def __init__(self, parent=None):
        """Generate default UI elements.

        Args:
            parent: Parent QWidget object
        """
        super(KeysWidget, self).__init__(parent=parent)

        self.clipboard = dict()

        self.cut_button = QtWidgets.QPushButton('Cut Keys')
        self.copy_button = QtWidgets.QPushButton('Copy Keys')
        self.paste_button = QtWidgets.QPushButton('Paste Keys')

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(3)
        self.setLayout(main_layout)

        main_layout.addWidget(self.cut_button)
        main_layout.addWidget(self.copy_button)
        main_layout.addWidget(self.paste_button)

        self.cut_button.clicked.connect(self.cut_keys)
        self.copy_button.clicked.connect(self.copy_keys)
        self.paste_button.clicked.connect(self.paste_keys)

    def cut_keys(self):
        """Copies and clears keys from selected object."""
        self.clipboard = core.cut_keys()

    def copy_keys(self):
        """Copies keys from selected object."""
        self.clipboard = core.copy_keys()

    def paste_keys(self):
        """Pastes key data from cut/copy operations onto the selected object."""
        core.paste_keys(self.clipboard)
