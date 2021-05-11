"""
    # FKIK fingers
    rig.fingerFKIKSetup(fingerNames=["Index", "Middle", "Ring", "Pinky", "Thumb"], sides=["L", "R"])

    # Rig control modifications
    modify.masterControl(controlScale=1.0)
    modify.bodyControl(controlScale=1.0)
    modify.cogControl(controlScale=1.0)
    modify.hipSwinger(controlScale=1.0)
    modify.fkikControls(controlScale=1.0)
    modify.curveControlColors()

"""

import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)
MAYA_VER = int(mel.eval('getApplicationVersionAsFloat'))
CONTROLS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'controls')

# JOINTS
ROOT_JNT = "cn_root_jnt"
AS_ROOT_JNT = "Root_M"
SPINE_BASE_JNT = "cog"

# ADVANCED SKELETON CONTROL NAMES
MASTER_CTRL = "master_M"
BODY_CTRL = "RootExtraX_M"
COG_CTRL = "RootX_M"
HIP_SWINGER_CTRL = "HipSwinger_M"

# CONTROLS SHAPES
MASTER_CTRL_SHP = "four_arrow_circle"#"leaper"
BODY_CTRL_SHP = "square"
COG_CTRL_SHP = "four_arrow_circle"
HIP_SWINGER_CTRL_SHP = "four_arrow_curved"
FKIK_CTRL_SHP = "gear"

# ADVANCED SKELETON SIDES
LEFT_AS = '_L'
RIGHT_AS = '_R'
CENTER_AS = '_M'
MIDDLE_AS = '_M'
BACK_AS = '_BK'
FRONT_AS = '_FT'
TOP_AS = '_TP'
BOT_AS = '_BT'
IN_AS = '_IN'
OUT_AS = '_OT'
UP_AS = '_UP'
DOWN_AS = '_DN'
SIDES_AS = {'left': LEFT_AS, 'right': RIGHT_AS, 'center': CENTER_AS, 'middle': MIDDLE_AS,
         'back': BACK_AS, 'front': FRONT_AS, 'top': TOP_AS, 'bottom': BOT_AS,
         'in': IN_AS, 'out': OUT_AS, 'up': UP_AS, 'down': DOWN_AS}

# ADVANCED SKELETON COLORS
NONE_AS = 0
RED_AS = 13
GREEN_AS = 14
BLUE_AS = 6
WHITE_AS = 16
YELLOW_AS = 17
CYAN_AS = 18
PINK_AS = 20
LTYELLOW_AS = 22

COLORS_AS = {'none': NONE_AS, 'red': RED_AS, 'green': GREEN_AS, 'blue': BLUE_AS, 'white': WHITE_AS,
          'yellow': YELLOW_AS, 'cyan': CYAN_AS, 'pink': PINK_AS, 'ltyellow': LTYELLOW_AS}
SIDE_COLOR_AS = {None: NONE_AS, LEFT_AS: BLUE_AS, RIGHT_AS: RED_AS, CENTER_AS: YELLOW_AS, MIDDLE_AS: YELLOW_AS, FRONT_AS: YELLOW_AS, BACK_AS: YELLOW_AS}
SIDE_COLOR2_AS = {None: NONE_AS, LEFT_AS: CYAN_AS, RIGHT_AS: PINK_AS, CENTER_AS: LTYELLOW_AS, MIDDLE_AS: LTYELLOW_AS, FRONT_AS: YELLOW_AS, BACK_AS: YELLOW_AS}


