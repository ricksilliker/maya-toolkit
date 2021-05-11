# built-ins
import os
import logging
import sys

# third party
import pymel.core as pm
from Qt import QtWidgets, QtCore, QtGui, __binding__

# internal
import core


LOG = logging.getLogger(__name__)


def fetchMayaWindow():
    """Get the main Maya window as a QtGui.QMainWindow instance.

    Returns:
        QMainWindow: Instance of the top level Maya window.
    """
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj

    raise RuntimeError('Could not find MayaWindow instance')


def createMayaWindow(widget, *args, **kwargs):
    """A safe way to parent a widget to a Maya window.

    Args:
        widget(QtWidgets.QWidget): A Qt widget to parent to a Maya window

    Returns:
        The new Maya window Qt object.
    """
    win = pm.window(*args, **kwargs)
    mayaMain = fetchMayaWindow()
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


class RigExtensionView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RigExtensionView, self).__init__(parent=parent)

        self.associateBtn = QtWidgets.QPushButton('associate')
        self.associateBtn.setToolTip('Pair a source node with a target node for mirroring.')
        self.associateBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.disassociateBtn = QtWidgets.QPushButton('disassociate')
        self.disassociateBtn.setToolTip('Break and clear the association of a node and its target.')
        self.disassociateBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.xAxisBtn = QtWidgets.QPushButton('X')
        self.xAxisBtn.setToolTip('Toggle on to mirror across the X Axis.')
        self.xAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.xAxisBtn.setCheckable(True)
        self.xAxisBtn.setChecked(True)
        self.yAxisBtn = QtWidgets.QPushButton('Y')
        self.yAxisBtn.setToolTip('Toggle on to mirror across the Y Axis.')
        self.yAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.yAxisBtn.setCheckable(True)
        self.zAxisBtn = QtWidgets.QPushButton('Z')
        self.zAxisBtn.setToolTip('Toggle on to mirror across the Z Axis.')
        self.zAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.zAxisBtn.setCheckable(True)

        mirrorAxisGrp = QtWidgets.QButtonGroup(self)
        mirrorAxisGrp.setExclusive(True)
        mirrorAxisGrp.addButton(self.xAxisBtn)
        mirrorAxisGrp.addButton(self.yAxisBtn)
        mirrorAxisGrp.addButton(self.zAxisBtn)

        self.simpleMirrorModeBtn = QtWidgets.QPushButton('Simple')
        self.simpleMirrorModeBtn.setToolTip('Toggle on to mirror a node in `FK` mode.')
        self.simpleMirrorModeBtn.setCheckable(True)
        self.simpleMirrorModeBtn.setChecked(True)
        self.simpleMirrorModeBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.inverseMirrorModeBtn = QtWidgets.QPushButton('Inverse')
        self.inverseMirrorModeBtn.setToolTip('Toggle on to mirror a node in `IK` mode.')
        self.inverseMirrorModeBtn.setCheckable(True)
        self.inverseMirrorModeBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        mirrorModeGrp = QtWidgets.QButtonGroup(self)
        mirrorModeGrp.setExclusive(True)
        mirrorModeGrp.addButton(self.simpleMirrorModeBtn)
        mirrorModeGrp.addButton(self.inverseMirrorModeBtn)

        self.editCustomMirrorBtn = QtWidgets.QPushButton('Edit Custom Mirroring')
        self.editCustomMirrorBtn.setToolTip('Customize how specific attributes mirror between associated nodes.')

        self.recursiveChb = QtWidgets.QCheckBox('Mirror Recursively')
        self.recursiveChb.setToolTip('Toggle on to run a mirror function on all children of a selected node.')
        self.mirrorBtn = QtWidgets.QPushButton('Mirror Node')
        self.mirrorBtn.setToolTip('Mirror the creation, parenting, and transform of a selected node.')
        self.mirrorParentingBtn = QtWidgets.QPushButton('Mirror Parenting')
        self.mirrorParentingBtn.setToolTip('Mirror only the parenting of a selected node, must be associated already.')
        self.mirrorTransformBtn = QtWidgets.QPushButton('Mirror Transform')
        self.mirrorTransformBtn.setToolTip('Mirror only the transformation of a selected node, must be associated already.')

        pairNodesLayout = QtWidgets.QHBoxLayout()
        pairNodesLayout.setAlignment(QtCore.Qt.AlignTop)
        pairNodesLayout.setSpacing(1)
        pairNodesLayout.setContentsMargins(0, 0, 0, 0)
        pairNodesLayout.addWidget(self.associateBtn)
        pairNodesLayout.addWidget(self.disassociateBtn)

        editCustomLayout = QtWidgets.QHBoxLayout()
        editCustomLayout.setAlignment(QtCore.Qt.AlignTop)
        editCustomLayout.setSpacing(1)
        editCustomLayout.setContentsMargins(0, 2, 0, 0)
        editCustomLayout.addWidget(self.editCustomMirrorBtn)

        mirrorDirLayout = QtWidgets.QHBoxLayout()
        mirrorDirLayout.setAlignment(QtCore.Qt.AlignTop)
        mirrorDirLayout.setSpacing(1)
        mirrorDirLayout.setContentsMargins(0, 10, 0, 0)
        mirrorDirLayout.addWidget(self.xAxisBtn)
        mirrorDirLayout.addWidget(self.yAxisBtn)
        mirrorDirLayout.addWidget(self.zAxisBtn)

        mirrorTypeLayout = QtWidgets.QHBoxLayout()
        mirrorTypeLayout.setAlignment(QtCore.Qt.AlignTop)
        mirrorTypeLayout.setSpacing(1)
        mirrorTypeLayout.setContentsMargins(0, 2, 0, 0)
        mirrorTypeLayout.addWidget(self.simpleMirrorModeBtn)
        mirrorTypeLayout.addWidget(self.inverseMirrorModeBtn)

        mirrorFuncLayout = QtWidgets.QVBoxLayout()
        mirrorFuncLayout.setAlignment(QtCore.Qt.AlignTop)
        mirrorFuncLayout.setSpacing(1)
        mirrorFuncLayout.setContentsMargins(0, 10, 0, 0)
        mirrorFuncLayout.addWidget(self.recursiveChb)
        mirrorFuncLayout.addWidget(self.mirrorBtn)
        mirrorFuncLayout.addWidget(self.mirrorParentingBtn)
        mirrorFuncLayout.addWidget(self.mirrorTransformBtn)

        # settings layout
        settingsLayout = QtWidgets.QVBoxLayout()
        settingsLayout.setAlignment(QtCore.Qt.AlignTop)
        settingsLayout.setSpacing(0)
        settingsLayout.setContentsMargins(5, 5, 5, 10)
        settingsLayout.addLayout(pairNodesLayout)
        settingsLayout.addLayout(editCustomLayout)
        settingsLayout.addLayout(mirrorDirLayout)
        settingsLayout.addLayout(mirrorTypeLayout)
        settingsLayout.addLayout(mirrorFuncLayout)

        mirrorSettingsGrp = QtWidgets.QGroupBox('')
        mirrorSettingsGrp.setLayout(settingsLayout)

        # top layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(mirrorSettingsGrp)

        self.setLayout(mainLayout)
        self.setObjectName('RigMirrorToolsView')
        self.setWindowTitle('Rig Mirror Tools')

        self.associateBtn.clicked.connect(self.associateNodes)
        self.disassociateBtn.clicked.connect(self.disassociateNodes)

        self.mirrorBtn.clicked.connect(self.mirrorNodes)
        self.mirrorParentingBtn.clicked.connect(self.mirrorParenting)
        self.mirrorTransformBtn.clicked.connect(self.mirrorTransforms)

    def associateNodes(self):
        selection = pm.selected()
        if len(selection) != 2:
            LOG.error('Select a source node and a target node to associate')
            return

        core.associate(*selection, force=True)

    def disassociateNodes(self):
        selection = pm.selected()
        for node in selection:
            core.disassociate(node)

    def mirrorNodes(self):
        kw = dict()
        kw['translate'] = True
        kw['rotate'] = True

        # get axis int kwarg
        for n, axis in enumerate([self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]):
            if axis.isChecked():
                kw['axis'] = n

        for axis in [self.simpleMirrorModeBtn, self.inverseMirrorModeBtn]:
            if axis.isChecked():
                kw['mirrorMode'] = str(axis.text().lower())

        mUtil = core.MirrorUtil(**kw)

        for node in pm.selected():
            if self.recursiveChb.isChecked():
                mUtil.mirrorRecursive(node)
            else:
                mUtil.mirror(node)

    def mirrorParenting(self):
        kw = dict()
        kw['translate'] = True
        kw['rotate'] = True

        # get axis int kwarg
        for n, axis in enumerate([self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]):
            if axis.isChecked():
                kw['axis'] = n

        for axis in [self.simpleMirrorModeBtn, self.inverseMirrorModeBtn]:
            if axis.isChecked():
                kw['mirrorMode'] = str(axis.text().lower())

        mUtil = core.MirrorUtil(**kw)

        for node in pm.selected():
            if self.recursiveChb.isChecked():
                mUtil.mirrorRecursive(node, create=False, transform=False)
            else:
                mUtil.mirror(node, create=False, transform=False)

    def mirrorTransforms(self):
        kw = dict()
        kw['translate'] = True
        kw['rotate'] = True

        # get axis int kwarg
        for n, axis in enumerate([self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]):
            if axis.isChecked():
                kw['axis'] = n

        for axis in [self.simpleMirrorModeBtn, self.inverseMirrorModeBtn]:
            if axis.isChecked():
                kw['mirrorMode'] = str(axis.text().lower())

        mUtil = core.MirrorUtil(**kw)

        for node in pm.selected():
            if self.recursiveChb.isChecked():
                mUtil.mirrorRecursive(node, create=False, reparent=False)
            else:
                mUtil.mirror(node, create=False, reparent=False)


