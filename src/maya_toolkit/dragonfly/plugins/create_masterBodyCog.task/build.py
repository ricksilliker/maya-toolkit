"""

    Requires:
        color-maya - https://github.magicleap.com/tcoleman/color-maya.git
"""
import py_tasker.tasks
import dragonfly.modules
import dragonfly.node
import dragonfly.meta_types
reload(dragonfly.meta_types)

import color.core as color

import maya.cmds as cmds

LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '0.0.1'

CTL = "ctl"
OFF = "off"
BUF = "buf"
GRP = "grp"
JNT = "jnt"
TFM = "tfm"
INV = "inv"

MASTER = "cn_master_{}".format(CTL)
MASTER_OFFSET = "cn_masterOffset_{}".format(CTL)
SCENE_OFFSET = "cn_sceneOffset_{}".format(BUF)
BODY = "cn_body_{}".format(CTL)
COG = "cn_cog_{}".format(CTL)
ROOT = "cn_root_{}".format(JNT)

TRS = ['t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz', 's', 'sx', 'sy', 'sz']
TRS9 = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
TRSV = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
TR = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
SV = ['sx', 'sy', 'sz', 'v']


def setUp(params, spec):
    """Special method used to intialize a `TaskSpec` instance of this `TaskFactory`.

    Args:
        params: These are the parameters for this `RigSpec` instance, get/set just like dictionary calls
        spec: The `TaskSpec` object that this method runs from, this gives you access to the entire class instance

    Returns:
        None
    """
    LOG.info("Running setup!!!")
    body_ctl = ""

    if not params['masterControl'] and not cmds.objExists(MASTER):
        master_ctl = create_curve(MASTER_SHAPE_DATA)
        color.set_color(master_ctl, 'CENTER')
        master_node = dragonfly.node.dfNode.fromName(master_ctl)
        spec.params()['masterControl'] = master_node

        master_offset_ctl = create_curve(MASTER_OFFSET_SHAPE_DATA)
        color.set_color(master_offset_ctl, 'CENTER')
        cmds.parent(master_offset_ctl, master_ctl)

        attrs_lock(TRSV, node=master_ctl)
        attrs_lock(TRSV, node=master_offset_ctl)

    if not params['bodyControl'] and not cmds.objExists(BODY):
        body_ctl = create_curve(BODY_SHAPE_DATA)
        color.set_color(body_ctl, 'CYAN')
        body_node = dragonfly.node.dfNode.fromName(body_ctl)
        spec.params()['bodyControl'] = body_node

        LOG.warning("Move body control to proper position if necessary...")
        
    if not params['cogControl'] and not cmds.objExists(COG):
        cog_ctl = create_curve(COG_SHAPE_DATA)
        color.set_color(cog_ctl, 'CYAN')
        cog_node = dragonfly.node.dfNode.fromName(cog_ctl)
        spec.params()['cogControl'] = cog_node

        # If body_ctl exists parent cog underneath
        if cmds.objExists(body_ctl):
            cmds.parent(cog_ctl, body_ctl)

    if not params['rootJoint'] and not cmds.objExists(ROOT):
        cmds.select(clear=True)
        root_jnt = cmds.joint(name="cn_root_jnt")
        root_node = dragonfly.node.dfNode.fromName(root_jnt)
        spec.params()['rootJoint'] = root_node

    elif cmds.objExists(ROOT):
        root_jnt = ROOT
        root_node = dragonfly.node.dfNode.fromName(root_jnt)
        spec.params()['rootJoint'] = root_node

def run(params, rig):
    # make sure matrixNodes plugin is loaded
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    master = params['masterControl']
    body = params['bodyControl']
    cog = params['cogControl']
    root = params['rootJoint']
    traj = params['addTrajectoryControl']

    rig['master'] = params['masterControl']
    rig['body'] = params['bodyControl']
    rig['cog'] = params['cogControl']
    rig['root'] = params['rootJoint']
    rig['traj'] = params['addTrajectoryControl']

    createMasterBodyCog(rig, master, body, cog, root, traj)