ROTATE_ORDER = {'xyz': 0, 'yzx': 1, 'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}


def run(params, rig):

    controlShapesColors = params['controlShapesColors']
    if controlShapesColors:
        #masterControl()
        hipSwinger()
        bodyControl()
        cogControl()
        fkikControls()
        curveControlColors()

    fkIkBlendRange = params['fkIkBlendRange']
    if fkIkBlendRange:
        do_fkikBlendValueRange()

    rotationOrdersXZY = params['rotationOrdersXZY']
    if rotationOrdersXZY:
        do_rotationOrdersXZY()

    addPropSpaceArmIK = params['addPropSpaceArmIK']
    if addPropSpaceArmIK:
        do_addPropSpaceArmIK()

    addFkGimbalControls = params['addFkGimbalControls']
    if addFkGimbalControls:
        do_addFkGimbalControls()

    fixFingerSpread = params['fixFingerSpread']
    if fixFingerSpread:
        do_fixFingerSpread()

    disableVolumeAttr = params['disableVolume']
    if disableVolumeAttr:
        disableVolume()

    parentUnderMasterBodyCog = params['parentUnderMasterBodyCog']
    if parentUnderMasterBodyCog:
        do_parentUnderMasterBodyCog(rig)

    disableRootFK = params['disableRootFK']
    if disableRootFK:
        do_disableRootFK()

    hideFollowAttrs = params['hideFollowAttrs']
    if hideFollowAttrs:
        do_hide_follow_attrs()

    hideGlobalAttrs = params['hideGlobalAttrs']
    if hideGlobalAttrs:
        do_hide_global_attrs()


def do_hide_global_attrs():
    global_attrs = cmds.ls('*.Global', long=True)
    if global_attrs:
        for global_attr in global_attrs:
            try:
                cmds.setAttr(global_attr, 0)
                cmds.setAttr(global_attr, k=False, l=True)
            except:
                LOG.warning('Unable to hide global attr on: {}'.format(global_attr))
                pass


def do_hide_follow_attrs():
    follow_attrs = cmds.ls('*.follow', long=True)
    if follow_attrs:
        for follow_attr in follow_attrs:
            try:
                cmds.setAttr(follow_attr, 0)
                cmds.setAttr(follow_attr, k=False, l=False)
            except:
                LOG.warning('Unable to hide follow attr on: {}'.format(follow_attr))
                pass


def do_disableRootFK():
    if cmds.objExists('FKRoot_M'):
        cmds.hide('FKRoot_MShape')


def do_parentUnderMasterBodyCog(rig):

    master_ctl = dragonfly.modules.name_from_uuid(str(rig['master']))
    root_jnt = dragonfly.modules.name_from_uuid(str(rig['root']))

    if cmds.objExists(root_jnt):
        if cmds.objExists('Main'):
            do_addRootJoint(root_joint=root_jnt, masterOffset='Main')

    if cmds.objExists(master_ctl):
        do_modifyAdvancedSkeletonTopHierarchy(rig)


def do_modifyAdvancedSkeletonTopHierarchy(rig):
    """Merges MasterBodyCog and AdvSkeleton rig hierarchies"""

    master_ctl = dragonfly.modules.name_from_uuid(str(rig['master']))
    master_offset_ctl = dragonfly.modules.get_metatype(dragonfly.meta_types.MTYPE_MASTER_OFFSET)[0]
    body_ctl = dragonfly.modules.name_from_uuid(str(rig['body']))
    cog_ctl = rig['cog']
    root_jnt = dragonfly.modules.get_metatype(dragonfly.meta_types.MTYPE_ROOT)[0]

    # Modify Main to master
    if cmds.objExists(master_ctl):
        cmds.parent('Main', master_ctl)

    # Body ctl mod
    if cmds.objExists(body_ctl):
        cmds.parent('cn_body_buf', 'Main')
        cmds.parentConstraint(body_ctl, 'RootExtraX_M', mo=True)
        #cmds.delete('RootExtraX_MShape')

    # Cog mod
    if cmds.objExists(cog_ctl):
        cmds.parentConstraint(cog_ctl, 'RootX_M', mo=True)

    # Master Offset ctl mod, renames and modifies "Main" node from AS rig
    if master_offset_ctl:
        if cmds.objExists(master_offset_ctl):
            cmds.delete(master_offset_ctl)
    
    if cmds.objExists('Main'):
        master_offset_ctl_name = master_offset_ctl.split('|')[-1]
        master_offset_ctl = cmds.rename('Main', master_offset_ctl_name)
        cmds.reorder(master_offset_ctl, relative=-1)
        setColor(master_offset_ctl, YELLOW_AS)
        cmds.setAttr('{}Shape.overrideEnabled'.format(master_offset_ctl), 0)

    # Designate masterOffset metatype to the new renamed Main control
    dragonfly.modules.add_metatype(master_offset_ctl, dragonfly.meta_types.MTYPE_MASTER_OFFSET)
    cmds.setAttr('{}.v'.format(master_offset_ctl), k=False, l=True)
    cmds.delete(cmds.listRelatives('RootX_M', shapes=True))

    # Connect the globalScale from the master ctl to the master_offset_ctl
    for attr in ['sx','sy','sz']:
        cmds.setAttr('{}.{}'.format(master_ctl, attr), k=False, lock=False)
        cmds.connectAttr('{}.globalScale'.format(master_ctl), '{}.{}'.format(master_ctl, attr))
        cmds.setAttr('{}.{}'.format(master_offset_ctl, attr), k=False, lock=True)
        cmds.setAttr('{}.{}'.format(master_ctl, attr), k=False, lock=True)

    # Constrain root_jnt to trajectory
    if dragonfly.modules.get_metatype(dragonfly.meta_types.MTYPE_TRAJECTORY):
        traj_ctl = dragonfly.modules.get_metatype(dragonfly.meta_types.MTYPE_TRAJECTORY)[0]
        cmds.parentConstraint(traj_ctl, root_jnt, mo=True)
    else:
        cmds.parentConstraint(master_ctl, root_jnt, mo=True)



def do_addRootJoint(root_joint='cn_root_jnt', masterOffset='Main'):
    """Renames root joint to body and adds a standard root joint at origin

    Args:
        masterOffset: Name of masterOffset control

    Returns:
        True if successful, errors otherwise
    """
    if cmds.objExists(AS_ROOT_JNT):
        cmds.rename(AS_ROOT_JNT, '%s_M' % SPINE_BASE_JNT)
        cmds.select(clear=True)
        if not cmds.objExists(root_joint):
            cmds.joint(name=root_joint)
        SKEL_GRP = cmds.listRelatives('%s_M' % SPINE_BASE_JNT, parent=True)[0]
        if not cmds.listRelatives(root_joint, parent=True):
            cmds.parent(root_joint, SKEL_GRP)
        cmds.parent('%s_M' % SPINE_BASE_JNT, root_joint)

        # Rename 'RootPart' joints
        rootPartJnts = cmds.ls('RootPart*', type="joint")
        if rootPartJnts:
            for jnt in rootPartJnts:
                newNm = jnt.replace('RootPart', '%sPart' % SPINE_BASE_JNT)
                cmds.rename(jnt, newNm)

        # Modify scaling to work on root joint
        for attr in ['sx', 'sy', 'sz']:
            scaleCxn = cmds.listConnections('%s.%s' % (root_joint, attr), s=True, d=False, plugs=True)
            if scaleCxn:
                cmds.disconnectAttr(scaleCxn[0], '%s.%s' % (root_joint, attr))

        cmds.delete(root_joint, constraints=True)
        cmds.scaleConstraint(masterOffset, root_joint)
        rootChildren = cmds.listRelatives(root_joint, children=True, type='joint')

        if rootChildren:
            for child in rootChildren:
                cmds.setAttr('%s.segmentScaleCompensate' % child, 0)
        LOG.debug("[rootJoint] Added root joint: %s" % ROOT_JNT)
        return True


def do_fixFingerSpread(finger_list=['Index','Middle','Ring','Pinky'], sides=['L','R']):
    """Switch rotation orders so spread and curl can be combined correctly"""
    for side in sides:
        for fing in finger_list:
            sdk1 = 'SDK1FK{}Finger1_{}'.format(fing, side)
            sdk2 = 'SDK2FK{}Finger1_{}'.format(fing, side)
            xtra = 'FKExtra{}Finger1_{}'.format(fing, side)
            if cmds.objExists(sdk1) and cmds.objExists(sdk2):
                if cmds.objExists(xtra):
                    par = cmds.listRelatives(sdk1, parent=True)[0]
                    cmds.parent(xtra, sdk1)
                    cmds.parent(sdk2, par)
                    cmds.parent(sdk1, sdk2)


def do_rotationOrdersXZY(centerParts = {}, sideParts = {"FKShoulder": "xzy", "FKElbow": "xzy", "FKWrist": "xzy"}):
    """Sets rotation orders based input dictionaries

    Args:
        centerParts:  Non-side control name : rotate order pairings
        sideParts:  Side control name : rotate order pairings

    Returns:
        None
    """
    if centerParts:
        for part, ro in centerParts.iteritems():
            if cmds.objExists(part):
                roVal = ROTATE_ORDER[ro]
                cmds.setAttr("%s.rotateOrder" % part, roVal)
                cmds.setAttr("%s.rotateOrder" % part, keyable=True, lock=False)

    if sideParts:
        for side in ["_L", "_R"]:
            for part, ro in sideParts.iteritems():
                if cmds.objExists(part + side):
                    roVal = ROTATE_ORDER[ro]
                    ctl = "{}{}".format(part, side)
                    cmds.setAttr("{}.rotateOrder".format(ctl), roVal)
                    cmds.setAttr("{}.rotateOrder".format(ctl), keyable=True, lock=False)

                    # Connect rotate order of control to corresponding bind joint
                    bind_jnt = ctl.replace('FK','')
                    if cmds.objExists(bind_jnt):
                        cmds.connectAttr("{}.rotateOrder".format(ctl), "{}.rotateOrder".format(bind_jnt))


def do_fkikBlendValueRange():
    """Modifies all FKIKBlend attr ranges from 0-10 to 0-1.

    Returns:
        None
    """
    switches = cmds.ls('FKIK*', type="transform")
    if switches:
        for switch in switches:
            if cmds.attributeQuery('FKIKBlend', node=switch, exists=True):
                connections = cmds.listConnections('%s.FKIKBlend' % switch, s=False, d=True)
                currentFKIKBlendVal = cmds.getAttr('%s.FKIKBlend' % switch)
                if currentFKIKBlendVal > 1:
                    cmds.setAttr('%s.FKIKBlend' % switch, 1)
                for node in connections:
                    if cmds.nodeType(node) == 'unitConversion':
                        cmds.setAttr('%s.conversionFactor' % node, 1.0)
                        cmds.addAttr('%s.FKIKBlend' % switch, edit=True, max=1)
                    elif cmds.nodeType(node) == 'setRange':
                        cmds.setAttr('%s.minX' % node, 1)
                        cmds.setAttr('%s.oldMaxX' % node, 1)
                    else:
                        pass
                LOG.debug("[fkikBlendValueRange] Modified fkik value range on %s" % switch)


def attributeSeparator(control, attr):
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


def do_addPropSpaceArmIK(remove=False, controlColor=3):
    """Adds a world space ik controller and constraint setup to armIK

    Args:
        remove:  If True, removes an existing world space IK control setup.
        controlColor:  Color index for world space ik control colors.

    Returns:
        List of created controls
    """
    # TODO Be able to specify individual limbs instead of assuming just L and R.
    ikWorldCtrls = []
    for side in ["L", "R"]:
        ikArm = "IKArm_%s" % side
        if cmds.objExists(ikArm):
            if remove:
                try:
                    ikArm = "IKArm_%s" % side
                    parC = cmds.listConnections("IKOffsetArm_%s" % side, s=True, d=False)[0]

                    # delete arm world space nodes
                    delNodes = cmds.listConnections("IKArmProp_%s.ikPropNodes" % side, s=True, d=False)
                    if delNodes:
                        for node in delNodes:
                            if cmds.objExists(node): cmds.delete(node)

                    # Delete arm world space attr
                    if cmds.attributeQuery("propArmIKSpace", exists=True, node=ikArm):
                        cmds.deleteAttr(ikArm, at="propArmIKSpace")

                    # Reconnect arm constraint
                    rng = "IKArm_%sSetRangeFollow" % side
                    cmds.connectAttr("%s.outValueX" % rng, "%s.Scapula_%sW1" % (parC, side))
                    cmds.connectAttr("%s.outValueY" % rng, "%s.IKOffsetArm_%sStaticW0" % (parC, side))

                    LOG.debug('[worldSpaceArmIK] Removed %s' % ikArmWorld)
                    return True
                except:
                    LOG.error("[worldSpaceArmIK] Error removing World IK controls")
                    raise

            if not remove:
                try:
                    ikOff = "IKOffsetArm_%s" % side
                    ikExtra = "IKExtraArm_%s" % side
                    ikArm = "IKArm_%s" % side
                    ikNodes = [ikOff, ikExtra, ikArm]

                    # duplicate ik arm nodes to create arm world ik nodes
                    for ikNode in ikNodes:
                        ikDup = cmds.duplicate(ikNode)[0]
                        cmds.delete(cmds.listRelatives(ikDup, f=True, children=True, type="transform"))
                        newNm = ikNode.replace("Arm_", "ArmProp_")
                        cmds.rename(ikDup, newNm)

                    ikOffProp = "IKOffsetArmProp_%s" % side
                    ikExtraProp = "IKExtraArmProp_%s" % side
                    ikArmProp = "IKArmProp_%s" % side

                    cmds.parent(ikExtraProp, ikOffProp)
                    cmds.parent(ikArmProp, ikExtraProp)

                    # Resize ik world arm box
                    scaleControl(ikArmProp, [1.2, 1.2, 1.2])

                    # Set color of world space arm control to grey
                    colorControl(ikArmProp, controlColor)

                    # Add message attr ik arm world to connect related nodes to
                    cmds.addAttr(ikArmProp, longName='ikPropNodes', attributeType='message', multi=True)

                    # Remove attrs on world arm ik
                    dupAttrs = ["follow", "stretchy", "antiPop", "Lenght1", "Lenght2", "volume"]
                    for attr in dupAttrs:
                        cmds.deleteAttr(ikArmProp, at=attr)

                    attributeSeparator(ikArm, 'prop')

                    # Visibitlity
                    cmds.connectAttr("%s.v" % ikOff, "%s.v" % ikOffProp)

                    cmds.addAttr(ikArm, longName="showPropCtl", at="double", min=0, max=1, dv=1)
                    cmds.setAttr("%s.showPropCtl" % ikArm, keyable=True)
                    cmds.connectAttr("%s.showPropCtl" % ikArm, "%sShape.v" % ikArmProp)
                    cmds.select(clear=True)

                    ikWorldCtrls.append(ikArmProp)

                    LOG.debug("[PropSpaceArmIK] Created %s" % ikArmProp)

                except:
                    LOG.debug("[PropSpaceArmIK] Error trying to create Prop IK control")
                    raise
    return ikWorldCtrls


def do_heelSwingControl():
    """Creates Lf/Rt_HeelSwing_ctrl

    Returns:
        List of created controls
    """
    # TODO Be able to specify individual limbs instead of assuming just L and R.
    heelSwingCtrls = []
    try:
        for side in ['L', 'R']:
            if cmds.objExists('RollHeel_{}'.format(side)):
                # Create control
                dupeCtrl = cmds.duplicate('RollHeel_%sShape' % side)[0]
                cmds.delete(cmds.listRelatives(dupeCtrl, children=True, f=True, type='transform'))
                heelSwingCtrl = cmds.rename(dupeCtrl, 'HeelSwing_%s' % side)

                # Rotate control
                cmds.select('%s.cv[0:*]' % heelSwingCtrl)
                cmds.rotate(0, 0, 90, os=True)

                # Reparent nodes
                cmds.parent(heelSwingCtrl, 'RollToesEnd_%s' % side)
                cmds.parent('RollOffsetToes_%s' % side, heelSwingCtrl)

                # Repo pivot to ball of foot
                pivotPos = cmds.xform('RollToes_%s' % side, q=True, ws=True, piv=True)
                cmds.move(pivotPos[0], pivotPos[1], pivotPos[2], '%s.scalePivot' % heelSwingCtrl,
                        '%s.rotatePivot' % heelSwingCtrl)

                for attr in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz']:
                    cmds.setAttr('%s.%s' % (heelSwingCtrl, attr), lock=True, keyable=False)

                heelSwingCtrls.append(heelSwingCtrl)

                LOG.debug('[heelSwingControl] Created %s' % heelSwingCtrl)
            else:
                LOG.debug('[heelSwingControl] Roll heel control {0} not found, skipping'.format('RollHeel_{}'.format(side)))
    except:
        LOG.error("[heelSwingControl] Error creating heelSwing control")
        raise
    return heelSwingCtrls


def do_trajectoryControl(masterControl="master_M", rootJoints=["Root_M"], controlScale=1.0):
    """Adds Trajectory control to rig and constrains listed root joints to it

    Args:
        masterControl:  Name of existing masterControl object
        rootJoints:  Name of root joint(s) to constrain.
        controlScale:  Scale value of created 

    Returns:
        Returns name of created 
    """
    if not cmds.objExists("Trajectory_M"):
        zero = cmds.group(name="Trajectory_zero_M", empty=True)
        ctrl = cmds.createNode("transform", name="Trajectory_M")
        handle(ctrl, ctrlShape="arrow")
        setColor(ctrl, COLORS_AS['cyan'])
        orientTweak(90, "y", "-")

        gScale = getNodeScale(cmds.ls(type="mesh")) * controlScale
        scaleControl(ctrl, [gScale, gScale, gScale])

        cmds.makeIdentity(ctrl, apply=True, translate=True, rotate=True, scale=True)
        cmds.parent(ctrl, zero)

        # Parent into rig
        if cmds.objExists(masterControl):
            cmds.parent(zero, masterControl)

        # Constrain rootJoints to Trajectory ctrl
        for rootJoint in rootJoints:
            cmds.parentConstraint(ctrl, rootJoint, mo=True)

        cmds.sets(ctrl, add="ControlSet")

        cmds.select(clear=True)
        LOG.debug('[trajectoryControl] Created %s' % ctrl)
        return ctrl
    else:
        LOG.error('[trajectoryControl] %s already exists!' % ctrl)
        raise
    
    
def do_addFkGimbalControls(controlColor=CYAN_AS, controlScale=.8):
    """Adds control under existing control for handling gimbal rotation problems

    Args:
        controlColor:  Color of created offset controls (uses cyan from py by default)
        controlScale:  Scale value for created offset 

    Returns:
        True/False
    """
    try:
        fkX = []
        fkXAll = cmds.ls("FKX*", type="joint")
        for node in fkXAll:
            for filter in ["Spine", "Chest", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle"]:
                if filter in node:
                    fkX.append(node)

        for fkXNode in fkX:
            ctrl = cmds.listRelatives(fkXNode, parent=True)
            if ctrl:
                if cmds.listRelatives(ctrl[0], shapes=True):
                    LOG.debug('[addFkGimbalControls]: Adding gimbal controls to %s' % ctrl[0])
                    cmds.addAttr(ctrl[0], ln="showGimbalCtrl", dv=0, min=0, max=1)
                    cmds.setAttr("%s.showGimbalCtrl" % ctrl[0], lock=False, cb=True)
                    gimbalCtrl = safeDuplicateNode(ctrl[0], ctrl[0].replace("_", "Gimbal_"), parentNode=fkXNode, insert=True)

                    duplicateShapes(ctrl[0], gimbalCtrl)
                    colorControl(gimbalCtrl, controlColor)
                    scaleControl(gimbalCtrl, [controlScale, controlScale, controlScale])

                    curveShape = cmds.listRelatives(gimbalCtrl, shapes=True)[0]
                    cmds.setAttr("%s.v" % curveShape, lock=False)
                    cmds.connectAttr("%s.showGimbalCtrl" % ctrl[0], "%s.v" % curveShape)

        LOG.debug('[addFkGimbalControls]: Successfully added gimbal controls to rig')
        return True
    except:
        LOG.error('[addFkGimbalControls]: Error adding gimbal controls')
        raise


def safeDuplicateNode(sourceNode, duplicateNodeName, parentNode="", insert=True):
    """
    safeDuplicateNode("FKShoulder_L", "FKShoulderGimbal_L", parentNode="FKXShoulder_L")
    """
    if cmds.objExists(sourceNode):
        dupNode = cmds.duplicate(sourceNode, name=duplicateNodeName, po=True)
        children = cmds.listRelatives(parentNode, children=True)
        cmds.parent(dupNode, parentNode)
        if children and insert:
            cmds.parent(children, duplicateNodeName)
        return duplicateNodeName
    
    
def setColor(node, color):
    """ sets the maya color on a node like a control or transform, takes int or string """
    # Resolve if color is string or int
    if isinstance(color, int):
        colorInt = color
    else:
        # Check for valid color
        if color in COLORS.keys():
            colorInt = COLORS[color]
        else:
            # Raise error
            raise TypeError(color+' is not a valid color')

    # Set color
    cmds.setAttr(node+'.overrideEnabled', 1)
    cmds.setAttr(node+'.overrideShading', 0)
    cmds.setAttr(node+'.overrideColor', colorInt)
    
    
def scaleControl(node, scaleVector):
    """Scale controlCurve by [x, y, z].
    Adjust controlCurve size of selected transform nodes.

    Args:
        node: Transform node.
        scaleVector: Scale vector.
        ocp: Object Center Pivot.
    Returns:
        None.
    Raises:
        Logs warning if node does not exist.
        Logs warning if node is not tranform type.
        Logs warning if scaleVector is not a list of three.
    """
    if not cmds.objExists(node):
        LOG.warning(node + ' does not exist.')
        return
    elif not (cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint')):
        LOG.warning('Input node requires transform or joint type.')
        return
    elif len(scaleVector) != 3:
        LOG.warning('Input scaleVector requires a list of three.')
        return

    shapeList = get_shape(node)
    for shape in shapeList:
        cmds.select(cl=1)
        cmds.select(shape + '.cv[:]')

        # Get center pivot of CVs
        cls = cmds.cluster()
        cp = cmds.xform(cls[1], q=True, ws=True, piv=True)
        cmds.delete(cls)

        cmds.select(shape + '.cv[:]')
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, p=(cp[0], cp[1], cp[2]))


def colorControl(node, index):
    """Drawing overrides selected 

    Args:
        node: Transform node or nurbsCurve.
        index: Color index.
    Returns:
        None.
    Raises:
        None.
    """
    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.setAttr("{0}.overrideEnabled".format(node), True)
        cmds.setAttr("{0}.overrideColor".format(node), index)

    elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
        shapeList = get_shape(node)
        for shape in shapeList:
            cmds.setAttr("{0}.overrideEnabled".format(shape), True)
            cmds.setAttr("{0}.overrideColor".format(shape), index)
            
            
def handle(ctrl, ctrlShape='circle', ctrlColor=None, ctrlScale=None, ctrlAxis=None):
    """Add valid ctrl shape (handle) to ctrl node. Rename to ctrlShape format.
    If ctrl has curve shapes, they will be deleted.

    Args:
        ctrl: Target control.
        ctrlShape: The control shape name.
        ctrlColor: The maya color of the control. Takes int or string.
        ctrlScale: The scale of the control.
        ctrlAxis: The normal axis name of the control, such as 'x', or '-z'.

    Returns: List of the added shape.
    """
    # check if ctrl exists
    if not cmds.objExists(ctrl):
        LOG.info('control.handle: "' + ctrl + '" node does not exist, skipping...')
        return (None)

    # load and add control shapes from json file
    filepath = os.path.join(CONTROLS_DIRECTORY, ctrlShape + '.json')
    if os.path.exists(filepath):
        importShapesFromJson(filepath, ctrl)
        # importControlCurves
    else:
        LOG.error('Control shape file %s does not exist! You lose... (said in Schwarzenegger voice)' % ctrlShape)
        return (None)

    # Add color
    controlShapes = cmds.listRelatives(ctrl, s=True)
    if ctrlColor:
        #setColor(ctrl, ctrlColor)
        if controlShapes:
            for ctrlShp in controlShapes:
                setColor(ctrlShp, ctrlColor)

    # Get ctrl info
    ctrlCenter = cmds.xform(ctrl, q=True, ws=True, t=True)
    pts = []
    if controlShapes:
        for s in controlShapes:
            pts = pts + cmds.ls(s + '.cp[*]')

    # Orient
    orientAxes = {"x": [0, 0, -90], "y": [0, 0, 0], "z": [90, 0, 0],
                  "-x": [0, 0, 90], "-y": [0, 0, 180], "-z": [-90, 0, 0]}
    if ctrlAxis:
        axis = orientAxes[ctrlAxis]
        cmds.rotate(axis[0], axis[1], axis[2], pts, p=ctrlCenter, r=True, os=True)

    # Scale
    if ctrlScale:
        cmds.scale(ctrlScale, ctrlScale, ctrlScale, pts, p=ctrlCenter, r=True)

    # rename
    controlShapes = cmds.listRelatives(ctrl, s=True)
    for s in controlShapes:
        cmds.rename(s, ctrl + 'Shape')

    return (controlShapes)



def orientTweak(degree, axis, operator):
    """
    Tweak controlCurve orientation by degree.
    Adjust controlCurve orientation of selected transform nodes by a certain degree.

    Args:
        degree: Rotation value.
        axis: Rotation axis.
        operator: + / -
    Returns:
        None.
    Raises:
        Logs warning if nothing is selected.
        Logs warning if axis input is NOT xyz.
        Logs warning if operator input is NOT +-.

    """
    sel = cmds.ls(sl=1, l=True)
    if len(sel) < 1:
        LOG.warning('Nothing is selected.')
        return

    if operator == '+':
        factor = 1
    elif operator == '-':
        factor = -1
    else:
        LOG.warning('Parameter operator is expecting + / - as input.')
        return

    if (axis in 'x') or (axis in 'X'):
        v = [degree * factor, 0, 0]
    elif (axis in 'y') or (axis in 'Y'):
        v = [0, degree * factor, 0]
    elif (axis in 'z') or (axis in 'Z'):
        v = [0, 0, degree * factor]
    else:
        LOG.warning('Parameter axis is expecting x / y / z as input.')
        return

    for node in sel:
        if cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
            shapeList = get_shape(node)
            for shape in shapeList:
                cmds.select(cl=1)
                cmds.select(shape + '.cv[:]')
                cmds.rotate(v[0], v[1], v[2], r=1, os=1, fo=1)
        elif cmds.objectType(node, isType='nurbsCurve'):
            cmds.select(cl=1)
            cmds.select(node + '.cv[:]')
            if MAYA_VER > 2015:
                cmds.rotate(v[0], v[1], v[2], r=1, os=1, fo=1)
            else:
                cmds.rotate(v[0], v[1], v[2], r=1, os=1)

    cmds.select(sel)
    
    
def duplicateShapes(source, target):
    """
    Copy shapes from one transform node to another.

    Args:
        source: Source of shapes.
        target: Target for shapes.
    Returns:
        None.
    Raises:
        Logs warning if source / target is not transform / joint.

    """
    if not (cmds.objectType(source, isType='joint') or cmds.objectType(source, isType='transform')):
        LOG.warning('Source object needs to be tranform type.')
        return
    elif not (cmds.objectType(target, isType='joint') or cmds.objectType(target, isType='transform')):
        LOG.warning('Target object needs to be tranform type.')
        return

    dup = cmds.duplicate(source, n='ctrlTmp', rc=True)[0]
    controlTempShapes = cmds.listRelatives(dup, s=True)
    for i in range(len(controlTempShapes)):
        cmds.parent(controlTempShapes[i], target, r=True, s=True)
        cmds.select(cl=True)
        if i == 0:
            cmds.rename(controlTempShapes[i], '%sShape' % target)
        if i > 0:
            cmds.rename(controlTempShapes[i], '%sShape%s' % (target, str(i)))
    cmds.delete(dup)
    
    
def get_shape(node, intermediate=False):
    """Get the shape node of a transform.
    This is useful if you don't want to have to check if a node is a shape node
    or transform.  You can pass in a shape node or transform and the function
    will return the shape node.

    Args:
        node: The name of the node.
        intermediate: True to get the intermediate shape.

    Returns:
        The name of the shape node.
    """
    returnShapes = []
    if cmds.nodeType(node) == 'transform' or 'joint':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                returnShapes.append(shape)
                # return shape
            elif not intermediate and not is_intermediate:
                returnShapes.append(shape)
                # return shape
        return returnShapes

    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        is_intermediate = cmds.getAttr('%s.intermediateObject' % node)
        if is_intermediate and not intermediate:
            node = cmds.listRelatives(node, parent=True, path=True)[0]
            return get_shape(node)
        else:
            return node
    return None


def get_knots(curve):
    """Gets the list of knots of a curve so it can be recreated.

    Args:
        curve: Curve to query.

    Returns:
        A list of knot values that can be passed into the curve creation command.
    """
    if not 'nurbsCurve' in cmds.nodeType(curve):
        curve = shape.getShape(curve)
    info = cmds.createNode('curveInfo')
    cmds.connectAttr('{0}.worldSpace'.format(curve), '{0}.inputCurve'.format(info))
    knots = cmds.getAttr('{0}.knots[*]'.format(info))
    cmds.delete(info)
    return knots


def create_curve(control, transform=None):
    """Create a curve.

    Args:
        control: A data dictionary generated from the dump function.
        transform: A transform node to add curveShape to.

    Returns:
        Curve name.
    """
    curve = control['name']
    curveShape = control['shape']

    periodic = control['form'] == 2
    degree = control['degree']
    points = control['cvs']

    if periodic and not cmds.objExists(curveShape):
        points = points + points[:degree]

    if cmds.objExists(curveShape):
        i = 0
        while i < len(points):
            cmds.move(points[i][0], points[i][1], points[i][2], '%s.cv[%s]' % (curveShape, i), os=True)
            i = i + 1

    else:
        if cmds.objExists(curve):
            curve = cmds.curve(degree=degree, p=points, n="TEMP" + control['name'], per=periodic, k=control['knots'])
        else:
            curve = cmds.curve(degree=degree, p=points, n=control['name'], per=periodic, k=control['knots'])
        curveShape = cmds.rename(cmds.listRelatives(curve, shapes=True)[0], curveShape)

        if 'parent' in control:
            if cmds.objExists(control['parent']):
                if control['parent'] != cmds.listRelatives(curveShape, parent=True)[0]:
                    try:
                        cmds.parent(curveShape, control['parent'], relative=True, shape=True)
                        cmds.delete(curve)
                    except:
                        pass

    # parenting
    if (transform and (transform is not cmds.listRelatives(curveShape, p=True, type='transform')[0])):
        try:
            cmds.parent(curveShape, transform, s=1, r=1)
            cmds.delete(curve)
        except:
            pass

    if cmds.objExists(curve):
        cmds.delete(curve, constructionHistory=True)

        cmds.setAttr('{0}.overrideEnabled'.format(curve), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curve), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curve), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curve), *control['overrideColorRGB'])
        except:
            pass

    if cmds.objExists(curveShape):
        cmds.setAttr('{0}.overrideEnabled'.format(curveShape), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curveShape), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curveShape), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curveShape), *control['overrideColorRGB'])
        except:
            pass

    return curve