class AnimExtensionView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        """Create the visual components.

        Args:
            parent (QtWidgets.QWidget): Qt object to be the parent this one lives under.

        Returns:
            None
        """
        super(AnimExtensionView, self).__init__(parent=parent)

        # mirror settings
        self.selectionBtn = QtWidgets.QPushButton('Selection')
        self.selectionBtn.setToolTip('Toggle on to mirror based on pairs of selected nodes.')
        self.selectionBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.selectionBtn.setCheckable(True)
        self.selectionBtn.setChecked(True)
        self.rigBtn = QtWidgets.QPushButton('Rig')
        self.rigBtn.setToolTip('Toggle on to mirror based on the rig settings.')
        self.rigBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.rigBtn.setMinimumWidth(self.selectionBtn.sizeHint().width())
        self.rigBtn.setCheckable(True)

        mirrorModeGrp = QtWidgets.QButtonGroup(self)
        mirrorModeGrp.setExclusive(True)
        mirrorModeGrp.addButton(self.selectionBtn)
        mirrorModeGrp.addButton(self.rigBtn)

        self.mirrorTypeCombo = QtWidgets.QComboBox()
        self.mirrorTypeCombo.setToolTip('How to mirror: Auto >> Rig Settings, Simple >> FK, Inverse >> IK.')
        self.mirrorTypeCombo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mirrorTypeCombo.addItems(['Auto', 'Simple', 'Inverse'])

        self.xAxisBtn = QtWidgets.QPushButton('X')
        self.xAxisBtn.setToolTip('Toggle on to mirror across the X Axis.')
        self.xAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.xAxisBtn.setCheckable(True)
        self.xAxisBtn.setChecked(True)
        self.yAxisBtn = QtWidgets.QPushButton('Y')
        self.yAxisBtn.setToolTip('Toggle on to mirror across the Y Axis.')
        self.yAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.yAxisBtn.setCheckable(True)
        self.zAxisBtn = QtWidgets.QPushButton('Z')
        self.zAxisBtn.setToolTip('Toggle on to mirror across the Z Axis.')
        self.zAxisBtn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.zAxisBtn.setCheckable(True)

        mirrorAxisGrp = QtWidgets.QButtonGroup(self)
        mirrorAxisGrp.setExclusive(True)
        mirrorAxisGrp.addButton(self.xAxisBtn)
        mirrorAxisGrp.addButton(self.yAxisBtn)
        mirrorAxisGrp.addButton(self.zAxisBtn)

        self.translateBtn = QtWidgets.QPushButton('Translate')
        self.translateBtn.setCheckable(True)
        self.translateBtn.setChecked(True)
        self.rotateBtn = QtWidgets.QPushButton('Rotate')
        self.rotateBtn.setMinimumWidth(self.translateBtn.sizeHint().width())
        self.rotateBtn.setCheckable(True)
        self.rotateBtn.setChecked(True)
        self.scaleBtn = QtWidgets.QPushButton('Scale')
        self.scaleBtn.setMinimumWidth(self.translateBtn.sizeHint().width())
        self.scaleBtn.setCheckable(True)
        self.scaleBtn.setChecked(True)

        self.mirrorAxisAddBtn = QtWidgets.QPushButton('+')
        self.mirrorAxisAddBtn.setToolTip('Add the selected node as the axis to mirror across.')
        self.mirrorAxisRemoveBtn = QtWidgets.QPushButton('x')
        self.mirrorAxisRemoveBtn.setToolTip('Set mirroring to mirror across the origin.')
        self.mirrorAxisField = QtWidgets.QLineEdit('origin')
        self.mirrorAxisField.setMinimumHeight(self.mirrorAxisAddBtn.sizeHint().height())
        self.mirrorAxisField.setReadOnly(True)

        mirrorModeLayout = QtWidgets.QHBoxLayout()
        mirrorModeLayout.setAlignment(QtCore.Qt.AlignLeft)
        mirrorModeLayout.setSpacing(1)
        mirrorModeLayout.setContentsMargins(0, 0, 0, 0)
        mirrorModeLayout.addWidget(self.selectionBtn)
        mirrorModeLayout.addWidget(self.rigBtn)

        mirrorTypeLayout = QtWidgets.QHBoxLayout()
        mirrorTypeLayout.setAlignment(QtCore.Qt.AlignLeft)
        mirrorTypeLayout.setSpacing(1)
        mirrorTypeLayout.setContentsMargins(0, 0, 0, 0)
        mirrorTypeLayout.addWidget(self.mirrorTypeCombo)

        mirrorDirLayout = QtWidgets.QHBoxLayout()
        mirrorDirLayout.setAlignment(QtCore.Qt.AlignLeft)
        mirrorDirLayout.setSpacing(1)
        mirrorDirLayout.setContentsMargins(0, 0, 0, 0)
        mirrorDirLayout.addWidget(self.xAxisBtn)
        mirrorDirLayout.addWidget(self.yAxisBtn)
        mirrorDirLayout.addWidget(self.zAxisBtn)

        mirrorTRSLayout = QtWidgets.QHBoxLayout()
        mirrorTRSLayout.setSpacing(1)
        mirrorTRSLayout.setContentsMargins(0, 0, 0, 0)
        mirrorTRSLayout.addWidget(self.translateBtn)
        mirrorTRSLayout.addWidget(self.rotateBtn)
        mirrorTRSLayout.addWidget(self.scaleBtn)

        mirrorAxisLayout = QtWidgets.QHBoxLayout()
        mirrorAxisLayout.setSpacing(1)
        mirrorAxisLayout.setContentsMargins(0, 0, 0, 0)
        mirrorAxisLayout.addWidget(self.mirrorAxisField)
        mirrorAxisLayout.addWidget(self.mirrorAxisAddBtn)
        mirrorAxisLayout.addWidget(self.mirrorAxisRemoveBtn)

        mirrorSettingsLayout = QtWidgets.QFormLayout()
        mirrorSettingsLayout.setSpacing(1)
        mirrorSettingsLayout.setContentsMargins(5, 5, 5, 10)
        mirrorSettingsLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        mirrorSettingsLayout.setLabelAlignment(QtCore.Qt.AlignLeft)
        mirrorSettingsLayout.addRow('Mirror Mode:', mirrorModeLayout)
        mirrorSettingsLayout.addRow('Mirror Type:', mirrorTypeLayout)
        mirrorSettingsLayout.addRow('Mirror TRS:', mirrorTRSLayout)
        mirrorSettingsLayout.addRow('Mirror Direction:', mirrorDirLayout)
        mirrorSettingsLayout.addRow('Mirror Across:', mirrorAxisLayout)

        mirrorSettingsGrp = QtWidgets.QGroupBox('')
        mirrorSettingsGrp.setLayout(mirrorSettingsLayout)

        # mirror functions
        self.mirrorBtn = QtWidgets.QPushButton('Mirror')
        self.mirrorBtn.setToolTip('Mirror based on the settings above. ')
        self.flipBtn = QtWidgets.QPushButton('Flip')
        self.flipBtn.setToolTip('Flip poses based on the settings above. Will flip non-mirror nodes in place.')

        self.flipCenteredBtn = QtWidgets.QPushButton('Flip Centered')
        self.flipCenteredBtn.setToolTip('Flip the selected non-mirror nodes in place.')

        mirrorFunctionsLayout = QtWidgets.QVBoxLayout()
        mirrorFunctionsLayout.setSpacing(1)
        mirrorFunctionsLayout.setContentsMargins(5, 5, 5, 10)
        mirrorFunctionsLayout.addWidget(self.mirrorBtn)
        mirrorFunctionsLayout.addWidget(self.flipBtn)

        mirrorFunctionsLayout.addWidget(self.flipCenteredBtn)

        mirrorFunctionsGrp = QtWidgets.QGroupBox('')
        mirrorFunctionsGrp.setLayout(mirrorFunctionsLayout)

        # top layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        mainLayout.addWidget(mirrorSettingsGrp)
        mainLayout.addWidget(mirrorFunctionsGrp)

        self.setLayout(mainLayout)
        self.setObjectName('AnimMirrorToolsView')
        self.setWindowTitle('Anim Mirror Tools')

        self.mirrorBtn.clicked.connect(self.mirror)
        self.flipBtn.clicked.connect(self.flip)
        self.flipCenteredBtn.clicked.connect(self.flipCentered)
        self.mirrorAxisAddBtn.clicked.connect(self.addMirrorAxisNode)
        self.mirrorAxisRemoveBtn.clicked.connect(self.removeMirrorAxisNode)

    def addMirrorAxisNode(self):
        """Add to the Mirror Axis field."""
        selection = pm.selected()

        if len(selection) != 1:
            LOG.error('Select a single node to mirror across')
            return

        self.mirrorAxisField.setText(selection[0].longName())

    def removeMirrorAxisNode(self):
        """Clear the Mirror Axis field."""
        self.mirrorAxisField.setText('origin')

    def mirror(self):
        """Mirror transforms of the mirror nodes."""

        # get mirror settings
        kw = dict()
        kw['setTranslate'] = self.translateBtn.isChecked()
        kw['setRotate'] = self.rotateBtn.isChecked()
        kw['setScale'] = self.scaleBtn.isChecked()

        # get axis int kwarg
        for n, axis in enumerate([self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]):
            if axis.isChecked():
                kw['axis'] = n

        # get axisMatrix matrix kwarg
        axisNode = self.mirrorAxisField.text()
        if axisNode and axisNode != 'origin':
            kw['axisMatrix'] = pm.PyNode(axisNode).wm.get()

        # get mirrorType name kwarg
        kw['mirrorMode'] = self.mirrorTypeCombo.currentText().lower()

        if self.selectionBtn.isChecked():
            selection = pm.selected()

            if len(selection) != 2:
                LOG.error('Must select a source and a target to mirror to only, 2 nodes max')
                return

            if kw['mirrorMode'] == 'Auto':
                if core.isMirrorNode(selection[0]):
                    kw['mirrorMode'] = core.getMirrorMode(selection[0]).lower()

            if kw['mirrorMode'] == 'Auto':
                    kw['mirrorMode'] = 'simple'

            mUtil = core.MirrorUtil(**kw)
            mUtil.mirrorTransform(*selection)

        if self.rigBtn.isChecked():
            if pm.selected():
                nodes = dict()
                nodes['sourceNode'] = pm.selected()[0]
                if len(pm.selected()) >= 2:
                    nodes['destNode'] = pm.selected()[1]

                if kw['mirrorMode'] == 'Auto':
                    if core.isMirrorNode(selection[0]):
                        kw['mirrorMode'] = core.getMirrorMode(selection[0]).lower()

                if kw['mirrorMode'] == 'Auto':
                    kw['mirrorMode'] = 'simple'

                mUtil = core.MirrorUtil(**kw)
                mUtil.mirrorTransform(**nodes)

    def flip(self):
        """Flip transforms of mirror nodes."""
        if self.selectionBtn.isChecked():
            selection = pm.selected()

            if len(selection) != 2:
                LOG.error('Must select a source and a target to mirror to only, 2 nodes max')
                return

            kw = dict()
            kw['setTranslate'] = self.translateBtn.isChecked()
            kw['setRotate'] = self.rotateBtn.isChecked()
            kw['setScale'] = self.scaleBtn.isChecked()

            # get axis int kwarg
            for n, axis in enumerate([self.xAxisBtn, self.yAxisBtn, self.zAxisBtn]):
                if axis.isChecked():
                    kw['axis'] = n

            # get axisMatrix matrix kwarg
            axisNode = self.mirrorAxisField.text()
            if axisNode and  axisNode != 'origin':
                kw['axisMatrix'] = pm.PyNode(axisNode).wm.get()

            # get mirrorType name kwarg
            mirrorModeName = self.mirrorTypeCombo.currentText().lower()
            if mirrorModeName == 'auto':
                mirrorModeName = 'simple'
            kw['mirrorMode'] = mirrorModeName

            mUtil = core.MirrorUtil(**kw)
            mUtil.flip(*selection)

        if self.rigBtn.isChecked():
            raise NotImplementedError('Mirror Mode: `Rig` is currently unsupported for Flip')

    def flipCentered(self):
        selection = pm.selected()
        mUtil = core.MirrorUtil(setTranslate=False)
        mUtil.flipCenter(selection)


