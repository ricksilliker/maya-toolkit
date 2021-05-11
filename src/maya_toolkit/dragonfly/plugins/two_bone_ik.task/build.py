import math

import py_tasker.tasks

import maya.cmds as cmds

LOG = py_tasker.tasks.get_task_logger(__name__)


def setUp(params, spec):
    LOG.info('set up two_bone_ik')


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

    # add stretch nodes
    if params['addStretch']:
        if params['axisDownBone'] != 1:
            LOG.exception('Stretch currently only works with Y down the bone orientations')
        create_vanilla_stretch(controls, ik_joints, params['axisDownBone'], params['isNegative'], ik_handle)


def create_vanilla_stretch(controls, joints, axis_down_bone, is_negative, ik_handle):
    """To replace plugin stretch, and phase out the py plugin until cpp inplimentation.
    Should be used instead of plugin in maya 2016 and up to not bottleneck the rig in parallel eval.
    """

    anim_attrs = [
        # {'showPoleVector': {'at': 'float', 'min': 0, 'max': 1, 'dv': 1, 'k': False}},
        {'ikStretchBlend': {'at': 'float', 'min': 0, 'max': 1, 'dv': 1, 'k': True}},
        {'length': {'at': 'float', 'min': 25, 'dv': 100, 'k': True}},
        {'upperLength': {'at': 'float', 'min': 0, 'dv': 100, 'k': True}},
        {'lowerLength': {'at': 'float', 'min': 0, 'dv': 100, 'k': True}},
        {'softness': {'at': 'float', 'min': 0, 'dv': 0, 'k': True}},
    ]

    rig_attrs = [
        {'lengthBoost': {'at': 'float', 'dv': 0, 'k': False}},
        {'upperLengthOrig': {'at': 'float', 'dv': 0, 'k': False}},
        {'lowerLengthOrig': {'at': 'float', 'dv': 0, 'k': False}},
        {'lengthCurrent': {'at': 'float', 'dv': 0, 'k': False}},
        {'upperLengthCurrent': {'at': 'float', 'dv': 0, 'k': False}},
        {'lowerLengthCurrent': {'at': 'float', 'dv': 0, 'k': False}},
        {'adjustedLength': {'at': 'float', 'dv': 0, 'k': False}},
        {'adjustedDistance': {'at': 'float', 'dv': 0, 'k': False}},
        {'pushBack': {'at': 'float', 'dv': 0, 'k': False}},
        {'ikGoalDistance': {'at': 'float', 'dv': 0, 'k': False}},
        {'ikStretchScale': {'at': 'float', 'dv': 0, 'k': False}},
        {'ikStretchScaleInv': {'at': 'float', 'dv': 0, 'k': False}},
    ]
    for attr in anim_attrs:
        for k, v in attr.iteritems():
            cmds.addAttr(controls[0], ln=k, **v)
            if 'k' in v:
                if v['k'] is False:
                    cmds.setAttr('{}.{}'.format(controls[0], k), cb=True)

    for attr in rig_attrs:
        for k, v in attr.iteritems():
            cmds.addAttr(controls[0], ln=k, **v)
            if 'k' in v:
                if v['k'] is False:
                    cmds.setAttr('{}.{}'.format(controls[0], k), cb=False)

    axis_string = ['x', 'y', 'z'][axis_down_bone]

    upper_length = cmds.getAttr('{0}.t{1}'.format(joints[1], axis_string))
    upper_length_abs = math.fabs(upper_length)
    print upper_length_abs
    cmds.setAttr('{}.upperLengthOrig'.format(controls[0]), upper_length_abs)

    lower_length = cmds.getAttr('{0}.t{1}'.format(joints[2], axis_string))
    lower_length_abs = math.fabs(lower_length)
    cmds.setAttr('{}.lowerLengthOrig'.format(controls[0]), lower_length_abs)

    set_lengths(controls[0])

    set_ik_stretch_scale(controls[0])

    set_ik_stretch_scale_inverse(controls[0])

    softBlendOut = add_softness(controls[0])

    rootPos = cmds.xform(joints[0], ws=True, q=True, t=True)
    endPos = cmds.xform(joints[2], ws=True, q=True, t=True)

    driver, reader = add_distance_reader(controls[2], rootPos, endPos, joints[0])
    cmds.parent(ik_handle, driver)
    cmds.connectAttr('{}.t{}'.format(reader, axis_string), '{}.ikGoalDistance'.format(controls[0]))
    cmds.connectAttr(softBlendOut, '{}.t{}'.format(driver, axis_string))

    midTranOut, endTranOut = add_ik_soft_stretch(controls[0])

    if is_negative:
        midTranNegate = cmds.createNode('multDoubleLinear')
        cmds.connectAttr(midTranOut, '{}.input1'.format(midTranNegate))
        cmds.setAttr('{}.input2'.format(midTranNegate), -1)
        midTranOut = '{}.output'.format(midTranNegate)

        endTranNegate = cmds.createNode('multDoubleLinear')
        cmds.connectAttr(endTranOut, '{}.input1'.format(endTranNegate))
        cmds.setAttr('{}.input2'.format(endTranNegate), -1)
        endTranOut = '{}.output'.format(endTranNegate)

    cmds.connectAttr(midTranOut, '{}.t{}'.format(joints[1], axis_string))
    cmds.connectAttr(endTranOut, '{}.t{}'.format(joints[2], axis_string))

    return driver


