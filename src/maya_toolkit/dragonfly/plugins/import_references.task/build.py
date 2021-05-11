import maya.cmds as cmds

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    refs = cmds.file(q=True, r=True)
    for ref in refs:
        LOG.debug('Importing Reference..')
        if cmds.referenceQuery(ref, il=True):
            cmds.file(ref, ir=True)