class View(QtWidgets.QWidget):
    """UI used by animation and rigging teams to set/setup mirroring for rigs."""
    def __init__(self, parent=None):
        """Create the visual components.

        Args:
            parent (QtWidgets.QWidget): Qt object to be the parent this one lives under.

        Returns:
            None
        """
        super(View, self).__init__(parent=parent)

        self.rigView = RigExtensionView(self)
        self.animView = AnimExtensionView(self)

        # top layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(5, 5, 5, 5)

        mainLayout.addWidget(self.animView)
        mainLayout.addWidget(self.rigView)

        self.setLayout(mainLayout)
        self.setObjectName('MirrorToolsView')
        self.setWindowTitle('Mirror Tools')

    def closeEvent(self, event):
        """Update UI settings for persistence."""
        position = self.mapToGlobal(self.pos())
        size = self.sizeHint()

        pm.optionVar['MirrorToolsViewPosition'] = [position.x(), position.y()]
        pm.optionVar['MirrorToolsViewSize'] = [size.width(), size.height()]

        super(View, self).closeEvent(event)

    def sizeHint(self):
        """Store current size instead of creation size."""
        return QtCore.QSize(self.width(), self.height())


def show(animMenu=True, rigMenu=True, force=True):
    """Show the main UI.

    Args:
        force (bool): Destroy an open version, and show a new one.

    Returns:
        QWidget: Inspector widget.
    """
    app = fetchMayaWindow()

    exists = pm.window('MayaMirrorToolsView', q=True, ex=True)

    if not force and exists:
        return

    if force and exists:
        pm.deleteUI('MayaMirrorToolsView')

    win = View(app)

    if not animMenu:
        win.animView.hide()

    if not rigMenu:
        win.rigView.hide()

    if 'MirrorToolsViewPosition' in pm.optionVar and 'MirrorToolsViewSize' in pm.optionVar:
        position = pm.optionVar['MirrorToolsViewPosition']
        size = pm.optionVar['MirrorToolsViewSize']
    else:
        position = [0, 0]
        size = [0, 0]

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styleView.css')) as f:
        css = f.read()
        win.setStyleSheet(css)

    winMaya = createMayaWindow(win, closeCommand=win.close)
    winMaya.show()

    winMaya.move(*position)
    winMaya.resize(*size)

    return winMaya