def set_lengths(ikControl):
    """Define length attrs for setupVanillaStretch."""
    lengthBoost = cmds.createNode('addDoubleLinear')
    cmds.connectAttr('{}.length'.format(ikControl), '{}.input1'.format(lengthBoost))
    cmds.connectAttr('{}.lengthBoost'.format(ikControl), '{}.input2'.format(lengthBoost))

    lengthRemap = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.output'.format(lengthBoost), '{}.input1'.format(lengthRemap))
    cmds.setAttr('{}.input2'.format(lengthRemap), 0.01)

    # upperLimb
    upperLengthRemap = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.upperLength'.format(ikControl), '{}.input1'.format(upperLengthRemap))
    cmds.setAttr('{}.input2'.format(upperLengthRemap), 0.01)

    upperLengthBoost = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.output'.format(lengthRemap), '{}.input1'.format(upperLengthBoost))
    cmds.connectAttr('{}.output'.format(upperLengthRemap), '{}.input2'.format(upperLengthBoost))

    upperLength = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.output'.format(upperLengthBoost), '{}.input1'.format(upperLength))
    cmds.connectAttr('{}.upperLengthOrig'.format(ikControl), '{}.input2'.format(upperLength))
    cmds.connectAttr('{}.output'.format(upperLength), '{}.upperLengthCurrent'.format(ikControl))

    # lowerLimb
    lowerLengthRemap = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.lowerLength'.format(ikControl), '{}.input1'.format(lowerLengthRemap))
    cmds.setAttr('{}.input2'.format(lowerLengthRemap), 0.01)

    lowerLengthBoost = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.output'.format(lengthRemap), '{}.input1'.format(lowerLengthBoost))
    cmds.connectAttr('{}.output'.format(lowerLengthRemap), '{}.input2'.format(lowerLengthBoost))

    lowerLength = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.output'.format(lowerLengthBoost), '{}.input1'.format(lowerLength))
    cmds.connectAttr('{}.lowerLengthOrig'.format(ikControl), '{}.input2'.format(lowerLength))
    cmds.connectAttr('{}.output'.format(lowerLength), '{}.lowerLengthCurrent'.format(ikControl))

    # totalLength
    length = cmds.createNode('addDoubleLinear')
    cmds.connectAttr('{}.output'.format(upperLength), '{}.input1'.format(length))
    cmds.connectAttr('{}.output'.format(lowerLength), '{}.input2'.format(length))
    cmds.connectAttr('{}.output'.format(length), '{}.lengthCurrent'.format(ikControl))


