"""
    BUG (from tcoleman, 02-28-18)
    For some reason I've run into a bug with this plugin in for Maya 2018.
    The parentConstraints for the FK chain/controls do not constrain
    properly and the FK joints are left with an incorrect rotation.
    I have found in a separate Python task that I need to delete the
    incorrect parentConstraints and re-constrain them.

"""

import maya.cmds as cmds
import py_tasker.tasks
import dragonfly.modules
import dragonfly.node
import pymel.core as pm

CTL = "ctl"
JNT = "jnt"
OFF = "off"
BUF = "buf"
EXP = "off_exp"

LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '1.0.0'
CONTROL_SHAPE_DATA = {
    "p": [[0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918], [0.0, 0.0, 0.5541],
          [-0.391, 0.0, 0.3918], [-0.554, 0.0, 0.0], [-0.391, 0.0, -0.3918], [0.0, 0.0, -0.5541],
          [0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918]],
    "k": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    "d": 1,
    "per": False
}


def setUp(params, spec):
    LOG.info('set up FK/IK')


def run(params, rig):
    """Run the IK setup for the Rig

    :param params:Reads UI data
    :param rig: UI Data
    :return:
    """

    # Make sure matrixNodes plugin is loaded
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    # Gather Task Data
    controls = list()
    controls.append(params['ikRootControl'].name())
    controls.append(params['ikPoleControl'].name())
    controls.append(params['ikGoalControl'].name())

    # Create IK Setup
    skeleton = [x.name() for x in params['ikSkeleton']]
    ik_joints = duplicate_joints(skeleton, 'ik')
    ik_chain_offset = group_with_transform(ik_joints[0])
    cmds.parent(ik_chain_offset, rig['rigGroup'])
    ik_handle, pole_crv, ik_buffer = create_ik_setup(controls, ik_joints)
    cmds.parent(pole_crv, rig['rigGroup'])

    # Run FK Setup
    fk_buffers = fk_run(params, rig)

    # Check if IK FK Switch is checked if so run its Setup
    switch_setup(params, rig, ik_joints)
    if params['fkIkSwitch'] is True:
        switch_setup(params, rig, ik_joints)

    visibility_attributes(params, fk_buffers, ik_buffer)
    if params['addIkPoleControlFollow']:
        follow_attribute(params)

    for x, y in zip(ik_joints, skeleton):
        cmds.pointConstraint(x, y, mo=False)
        cmds.orientConstraint(x, y, mo=False)
        cmds.scaleConstraint(x, y, mo=False)


def duplicate_joints(joints, suffix):
    new_joints = []
    for n, jnt in enumerate(joints):
        new_joint_name = '{0}_{1}'.format(jnt, suffix)
        new_joint = cmds.duplicate(jnt, name=new_joint_name, po=True)[0]
        new_joints.append(str(new_joint))

        if n > 0:
            cmds.parent(new_joint, new_joints[n - 1])
        else:
            cmds.parent(new_joint, world=True)
    return new_joints


def group_with_transform(node):
    """Create an offset transform for the given node

    :param node: Duplicated joints to be grouped and zeroed
    :return:
    """

    # Group and zero out input nodes, and return new offset groups that contain nodes
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
    """Lock and hide the attrs for the IK setup

    :param node: Ik Controllers
    :param lock: Attribute
    :param hide: Attribute
    :param attrs: Attribute
    """
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

    # Create control offset transforms
    exp_tf_ms = []
    for ctl in controls:
        par = cmds.listRelatives(ctl, parent=True)
        buf = create_offset_transform(ctl, BUF)
        exp = create_offset_transform(ctl, EXP)
        off = create_offset_transform(ctl, OFF)
        cmds.parent(ctl, off)
        cmds.parent(off, exp)
        cmds.parent(exp, buf)
        if par:
            cmds.parent(buf, par[0])
        exp_tf_ms.append(buf)

    root_control, pole_control, goal_control = controls
    handle, effector = cmds.ikHandle(sj=joints[0], ee=joints[-1], sol='ikRPsolver')
    cmds.setAttr('{}.hiddenInOutliner'.format(handle), True)
    cmds.orientConstraint(goal_control, joints[-1], mo=True)
    cmds.parent(handle, goal_control)
    cmds.hide(handle)

    # Connect root control to ik joint offset group
    ik_joints_offset = cmds.listRelatives(joints[0], p=True)[0]
    cmds.parentConstraint(root_control, ik_joints_offset, mo=True)
    cmds.scaleConstraint(root_control, ik_joints_offset, mo=True)

    # Connect twisting and pole vector control
    cmds.addAttr(goal_control, ln='twist', at='float', k=True)
    cmds.connectAttr('{}.twist'.format(goal_control), '{}.twist'.format(handle))
    cmds.poleVectorConstraint(pole_control, handle)

    # Add PV visibility attribute
    cmds.addAttr(goal_control, shortName='pv', longName='poleVector', at='bool', k=True)
    cmds.connectAttr('{}.pv'.format(goal_control), '{}.v'.format(pole_control))
    cmds.setAttr('{}.pv'.format(goal_control),1)

    # Add curve that points elbow to pole control
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

    return handle, crv, exp_tf_ms