def createMasterBodyCog(rig, master, body, cog, root, traj):
    """Creates top rig hierarchy """

    master_ctl = None
    master_offset_ctl = None
    body_ctl = None
    piv_inv = None
    root_jnt = None

    if master:
        # Create buffer and scene_offset nodes
        master_GRP = cmds.createNode("transform", name=MASTER.replace(CTL, GRP))
        scene_OFF = cmds.createNode("transform", name="sceneOffset_{}".format(GRP))

        # Master and master_offset
        master_ctl = master.name()
        master_ctl_parent = cmds.listRelatives(master_ctl, parent=True)
        if master_ctl_parent:
            cmds.parent(master_GRP, master_ctl_parent)

        master_offset_ctl = ""
        if cmds.objExists(MASTER_OFFSET):
            master_offset_ctl = MASTER_OFFSET

        attrs_show(TRS, node=master_ctl)
        attrs_show(TRS, node=master_offset_ctl)

        cmds.parent(scene_OFF, master_GRP)
        cmds.parent(master_ctl, scene_OFF)

        # Try to parent master_grp under rig node
        try:
            cmds.parent(master_GRP, rig['rigGroup'])
        except:
            pass

        # Setup global scale on master and connect to master_offset
        cmds.addAttr(master_ctl, ln="globalScale", min=0.0001, dv=1)
        cmds.setAttr("{}.globalScale".format(master_ctl), edit=True, l=False, k=True)

        for attr in ['sx', 'sy', 'sz']:
            cmds.connectAttr("{}.globalScale".format(master_ctl), "{}.{}".format(master_offset_ctl, attr))
            cmds.setAttr("{}.{}".format(master_offset_ctl, attr), lock=True)
            cmds.setAttr("{}.{}".format(master_ctl, attr), lock=True)

        # Set channels
        attrs_lock_hide(SV, node=master_ctl)
        attrs_lock_hide(SV, node=master_offset_ctl)

        # Meta types
        dragonfly.modules.add_metatype(master_ctl, dragonfly.meta_types.MTYPE_MASTER)
        dragonfly.modules.add_metatype(master_offset_ctl, dragonfly.meta_types.MTYPE_MASTER_OFFSET)
        dragonfly.modules.add_metatype(master_ctl, dragonfly.meta_types.MTYPE_CTL)
        dragonfly.modules.add_metatype(master_offset_ctl, dragonfly.meta_types.MTYPE_CTL)


    if body:
        # Create buffer
        body_BUF = cmds.createNode("transform", name=BODY.replace(CTL, BUF))

        # Body control
        body_ctl = body.name()
        match_nodes(body_ctl, body_BUF)
        cmds.parent(body_ctl, body_BUF)

        if cmds.objExists(MASTER_OFFSET):
            cmds.parent(body_BUF, MASTER_OFFSET)
        else:
            cmds.parent(body_BUF, MASTER)

        piv_inv = add_movable_pivot(BODY.replace("_{}".format(CTL), ""), body_ctl)

        # Set channels
        attrs_lock_hide(SV, node=body_ctl)

        # Meta type
        dragonfly.modules.add_metatype(body_ctl, dragonfly.meta_types.MTYPE_BODY)

    if cog:
        # Create buffer
        cog_BUF = cmds.createNode("transform", name=COG.replace(CTL, BUF))
        cog_ctl = cog.name()
        match_nodes(cog_ctl, cog_BUF)

        if body_ctl:
            cmds.parent(cog_BUF, BODY)
            cog_off = cmds.createNode("transform", name=COG.replace(CTL, OFF))
            match_nodes(cog_ctl, cog_off)
            cmds.parent(cog_off, cog_BUF)
            cmds.parent(cog_ctl, cog_off)
            cmds.parentConstraint(piv_inv, cog_BUF, mo=True)
        else:
            cmds.parent(cog_ctl, cog_BUF)

        # Set channels
        attrs_lock_hide(SV, node=cog_ctl)

        # Meta type
        dragonfly.modules.add_metatype(cog_ctl, dragonfly.meta_types.MTYPE_COG)


    if root:
        root_jnt = root.name()
        attrs_show(TRSV, node=root_jnt)

        if master_offset_ctl:
            cmds.parentConstraint(master_offset_ctl, root_jnt)
            cmds.scaleConstraint(master_offset_ctl, root_jnt)

        try:
            skel_grp = rig['skeletonGroup']
            if skel_grp:  cmds.parent(root_jnt, skel_grp)
        except:
            pass

        # Meta type
        dragonfly.modules.add_metatype(root_jnt, dragonfly.meta_types.MTYPE_ROOT)


    if traj:
        if master_ctl and root_jnt:
            traj = trajectoryControl(masterControl=master_ctl, rootJoints=[root_jnt])
            attrs_lock_hide(SV, node=traj)
            dragonfly.modules.add_metatype(traj, dragonfly.meta_types.MTYPE_TRAJECTORY)


def getNodeScale(node):
    """ Returns bbox scale of node as vector """
    bBox = cmds.exactWorldBoundingBox(node)
    gScale = min(bBox[3] - bBox[0], bBox[4] - bBox[1], bBox[5] - bBox[2])
    return gScale

def create_curve(curve_data):
    """Uses dictionary of curve data to create curve and properly rename curve shape node"""
    crv = cmds.curve(**curve_data)
    crvShp = cmds.listRelatives(crv, shapes=True)[0]
    cmds.rename(crvShp, "{}Shape".format(crv))
    return crv

def create_pivot_sphere(curve_data, transform):
    """Uses dictionary of curve data to create curve and properly rename curve shape node"""
    try:
        crv = cmds.curve(**curve_data)
        crvShp = cmds.listRelatives(crv, shapes=True)[0]
        cmds.parent(crvShp, transform, r=True, s=True)
        cmds.rename( crvShp, "{}Shape".format(transform) )
        cmds.delete(crv)
        return True
    except:
        LOG.error("Unable to add pivot curve to {}".format(transform))
        raise

