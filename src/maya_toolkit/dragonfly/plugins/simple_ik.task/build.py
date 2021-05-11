import py_tasker.tasks
import maya.cmds as cmds
import pymel.core as pm

LOG = py_tasker.tasks.get_task_logger(__name__)


def setUp(params, spec):
    LOG.info('set up simple_ik')


def run(params, rig):
    # make sure matrixNodes plugin is loaded
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    controls = list()
    controls.append(params['rootControl'].name())
    controls.append(params['poleControl'].name())
    controls.append(params['goalControl'].name())

    # create ik setup
    skeleton = [x.name() for x in params['skeleton']]
    ik_joints = duplicate_joints(joints=skeleton)
    ik_chain_offset = group_with_transform(ik_joints[0])
    cmds.parent(ik_chain_offset, rig['rigGroup'])
    ik_handle, pole_crv = create_ik_setup(controls, ik_joints)
    cmds.parent(pole_crv, rig['rigGroup'])

    for x, y in zip(ik_joints, skeleton):
        cmds.pointConstraint(x, y, mo=False)
        cmds.orientConstraint(x, y, mo=False)
        cmds.scaleConstraint(x, y, mo=False)

    follow_attribute(params)

def duplicate_joints(joints):
    new_joints = []
    for n, jnt in enumerate(joints):
        new_joint_name = '{0}_ik'.format(jnt)
        new_joint = cmds.createNode('joint', n=new_joint_name)
        new_joints.append(new_joint)

        position = cmds.xform(jnt, q=True, ws=True, t=True)
        rotation = cmds.xform(jnt, q=True, ws=True, ro=True)
        radius = cmds.getAttr('{}.radius'.format(jnt))

        cmds.setAttr('{}.radius'.format(new_joint), radius)
        cmds.setAttr('{}.translate'.format(new_joint), *position)
        cmds.setAttr('{}.jointOrient'.format(new_joint), *rotation)

        if n > 0:
            cmds.parent(new_joint, new_joints[n-1])

    return new_joints


def group_with_transform(node):
    """Create an offset transform for the given node."""

    new_transform_name = '{0}_zero'.format(node)

    offset = cmds.createNode('transform', n=new_transform_name)

    position = cmds.xform(node, q=True, ws=True, t=True)
    rotation = cmds.xform(node, q=True, ws=True, ro=True)

    cmds.xform(offset, ws=True, t=position)
    cmds.xform(offset, ws=True, t=rotation)

    node_parent = cmds.listRelatives(node, p=True)
    if node_parent:
        cmds.parent(offset, node_parent)

    cmds.parent(node, offset)

    return offset


def lock_hide_attrs(node, lock=True, hide=True, attrs=None):
    kw = dict()
    if lock:
        kw['l'] = lock
    if hide:
        kw['cb'] = not hide
        kw['k'] = not hide

    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), **kw)


def create_ik_setup(controls, joints):
    """Creates an IK rig setup.

    Args:
        controls (list): control objects.
        joints (list): ik joint objects.

    Returns:
        str: ikHandle name
    """

    root_control, pole_control, goal_control = controls

    handle, effector = cmds.ikHandle(sj=joints[0], ee=joints[-1], sol='ikRPsolver')
    cmds.setAttr('{}.hiddenInOutliner'.format(handle), True)
    cmds.orientConstraint(goal_control, joints[-1], mo=True)
    cmds.parent(handle, goal_control)

    # connect root control to ik joint offset group
    ik_joints_offset = cmds.listRelatives(joints[0], p=True)[0]
    cmds.parentConstraint(root_control, ik_joints_offset, mo=True)
    cmds.scaleConstraint(root_control, ik_joints_offset, mo=True)

    # connect twisting and pole vector control
    cmds.addAttr(goal_control, ln='twist', at='float', k=True)
    cmds.connectAttr('{}.twist'.format(goal_control), '{}.twist'.format(handle))

    cmds.poleVectorConstraint(pole_control, handle)

    # add curve that points elbow to pole control
    crv = cmds.curve(p=[[0, 0, 0], [0, 1, 0]], d=1)
    cmds.connectAttr('{}.visibility'.format(pole_control), '{}.visibility'.format(crv))
    lock_hide_attrs(crv, attrs=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
    cmds.setAttr('{}.overrideEnabled'.format(crv), True)
    cmds.setAttr('{}.overrideDisplayType'.format(crv), 2)
    decomp_joint = cmds.createNode('decomposeMatrix')
    decomp_control = cmds.createNode('decomposeMatrix')
    cmds.connectAttr('{}.worldMatrix'.format(joints[1]), '{}.inputMatrix'.format(decomp_joint))
    cmds.connectAttr('{}.worldMatrix'.format(pole_control), '{}.inputMatrix'.format(decomp_control))
    cmds.connectAttr('{}.outputTranslate'.format(decomp_joint), '{}.controlPoints[0]'.format(crv))
    cmds.connectAttr('{}.outputTranslate'.format(decomp_control), '{}.controlPoints[1]'.format(crv))
    
    return handle, crv


def follow_attribute(params):
    '''
    This function will add the follow function to the Pole Vector Controls on the IK/FK Legs
    '''

    # Declare the variables that will be used to create the follow attribute in the function
    root_ctl = params['rootControl'].name()
    goal_ctl = params['goalControl'].name()
    pole_ctl = params['poleControl'].name()
    pole_off = pole_ctl.replace('_ctl', '_off_exp')
    ik1_jnt = params['skeleton'][0].name()
    null_fp = cmds.createNode('transform', n='Auto_FollowBase' + '_' + root_ctl, p='rt_fk0_jnt')
    null_ff = cmds.createNode('transform', n='Auto_FollowGoal' + '_' + goal_ctl, p=null_fp)

    # Parent the null groups under the noXform
    cmds.parent(null_fp, 'noXform')

    # Create the Aim Constraints for the follow base
    pm.aimConstraint(goal_ctl, null_fp, weight=1, upVector=(0, 1, 0), worldUpObject=root_ctl,
                     worldUpType="objectrotation", offset=(0, 0, 0), aimVector=(0, -1, 0),
                     worldUpVector=(1, 0, 0))
    cmds.pointConstraint(ik1_jnt, null_fp, mo=True)

    # Create the Aim Constraints for the follow goal
    pm.aimConstraint(goal_ctl, null_ff, weight=1, upVector=(0, 1, 0), worldUpObject=goal_ctl,
                     worldUpType="objectrotation", offset=(0, 0, 0), aimVector=(0, -1, 0),
                     worldUpVector=(1, 0, 0))

    # Create the parent constraint for the pole vector control
    pole_vector_constraint = cmds.parentConstraint(null_ff, pole_off, mo=True)
    i = cmds.parentConstraint(pole_vector_constraint[0], wal=True, q=True)

    # Connect follow and pole vector control
    cmds.addAttr(goal_ctl, ln='poleVectorFollow', at='bool', k=True)
    cmds.connectAttr('{}.poleVectorFollow'.format(goal_ctl), '{}.{}'.format(str(pole_vector_constraint[0]),
                                                                            str(i[0])))