def setUp(params, spec):
    """Special method used to intialize a `TaskSpec` instance of this `TaskFactory`.

    Args:
        params: These are the parameters for this `RigSpec` instance, get/set just like dictionary calls
        spec: The `TaskSpec` object that this method runs from, this gives you access to the entire class instance

    Returns:
        None
    """

    if not params['fkSkeleton']:
        joints = []

        for x in range(params['numberOfSegments']):
            jnt = cmds.createNode('joint')
            jnt = cmds.rename(jnt, '{baseName}{index}_{JNT}'.format(baseName=spec.name, index=x, JNT=JNT)).split('|')[-1]
            if x > 0:
                cmds.parent(jnt, joints[x - 1])
                cmds.setAttr('{node}.translateY'.format(node=jnt), 1.0)
            joints.append(jnt)

        spec.params()['fkSkeleton'] = dragonfly.node.dfNode.fromList(joints)

    if not params['fkControls']:
        controls = []

        for x in range(params['fkNumberOfSegments']):
            ctl = cmds.curve(**CONTROL_SHAPE_DATA)
            cmds.controller(ctl)
            ctl = cmds.rename(ctl, '{baseName}{index}_{CTL}'.format(baseName=spec.name, index=x, CTL=CTL))
            match_nodes(params['fkSkeleton'][x].name(), ctl)
            if x > 0:
                cmds.parent(ctl, controls[x-1])
            controls.append(ctl)

        spec.params()['fkControls'] = dragonfly.node.dfNode.fromList(controls)


def fk_run(params, rig):
    '''
    Run the Setup for the FK part of the chain.
    :param params:
    :param rig:
    rn: None
    '''

    if params['fkUseConstraints'] is False:
        LOG.exception('`useConstraints` is currently not implemented, will continue building using default constraints.')

    fkControls = [x.name() for x in params['fkControls']]
    fkSkeleton = [x.name() for x in params['fkSkeleton']]
    contraint_nodes, fk_buffer = create_fk_chain(fkControls, fkSkeleton)

    # cleanup not used channels for controls
    if params['fkDisableScaling']:
        for ctl in fkControls:
            cmds.setAttr('{node}.sx'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sy'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sz'.format(node=ctl), l=True, cb=False)

    return fk_buffer


def create_fk_chain(controls, joints):
    """Creates an FK rig setup.

    Args:
        controls (list): Control objects
        joints (list): FK joints

    Returns:
        list: Constraint nodes generated
    """

    # create control offset transforms
    constraints = []
    exp_tf_ms = []

    for ctl in controls:
        par = cmds.listRelatives(ctl, parent=True)
        buf = create_offset_transform(ctl, BUF)
        exp = create_offset_transform(ctl, EXP)
        off = create_offset_transform(ctl, OFF)

        cmds.parent(ctl, off)
        cmds.parent(off, exp)
        cmds.parent(exp, buf)
        if par: cmds.parent(buf, par[0])

        exp_tf_ms.append(buf)

    for src, trg in zip(controls, joints):
        # constrain fk joints to controls, hide the constraint nodes
        pc = cmds.parentConstraint(src, trg, mo=True)[0]
        cmds.setAttr('{node}.interpType'.format(node=pc), 2)
        cmds.setAttr('{node}.visibility'.format(node=pc), False)
        sc = cmds.scaleConstraint(src, trg)[0]
        cmds.setAttr('{node}.visibility'.format(node=sc), False)
        constraints.extend([pc, sc])

    return constraints, exp_tf_ms


