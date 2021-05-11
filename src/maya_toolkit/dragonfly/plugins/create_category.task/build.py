import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules


LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '1.0.0'
RIG_CATEGORIES = ['meshes', 'skeleton', 'ctls', 'rig', 'spaces', 'sim', 'noXform']
MTYPE_CATEGORY = 'dragonfly.category'


def run(params, rig):
    for cat in params['categories']:
        cat_node = cmds.createNode('transform', name=cat['name'])
        dragonfly.modules.add_metatype(cat_node, MTYPE_CATEGORY)
        rig['{}Group'.format(cat['name'])] = cat_node

        if 'rig' in rig:
            cmds.parent(cat_node, rig['rig'])
            if cat['vis']:
                add_vis_switch(cat_node, rig['rig'])

        for attr_name in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
            cmds.setAttr('{}.{}'.format(cat_node, attr_name), l=True, k=False, cb=False)

    # parent category nodes into the proper group of the rig
    for cat in params['categories']:
        LOG.debug('Populating {} category group..'.format(cat))
        if cat['nodes']:
            nodes = [cmds.ls(x, long=True)[0] for x in cat['nodes']]
            parent_node = get_parent_nodes(nodes)
            cmds.parent(parent_node, rig['{}Group'.format(cat['name'])])


def get_parent_nodes(nodes):
    """Given a list of nodes, get the top-most level nodes of the list.

    Args:
        nodes (list): Node names.

    Returns:
        list: Top most representation in the hierarchy of each node
    """
    result = []
    for n in nodes:
        if any([p in nodes for p in get_all_parents(n)]):
            continue
        result.append(n)
    return result


def get_all_parents(node):
    """Give a node, get the parent nodes at each level.

    Args:
        node: Node long name

    Returns:
        list: Parent nodes to a given node
    """
    split = node.split('|')
    return ['|'.join(split[:i]) for i in reversed(range(2, len(split)))]


def add_vis_switch(grp, vis_node):

    cmds.addAttr(vis_node, ln='{}_outA'.format(grp), at='long', dv=0, k=False, h=False)
    cmds.addAttr(vis_node, ln='{}_outB'.format(grp), at='long', dv=2, k=False, h=False)
    cmds.addAttr(vis_node, ln='{}_outC'.format(grp), at='long', dv=0, k=False, h=False)
    cmds.addAttr(vis_node, ln='{}_outD'.format(grp), at='long', dv=1, k=False, h=False)

    # add visibility attr
    cmds.addAttr(vis_node, ln=grp, at='enum', enumName='off:on:reference:template', dv=1, k=False)
    cmds.setAttr("{}.{}".format(vis_node, grp), cb=True)

    # Set visibility and overrides
    cmds.connectAttr("{}.{}".format(vis_node, grp), '{}.visibility'.format(grp))
    cmds.connectAttr("{}.{}".format(vis_node, grp), '{}.overrideEnabled'.format(grp))

    # set up choice nodes to drive overrides instead of SDK
    choiceOverride = cmds.createNode('choice', n='%s_override_choice' % grp)

    cmds.connectAttr('{}.{}'.format(vis_node, grp), '{}.selector'.format(choiceOverride))
    cmds.connectAttr('{}.{}_outA'.format(vis_node, grp), '{}.input[0]'.format(choiceOverride))
    cmds.connectAttr('{}.{}_outC'.format(vis_node, grp), '{}.input[1]'.format(choiceOverride))
    cmds.connectAttr('{}.{}_outB'.format(vis_node, grp), '{}.input[2]'.format(choiceOverride))
    cmds.connectAttr('{}.{}_outD'.format(vis_node, grp), '{}.input[3]'.format(choiceOverride))

    cmds.connectAttr('{}.output'.format(choiceOverride), '{}.overrideDisplayType'.format(grp))
