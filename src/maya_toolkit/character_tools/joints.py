import maya.cmds as cmds
import maya.api.OpenMaya as om2

import math

import errors


def spline_to_joints(*args, **kwargs):
    selection = cmds.ls(sl=True)

    if not selection:
        raise errors.CharacterToolsError('No object has been selected')

    if cmds.nodeType(selection[0]) != 'nurbsCurve':
        if cmds.nodeType(selection[0]) == 'transform':
            selection = cmds.listRelatives(selection[0], s=True)
            if not selection or cmds.nodeType(selection[0]) != 'nurbsCurve':
                raise errors.CharacterToolsError('No curve object has been selected')

    sel = om2.MSelectionList()
    sel.add(selection[0])
    mobject = sel.getDagPath(0)
    mfn_curve = om2.MFnNurbsCurve(mobject)

    last_joint = None
    for mpoint in mfn_curve.cvPositions(space=om2.MSpace.kWorld):
        jnt = cmds.createNode('joint')
        cmds.xform(jnt, ws=True, t=[mpoint.x, mpoint.y, mpoint.z])
        closest_point, param = mfn_curve.closestPoint(mpoint, space=om2.MSpace.kWorld)
        n = mfn_curve.normal(param, space=om2.MSpace.kWorld)
        t = mfn_curve.tangent(param, space=om2.MSpace.kWorld)
        n.normalize()
        t.normalize()
        b = n ^ t
        mat = [(n.x, n.y, n.z, 0.0), (t.x, t.y, t.z, 0.0), (b.x, b.y, b.z, 0.0), (0.0, 0.0, 0.0, 1.0)]
        rot = om2.MEulerRotation().setValue(om2.MMatrix(mat))
        rot = [math.degrees(x) for x in [rot.x, rot.y, rot.z]]
        cmds.xform(jnt, ws=True, ro=rot)
        if last_joint is not None:
            cmds.parent(jnt, last_joint)
        last_joint = jnt

    cmds.delete(cmds.listRelatives(selection[0], p=True))


def joints_to_spline(*args, **kwargs):
    joints = [x for x in cmds.ls(sl=True) if cmds.nodeType(x) == 'joint']
    points = [cmds.xform(x, q=True, ws=True, t=True) for x in joints]
    cmds.curve(p=points, d=3)
    cmds.delete(joints)


def convert_to_nulls(*args, **kwargs):
    for x in cmds.ls(sl=True):
        if cmds.nodeType(x) == 'joint':
            grp = cmds.createNode('transform')