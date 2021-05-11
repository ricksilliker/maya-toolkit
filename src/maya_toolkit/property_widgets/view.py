# built-ins
import logging

# third party
from Qt import QtWidgets, QtCore, QtGui

# internal
import utils

LOG = logging.getLogger(__name__)
DEFAULT_OPTIONS = dict(numericMin=0, numericMax=100, numericPrecision=3, listDisplaysAsRadios=False)


def show(dockable=True, **kwargs):
    app = utils.maya_main_window()
    win = PropSheetWidget(parent=app)

    if dockable:
        dock = utils.dock_widget(win, 'PropSheet', **kwargs)

    win.show()
    win.resize(600, 700)

    return win


def debug():
    widget = show()
    test_data = dict(
        Properties=dict(Enum='One, Two, Three', Boolean=True, Integer=10, Float=20.4, String='This That', Vector=[2, 4, 2], Color=dict(r=0, g=0, b=0)),
        Test=dict(Enum='One, Two, Three', Boolean=True, Integer=10, Float=20.4, String='This That', Vector=[2, 4, 2], Color=dict(r=0, g=0, b=0))
    )
    widget.set_props(test_data, None)


def get_input(title, data, options=None):
    if options is None:
        options = DEFAULT_OPTIONS.copy()

    dialog = QtWidgets.QWidget()

    layout = QtWidgets.QGridLayout()
    dialog.setLayout(layout)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    widget_map = dict()

    row = 0
    for key, value in data.items():
        label = QtWidgets.QLabel('{name}:'.format(name=key))
        layout.addWidget(label, row, 0)

        if PropValue.isBool(value):
            widget = QtWidgets.QCheckBox()
            widget.setChecked(PropValue.toBool(value))
            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        elif PropValue.isColor(value):
            widget = SetColorButton()
            widget.set_color(PropValue.toColor(value))
            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        elif PropValue.isFloat(value):
            widget = QtWidgets.QDoubleSpinBox()
            widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            widget.setMaximum(options['numericMax'])
            widget.setMinimum(options['numericMin'])
            widget.setDecimals(options['numericPrecision'])
            widget.setValue(PropValue.toFloat(value))
            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        elif PropValue.isInt(value):
            widget = QtWidgets.QSpinBox()
            widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            widget.setMaximum(options['numericMax'])
            widget.setMinimum(options['numericMin'])
            widget.setValue(PropValue.toInt(value))
            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        elif PropValue.isVector3D(value):
            value = PropValue.toVector3D(value)
            widget = QtWidgets.QWidget()
            wlayout = QtWidgets.QHBoxLayout(widget)
            wlayout.setContentsMargins(2, 2, 2, 2)
            wlayout.setSpacing(2)

            xwidget = QtWidgets.QDoubleSpinBox()
            xwidget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            xwidget.setValue(value.x)
            wlayout.addWidget(xwidget)

            ywidget = QtWidgets.QDoubleSpinBox()
            ywidget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            ywidget.setValue(value.y)
            wlayout.addWidget(ywidget)

            zwidget = QtWidgets.QDoubleSpinBox()
            zwidget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            zwidget.setValue(value.z)
            wlayout.addWidget(zwidget)

            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        elif PropValue.isEnum(value):
            if options['listDisplaysAsRadios']:
                values = PropValue.toEnum(value)
                widget = QtWidgets.QWidget()
                button_group = QtWidgets.QButtonGroup()
                wlayout = QtWidgets.QHBoxLayout(widget)
                wlayout.setContentsMargins(2, 2, 2, 2)
                wlayout.setSpacing(2)

                isChecked = False
                for val in values:
                    button = QtWidgets.QRadioButton(val)
                    button_group.addButton(button)
                    wlayout.addWidget(button)

                if not isChecked:
                    button.setChecked(True)
                    isChecked = True
                layout.addWidget(widget, row, 1)
                widget_map[key] = widget
            else:
                widget = QtWidgets.QComboBox()
                widget.addItems(PropValue.toEnum(value))
                layout.addWidget(widget, row, 1)
                widget_map[key] = widget

        elif PropValue.isString(value):
            widget = QtWidgets.QLineEdit(PropValue.toString(value))
            layout.addWidget(widget, row, 1)
            widget_map[key] = widget

        row += 1

    dialog.widget_map = widget_map
    grp = PropGroup(title, dialog)

    return grp


class SetColorButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(SetColorButton, self).__init__('', parent=parent)

        self._color = QtGui.QColor(0, 0, 0)

        self.setAutoFillBackground(True)
        self.setFlat(True)

        self.clicked.connect(self.change_color)

    def change_color(self):
        dialog = QtWidgets.QColorDialog()
        cursor = QtGui.QCursor()
        dialog.move(cursor.pos())
        dialog.setCurrentColor(self._color)
        newColor = dialog.getColor(self._color)

        if newColor != self._color:
            self.set_color(newColor)

    def set_color(self, color):
        self._color = color
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Button, color)
        self.setPalette(pal)
        self.update()

    def color(self):
        return self._color