def removeControl(controlTransform):
    """Removes any exisiting control curve shapes under the controlTransform

    Args:
        controlTransform: Transform node whose curve shapes are to be removed.
    Returns:
        None.
    Raises:
        Logs error if controlTransform does not exist.

    """
    if cmds.objExists(controlTransform):
        curveShapes = cmds.listRelatives(controlTransform, pa=1, shapes=True, type='nurbsCurve')
        if curveShapes:
            cmds.delete(curveShapes)
            LOG.debug('Deleted %s' % curveShapes)
            return True
        else:
            return
    else:
        LOG.error('%s does not exist' % controlTransform)
        return


def importShapesFromJson(filepath, transform=None):
    """
    Import control shape to node.

    Args:
        filepath: The absolute filepath to a json file.
        transform: Target node.

    Returns: Filepath if succeeds. None if fails.

    """
    if os.path.exists(filepath):

        fh = open(filepath, 'r')
        curveData = json.load(fh)
        fh.close()

        # make sure it's a list - some control jason files are dicts in a list some are just dicts
        # this deals with that issue
        if type(curveData) != list:
            curveData = [curveData]

        # if the transform already has shapes delete them and create new ones
        if transform:
            shapes = cmds.listRelatives(transform, s=True)
            if shapes:
                for s in shapes:
                    cmds.delete(s)
                    # create_curve(curveData)
        for dataBlock in curveData:
            create_curve(dataBlock, transform)

        LOG.debug('Imported Control Curves from: %s' % filepath)
        return filepath
    else:
        LOG.error('Control curve file %s does not exist!' % filepath)
        return None
    
    
