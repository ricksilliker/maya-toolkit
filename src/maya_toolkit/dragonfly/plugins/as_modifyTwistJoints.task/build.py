import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):

    for twist_joints in params['twistParentJoints']:

        twist_par_joint = twist_joints['twistParentJoint']
        twist_joints = [twjnt for twjnt in twist_joints['twistJoints'].replace(' ', '').split(",")]

        LOG.info('Modifying twist joint parenting for {}'.format(twist_par_joint))

        if twist_par_joint and twist_joints:
            reparent_twist_joints(twist_joints, twist_par_joint)

        LOG.info('Successfully modified twist joint parenting for {}'.format(twist_par_joint))


def reparent_twist_joints(twist_joints, parent):
    """Reparents a list of twist joints to new parent, useful
    when you need to modify in-line twist joints to being siblings

    Args:
        twist_joints: list of twist joints in hierarchical order (lowest last)
        parent: node to parent twist joints and last twist joint's children

    reparent_twist_joints(['ShoulderPart1_R', 'ShoulderPart2_R'], 'Shoulder_R')
    """
    for tw_jnt in twist_joints:
        child = cmds.listRelatives(twist_joints[-1], children=True)
        if child:  cmds.parent(child, parent)

        parent_jnt = cmds.listRelatives(tw_jnt, parent=True)
        if parent_jnt:
            if not parent in parent_jnt:
                cmds.parent(tw_jnt, parent)