import json
import logging

import maya.cmds as cmds


LOG = logging.getLogger(__name__)
MTYPE_RIG = 'dragonfly.rig'
MTYPE_CTL = 'dragonfly.ctl'


def get_rigs():
    result = list()
    attrs = cmds.ls('*.metaTypes', long=True, r=True)
    result.extend([attr.split('.', 1)[0] for attr in attrs if MTYPE_RIG in json.loads(cmds.getAttr(attr))])

    return result


def get_rig_controls(rig=None):
    result = list()
    attrs = cmds.ls('*.metaTypes', long=True, r=True)
    result.extend([attr.split('.', 1)[0] for attr in attrs if MTYPE_CTL in json.loads(cmds.getAttr(attr))])

    if rig is not None:
        result = [node_name for node_name in result if rig in node_name]

    return result


def get_rig_control_defaults(rig=None):
    result = dict()

    controls = get_rig_controls(rig)
    for ctl in controls:
        raw_value = cmds.getAttr('{0}.defaults'.format(ctl))
        value = json.loads(raw_value)
        result[ctl] = value

    return result


def get_selected_controls():
    result = list()
    selection = cmds.ls(sl=True, long=True, r=True)

    if not selection:
        LOG.debug('No control objects selected, exiting')
        return

    for node in selection:
        if not cmds.attributeQuery('metaTypes', n=node, ex=True):
            continue

        attr = '{0}.metaTypes'.format(node)
        if MTYPE_CTL in json.loads(cmds.getAttr(attr)):
            ctl = attr.split('.', 1)[0]
            result.append(ctl)

    return result