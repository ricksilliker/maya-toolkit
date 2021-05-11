import maya.cmds as cmds

import py_tasker.tasks


LOG = py_tasker.tasks.get_task_logger(__name__)

def run(params, rig):
    for cat in params['spaces']:
        space_object = cat['target'].name()

        cmds.addAttr(space_object, ln='spaceName', dt='string')
        cmds.setAttr('{}.spaceName'.format(space_object), cat['spaceName'], type='string')
        cmds.addAttr(space_object, ln='spaceDelegates', at='message')

        if cat['delegates']:
            for node in cat['delegates']:
                cmds.addAttr(node.name(), ln='spaceRoot', at='message')
                cmds.connectAttr('{}.spaceDelegates'.format(space_object), '{}.spaceRoot'.format(node.name()))