def set_ik_stretch_scale(root_control):
    """Sets scale for setupVanillaStretch.
    Not in use.
    """
    div = cmds.createNode('multiplyDivide')
    cmds.setAttr('{}.operation'.format(div), 2)

    clamp = cmds.createNode('clamp')
    cmds.setAttr('{}.minR'.format(clamp), 1.0)
    cmds.setAttr('{}.maxR'.format(clamp), 9999.0)

    cmds.connectAttr('{}.ikGoalDistance'.format(root_control), '{}.input1X'.format(div))
    cmds.connectAttr('{}.lengthCurrent'.format(root_control), '{}.input2X'.format(div))
    cmds.connectAttr('{}.outputX'.format(div), '{}.inputR'.format(clamp))
    cmds.connectAttr('{}.outputR'.format(clamp), '{}.ikStretchScale'.format(root_control))


def set_ik_stretch_scale_inverse(root_control):
    """
    Sets inverted scale for setupVanillaStretch.
    Not in use.
    """
    div = cmds.createNode('multiplyDivide')
    cmds.setAttr('{}.operation'.format(div), 2)
    cmds.setAttr('{}.input1X'.format(div), 1.0)
    cmds.connectAttr('{}.ikStretchScale'.format(root_control), '{}.input2X'.format(div))
    cmds.connectAttr('{}.outputX'.format(div), '{}.ikStretchScaleInv'.format(root_control))


def add_softness(ikControl):
    """Adds soft attr to IK for setupVanillaStretch.

    Notes:
        Mirrors functionality for right side.
    """
    softClamp = cmds.createNode('clamp')
    cmds.connectAttr('{}.softness'.format(ikControl), '{}.inputR'.format(softClamp))
    cmds.setAttr('{}.minR'.format(softClamp), 0.001)
    cmds.setAttr('{}.maxR'.format(softClamp), 100.0)

    lengthSub = cmds.createNode('plusMinusAverage')
    cmds.setAttr('{}.operation'.format(lengthSub), 2)
    cmds.connectAttr('{}.lengthCurrent'.format(ikControl), '{}.input1D[0]'.format(lengthSub))
    cmds.connectAttr('{}.outputR'.format(softClamp), '{}.input1D[1]'.format(lengthSub))

    ikGoalSub = cmds.createNode('plusMinusAverage')
    cmds.setAttr('{}.operation'.format(ikGoalSub), 2)
    cmds.connectAttr('{}.output1D'.format(lengthSub), '{}.input1D[0]'.format(ikGoalSub))
    cmds.connectAttr('{}.ikGoalDistance'.format(ikControl), '{}.input1D[1]'.format(ikGoalSub))

    softDiv = cmds.createNode('multiplyDivide')
    cmds.setAttr('{}.operation'.format(softDiv), 2)
    cmds.connectAttr('{}.output1D'.format(ikGoalSub), '{}.input1X'.format(softDiv))
    cmds.connectAttr('{}.outputR'.format(softClamp), '{}.input2X'.format(softDiv))

    powE = cmds.createNode('multiplyDivide')
    cmds.setAttr('{}.operation'.format(powE), 3)
    cmds.setAttr('{}.input1X'.format(powE), 2.718)
    cmds.connectAttr('{}.outputX'.format(softDiv), '{}.input2X'.format(powE))

    kValueMult = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.outputR'.format(softClamp), '{}.input1'.format(kValueMult))
    cmds.connectAttr('{}.outputX'.format(powE), '{}.input2'.format(kValueMult))

    adjustTotal = cmds.createNode('plusMinusAverage')
    cmds.setAttr('{}.operation'.format(adjustTotal), 2)
    cmds.connectAttr('{}.lengthCurrent'.format(ikControl), '{}.input1D[0]'.format(adjustTotal))
    cmds.connectAttr('{}.output'.format(kValueMult), '{}.input1D[1]'.format(adjustTotal))

    longEnoughCond = cmds.createNode('condition')
    cmds.setAttr('{}.operation'.format(longEnoughCond), 5)
    cmds.connectAttr('{}.ikGoalDistance'.format(ikControl), '{}.firstTerm'.format(longEnoughCond))
    cmds.connectAttr('{}.output1D'.format(lengthSub), '{}.secondTerm'.format(longEnoughCond))
    cmds.connectAttr('{}.ikGoalDistance'.format(ikControl), '{}.colorIfTrueR'.format(longEnoughCond))
    cmds.connectAttr('{}.output1D'.format(adjustTotal), '{}.colorIfFalseR'.format(longEnoughCond))
    cmds.connectAttr('{}.outColorR'.format(longEnoughCond), '{}.adjustedDistance'.format(ikControl))

    softBlend = cmds.createNode('blendTwoAttr')
    cmds.connectAttr('{}.outColorR'.format(longEnoughCond), '{}.input[0]'.format(softBlend))
    cmds.connectAttr('{}.ikGoalDistance'.format(ikControl), '{}.input[1]'.format(softBlend))
    cmds.connectAttr('{}.ikStretchBlend'.format(ikControl), '{}.attributesBlender'.format(softBlend))

    return '{}.output'.format(softBlend)


