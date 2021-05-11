import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules
import dragonfly.meta_types

LOG = py_tasker.tasks.get_task_logger(__name__)


def setUp(params, spec):
    pass


def run(params, rig):
    cmds.addAttr(rig['rig'], ln='bakeNodes', at='message', multi=True)

    for index, node in enumerate(params['nodes']):
        dragonfly.modules.add_metatype(node.name(), dragonfly.meta_types.MTYPE_BAKEABLE)
        cmds.connectAttr('{}.message'.format(node.name()), '{}.bakeNodes[{}]'.format(rig['rig'], index))