def hipSwinger(controlShape=HIP_SWINGER_CTRL_SHP, controlScale=1.0):
    """ Modifies default hipSwinger control position from side of char to center of pelvis

    Args:
        controlShape:  Name of the hip swinger control shape to modify.
        controlScale:  Scale of the new hip swinger (pelvis) 

    Returns:
        Bool
    """
    if cmds.objExists(HIP_SWINGER_CTRL):
        hipSwingerOffset = cmds.listRelatives(HIP_SWINGER_CTRL, parent=True)[0]
        cmds.delete(cmds.pointConstraint('RootX_M', hipSwingerOffset))

        # Update constraint so HipSwinger works in FK mode as well
        if cmds.objExists('HipSwingerStabilizer_orientConstraint1'):
            cmds.delete('HipSwingerStabilizer_orientConstraint1')
        cmds.orientConstraint('HipSwingerStabilizerTarget', 'HipSwingerStabilizer')

        # Create new control to replace original
        removeControl(HIP_SWINGER_CTRL)
        gScale = 2.0
        if cmds.ls(type="mesh"):
            gScale = getNodeScale(cmds.ls(type="mesh")) / 2 * controlScale
        handle(HIP_SWINGER_CTRL, ctrlShape=controlShape, ctrlColor=SIDE_COLOR_AS['_M'],
                       ctrlScale=gScale)
        orientTweak("90", "z", "+")

        # Follow setup
        if cmds.objExists("HipSwingerOffset_M"):
            follow = cmds.duplicate("HipSwingerOffset_M", name="HipSwingerFollow_M", po=True)[0]
            cmds.delete(cmds.pointConstraint("HipSwingReverseRoot", follow))
            cmds.parent("HipSwingerOffset_M", follow)
            cmds.connectAttr("HipSwinger_M.rotate", "%s.rotate" % follow)

        cmds.select(clear=True)

        return True
    else:
        return