def add_ik_soft_stretch(root_control):
    """Setup for blending stretch for setupVanillaStretch."""
    softGoalDivide = cmds.createNode('multiplyDivide')
    cmds.setAttr('{}.operation'.format(softGoalDivide), 2)
    cmds.connectAttr('{}.ikGoalDistance'.format(root_control), '{}.input1X'.format(softGoalDivide))
    cmds.connectAttr('{}.adjustedDistance'.format(root_control), '{}.input2X'.format(softGoalDivide))

    softAdjMinus = cmds.createNode('addDoubleLinear')
    cmds.setAttr('{}.input2'.format(softAdjMinus), -1.0)
    cmds.connectAttr('{}.outputX'.format(softGoalDivide), '{}.input1'.format(softAdjMinus))

    softStretchPlus = cmds.createNode('addDoubleLinear')
    cmds.setAttr('{}.input2'.format(softStretchPlus), 1.0)
    cmds.connectAttr('{}.output'.format(softAdjMinus), '{}.input1'.format(softStretchPlus))

    softScale = cmds.createNode('condition')
    cmds.setAttr('{}.operation'.format(softScale), 2)
    cmds.connectAttr('{}.ikGoalDistance'.format(root_control), '{}.firstTerm'.format(softScale))
    cmds.connectAttr('{}.adjustedDistance'.format(root_control), '{}.secondTerm'.format(softScale))
    cmds.connectAttr('{}.output'.format(softStretchPlus), '{}.colorIfTrueR'.format(softScale))

    # upperLimb
    kneeSoftScaledTranslate = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.upperLengthCurrent'.format(root_control), '{}.input1'.format(kneeSoftScaledTranslate))
    cmds.connectAttr('{}.outColorR'.format(softScale), '{}.input2'.format(kneeSoftScaledTranslate))

    kneeIkSoftStretch = cmds.createNode('blendTwoAttr')
    cmds.connectAttr('{}.ikStretchBlend'.format(root_control), '{}.attributesBlender'.format(kneeIkSoftStretch))
    cmds.connectAttr('{}.upperLengthCurrent'.format(root_control), '{}.input[0]'.format(kneeIkSoftStretch))
    cmds.connectAttr('{}.output'.format(kneeSoftScaledTranslate), '{}.input[1]'.format(kneeIkSoftStretch))

    # lowerLimb
    ankleSoftScaledTranslate = cmds.createNode('multDoubleLinear')
    cmds.connectAttr('{}.lowerLengthCurrent'.format(root_control), '{}.input1'.format(ankleSoftScaledTranslate))
    cmds.connectAttr('{}.outColorR'.format(softScale), '{}.input2'.format(ankleSoftScaledTranslate))

    ankleIkSoftStretch = cmds.createNode('blendTwoAttr')
    cmds.connectAttr('{}.ikStretchBlend'.format(root_control), '{}.attributesBlender'.format(ankleIkSoftStretch))
    cmds.connectAttr('{}.lowerLengthCurrent'.format(root_control), '{}.input[0]'.format(ankleIkSoftStretch))
    cmds.connectAttr('{}.output'.format(ankleSoftScaledTranslate), '{}.input[1]'.format(ankleIkSoftStretch))

    knee_output = '{}.output'.format(kneeIkSoftStretch)
    ankle_output = '{}.output'.format(ankleIkSoftStretch)

    return [knee_output, ankle_output]


