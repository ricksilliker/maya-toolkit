import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)
import dragonfly.meta_types
reload(dragonfly.meta_types)

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):

    for fkik in params['fkikSwitches']:

        # FKIK Switch
        fkik_switch = fkik['fkikSwitch']

        # FK nodes
        fk_ctls = [fk_ctl for fk_ctl in fkik['fkControls'].replace(' ', '').split(",")]

        # IK nodes
        ik_ctls = [ik_ctl for ik_ctl in fkik['ikControls'].replace(' ', '').split(",")]
        ik_ctl = ik_ctls[0]
        ik_pv = ik_ctls[1]
        ik_ctl_align = cmds.listRelatives(fk_ctls[2], ad=True, type='transform')[0]

        # If this is a leg, there should be FKToe control in the list
        ik_toe_align = None
        if len(fk_ctls) > 3:
            ik_toe_align = cmds.listRelatives(fk_ctls[3], ad=True, type='transform')[0]
            LOG.warning('Found FKToeAlign node: {}'.format(ik_toe_align))

        ik_jnts = list()
        for fk_ctl in fk_ctls:
            ik_jnt = fk_ctl.replace('FK', 'IKX')
            if cmds.objExists(ik_jnt):
                ik_jnts.append(ik_jnt)
        ik_local = ik_ctl.replace('IK', 'IKLocal')

        # Add message attrs to fkik switch control
        add_message_attribute(fkik_switch, [fkik_switch], 'fkik_switch')
        add_message_attribute(fkik_switch, fk_ctls, 'fk_ctls')
        add_message_attribute(fkik_switch, [ik_ctl], 'ik_ctl')
        add_message_attribute(fkik_switch, [ik_pv], 'ik_pv')
        add_message_attribute(fkik_switch, [ik_ctl_align], 'ik_ctl_align')
        add_message_attribute(fkik_switch, ik_jnts, 'ik_jnts')
        if cmds.objExists(ik_local):
            add_message_attribute(fkik_switch, [ik_local], 'ik_local')

        if len(fk_ctls) > 3:
            add_message_attribute(fkik_switch, [ik_toe_align], 'ik_toe_align')

        # Add message attrs to IK nodes
        add_message_attribute(ik_ctl, [fkik_switch], 'fkik_switch')
        add_message_attribute(ik_pv, [fkik_switch], 'fkik_switch')
        if cmds.objExists(ik_local):
            add_message_attribute(ik_local, [fkik_switch], 'fkik_switch')

        # Add message attrs to FK nodes
        for fk_ctl in fk_ctls:
            add_message_attribute(fk_ctl, [fkik_switch], 'fkik_switch')

        # Add metatype tags
        if 'Arm' in fkik_switch:
            dragonfly.modules.add_metatype(fkik_switch, dragonfly.meta_types.MTYPE_BIPED_ARM)

        elif 'Leg' in fkik_switch:
            dragonfly.modules.add_metatype(fkik_switch, dragonfly.meta_types.MTYPE_BIPED_LEG)

        LOG.info('Added FKIK control message attributes to {}'.format(fkik_switch))


def add_message_attribute(src, tgts, attr_name):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        add_message_attribute("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attr_name, exists=True, node=src):
            cmds.addAttr(src, sn=attr_name, at='message', m=True)

        i = 0
        while i < len(tgts):
            idx = get_next_free_multi_index("{}.{}".format(src, attr_name), i)
            cmds.connectAttr("%s.message" % (tgts[i]), "%s.%s[%s]" % (src, attr_name, str(idx)), f=True)
            i = i + 1

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise

def get_message_attribute_connections(src, attr_name):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        get_message_attribute_connections("box_fk_ctrl", attr_name="pivot_node")
    """
    try:
        if cmds.attributeQuery(attr_name, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attr_name))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attr_name, src))
        raise

def get_next_free_multi_index(attr_name, start_index):
    """Find the next unconnected multi index starting at the passed in index"""
    # assume a max of 10 million connections
    while start_index < 10000000:
        if len(cmds.connectionInfo('{}[{}]'.format(attr_name, start_index), sfd=True) or []) == 0:
            return start_index
        start_index += 1

    # No connections means the first index is available
    return 0


