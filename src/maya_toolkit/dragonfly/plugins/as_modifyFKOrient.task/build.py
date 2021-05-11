import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)

MAYA_VER = int(mel.eval('getApplicationVersionAsFloat'))


def run(params, rig):

    for fk in params['reorientFKControls']:

        fk_ctl = fk['FKcontrol']
        fk_off = fk['FKcontrolOffset']
        orient_str = [ori for ori in fk['OrientValue'].replace(' ', '').split(",")]
        orient_val = map(int, orient_str)
        is_neck = fk['isNeckControl']

        # Record all ctl cvs positions
        crvData = {}
        cmds.select("%s.cv[0:*]" % fk_ctl)
        for item in cmds.ls(selection=True, flatten=True):
            cvPos = cmds.xform(item, q=True, ws=True, t=True)
            crvData[item] = cvPos

        if is_neck:
            try:
                # Re-orient control
                reorientFKNeckControl(fk_ctl, orientRotate=orient_val)

                # Restore orig ctl cv positions of control
                for cv, pos in crvData.iteritems():
                    cmds.move(pos[0], pos[1], pos[2], cv, ws=True)

                LOG.info('Modified FK Neck Control orientation for: {}'.format(fk_ctl))

            except:
                LOG.error('Error modifying FK Neck Control orientation for:'.format(fk_ctl))
                pass

        else:
            try:
                # Re-orient control
                reorientFKControl(fk_ctl, fk_off, orientRotate=orient_val, insertOffsetTransform=fk['insertNewOffsetTransform'])

                # Restore orig ctl cv positions of control
                for cv, pos in crvData.iteritems():
                    cmds.move(pos[0], pos[1], pos[2], cv, ws=True)

                LOG.info('Modified FK Control orientation for: {}'.format(fk_ctl))

            except:
                LOG.error('Error modifying FK Control orientation for:'.format(fk_ctl))
                pass


def reorientFKControl(fkCtrlName, fkOffsetNode, orientRotate=[0, -90, -90], insertOffsetTransform=True):
    """Use to reorient FK controllers (ie., to match IKspline ctrls)
    reorientFKControl("FKChest_M", "FKOffsetChest_M")
    """
    if insertOffsetTransform:
        ori_node = insertAsParent(fkOffsetNode, name=None, suffix="ReOrient", match=True, nodeType='transform')
        fkOffsetNode = ori_node

    fkChild = cmds.listRelatives(fkCtrlName, children=True, type="joint")
    if fkChild:
        cmds.parent(fkChild, world=True)
    cmds.setAttr("%s.rotate" % fkOffsetNode, *orientRotate)
    if fkChild:
        cmds.parent(fkChild, fkCtrlName)
    return True


def reorientFKNeckControl(fkCtrlName, orientRotate=[0, -90, -90]):
    """

    reorientFKNeckControl('FKNeck_M', orientRotate=[0,-90,-90])
    """
    fk_rename = cmds.rename(fkCtrlName, '{}_orig'.format(fkCtrlName))
    fk_copy = cmds.duplicate(fk_rename, name=fkCtrlName)

    if cmds.listRelatives(fk_copy[0], children=True):
        cmds.delete(cmds.listRelatives(fk_copy[0], children=True))

    #cmds.parent('{}Shape'.format(fk_rename), fk_copy[0], relative=True, shape=True)
    cmds.delete('{}Shape'.format(fk_rename))
    cmds.hide(fk_rename)

    ori_node = insertAsParent(fkCtrlName, name=None, suffix="ReOrient", match=True, nodeType='transform')
    off_node = insertAsParent(fkCtrlName, name=None, suffix="Offset", match=True, nodeType='transform')

    fkChild = cmds.listRelatives(fkCtrlName, children=True, type="joint")
    if fkChild:
        cmds.parent(fkChild, world=True)
    cmds.setAttr("%s.rotate" % ori_node, *orientRotate)
    if fkChild:
        cmds.parent(fkChild, fkCtrlName)

    cmds.parentConstraint(fk_copy[0], fk_rename, mo=True)
    cmds.scaleConstraint(fk_copy[0], fk_rename, mo=True)

    cmds.sets(fkCtrlName, off_node, add='ControlSet')

    return True