def add_distance_reader(goal_control, start_position, end_position, root_joint):
    """Setup for reading length of root to ikHandle for setupVanillaStretch."""
    distance_reader_grp = cmds.createNode('transform', n='twoBoneIkFk_distanceReader_grp')
    cmds.parent(distance_reader_grp, cmds.listRelatives(root_joint, p=True)[0])
    start_joint = cmds.createNode('joint')
    cmds.setAttr('{}.translate'.format(start_joint), *start_position)
    cmds.parent(start_joint, distance_reader_grp)
    end_joint = cmds.createNode('joint')
    cmds.setAttr('{}.translate'.format(end_joint), *end_position)
    cmds.parent(end_joint, start_joint)
    ori = build_orient()
    cmds.joint(start_joint, e=True, oj=ori[0], sao=ori[1])
    cmds.setAttr('{}.jointOrient'.format(end_joint), 0, 0, 0)
    handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint, sol='ikSCsolver')
    cmds.parent(handle, distance_reader_grp)
    cmds.pointConstraint(goal_control, handle, mo=True)
    reader_node = cmds.spaceLocator(n='ikReader#')[0]
    driver_node = cmds.spaceLocator(n='ikDriver#')[0]
    cmds.parent(reader_node, driver_node, end_joint)
    cmds.setAttr('{}.translate'.format(reader_node), 0, 0, 0)
    cmds.setAttr('{}.rotate'.format(reader_node), 0, 0, 0)
    cmds.setAttr('{}.translate'.format(driver_node), 0, 0, 0)
    cmds.setAttr('{}.rotate'.format(driver_node), 0, 0, 0)
    cmds.parent(reader_node, driver_node, start_joint)
    cmds.pointConstraint(goal_control, reader_node, mo=True)

    return driver_node, reader_node


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

    handle, effector = cmds.ikHandle(sj=joints[0], ee=joints[2], sol='ikRPsolver')
    cmds.setAttr('{}.hiddenInOutliner'.format(handle), True)
    cmds.orientConstraint(goal_control, joints[2], mo=True)
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


def build_orient(aimAxis='y', upAxis='+z'):
    """Builds an orienation based on string input.
    Converts positive and negative signs to key words for Maya's orient arguments on joints.
    """
    if '+' in upAxis:
        direction = 'up'
        upAxis = upAxis.strip('+')
    elif '-' in upAxis:
        direction = 'down'
        upAxis = upAxis.strip('-')
    up = upAxis + direction
    axes = ['x', 'y', 'z']
    axes.remove(aimAxis)
    axes.remove(upAxis)
    ori = aimAxis + upAxis + axes[0]
    return [ori, up]


def circle_control(name):
    node = cmds.createNode('transform', n=name)

    shapeData = {
        'p': [[0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918], [0.0, 0.0, 0.5541],
              [-0.391, 0.0, 0.3918], [-0.554, 0.0, 0.0], [-0.391, 0.0, -0.3918], [0.0, 0.0, -0.5541],
              [0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918]],
        'k': [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        'd': 3,
        'per': True
    }

    curve = cmds.curve(**shapeData)
    shape = cmds.listRelatives(curve, s=True)[0]
    cmds.parent(shape, node, s=True, r=True)
    cmds.delete(curve)

    return node


def cube_control(name):
    node = cmds.createNode('transform', n=name)

    shapeData = {
        'p': [[-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5],
                  [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5],
                  [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5],
                  [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5]],
        'k': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0],
        'd': 1,
        'per': False
    }

    curve = cmds.curve(**shapeData)
    shape = cmds.listRelatives(curve, s=True)[0]
    cmds.parent(shape, node, s=True, r=True)
    cmds.delete(curve)

    return node