def pivot_snap():
    """Calculates offset between control and pivot control"""
    sel = cmds.ls(selection=True)
    if sel:
        doSnap = 0

        pivot_inv = ""
        # Determine if control or pivot is selected and query message attrs
        if cmds.attributeQuery('PIVOT', exists=True, node=sel[0]):# CONTROL
            ctl_node = sel[0]
            pivot_ctl = attrs_get_message(ctl_node, 'PIVOT')[0]
            pivot_inv = attrs_get_message(ctl_node, 'PIVOT_INV')[0]
            doSnap = 1

        elif cmds.attributeQuery('PIVOT_CONTROL', exists=True, node=sel[0]):# PIVOT
            pivot_ctl = sel[0]
            ctl_node = attrs_get_message(pivot_ctl, 'PIVOT_CONTROL')[0]
            pivot_inv = attrs_get_message(pivot_ctl, 'PIVOT_INV')[0]
            doSnap = 1

        if doSnap:
            inv_position = cmds.xform(pivot_inv, q=True, ws=True, t=True)
            inv_rotation = cmds.xform(pivot_inv, q=True, ws=True, ro=True)

            cmds.setAttr("{}.t".format(pivot_ctl), 0,0,0)
            cmds.setAttr("{}.r".format(pivot_ctl), 0,0,0)

            cmds.xform(ctl_node, ws=True, t=inv_position)
            cmds.xform(ctl_node, ws=True, ro=inv_rotation)

            LOG.info("Successfully snapped {} to pivot control {}".format(ctl_node, pivot_ctl))

        else:
            LOG.debug("Unable to snap pivot, please select pivot of control to be snapped")
    else:
        LOG.error("Nothing selected to snap, select control or pivot and try again")


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


def add_movable_pivot(baseName, control):
    """Adds node hierarchy for animating pivot position of control

    add_movable_pivot("boxB", "boxB_fk_ctl")
    """
    if cmds.objExists(control):
        piv_grp = cmds.duplicate(control, po=True, name="{}Pivot_{}".format(baseName, BUF))[0]
        piv_ctl = cmds.duplicate(control, po=True, name="{}Pivot_{}".format(baseName, CTL))[0]
        piv_tfm = cmds.duplicate(control, po=True, name="{}Pivot_{}".format(baseName, TFM))[0]
        piv_inv = cmds.duplicate(control, po=True, name="{}Pivot_{}".format(baseName, INV))[0]

        create_pivot_sphere(PIVOT_SHAPE_DATA, piv_ctl)

        cmds.parent(piv_grp, piv_ctl, piv_tfm, piv_inv, control)
        cmds.parent(piv_ctl, piv_grp)
        cmds.parent(piv_inv, piv_tfm)

        # Connect piv_ctl to piv_tfm
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            cmds.connectAttr("{}.{}".format(piv_ctl, attr), "{}.{}".format(piv_tfm, attr))

        # Invert transform from piv_ctl to piv_inv
        mdn = cmds.createNode('multiplyDivide', name="{}_mdn".format(piv_ctl))
        cmds.connectAttr("{}.translate".format(piv_ctl), "{}.input1".format(mdn))
        cmds.setAttr("{}.input2".format(mdn), -1, -1, -1)
        cmds.connectAttr("{}.output".format(mdn), "{}.translate".format(piv_inv))

        # Add message attrs
        attrs_add_message(control, [piv_ctl], "PIVOT")
        attrs_add_message(control, [piv_inv], "PIVOT_INV")
        attrs_add_message(piv_ctl, [control], "PIVOT_CONTROL")
        attrs_add_message(piv_ctl, [piv_inv], "PIVOT_INV")

        return piv_inv

    else:
        LOG.error("{} does not exist!".format(control))
        
        
def trajectoryControl(masterControl="cn_master_ctl", rootJoints=[], controlScale=1.0):
    """Adds Trajectory control to rig and constrains listed root joints to it

    Args:
        masterControl:  Name of existing masterControl object
        rootJoints:  Name of root joint(s) to constrain.
        controlScale:  Scale value of created controls.

    Returns:
        Returns name of created controls.
    """
    if not rootJoints:
        rootJoints = ["cn_root_jnt"]
    traj_ctl = create_curve(TRAJECTORY_SHAPE_DATA)
    color.set_color(traj_ctl, 3)
    zero = cmds.group(name=traj_ctl.replace(CTL, BUF), empty=True)

    if cmds.ls(type="mesh"):
        gScale = getNodeScale(cmds.ls(type="mesh")) + controlScale

    cmds.makeIdentity(traj_ctl, apply=True, translate=True, rotate=True, scale=True)
    cmds.parent(traj_ctl, zero)

    # Parent into rig
    if cmds.objExists(masterControl):
        cmds.parent(zero, masterControl)

    # Constrain rootJoints to Trajectory ctrl
    for rootJoint in rootJoints:
        # Check for existing constraint on root jnt and delete
        pc = cmds.listConnections("{}.tx".format(rootJoint), s=True, d=False)
        if pc:
            if "parentConstraint" in cmds.objectType(pc[0]):
                cmds.delete(pc[0])
        cmds.parentConstraint(traj_ctl, rootJoint, mo=True)

    cmds.select(clear=True)
    LOG.debug('[trajectoryControl] Created %s' % traj_ctl)
    return traj_ctl