def create_offset_transform(node):
    """Create a group above the given node.

    This cleans up transformation(TRS) values from the channel box.

    Args:
        node: Node to be parented under the offset transform, used also to solve for offset transform's transform

    Returns:
        str: Name of the new offset transform node
    """

    offset_transform = cmds.createNode('transform')
    match_nodes(node, offset_transform)
    offset_transform = cmds.rename(offset_transform, '{node}_zero'.format(node=node))

    return offset_transform


def match_nodes(source_node, target_node):
    """Move and orient one target node to another source node.

    Args:
        source_node: Node to get transform data from
        target_node: Node to apply transform data to

    Returns:
        None
    """

    node_position = cmds.xform(source_node, q=True, ws=True, t=True)
    node_rotation = cmds.xform(source_node, q=True, ws=True, ro=True)
    cmds.xform(target_node, ws=True, t=node_position)
    cmds.xform(target_node, ws=True, ro=node_rotation)


def switch_setup(params, rig, ik_joints):
    """This will add visibility option

    :return:

    """

    # Duplicate for bind skeleton
    skeleton = [x.name() for x in params['ikSkeleton']]
    bind_skeleton = cmds.duplicate(skeleton, n=skeleton[0] + '_bnd_0')
    #bind_skeleton

    # Hide all attribute on Controller
    fkikcontrol = params['fkIkSwitch'].name()
    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    for i in attrs:
        cmds.setAttr('{node}.{attr}'.format(node=fkikcontrol, attr=i), k=False, cb=False)

    # Create FK/IK Switch attributes
    cmds.addAttr(fkikcontrol, sn='FKIKBlend', at='float', min=0, max=1, dv=0, k=True)
    cmds.addAttr(fkikcontrol, sn='AutoVis', at='bool', dv=1, k=True)
    cmds.addAttr(fkikcontrol, ln='FKVis', at='bool', dv=1, k=True)
    cmds.addAttr(fkikcontrol, ln='IKVis', at='bool', dv=1, k=True)

    # create control offset transforms
    # par = cmds.listRelatives(fkikcontrol, parent=True)
    # buf = create_offset_transform(fkikcontrol, BUF)
    # cmds.parent(fkikcontrol, buf)
    # if par: cmds.parent(buf, par[0])

    # Parent Skeleton to rig group
    ik_skeleton = [x.name() for x in params['ikSkeleton']]
    fk_skeleton = [x.name() for x in params['fkSkeleton']]
    cmds.parent(ik_skeleton[0], rig['rigGroup'])
    cmds.parent(fk_skeleton[0], rig['rigGroup'])

    # Constraint Bind Skeleton
    fk_ik_finish(ik_joints, bind_skeleton, params)


def create_offset_transform(node, suffix):
    """Create a group above the given node.

    This cleans up transformation(TRS) values from the channel box.

    Args:
        node: Node to be parented under the offset transform, used also to solve for offset transform's transform

    Returns:
        str: Name of the new offset transform node
    """
    offset_transform = cmds.createNode('transform')
    match_nodes(node, offset_transform)
    if "ctl" in node:
        offset_transform = cmds.rename(offset_transform, '{node}_{suffix}'.format(node=node.replace("_ctl", ""),
                                                                                  suffix=suffix))
    else:
        offset_transform = cmds.rename(offset_transform, '{node}_{suffix}'.format(node=node, suffix=suffix))

    return offset_transform


