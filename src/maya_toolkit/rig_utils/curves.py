import logging
LOG = logging.getLogger(__name__)

import maya.cmds as cmds


def create_curveConnector(node1, node2):
    """Creates degree one curve between node1 and node2 objects

    create_curveConnector("lf_tentA7_ctl1", "lf_tentA8_ctl1")
    """
    # Create connection curve, duplicate curve and parent under node1
    crv, crvShp = twoPointCurve(node1, node2)
    crvDup = cmds.duplicate(crv)
    crvDupShp = cmds.listRelatives(crvDup, shapes=True)[0]
    cmds.parent(crvDupShp, crv, r=True, s=True)
    cmds.delete(crvDup)
    cmds.setAttr("{}.inheritsTransform".format(crv), 0)
    cmds.parent(crv, node1)

    # Create leastSquaresModifier and decomposeMatrix nodes
    lsm = cmds.createNode("leastSquaresModifier", name="{}_lsm".format(node1))
    dcm1 = cmds.createNode("decomposeMatrix", name="{}_dcm".format(node1))
    dcm2 = cmds.createNode("decomposeMatrix", name="{}_dcm".format(node2))

    # Connect nodes and curveShapes
    cmds.connectAttr("{}.worldMatrix[0]".format(node1), "{}.inputMatrix".format(dcm1))
    cmds.connectAttr("{}.worldMatrix[0]".format(node2), "{}.inputMatrix".format(dcm2))

    cmds.connectAttr("{}.outputTranslate".format(dcm1), "{}.pointConstraint[0].pointPositionXYZ".format(lsm))
    cmds.connectAttr("{}.outputTranslate".format(dcm2), "{}.pointConstraint[1].pointPositionXYZ".format(lsm))
    cmds.connectAttr("{}.outputNurbsObject".format(lsm), "{}.create".format(crvShp))
    cmds.connectAttr("{}.worldMatrix[0]".format(crvShp), "{}.worldSpaceToObjectSpace".format(lsm))
    cmds.connectAttr("{}.worldSpace[0]".format(crvDupShp), "{}.inputNurbsObject".format(lsm))

    cmds.setAttr("{}.pointConstraint[0].pointConstraintU".format(lsm), 0)
    cmds.setAttr("{}.pointConstraint[1].pointConstraintU".format(lsm), 1)

    cmds.parent(crvShp, crvDupShp, node1, r=True, s=True)
    cmds.hide(crvDupShp)
    cmds.delete(crv)
    return crvShp


def create_curveConnectFromList(nodeList):
    """Creates degree one curve between from ordered list of objects
    sel = cmds.ls(selection=True)
    create_curveConnectFromList(sel)
    """
    i = 0
    while i < len(nodeList) - 1:
        create_curveConnector(nodeList[i], nodeList[i + 1])
        i = i + 1


def twoPointCurve(node1, node2, degree=1):
    """Creates a degree 3 NURBS curve from two input objects """
    crvCmd = 'cmds.curve(degree=1, p=['
    startEndCtrls = [node1, node2]
    for ctrl in startEndCtrls:
        tfm = cmds.xform(ctrl, query=True, worldSpace=True, translation=True)
        crvCmd += ' ('
        for tfmItem in tfm:
            crvCmd += ' ' + str(tfmItem) + ','
        crvCmd += '),'

    crvCmd += '], k=[0,1])'
    crv = cmds.python(crvCmd)
    if degree > 1:
        cmds.rebuildCurve(crv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=degree, tol=0.01)
    crv = cmds.rename(crv, "{}_crv".format(node1))
    crvShp = cmds.listRelatives(crv, shapes=True)[0]
    return crv, crvShp