def matchPose(src, dst, poseType='pose'):
    """Match dst transform to src transform (follows maya constraint argument order: src, dst)"""
    if (poseType == 'position'):
        position = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        cmds.xform(dst, worldSpace=True, translation=position)

    elif (poseType == 'rotation'):
        rotation = cmds.xform(src, query=True, worldSpace=True, rotation=True)
        cmds.xform(dst, worldSpace=True, rotation=rotation)

    elif (poseType == 'scale'):
        scale = cmds.xform(src, query=True, worldSpace=True, scale=True)
        cmds.xform(dst, worldSpace=True, scale=scale)

    elif (poseType == 'pose'):
        pivot = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        matrix = cmds.xform(src, query=True, worldSpace=True, matrix=True)
        matrix[12] = pivot[0]
        matrix[13] = pivot[1]
        matrix[14] = pivot[2]
        cmds.xform(dst, worldSpace=True, matrix=matrix)


def getParent(node, recursive=False, breakNode=None):
    """Get parent node, if recursive get topnode in heirarchy """
    parents = cmds.listRelatives(node, parent=True)
    if not parents:
        return None
    parent = parents[0]

    if recursive:
        recursiveParents = [parent]
        while parent:
            parents = cmds.listRelatives(parent, parent=True)
            if parents:
                parent = parents[0]
                if parent == breakNode:
                    break
                else:
                    recursiveParents.append(parent)
            else:
                break
        return recursiveParents
    else:
        return parent


def insertAsParent(node, name=None, suffix=None, match=True, nodeType='transform'):
    """Insert parent node"""
    # Get node parent
    parent = getParent(node)

    # Resolve name
    if not name:
        if suffix:
            name = node + '_' + suffix
        else:
            name = node + '_grp'

    # Create new node under parent
    insert = cmds.createNode(nodeType, name=name, parent=parent)

    # Match node
    if match:
        matchPose(node, insert)
    else:
        matchPose(parent, insert)

    # Parent node under insert
    cmds.parent(node, insert)

    return insert


def toList(input):
    """Takes input and returns it as a list"""
    if isinstance( input, list ):
        return input

    elif isinstance( input, tuple ):
        return list(input)

    return [input]


def dump(curves=None):
    """Get a data dictionary representing all the given curves.

    Args:
        curves: Optional list of curves.

    Returns: A json serializable list of dictionaries containing the data required to recreate the curves.
    """
    curves = toList(curves)
    data = []
    for node in curves:
        cmds.delete(node, constructionHistory=True)
        shapes = cmds.listRelatives(node, s=True)
        if not shapes:
            continue
        for shp in shapes:
            if cmds.nodeType(shp) == 'nurbsCurve':
                control = {}
                control = {
                    'name': node,
                    'shape': shp,
                    'cvs': cmds.getAttr('{0}.cv[*]'.format(shp)),
                    'degree': cmds.getAttr('{0}.degree'.format(shp)),
                    'form': cmds.getAttr('{0}.form'.format(shp)),
                    'xform': cmds.xform(node, q=True, ws=True, matrix=True),
                    'knots': get_knots(shp),
                    'pivot': cmds.xform(node, q=True, rp=True),
                    'overrideEnabled': cmds.getAttr('{0}.overrideEnabled'.format(shp)),
                    'overrideColor': cmds.getAttr('{0}.overrideColor'.format(shp)),
                }
                if MAYA_VER > 2015:
                    control['overrideRGBColors'] = cmds.getAttr('{0}.overrideRGBColors'.format(shp))
                    control['overrideColorRGB'] = cmds.getAttr('{0}.overrideColorRGB'.format(shp))[0]
                control['parent'] = cmds.ls(node)[0]
                data.append(control)
    return data


def get_knots(curve):
    """Gets the list of knots of a curve so it can be recreated.

    Args:
        curve: Curve to query.

    Returns: A list of knot values that can be passed into the curve creation command.

    """
    if not 'nurbsCurve' in cmds.nodeType(curve):
        curve = shape.getShape(curve)
    info = cmds.createNode('curveInfo')
    cmds.connectAttr('{0}.worldSpace'.format(curve), '{0}.inputCurve'.format(info))
    knots = cmds.getAttr('{0}.knots[*]'.format(info))
    cmds.delete(info)
    return knots


