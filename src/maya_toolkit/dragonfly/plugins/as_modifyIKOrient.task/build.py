import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)

from maya import cmds


def run(params, rig):

    for ik in params['IKControls']:
        ik_ctl = ik['IKControl']
        ik_off = ik['IKOffsetNode']
        orient_str = [ori for ori in ik['AxisRotation'].replace(' ', '').split(",")]
        orient_val = map(int, orient_str)
        flip_IK_control(ik_ctl, ik_off, flip_axis=orient_val)


def flip_IK_control(ik_control, flip_node, flip_axis=[0,0,180]):
    """
    
    flip_IK_control('rt_leg_ik_ctl', 'rt_IKOffsetLeg', flip_axis=[0,0,180])
    flip_IK_control('rt_leg_ik_ctl', 'rt_IKOffsetLeg', flip_axis=[0,180,180])
    flip_IK_control('rt_leg_ik_ctl', 'rt_IKOffsetLeg', flip_axis=[180,0,0])
    """
    
    # Record all ctl cvs positions
    crvData = {}
    cmds.select("%s.cv[0:*]" % ik_control)
    for item in cmds.ls(selection=True, flatten=True):
        cvPos = cmds.xform(item, q=True, ws=True, t=True)
        crvData[item] = cvPos
        
    # Unparent children of IK control
    ik_children = cmds.listRelatives(ik_control, children=True, type=['transform', 'joint'])
    print ik_children
    if ik_children:
        cmds.parent(ik_children, world=True)
        
    flip_tfm = insertAsParent(flip_node, name=None, suffix='flip')
    cmds.setAttr('{}.rotateAxis'.format(flip_tfm), *flip_axis)
    cmds.parent(ik_children, ik_control)
        
    # Restore orig ctl cv positions of control
    for cv, pos in crvData.iteritems():
        cmds.move(pos[0], pos[1], pos[2], cv, ws=True)
        
        
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