class PropValue(object):
    def __init__(self, default_value):
        self.default_value = default_value

    @classmethod
    def isColor(cls, value):
        if isinstance(value, QtGui.QColor):
            return True
        if isinstance(value, dict):
            if all([True if x in ['r', 'g', 'b'] else False for x in value.keys()]):
                return True
        return False

    @classmethod
    def isString(cls, value):
        return isinstance(value, basestring)

    @classmethod
    def isInt(cls, value):
        if isinstance(value, (int, long)):
            if value is int(value):
                return True
        return False

    @classmethod
    def isFloat(cls, value):
        if isinstance(value, float):
            if value is float(value):
                return True
        return False

    @classmethod
    def isEnum(cls, value):
        if isinstance(value, (list, tuple)):
            if all([True if isinstance(x, basestring) else False for x in value]):
                return True
        if isinstance(value, basestring):
            if ',' in value:
                return True
        return False

    @classmethod
    def isBool(cls, value):
        if value is True or value is False:
            return True
        for val in (True, False):
            if str(value) == str(val):
                return True
        return False

    @classmethod
    def isVector3D(cls, value):
        if isinstance(value, (list, tuple)):
            if len(value) == 3:
                return True
        if isinstance(value, dict):
            if all([True if x in ['x', 'y', 'z'] else False for x in value.keys()]):
                return True
        if isinstance(value, Vector3D):
            return True
        return False

    @classmethod
    def toColor(cls, value):
        if isinstance(value, QtGui.QColor):
            return value
        else:
            value = [value['r'], value['g'], value['b']]
            return QtGui.QColor(*[val if val <= 1.0 else val * 255.0 for val in value])

    @classmethod
    def toVector3D(cls, value):
        vec = Vector3D()
        vec.set_value(value)

        return vec

    @classmethod
    def toEnum(cls, value):
        if isinstance(value, (list, tuple)):
            return value
        elif isinstance(value, basestring):
            return value.replace(' ', '').split(',')
        return []

    @classmethod
    def toInt(cls, value):
        return int(value)

    @classmethod
    def toFloat(cls, value):
        return float(value)

    @classmethod
    def toString(cls, value):
        return str(value)

    @classmethod
    def toBool(cls, value):
        return bool(value)


class Vector3D(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def set_value(self, value):
        axes = ['x', 'y', 'z']
        if isinstance(value, (list, tuple)):
            for n, v in enumerate(value):
                setattr(self, axes[n], v)

        if isinstance(value, dict):
            for k, v in value.items():
                if k in axes:
                    setattr(self, k, v)


class PropSheetWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PropSheetWidget, self).__init__(parent=parent)

        self.dialog = None
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout()

        self.setWindowTitle('Prop Sheet')
        self.setObjectName('PropSheetWidget')

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        scroll_area = QtWidgets.QScrollArea()
        self.layout.addWidget(scroll_area)

        # default settings
        scroll_area.setLayout(self.central_layout)
        scroll_area.setFrameShape(QtWidgets.QScrollArea.NoFrame)
        scroll_area.setAutoFillBackground(False)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMouseTracking(True)
        scroll_area.verticalScrollBar().setMaximumWidth(10)

        self.central_layout.setAlignment(QtCore.Qt.AlignTop)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(15)

        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)

    def clear_props(self):
        for child in self.central_layout.children():
            child.deleteLater()

    def set_props(self, data, options):
        self.clear_props()
        for title, props in data.items():
            grp = get_input(title, props, options)
            self.central_layout.addWidget(grp)

    def get_props(self):
        return [self.central_layout.itemAt(x) for x in range(self.central_layout.count())]


class PropGroup(QtWidgets.QGroupBox):
    def __init__(self, title, widget, parent=None):
        super(PropGroup, self).__init__(parent=parent)

        self._widget = widget
        self._closed = False
        self._clicked = False

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 10, 5, 5)
        layout.setSpacing(0)
        layout.addWidget(widget)

        self.setLayout(layout)

        # default settings
        self.setTitle(title)

    @property
    def isCollapsed(self):
        return self._closed

    def widget(self):
        return self._widget

    def toggle_collapsed(self):
        self.set_collapsed(not(self.isCollapsed))

    def set_collapsed(self, state):
        self._closed = state

        if (state):
            self.setMinimumHeight(22)
            self.setMaximumHeight(22)
            self.widget().setVisible(False)
        else:
            self.setMinimumHeight(0)
            self.setMaximumHeight(1000000)
            self.widget().setVisible(True)

    def expand_collapse_rect(self):
        return QtCore.QRect(0, 0, self.width(), 20)

    def mouseReleaseEvent(self, event):
        if self._clicked and self.expand_collapse_rect().contains(event.pos()):
            self.toggle_collapsed()
            event.accept()
        else:
            event.ignore()

        self._clicked = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.expand_collapse_rect().contains(event.pos()):
            self._clicked = True
            event.accept()
        else:
            event.ignore()
