import maya.cmds as cmds

import py_tasker.tasks


LOG = py_tasker.tasks.get_task_logger(__name__)
CONSTRAINT_TYPES = [cmds.pointConstraint,
                    cmds.orientConstraint,
                    cmds.scaleConstraint,
                    cmds.parentConstraint,
                    [cmds.parentConstraint, cmds.scaleConstraint]]


def run(params, rig):
    leader = params['leader'].name()
    followers = [x.name() for x in params['followers']]

    constraint = CONSTRAINT_TYPES[params['constraintType']]

    if isinstance(constraint, (list, tuple)):
        for cnt in constraint:
            cnt = cnt(leader, followers, mo=params['maintainOffset'])
    else:
        cnt = constraint(leader, followers, mo=params['maintainOffset'])

    cmds.parent(cnt, rig['noXformGroup'])