def create_curve(control, transform=None):
    """Create a curve.

    Args:
        control: A data dictionary generated from the dump function.
        transform: A transform node to add curveShape to.

    Returns:
        Curve name.
    """
    curve = control['name']
    curveShape = control['shape']

    periodic = control['form'] == 2
    degree = control['degree']
    points = control['cvs']

    if periodic and not cmds.objExists(curveShape):
        points = points + points[:degree]

    if cmds.objExists(curveShape):
        i = 0
        while i < len(points):
            cmds.move(points[i][0], points[i][1], points[i][2], '%s.cv[%s]' % (curveShape, i), os=True)
            i = i + 1

    else:
        if cmds.objExists(curve):
            curve = cmds.curve(degree=degree, p=points, n="TEMP" + control['name'], per=periodic, k=control['knots'])
        else:
            curve = cmds.curve(degree=degree, p=points, n=control['name'], per=periodic, k=control['knots'])
        curveShape = cmds.rename(cmds.listRelatives(curve, shapes=True)[0], curveShape)

        if 'parent' in control:
            if cmds.objExists(control['parent']):
                if control['parent'] != cmds.listRelatives(curveShape, parent=True)[0]:
                    try:
                        cmds.parent(curveShape, control['parent'], relative=True, shape=True)
                        cmds.delete(curve)
                    except:
                        pass

    # parenting
    if (transform and (transform is not cmds.listRelatives(curveShape, p=True, type='transform')[0])):
        try:
            cmds.parent(curveShape, transform, s=1, r=1)
            cmds.delete(curve)
        except:
            pass

    if cmds.objExists(curve):
        cmds.delete(curve, constructionHistory=True)

        cmds.setAttr('{0}.overrideEnabled'.format(curve), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curve), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curve), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curve), *control['overrideColorRGB'])
        except:
            pass

    if cmds.objExists(curveShape):
        cmds.setAttr('{0}.overrideEnabled'.format(curveShape), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curveShape), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curveShape), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curveShape), *control['overrideColorRGB'])
        except:
            pass

    return curve


def fixSplineIKControlOrientation(controlObject, orientObject="", endControl=False):
    """Use to properly orient spline IK controls down chain (default is World orientation)
    Args:
        controlObject:  IKSpline control node
        orientObject:   Object that controlObject's orientation will be matched.
                        Suggest using the "AlignTo" node under the first IKSpline control.
        endControl:     Used to specify that this is the last IKSpline control for extra setup steps
    *Uses cvs on original cube control shape to get orientation
    Example:
        fixSplineIKControlOrientation("IKSplineSac1_M", orientObject="IKSplineSac0AlignTo_M")
        fixSplineIKControlOrientation("IKSplineSac2_M", orientObject="IKSplineSac0AlignTo_M")
        fixSplineIKControlOrientation("IKSplineSac3_M", orientObject="IKSplineSac0AlignTo_M", endControl=True)
    """
    if mc.objExists(controlObject):
        ctlLoc = mc.listRelatives(controlObject, children=True, type="transform")
        if ctlLoc:
            mc.parent(ctlLoc, world=True)
        ctlExtra = mc.listRelatives(controlObject, parent=True)[0]
        ctlOff = mc.listRelatives(ctlExtra, parent=True)[0]
        ctlShp = mc.listRelatives(controlObject, shapes=True)
        ctlParCon = mc.listConnections("%s.tx" % ctlOff, s=True, d=False)[0]
        if ctlShp:
            # Record all ctl cvs positions
            crvData = {}
            mc.select("%s.cv[0:*]" % controlObject)
            for item in mc.ls(selection=True, flatten=True):
                cvPos = mc.xform(item, q=True, ws=True, t=True)
                crvData[item] = cvPos
            # Reorient ctls parentConstraint targets
            parConTgts = mc.parentConstraint(ctlParCon, q=True, targetList=True)
            mc.delete(mc.orientConstraint(orientObject, parConTgts[0]))
            mc.delete(mc.listConnections("%s.tx" % parConTgts[1], s=True, d=False))
            mc.delete(mc.orientConstraint(orientObject, parConTgts[1]))
            mc.parentConstraint("%sNoScale" % parConTgts[1], parConTgts[1], mo=True)
            # Restore orig ctl cv positions
            for cv, pos in crvData.iteritems():
                mc.move(pos[0], pos[1], pos[2], cv, ws=True)
            # If end control, do a few more steps
            if endControl:
                endOriCon = mc.listConnections("%s.rotate" % controlObject, s=False, d=True)
                if endOriCon:
                    for axis in ["X", "Y", "Z"]:
                        mc.setAttr("%s.offset%s" % (endOriCon[0], axis), 0)
        if ctlLoc:
            mc.parent(ctlLoc, controlObject)
        mc.select(controlObject)


