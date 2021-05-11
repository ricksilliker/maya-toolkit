import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules
import dragonfly.node

CTL = "ctl"
JNT = "jnt"

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
    """Special method used to intialize a `TaskSpec` instance of this `TaskFactory`.

    Args:
        params: These are the parameters for this `RigSpec` instance, get/set just like dictionary calls
        spec: The `TaskSpec` object that this method runs from, this gives you access to the entire class instance

    Returns:
        None
    """
    if not params['skeleton']:
        joints = []

        for x in range(params['numberOfSegments']):
            jnt = cmds.createNode('joint')
            jnt = cmds.rename(jnt, '{baseName}{index}_{JNT}'.format(baseName=spec.name, index=x, JNT=JNT)).split('|')[-1]
            if x > 0:
                cmds.parent(jnt, joints[x - 1])
                cmds.setAttr('{node}.translateY'.format(node=jnt), 1.0)
            joints.append(jnt)

        spec.params()['skeleton'] = dragonfly.node.dfNode.fromList(joints)

    if not params['controls']:
        controls = []

        for x in range(params['numberOfSegments']):
            ctl = cmds.curve(**CONTROL_SHAPE_DATA)
            cmds.controller(ctl)
            ctl = cmds.rename(ctl, '{baseName}{index}_{CTL}'.format(baseName=spec.name, index=x, CTL=CTL))
            match_nodes(params['skeleton'][x].name(), ctl)
            if x > 0:
                cmds.parent(ctl, controls[x-1])
            controls.append(ctl)

        spec.params()['controls'] = dragonfly.node.dfNode.fromList(controls)


def run(params, rig):
    # make sure matrixNodes plugin is loaded
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    if params['useConstraints'] is False:
        LOG.exception('`useConstraints` is currently not implemented, will continue building using default constraints.')

    controls = [x.name() for x in params['controls']]
    skeleton = [x.name() for x in params['skeleton']]
    contraint_nodes = createFkChain(controls, skeleton)

    # cleanup not used channels for controls
    if params['disableScaling']:
        for ctl in controls:
            cmds.setAttr('{node}.sx'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sy'.format(node=ctl), l=True, cb=False)
            cmds.setAttr('{node}.sz'.format(node=ctl), l=True, cb=False)


def createFkChain(controls, joints):
    """Creates an FK rig setup.

    Args:
        controls (list): Control objects
        joints (list): FK joints

    Returns:
        list: Constraint nodes generated
    """
    constraints = []
    if joints == 1:
        pc = cmds.parentConstraint(controls, joints)[0]
        cmds.setAttr('{node}.interpType'.format(node=pc), 2)
        cmds.setAttr('{node}.visibility'.format(node=pc), False)
        sc = cmds.scaleConstraint(controls, joints)[0]
        cmds.setAttr('{node}.visibility'.format(node=sc), False)
        constraints.extend([pc, sc])
    else:
        for src, trg in zip(controls, joints):
            # constrain fk joints to controls, hide the constraint nodes
            pc = cmds.parentConstraint(src, trg)[0]
            cmds.setAttr('{node}.interpType'.format(node=pc), 2)
            cmds.setAttr('{node}.visibility'.format(node=pc), False)
            sc = cmds.scaleConstraint(src, trg)[0]
            cmds.setAttr('{node}.visibility'.format(node=sc), False)
            constraints.extend([pc, sc])

    return constraints


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