def masterControl(controlShape=MASTER_CTRL_SHP, controlScale=1.0):
    """ Adds control curve to master node

    Args:
        controlShape:  Name of the master control shape to modify.
        controlScale:  Scale of the new master 

    Returns:
        Bool
    """
    if cmds.objExists(MASTER_CTRL):
        #removeControl(MASTER_CTRL)
        gScale = 1.0
        if cmds.ls(type="mesh"):
            gScale = (getNodeScale(cmds.ls(type="mesh")) * controlScale)/3
        handle(MASTER_CTRL, ctrlShape=controlShape, ctrlColor=SIDE_COLOR_AS['_M'],
                       ctrlScale=gScale)
        cmds.sets(MASTER_CTRL, add="ControlSet")
        cmds.select(clear=True)
        LOG.debug("[masterControl]: Successfully modified masterControl.")
        return True
    else:
        return


def bodyControl(controlShape=BODY_CTRL_SHP, controlScale=1.0):
    """ Adds control curve to default RootExtraX_M node

    Args:
        controlShape:  Name of the body control shape to modify.
        controlScale:  Scale of the new body 

    Returns:
        Bool
    """
    if cmds.objExists(BODY_CTRL):
        #removeControl(BODY_CTRL)
        gScale = 5.0
        if cmds.ls(type="mesh"):
            gScale = (getNodeScale(cmds.ls(type="mesh")) * controlScale) / 3
        handle(BODY_CTRL, ctrlShape=controlShape, ctrlColor=SIDE_COLOR_AS['_M'], ctrlScale=gScale)
        orientTweak("90", "z", "+")
        orientTweak("45", "y", "+")
        cmds.select(clear=True)
        return True
    else:
        return