def attrs_keyable(attrs, node=None):
    """Make an attr or a list of attrs keyable"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), keyable=True)


def attrs_show(attrs, node=None):
    """Show a hidden attribute in the channel box and make it keyable and unlocked"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), keyable=True)
        cmds.setAttr('{}.{}'.format(node, a), lock=False)


def attrs_hide(attrs, node=None):
    """Hide attribute in the channel box and make it not keyable and locked"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), keyable=False, channelBox=False)


def attrs_lock(attrs, node=None):
    """Lock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), lock=True)


def attrs_lock_hide(attrs, node=None):
    """Lock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), lock=True)
        cmds.setAttr('{}.{}'.format(node, a), keyable=False)


def attrs_unlock(attrs, node=None):
    """Unlock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node, a), lock=False)


def attrs_add_message(src, tgts, attrName):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        attrs_add_message("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attrName, exists=True, node=src):
            cmds.addAttr(src, sn=attrName, at='message')

        for tgt in tgts:
            cmds.connectAttr("%s.message" % (tgt), "%s.%s" % (src, attrName))
        return True

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise


def attrs_get_message(src, attrName):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        attrs_get_message("box_fk_ctrl", attrName="pivot_node")
    """
    try:
        if cmds.attributeQuery(attrName, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attrName))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attrName, src))
        raise


def attrs_attributeSeparator(control, attr):
    """Create a separator attribute on the specified control object

    Args:
        control: The control to add the separator attribute to
        attr: The separator attribute name

    Returns:

    Example:
        attributeSeparator('Lf_arm_ctrl', '___')
    """
    # Check control
    if not cmds.objExists(control):
        raise Exception('Control object "' + control + '" does not exist!')

    # Check attribute
    if cmds.objExists(control + '.' + attr):
        raise Exception('Control attribute "' + control + '.' + attr + '" already exists!')

    # Create attribute
    cmds.addAttr(control, ln=attr, at='enum', en=':-:')
    cmds.setAttr(control + '.' + attr, cb=True)
    cmds.setAttr(control + '.' + attr, l=True)

    # Return result
    return "{}.{}".format(control, attr)


TRAJECTORY_SHAPE_DATA = {
    "p" : [
            [
                0.1065953397981777,
                0.0,
                -0.26648834949544425
            ],
            [
                0.10659533979817783,
                0.0,
                -0.05329766989908894
            ],
            [
                0.21319067959635576,
                0.0,
                -0.053297669899089
            ],
            [
                1.3448250063827173e-16,
                0.0,
                0.26648834949544425
            ],
            [
                -0.21319067959635576,
                0.0,
                -0.053297669899088664
            ],
            [
                -0.10659533979817791,
                0.0,
                -0.053297669899088754
            ],
            [
                -0.10659533979817798,
                0.0,
                -0.2664883494954441
            ],
            [
                0.1065953397981777,
                0.0,
                -0.26648834949544425
            ]
        ],
    "k": [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0
        ],
    "d": 1,
    "per": False,
    "name" : "cn_trajectory_ctl"
}


PIVOT_SHAPE_DATA = {
    "p": [
            [
                0.0,
                0.07251737211953482,
                0.0
            ],
            [
                -0.02775116551481995,
                0.0669973497537958,
                0.0
            ],
            [
                -0.05127754144732793,
                0.05127754144732793,
                0.0
            ],
            [
                -0.0669973497537958,
                0.02775116551481995,
                0.0
            ],
            [
                -0.07251737211953482,
                0.0,
                0.0
            ],
            [
                -0.0669973497537958,
                -0.02775116551481995,
                0.0
            ],
            [
                -0.05127754144732793,
                -0.05127754144732793,
                0.0
            ],
            [
                -0.02775116551481995,
                -0.0669973497537958,
                0.0
            ],
            [
                0.0,
                -0.07251737211953482,
                0.0
            ],
            [
                0.02775116551481995,
                -0.0669973497537958,
                0.0
            ],
            [
                0.05127754144732793,
                -0.05127754144732793,
                0.0
            ],
            [
                0.0669973497537958,
                -0.02775116551481995,
                0.0
            ],
            [
                0.07251737211953482,
                0.0,
                0.0
            ],
            [
                0.0669973497537958,
                0.02775116551481995,
                0.0
            ],
            [
                0.05127754144732793,
                0.05127754144732793,
                0.0
            ],
            [
                0.02775116551481995,
                0.0669973497537958,
                0.0
            ],
            [
                0.0,
                0.07251737211953482,
                0.0
            ],
            [
                0.0,
                0.0669973497537958,
                0.02775116551481995
            ],
            [
                0.0,
                0.05127754144732793,
                0.05127754144732793
            ],
            [
                0.0,
                0.02775116551481995,
                0.0669973497537958
            ],
            [
                0.0,
                0.0,
                0.07251737211953482
            ],
            [
                0.0,
                -0.02775116551481995,
                0.0669973497537958
            ],
            [
                0.0,
                -0.05127754144732793,
                0.05127754144732793
            ],
            [
                0.0,
                -0.0669973497537958,
                0.02775116551481995
            ],
            [
                0.0,
                -0.07251737211953482,
                0.0
            ],
            [
                0.0,
                -0.0669973497537958,
                -0.02775116551481995
            ],
            [
                0.0,
                -0.05127754144732793,
                -0.05127754144732793
            ],
            [
                0.0,
                -0.02775116551481995,
                -0.0669973497537958
            ],
            [
                0.0,
                0.0,
                -0.07251737211953482
            ],
            [
                0.0,
                0.02775116551481995,
                -0.0669973497537958
            ],
            [
                0.0,
                0.05127754144732793,
                -0.05127754144732793
            ],
            [
                0.0,
                0.0669973497537958,
                -0.02775116551481995
            ],
            [
                0.0,
                0.07251737211953482,
                0.0
            ],
            [
                -0.02775116551481995,
                0.0669973497537958,
                0.0
            ],
            [
                -0.05127754144732793,
                0.05127754144732793,
                0.0
            ],
            [
                -0.0669973497537958,
                0.02775116551481995,
                0.0
            ],
            [
                -0.07251737211953482,
                0.0,
                0.0
            ],
            [
                -0.0669973497537958,
                0.0,
                0.02775116551481995
            ],
            [
                -0.05127754144732793,
                0.0,
                0.05127754144732793
            ],
            [
                -0.02775116551481995,
                0.0,
                0.0669973497537958
            ],
            [
                0.0,
                0.0,
                0.07251737211953482
            ],
            [
                0.02775116551481995,
                0.0,
                0.0669973497537958
            ],
            [
                0.05127754144732793,
                0.0,
                0.05127754144732793
            ],
            [
                0.0669973497537958,
                0.0,
                0.02775116551481995
            ],
            [
                0.07251737211953482,
                0.0,
                0.0
            ],
            [
                0.0669973497537958,
                0.0,
                -0.02775116551481995
            ],
            [
                0.05127754144732793,
                0.0,
                -0.05127754144732793
            ],
            [
                0.02775116551481995,
                0.0,
                -0.0669973497537958
            ],
            [
                0.0,
                0.0,
                -0.07251737211953482
            ],
            [
                -0.02775116551481995,
                0.0,
                -0.0669973497537958
            ],
            [
                -0.05127754144732793,
                0.0,
                -0.05127754144732793
            ],
            [
                -0.0669973497537958,
                0.0,
                -0.02775116551481995
            ],
            [
                -0.07251737211953482,
                0.0,
                0.0
            ]
        ],
    "k": [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            9.0,
            10.0,
            11.0,
            12.0,
            13.0,
            14.0,
            15.0,
            16.0,
            17.0,
            18.0,
            19.0,
            20.0,
            21.0,
            22.0,
            23.0,
            24.0,
            25.0,
            26.0,
            27.0,
            28.0,
            29.0,
            30.0,
            31.0,
            32.0,
            33.0,
            34.0,
            35.0,
            36.0,
            37.0,
            38.0,
            39.0,
            40.0,
            41.0,
            42.0,
            43.0,
            44.0,
            45.0,
            46.0,
            47.0,
            48.0,
            49.0,
            50.0,
            51.0,
            52.0
    ],
    "d": 1,
    "per": False
}

MASTER_SHAPE_DATA = {
    "p": [
            [
                -1.0839478531420554,
                8.801334861957671e-17,
                -0.33308770921896935
            ],
            [
                -1.166748847719989,
                8.801334861957671e-17,
                -0.33308770921896935
            ],
            [
                -1.2495498422979294,
                1.3202002292936505e-16,
                -0.33308770921896935
            ],
            [
                -1.3323508368758699,
                1.3202002292936505e-16,
                -0.33308770921896935
            ],
            [
                -1.3323508368758699,
                1.3202002292936505e-16,
                -0.44411694562529513
            ],
            [
                -1.3323508368758699,
                2.200333715489418e-17,
                -0.5551461820316129
            ],
            [
                -1.3323508368758699,
                8.801334861957671e-17,
                -0.6661754184379315
            ],
            [
                -1.5544093096885143,
                2.2003337154894173e-16,
                -0.44411694562529513
            ],
            [
                -1.7764677825011592,
                2.2003337154894173e-16,
                -0.22205847281264388
            ],
            [
                -1.9985262553138028,
                3.7405673163320107e-16,
                1.100166857744709e-17
            ],
            [
                -1.7764677825011592,
                3.9606006878809514e-16,
                0.22205847281264388
            ],
            [
                -1.5544093096885143,
                3.9606006878809514e-16,
                0.44411694562528775
            ],
            [
                -1.3323508368758699,
                4.84073417407672e-16,
                0.6661754184379315
            ],
            [
                -1.3323508368758699,
                3.7405673163320107e-16,
                0.5551461820316131
            ],
            [
                -1.3323508368758699,
                3.9606006878809514e-16,
                0.44411694562528775
            ],
            [
                -1.3323508368758699,
                3.0804672016851843e-16,
                0.3330877092189623
            ],
            [
                -1.2461886159191116,
                3.0804672016851843e-16,
                0.3330877092189623
            ],
            [
                -1.1600263949623584,
                2.640400458587301e-16,
                0.3330877092189623
            ],
            [
                -1.0831632990238762,
                4.400667430978836e-17,
                0.32168629217150224
            ],
            [
                -1.029319039925524,
                2.2003337154894173e-16,
                0.5010551696844937
            ],
            [
                -0.8366929092356985,
                3.0804672016851843e-16,
                0.8303526351722582
            ],
            [
                -0.5090357863268071,
                3.9606006878809514e-16,
                1.0246191084409495
            ],
            [
                -0.33308770921896225,
                3.0804672016851843e-16,
                1.0764680838415435
            ],
            [
                -0.33308770921896225,
                2.2003337154894173e-16,
                1.1617623348529915
            ],
            [
                -0.33308770921896225,
                3.9606006878809514e-16,
                1.2470565858644242
            ],
            [
                -0.33308770921896225,
                2.2003337154894173e-16,
                1.3323508368758696
            ],
            [
                -0.44411694562529513,
                2.2003337154894173e-16,
                1.3323508368758696
            ],
            [
                -0.5551461820316131,
                3.9606006878809514e-16,
                1.3323508368758699
            ],
            [
                -0.6661754184379315,
                3.9606006878809514e-16,
                1.3323508368758699
            ],
            [
                -0.44411694562529513,
                2.2003337154894173e-16,
                1.5544093096885143
            ],
            [
                -0.22205847281264388,
                7.481134632664021e-16,
                1.7764677825011592
            ],
            [
                3.3606127893509034e-18,
                3.7405673163320107e-16,
                1.9985262553138021
            ],
            [
                0.22205847281264388,
                7.481134632664021e-16,
                1.7764677825011592
            ],
            [
                0.44411694562528775,
                2.200333715489418e-17,
                1.5544093096885143
            ],
            [
                0.6661754184379315,
                2.2003337154894173e-16,
                1.3323508368758699
            ],
            [
                0.5551461820316131,
                2.2003337154894173e-16,
                1.3323508368758699
            ],
            [
                0.44411694562528775,
                2.2003337154894173e-16,
                1.3323508368758699
            ],
            [
                0.33308770921896225,
                2.2003337154894173e-16,
                1.3323508368758699
            ],
            [
                0.33308770921896225,
                1.7602669723915343e-16,
                1.2468920568573738
            ],
            [
                0.33308770921896225,
                8.801334861957671e-17,
                1.1614332768388766
            ],
            [
                0.3332063140118288,
                4.84073417407672e-16,
                1.0796397060975307
            ],
            [
                0.5081856540057031,
                3.0804672016851843e-16,
                1.0251227863761918
            ],
            [
                0.8307571036906276,
                3.0804672016851843e-16,
                0.8341460697741663
            ],
            [
                1.0225965365868903,
                2.2003337154894173e-16,
                0.5124373363834785
            ],
            [
                1.0806483222680021,
                -1.7602669723915343e-16,
                0.3330877092189625
            ],
            [
                1.1645491604706226,
                -1.9803003439404757e-16,
                0.3330877092189625
            ],
            [
                1.2484499986732505,
                -2.640400458587301e-16,
                0.3330877092189625
            ],
            [
                1.3323508368758699,
                -2.640400458587301e-16,
                0.3330877092189625
            ],
            [
                1.3323508368758699,
                -1.9803003439404757e-16,
                0.44411694562528775
            ],
            [
                1.3323508368758699,
                -8.801334861957671e-17,
                0.5551461820316129
            ],
            [
                1.3323508368758699,
                -1.7602669723915343e-16,
                0.6661754184379315
            ],
            [
                1.5544093096885143,
                -2.640400458587301e-16,
                0.44411694562528775
            ],
            [
                1.7764677825011592,
                -3.7405673163320107e-16,
                0.22205847281264388
            ],
            [
                1.9985262553138028,
                -4.1806340594298935e-16,
                1.100166857744709e-17
            ],
            [
                1.7764677825011592,
                -4.84073417407672e-16,
                -0.22205847281264388
            ],
            [
                1.5544093096885143,
                -4.1806340594298935e-16,
                -0.44411694562528775
            ],
            [
                1.3323508368758699,
                -5.280800917174602e-16,
                -0.6661754184379315
            ],
            [
                1.3323508368758699,
                -4.1806340594298935e-16,
                -0.5551461820316131
            ],
            [
                1.3323508368758699,
                -4.1806340594298935e-16,
                -0.44411694562528775
            ],
            [
                1.3323508368758699,
                -4.1806340594298935e-16,
                -0.3330877092189623
            ],
            [
                1.2450377928874494,
                -4.1806340594298935e-16,
                -0.3330877092189623
            ],
            [
                1.1577247488990277,
                -3.9606006878809514e-16,
                -0.3330877092189623
            ],
            [
                1.0782351966300798,
                -1.9803003439404757e-16,
                -0.33768236030600673
            ],
            [
                1.023480192800713,
                -2.640400458587301e-16,
                -0.5109536132764023
            ],
            [
                0.8313141539213817,
                -4.1806340594298935e-16,
                -0.8340193432206575
            ],
            [
                0.5075575165048203,
                -6.160934403370369e-16,
                -1.0254944746276868
            ],
            [
                0.33308770921896225,
                -3.7405673163320107e-16,
                -1.075813001909269
            ],
            [
                0.33308770921896225,
                -3.0804672016851843e-16,
                -1.161325613564803
            ],
            [
                0.33308770921896225,
                -7.481134632664021e-16,
                -1.2468382252203376
            ],
            [
                0.33308770921896225,
                -3.0804672016851843e-16,
                -1.3323508368758696
            ],
            [
                0.44411694562529513,
                -3.0804672016851843e-16,
                -1.3323508368758696
            ],
            [
                0.5551461820316131,
                -4.84073417407672e-16,
                -1.3323508368758699
            ],
            [
                0.6661754184379315,
                -4.84073417407672e-16,
                -1.3323508368758699
            ],
            [
                0.44411694562529513,
                -3.0804672016851843e-16,
                -1.5544093096885139
            ],
            [
                0.22205847281264388,
                -7.481134632664021e-16,
                -1.7764677825011592
            ],
            [
                3.3606127893509034e-18,
                -4.1806340594298935e-16,
                -1.9985262553138021
            ],
            [
                -0.22205847281264388,
                -7.481134632664021e-16,
                -1.7764677825011592
            ],
            [
                -0.44411694562528775,
                -8.801334861957671e-17,
                -1.5544093096885143
            ],
            [
                -0.6661754184379315,
                -3.7405673163320107e-16,
                -1.3323508368758699
            ],
            [
                -0.5551461820316131,
                -3.7405673163320107e-16,
                -1.3323508368758699
            ],
            [
                -0.44411694562528775,
                -3.7405673163320107e-16,
                -1.3323508368758699
            ],
            [
                -0.33308770921896225,
                -3.7405673163320107e-16,
                -1.3323508368758699
            ],
            [
                -0.33308770921896225,
                -3.0804672016851843e-16,
                -1.2476635432844865
            ],
            [
                -0.33308770921896225,
                -2.640400458587301e-16,
                -1.162976249693103
            ],
            [
                -0.33308770921896225,
                -1.9803003439404757e-16,
                -1.0782889561017113
            ],
            [
                -0.5080435380215272,
                -4.1806340594298935e-16,
                -1.025206915292304
            ],
            [
                -0.8334514515222526,
                -3.7405673163320107e-16,
                -0.8325971306956721
            ],
            [
                -1.0258418621023937,
                -2.640400458587301e-16,
                -0.5069698431784583
            ],
            [
                -1.0802501247506302,
                -1.9803003439404757e-16,
                -0.33124095054657815
            ]
        ],
    "k": [
            15.74575077,
            15.74575077,
            15.74575077,
            15.994336930000005,
            15.994336930000005,
            15.994336930000005,
            16.994336930000003,
            16.994336930000003,
            16.994336930000003,
            17.994336930000003,
            17.994336930000003,
            17.994336930000003,
            18.994336930000003,
            18.994336930000003,
            18.994336930000003,
            19.994336930000003,
            19.994336930000003,
            19.994336930000003,
            20.253014205,
            20.253014205,
            20.253014205,
            20.88520212,
            21.502214874,
            21.502214874,
            21.502214874,
            21.758286319,
            21.758286319,
            21.758286319,
            22.758286319,
            22.758286319,
            22.758286319,
            23.758286319,
            23.758286319,
            23.758286319,
            24.758286319,
            24.758286319,
            24.758286319,
            25.758286319,
            25.758286319,
            25.758286319,
            26.014851715,
            26.014851715,
            26.014851715,
            26.633484611,
            27.244006169,
            27.244006169,
            27.244006169,
            27.495894293,
            27.495894293,
            27.495894293,
            28.495894293,
            28.495894293,
            28.495894293,
            29.495894293,
            29.495894293,
            29.495894293,
            30.495894293,
            30.495894293,
            30.495894293,
            31.495894293,
            31.495894293,
            31.495894293,
            31.758026583,
            31.758026583,
            31.758026583,
            32.371381249,
            32.991210664,
            32.991210664,
            32.991210664,
            33.247937674,
            33.247937674,
            33.247937674,
            34.247937674,
            34.247937674,
            34.247937674,
            35.247937674,
            35.247937674,
            35.247937674,
            36.247937674,
            36.247937674,
            36.247937674,
            37.247937674,
            37.247937674,
            37.247937674,
            37.502186904,
            37.502186904,
            37.502186904,
            38.1210905535,
            38.742038981499995,
            38.742038981499995,
            38.742038981499995
    ],
    "d": 3,
    "per": False,
    "name": MASTER
}

MASTER_OFFSET_SHAPE_DATA = {
    "p": [
            [
                0.7283872868457305,
                0.0,
                -0.7284302462952323
            ],
            [
                1.0301336599282118,
                0.0,
                0.0
            ],
            [
                0.7283872868457305,
                0.0,
                0.7284302462952323
            ],
            [
                -4.29594495016838e-05,
                0.0,
                1.0301766193777124
            ],
            [
                -0.726985854552706,
                0.0,
                0.7284302462952323
            ],
            [
                -1.030033659928211,
                0.0,
                0.0
            ],
            [
                -0.726985854552706,
                0.0,
                -0.7284302462952323
            ],
            [
                -4.29594495016838e-05,
                0.0,
                -1.0301766193777124
            ],
            [
                0.7283872868457305,
                0.0,
                -0.7284302462952323
            ],
            [
                1.0301336599282118,
                0.0,
                0.0
            ],
            [
                0.7283872868457305,
                0.0,
                0.7284302462952323
            ]
        ],
    "k": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    "d": 1,
    "per": False,
    "name": MASTER_OFFSET
}

BODY_SHAPE_DATA = {
    "p": [
            [
                1.0182337649086286,
                -1.5987211554602254e-16,
                -2.398081733190338e-16
            ],
            [
                7.993605777301127e-17,
                1.5987211554602254e-16,
                1.0182337649086286
            ],
            [
                -1.0182337649086286,
                1.5987211554602254e-16,
                2.398081733190338e-16
            ],
            [
                -7.993605777301127e-17,
                -1.5987211554602254e-16,
                -1.0182337649086286
            ],
            [
                1.0182337649086286,
                -1.5987211554602254e-16,
                -2.398081733190338e-16
            ]
        ],
    "k": [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0
        ],
    "d": 1,
    "per": False,
    "name": BODY
}

COG_SHAPE_DATA = {
    "p": [
            [
                -0.16860613428303348,
                0.0,
                -0.16331520724351714
            ],
            [
                -0.16860613428303348,
                0.0,
                -0.5039294062997062
            ],
            [
                -0.16860613428303348,
                0.0,
                -0.5039294062997062
            ],
            [
                -0.33398100236815464,
                0.0,
                -0.500971503552232
            ],
            [
                0.0,
                0.0,
                -0.8349525059203887
            ],
            [
                0.33398100236815464,
                0.0,
                -0.500971503552232
            ],
            [
                0.16699050118407732,
                0.0,
                -0.500971503552232
            ],
            [
                0.16699050118407732,
                0.0,
                -0.16699050118407732
            ],
            [
                0.500971503552232,
                0.0,
                -0.16699050118407732
            ],
            [
                0.500971503552232,
                0.0,
                -0.33398100236815464
            ],
            [
                0.8349525059203887,
                0.0,
                0.0
            ],
            [
                0.500971503552232,
                0.0,
                0.33398100236815464
            ],
            [
                0.500971503552232,
                0.0,
                0.16699050118407732
            ],
            [
                0.16699050118407732,
                0.0,
                0.16699050118407732
            ],
            [
                0.16699050118407732,
                0.0,
                0.500971503552232
            ],
            [
                0.33398100236815464,
                0.0,
                0.500971503552232
            ],
            [
                0.0,
                0.0,
                0.8349525059203887
            ],
            [
                -0.33398100236815464,
                0.0,
                0.500971503552232
            ],
            [
                -0.16699050118407732,
                0.0,
                0.500971503552232
            ],
            [
                -0.16699050118407732,
                0.0,
                0.16699050118407732
            ],
            [
                -0.500971503552232,
                0.0,
                0.16699050118407732
            ],
            [
                -0.500971503552232,
                0.0,
                0.33398100236815464
            ],
            [
                -0.8349525059203887,
                0.0,
                0.0
            ],
            [
                -0.500971503552232,
                0.0,
                -0.33398100236815464
            ],
            [
                -0.500971503552232,
                0.0,
                -0.16699050118407732
            ],
            [
                -0.16699050118407732,
                0.0,
                -0.16699050118407732
            ]
        ],
    "k": [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            9.0,
            10.0,
            11.0,
            12.0,
            13.0,
            14.0,
            15.0,
            16.0,
            17.0,
            18.0,
            19.0,
            20.0,
            21.0,
            22.0,
            23.0,
            24.0,
            25.0
        ],
    "d": 1,
    "per": False,
    "name": COG
}
