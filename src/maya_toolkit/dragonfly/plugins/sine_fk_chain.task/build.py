import py_tasker.tasks
import dragonfly.modules
import dragonfly.node

import maya.cmds as cmds


LOG = py_tasker.tasks.get_task_logger(__name__)
CTL = "ctl"
OFF = "off"
BUF = "buf"
EXP = "off_exp"
JNT = "jnt"
CONTROL_SHAPE_DATA = {
    "p": [[0.5,0.5,-0.5],[0.5,0.5,0.5],[0.5,-0.5,0.5],[0.5,-0.5,-0.5],[0.5,0.5,-0.5],[-0.5,0.5,-0.5],
        [-0.5,-0.5,-0.5],[-0.5,-0.5,0.5],[-0.5,0.5,0.5],[0.5,0.5,0.5],[0.5,-0.5,0.5],[-0.5,-0.5,0.5],
        [-0.5,-0.5,-0.5],[0.5,-0.5,-0.5],[0.5,0.5,-0.5],[-0.5,0.5,-0.5],[-0.5,0.5,0.5],[0.5,0.5,0.5],
        [0.5,0.5,-0.5]],
    "k": [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8],
    "d": 1,
    "per": False
}
SINE_CONTROL_SHAPE_DATA = {
    "p": [[0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918], [0.0, 0.0, 0.5541],
          [-0.391, 0.0, 0.3918], [-0.554, 0.0, 0.0], [-0.391, 0.0, -0.3918], [0.0, 0.0, -0.5541],
          [0.3918, 0.0, -0.3918], [0.5541, 0.0, 0.0], [0.3918, 0.0, 0.3918]],
    "k": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    "d": 1,
    "per": False
}


def setUp(params, spec):
    """Special method used to intialize a `TaskSpec` instance of this `TaskFactory`.

    Args:
        params: These are the parameters for this `RigSpec` instance, get/set just like dictionary calls
        spec: The `TaskSpec` object that this method runs from, this gives you access to the entire class instance

    Returns:
        None
    """
    baseName = params['baseName']

    if not params['sineControl']:
        sineCtl = create_curve(SINE_CONTROL_SHAPE_DATA)
        sineCtl = cmds.rename(sineCtl, "{}_{}".format(baseName, CTL))
        spec.params()['sineControl'] = dragonfly.node.dfNode.fromName(sineCtl)

    if not params['skeleton']:
        joints = []

        for x in range(params['numberOfSegments']):
            jnt = cmds.createNode('joint')
            jnt = cmds.rename(jnt, '{}{index}_jnt'.format(baseName, index=x)).split('|')[-1]
            if x > 0:
                cmds.parent(jnt, joints[x - 1])
                cmds.setAttr('{node}.translateZ'.format(node=jnt), -2.0)
            joints.append(jnt)

        spec.params()['skeleton'] = [[x, dragonfly.modules.get_uuid(x)] for x in joints]

    if not params['controls']:
        controls = []

        for x in range(params['numberOfSegments']):
            ctl = cmds.curve(**CONTROL_SHAPE_DATA)
            cmds.controller(ctl)
            ctl = cmds.rename(ctl, '{}{index}_ctl'.format(baseName, index=x))
            match_nodes((params['skeleton'][x])[0], ctl)
            if x > 0:
                cmds.parent(ctl, controls[x-1])
            controls.append(ctl)

        spec.params()['controls'] = [[x, dragonfly.modules.get_uuid(x)] for x in controls]


def run(params, rig):
    # make sure matrixNodes plugin is loaded
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    baseName = params['baseName']
    controls = [x.name() for x in params['controls']]
    skeleton = [x.name() for x in params['skeleton']]
    sineControl = params['sineControl'].name()
    sineAxis = params['sineAxis'].split(',')
    contraint_nodes = createFishFk(baseName, controls, skeleton, sineControl, sineAxis)

    # cleanup not used channels for controls
    if params['disableScaling']:
        for ctl in controls:
            cmds.setAttr('{node}.sx'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sy'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sz'.format(node=ctl), l=True, cb=False)