def cogControl(controlShape=COG_CTRL_SHP, controlScale=1.0):
    """ Adds control curve to default RootX_M node

    Args:
        controlShape:  Name of the cog control shape to modify.
        controlScale:  Scale of the new cog 

    Returns:
        Bool
    """
    if cmds.objExists(COG_CTRL):
        #removeControl(COG_CTRL)
        gScale = .5
        if cmds.ls(type="mesh"):
            gScale = (getNodeScale(cmds.ls(type="mesh")) * controlScale) / 3
        handle(COG_CTRL, ctrlShape=controlShape, ctrlColor=CYAN_AS, ctrlScale=gScale)
        cmds.select(clear=True)
        return True
    else:
        return


def fkikControls(controlShape=FKIK_CTRL_SHP, controlScale=1.0):
    """Swaps control curve for FKIK switch controls

    Args:
        controlShape:  Controls shape to use when swapping out existing shape.
        controlScale:  Scale of newly created fkik

    Returns:
        Bool
    """
    fkikSwitches = []
    fkikNodes = cmds.ls('FKIK*', type='transform')
    if fkikNodes:
        for node in fkikNodes:
            if cmds.attributeQuery('FKIKBlend', node=node, exists=True):
                fkikSwitches.append(node)
                #removeControl(node)
                gScale = .3
                if cmds.ls(type="mesh"):
                    gScale = getNodeScale(cmds.ls(type="mesh")) / 20 * controlScale
                handle(node, ctrlShape=controlShape, ctrlColor=CYAN_AS, ctrlScale=gScale)
                orientTweak("90", "x", "+")
                if "_L" in node:
                    colorControl(node, SIDE_COLOR_AS['_L'])
                elif "_R" in node:
                    colorControl(node, SIDE_COLOR_AS['_R'])
                else:
                    colorControl(node, SIDE_COLOR_AS['_M'])
        cmds.select(clear=True)
        return fkikSwitches
    else:
        return