def fk_ik_finish(ik_joints, bind_skeleton, params):
    """Constraint Bind Skeleton, Add SDk FKIK Switch, and Connect Visibility Attributes

    :param ik_joints: Ik joints for constraining
    :param bind_skeleton: Bind Skeleton for joints to be constrained too
    :param params:
    :return:
    """

    # Constraint to Bind Skeleton
    fkSkeleton = [x.name() for x in params['fkSkeleton']]
    for x, y in zip(ik_joints, bind_skeleton):
        cmds.parentConstraint(x, y, mo=False)
    for x, y in zip(fkSkeleton, bind_skeleton):
        cmds.parentConstraint(x, y, mo=False)

    # Add SDK for fk ik switch
    fk_ik_control = params['fkIkSwitch'].full_path()
    new_skeleton = cmds.listRelatives(bind_skeleton[0], ad=True, typ='joint')
    new_skeleton.append(str(bind_skeleton[0]))

    for ik in new_skeleton:
        ik_attr = cmds.listAttr(ik + '_parentConstraint1', k=True)
        driver = str(fk_ik_control) + '.FKIKBlend'
        driven_a = ik + '_parentConstraint1' + str('.' + ik_attr[-2])
        cmds.connectAttr(driver, driven_a)

    for fk in new_skeleton:
        reverse_node = cmds.createNode('reverse', n=str(fk) + 'fkIkReverse')
        input_x = str(reverse_node) + '.inputX'
        temp_driver = str(fk_ik_control) + '.FKIKBlend'
        cmds.connectAttr(temp_driver, input_x)
        fk_attr = cmds.listAttr(fk + '_parentConstraint1', k=True)
        driven_b = fk + '_parentConstraint1' + str('.' + fk_attr[-1])
        cmds.connectAttr(reverse_node + '.outputX', driven_b)


def visibility_attributes(params, fk_buffers, ik_buffers):
    '''
    :param params:
    :param fk_buffers:
    :param ik_buffers:
    :return:
    '''

    fk_ik_control = params['fkIkSwitch'].full_path()

    fk_ik_driver = str(fk_ik_control) + '.FKIKBlend'

    ik_controls = [params['ikPoleControl'].full_path(), params['ikGoalControl'].full_path()]
    ik_buf_controls = []

    for i in ik_controls:
        parents = cmds.listRelatives(i, ap=True)
        grandparents = cmds.listRelatives(parents, ap=True)
        great_grandparents = cmds.listRelatives(grandparents, ap=True)
        ik_buf_controls.append(great_grandparents[0])

    # IK Connect Visibility Attributes
    ik_driven = str(ik_buffers[0]) + '.visibility'
    cmds.connectAttr(fk_ik_driver, ik_driven)
    for v in ik_buf_controls:
        cmds.connectAttr(fk_ik_driver, v + '.visibility')

    # FK Connect Visibility Attributes
    reverse_node = cmds.createNode('reverse', n=str(fk_buffers[0]) + 'fkIkReverse')
    fk_driven = str(fk_buffers[0]) + '.visibility'
    cmds.connectAttr(fk_ik_driver, reverse_node + '.inputX')
    cmds.connectAttr(reverse_node + '.outputX', fk_driven)


def follow_attribute(params):
    '''
    This function will add the follow function to the Pole Vector Controls on the IK/FK Legs
    '''

    # Declare the variables that will be used to create the follow attribute in the function
    root_ctl = params['ikRootControl'].name()
    goal_ctl = params['ikGoalControl'].name()
    pole_ctl = params['ikPoleControl'].name()
    pole_off = pole_ctl.replace('_ctl', '_off_exp')
    ik1_jnt = params['ikSkeleton'][0].name()
    #null_fp = cmds.createNode('transform', n='Auto_FollowBase' + '_' + root_ctl, p='rt_fk0_jnt')
    null_fp = cmds.createNode('transform', n='Auto_FollowBase' + '_' + root_ctl, p='noXform')
    null_ff = cmds.createNode('transform', n='Auto_FollowGoal' + '_' + goal_ctl, p=null_fp)

    # Parent the null groups under the noXform
    #cmds.parent(null_fp, 'noXform')

    # Create the Aim Constraints for the follow base
    pm.aimConstraint(goal_ctl, null_fp, weight=1, upVector=(1, 0, 0), worldUpObject=root_ctl,
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