def createFishFk(baseName, controls, joints, sineControl, sineAxis):
    """Creates procedurally swimming fish spine using Maya expressions"""

    constraints = []

    # create control offset transforms
    expTfms = []
    for ctl in controls:
        par = cmds.listRelatives(ctl, parent=True)
        buf = create_offset_transform(ctl, BUF)
        exp = create_offset_transform(ctl, EXP)
        off = create_offset_transform(ctl, OFF)

        cmds.parent(ctl, off)
        cmds.parent(off, exp)
        cmds.parent(exp, buf)
        if par: cmds.parent(buf, par[0])

        expTfms.append(exp)

    # connect joints to controls
    for ctl, jnt in zip(controls, joints):
        pc = cmds.parentConstraint(ctl, jnt, mo=True)[0]
        sc = cmds.scaleConstraint(ctl, jnt, mo=True)[0]
        constraints.append(pc)
        constraints.append(sc)

    # add auto-swim expressions
    swimCtl = sineControl

    if cmds.objExists(swimCtl):
        attrs = ['onOff', 'magnitude', 'frequency']

        expr = "// {} AutoSwim Expression\n".format(swimCtl)

        if not cmds.attributeQuery("_all_", node=swimCtl, exists=True):
            attrs_attributeSeparator(swimCtl, '_all_')

        if not cmds.attributeQuery("all_on_off", node=swimCtl, exists=True):
            cmds.addAttr(swimCtl, ln="all_on_off", dv=1, min=0, max=1)
            cmds.setAttr("{}.all_on_off".format(swimCtl), k=True, l=False)

        if not cmds.attributeQuery("all_magnitude", node=swimCtl, exists=True):
            cmds.addAttr(swimCtl, ln="all_magnitude", dv=1)
            cmds.setAttr("{}.all_magnitude".format(swimCtl), k=True, l=False)

        if not cmds.attributeQuery("all_frequency", node=swimCtl, exists=True):
            cmds.addAttr(swimCtl, ln="all_frequency", dv=1)
            cmds.setAttr("{}.all_frequency".format(swimCtl), k=True, l=False)

        # Per axis expression control attrs
        attrs_attributeSeparator(swimCtl, '__{}__'.format(baseName))
        for axis in sineAxis:
            for attr in attrs:
                attr = '{}_R{}'.format(attr, axis)

                if "onOff" in attr:
                    cmds.addAttr(swimCtl, longName="{}_{}".format(baseName, attr), dv=0, min=0, max=1)
                else:
                    cmds.addAttr(swimCtl, longName="{}_{}".format(baseName, attr), dv=1, min=0)
                cmds.setAttr("{}.{}_{}".format(swimCtl, baseName, attr), lock=False, keyable=True)

            # Create Auto-Swim Expression
            expr += "float $all_onOff_R{} = {}.all_on_off;\n".format(axis, swimCtl)
            expr += "float $all_mag_R{} = ({}.all_magnitude);\n".format(axis, swimCtl)
            expr += "float $all_freq_R{} = {}.all_frequency;\n".format(axis, swimCtl)
            expr += "\n"

            expr += "float $onOff_R{} = {}.{}_onOff_R{};\n".format(axis, swimCtl, baseName, axis)
            expr += "float $freq_R{} = ({}.{}_frequency_R{})/100;\n".format(axis, swimCtl, baseName, axis)
            expr += "float $GLOBAL_mag_R{} = {}.{}_magnitude_R{};\n".format(axis, swimCtl, baseName, axis)
            expr += "\n"

        i = 0
        for ctl, exp in zip(controls, expTfms):
            attrs_attributeSeparator(ctl, '__SINE_MOTION_R{}__'.format(axis.upper()))
            for axis in sineAxis:

                cmds.addAttr(ctl, longName="frameDelay_R{}".format(axis), dv=i)
                cmds.setAttr("{}.frameDelay_R{}".format(ctl, axis), lock=False, keyable=True)

                cmds.addAttr(ctl, longName="magnitude_R{}".format(axis), dv=i)
                cmds.setAttr("{}.magnitude_R{}".format(ctl, axis), lock=False, keyable=True)

                expr += "float $LOCAL_delay{}_R{} = {}.frameDelay_R{};\n".format(str(i), axis, ctl, axis)
                expr += "float $LOCAL_mag{}_R{} = {}.magnitude_R{};\n".format(str(i), axis, ctl, axis)
                expr += "{}.rotate{} = ($onOff_R{} * sin(( frame * ($freq_R{} * $all_freq_R{})) + $LOCAL_delay{}_R{} ) * ( ($GLOBAL_mag_R{} * $LOCAL_mag{}_R{} * $all_mag_R{}))) * $all_onOff_R{};\n".format(exp, axis.upper(), axis, axis, axis, str(i), axis, axis, str(i), axis, axis, axis)
                expr += "\n"
            i = i + 1

        cmds.expression(s=expr, o="", n="{}_AutoSwim_expr".format(baseName), ae=0, uc='all')

        return constraints


def create_curve(curve_data):
    """Uses dictionary of curve data to create curve and properly rename curve shape node"""
    crv = cmds.curve(**curve_data)
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], "{}Shape".format(crv))
    return crv


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
        offset_transform = cmds.rename(offset_transform, '{node}_{suffix}'.format(node=node.replace("_ctl", ""), suffix=suffix))
    else:
        offset_transform = cmds.rename(offset_transform, '{node}_{suffix}'.format(node=node, suffix=suffix))

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


def attrs_attributeSeparator(control, attr):
    """Create a separator attribute on the specified control object

    Args:
        control: The control to add the separator attribute to
        attr: The separator attribute name

    Returns:

    Example:
        attrs_attributeSeparator('Lf_arm_ctrl', '___')
    """
    # Check control
    if not cmds.objExists(control):
        raise Exception('Control object "'+control+'" does not exist!')

    # Check attribute
    if cmds.objExists(control+'.'+attr):
        raise Exception('Control attribute "'+control+'.'+attr+'" already exists!')

    # Create attribute
    cmds.addAttr(control,ln=attr,at='enum',en=':-:')
    cmds.setAttr(control+'.'+attr,cb=True)
    cmds.setAttr(control+'.'+attr,l=True)

    # Return result
    return (control+'.'+attr)