def curveControlColors():
    """ Colors all curve controllers as specified in py based on side naming.

    Returns:
        None
    """
    for key in SIDES_AS:
        sideNm = SIDES_AS[key]
        sideCrvs = cmds.ls('*%sShape*' % sideNm)
        if sideCrvs:
            for crv in sideCrvs:
                if "_L" in crv:
                    colorControl(crv, SIDE_COLOR_AS['_L'])
                    LOG.debug("Colored %s %s" % (crv, SIDE_COLOR_AS['_L']))
                elif "_R" in crv:
                    colorControl(crv, SIDE_COLOR_AS['_R'])
                    LOG.debug("Colored %s %s" % (crv, SIDE_COLOR_AS['_R']))
                elif "_M" in crv:
                    colorControl(crv, SIDE_COLOR_AS['_M'])
                    LOG.debug("Colored %s %s" % (crv, SIDE_COLOR_AS['_M']))
                else:
                    pass
        else:
            pass


def getNodeScale(node):
    """Returns bbox scale of node as vector """
    bBox = cmds.exactWorldBoundingBox(node)
    gScale = min(bBox[3] - bBox[0], bBox[4] - bBox[1], bBox[5] - bBox[2])
    return gScale


def disableVolume():
    """Sets attr to 0, then locks & hides it"""
    a = cmds.ls('*IK*', r=1)
    for i in a:
        exist = cmds.attributeQuery('volume', node=str(i), ex=1)
        if exist:
            v = '.volume'
            attr = str(i) + str(v)
            cmds.setAttr(attr, 0, k=0, l=1)

