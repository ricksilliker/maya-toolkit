#TODO: Add tentacle stretch output percentage attr
#TODO: Support stretch and volume on all axis combinations

import py_tasker.tasks
import dragonfly.modules


LOG = py_tasker.tasks.get_task_logger(__name__)


import maya.cmds as cmds
import maya.api.OpenMaya as om2
from math import pow,sqrt

LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '1.0.0'
DIRECTION = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def run(params, rig):
    all_axis = ['X','Y','Z']
    input_joints = get_node_branch(params['rootJoint'].name(), params['endJoint'].name())
    rig_joints = duplicate_joints(input_joints)

    controls = [x.name() for x in params['controls']]
    aim_weights = get_weights(controls, rig_joints)
    last_orienter = None
    i=len(controls)
    orienters = []
    aimCons = []
    oc = None
    for node, weight in reversed(zip(rig_joints, aim_weights)):
        (a, av), (b, bv) = weight.items()
        orienter = cmds.createNode('transform', name="{}Ori{}_tfm".format(params['baseName'], i))
        orienters.insert(0, orienter)
        cmds.parent(orienter, node)
        cmds.setAttr('{}.translate'.format(orienter), *[0, 0, 0])
        cmds.setAttr('{}.rotate'.format(orienter), *[0, 0, 0])
        if last_orienter is not None:
            upObject = (a if av >= bv else b)
            ac = cmds.aimConstraint(last_orienter, orienter, aimVector=DIRECTION[params['axisDownBone']],
                               upVector=DIRECTION[params['upAxis']], worldUpType='objectrotation',
                               worldUpObject=upObject, mo=True)
            aimCons.append(ac[0])
        else:
            #oc = cmds.orientConstraint(a, orienter, mo=True)
            tip_rot_tfm = cmds.duplicate(orienter, name="{}TipOri_tfm".format(params['baseName']))[0]
            cmds.parent(tip_rot_tfm, orienter)
            cmds.orientConstraint(controls[-1], orienter, mo=True)
            oc = cmds.orientConstraint(a, tip_rot_tfm, mo=True)

        last_orienter = orienter
        i = i - 1

    handle, effector = cmds.ikHandle(sj=rig_joints[0], ee=rig_joints[-1], sol='ikSplineSolver', c=params['curve'].name(), ccv=False, pcv=False)
    handle = cmds.rename(handle, "{}_splineIK".format(params['baseName']))
    cmds.hide(handle)

    clusters = cluster_curve(params['curve'].name(), prefix=params['baseName'])
    weights = get_weights(controls, clusters)
    for node, weight in reversed(zip(clusters, weights)):
        for target, weight_value in weight.items():
            cmds.parentConstraint(target, node, w=weight_value, mo=True)

    organize_grp = cmds.createNode('transform', n='{}FKIKSpline_grp'.format(params['baseName']))
    scale_grp = cmds.createNode('transform', n='{}FKIKSplineScale_grp'.format(params['baseName']))
    cmds.parent(scale_grp, organize_grp)
    cmds.addAttr(scale_grp, ln="globalScale", dv=1)
    cmds.setAttr("{}.globalScale".format(scale_grp), cb=1, l=0)
    for attr in ["X", "Y", "Z"]:
        cmds.connectAttr("{}.globalScale".format(scale_grp), "{}.scale{}".format(scale_grp, attr))
    dragonfly.modules.add_metatype(scale_grp, "global_scale_connect")

    for pointer, orienter, target in zip(rig_joints, orienters, input_joints):
        pc = cmds.pointConstraint(pointer, target, mo=False)
        oc = cmds.orientConstraint(orienter, target, mo=True)
        for axs in all_axis:
            if not axs in all_axis[params['axisDownBone']]:
                cmds.connectAttr('{}.scale{}'.format(pointer, axs), '{}.scale{}'.format(target, axs))
            else:
                cmds.connectAttr("{}.globalScale".format(scale_grp), '{}.scale{}'.format(target, axs))
        if 'noXformGroup' in rig:
            cmds.parent(pc, oc, rig['noXformGroup'])

    if 'rigGroup' in rig:
        cmds.parent(organize_grp, rig['rigGroup'])
    cmds.parent(handle, organize_grp)
    cmds.parent(clusters, scale_grp)
    cmds.parent(rig_joints[0], organize_grp)
    cmds.parent(params['curve'].name(), organize_grp)
    cmds.hide(clusters)

    attrs_attributeSeparator(controls[-1], '___')

    if params['stretchy']:
        axis = ['X', 'Y', 'Z'][params['axisDownBone']]
        stretchy_drivers = add_stretchy(params['curve'].name(), rig_joints, axis, controls[-1])
        cmds.parent(stretchy_drivers, organize_grp)
        cmds.parent(rig_joints[0], scale_grp)

    if params['volume']:
        if params['stretchy']:
            axis = ['X', 'Y', 'Z']
            axisBone = ['X', 'Y', 'Z'][params['axisDownBone']]
            axis.remove(axisBone)
            axisVolume = axis
            vol_nodes = add_volume_scale(params['curve'].name(), rig_joints, controls, controls[-1], rig_group=organize_grp, scaleAxis=axisVolume)
            cmds.parent(vol_nodes, scale_grp)
        else:
            LOG.warning("Can only add volume scale when stretchy is added!")

    # Tapered twist - attrs that will gradate twist from one end (full twist) to other (no twist)
    cmds.addAttr(controls[-1], ln="startTwist", dv=0)
    cmds.setAttr("{}.startTwist".format(controls[-1]), k=1, l=0)

    cmds.addAttr(controls[-1], ln="endTwist", dv=0)
    cmds.setAttr("{}.endTwist".format(controls[-1]), k=1, l=0)

    twAxis = ['X', 'Y', 'Z'][params['axisDownBone']]
    twPmas = list()
    i = 0
    while i < len(aimCons):
        aimCon = aimCons[i]
        twRatio = float( (i+1.0) / len(aimCons) )
        lenTw_mdn = cmds.createNode("multiplyDivide", name=aimCon.replace("tfm_aimConstraint1","lengthTwist_mdn"))
        cmds.setAttr("{}.operation".format(lenTw_mdn), 1)
        cmds.setAttr("{}.input1X".format(lenTw_mdn), twRatio)
        cmds.connectAttr("{}.startTwist".format(controls[-1]), "{}.input2X".format(lenTw_mdn))
        lenTw_pma = cmds.createNode("plusMinusAverage", name=aimCon.replace("tfm_aimConstraint1", "lengthTwist_pma"))
        cmds.connectAttr("{}.outputX".format(lenTw_mdn), "{}.input1D[0]".format(lenTw_pma))
        twPmas.append(lenTw_pma)
        i = i + 1

    aimConsRev = list(reversed(aimCons))
    twPmasRev = list(reversed(twPmas))
    i = 0
    while i < len(aimConsRev):
        aimCon = aimConsRev[i]
        twRatio = 0.0
        if i:
            twRatio = float((i + 1.0) / len(aimConsRev))
        lenTw_mdn = aimCon.replace("tfm_aimConstraint1", "lengthTwist_mdn")
        cmds.setAttr("{}.input1Y".format(lenTw_mdn), twRatio)
        cmds.connectAttr("{}.endTwist".format(controls[-1]), "{}.input2Y".format(lenTw_mdn))
        cmds.connectAttr("{}.outputY".format(lenTw_mdn), "{}.input1D[1]".format(twPmasRev[i]))
        cmds.connectAttr("{}.output1D".format(twPmasRev[i]), "{}.offset{}".format(aimCon, twAxis))
        i = i + 1

    if oc:
        cmds.connectAttr("{}.endTwist".format(controls[-1]), "{}.offset{}".format(oc[0], twAxis))

    # Add sine motion
    if params['sine']:
        sine_nodes = add_tentacle_sine_deformer(params['curve'].name(), aimAxis=[0, -1, 0], upAxis=[1, 0, 0], cvIndexRemove=[0])
        sine_control = ""
        if params['sineControl']:
            sine_control = params['sineControl'].name()
        else:
            sine_control = controls[-1]
        add_tentacle_sine_attrs(params['baseName'], sine_control, sine_nodes[0], sine_nodes[1], master_control=None)
        if params['sineParent']:
            cmds.parent(sine_nodes[2], params['sineParent'].name())

    # Add line connections between controls
    create_curveConnectFromList(controls)

    # Add message attrs
    addMessageAttribute(controls[-1], input_joints, attrName="joints")
    addMessageAttribute(controls[-1], controls, attrName="controls")

    # Cleanup
    for ctl in controls:
        cmds.setAttr("{}.v".format(ctl), k=False, l=True)

    cmds.hide(params['curve'].name())


def get_volume_weights(joint_list):
    """Returns bell curve values from input list

    get_volume_weights(jnts)
    // Result: {'cn_tent1_jnt': 0.0,
     'cn_tent2_jnt': 0.25,
     'cn_tent3_jnt': 0.5,
     'cn_tent4_jnt': 0.75,
     'cn_tent5_jnt': 1.0,
     'cn_tent6_jnt': 0.75,
     'cn_tent7_jnt': 0.5,
     'cn_tent8_jnt': 0.25,
     'cn_tent9_jnt': 0.0} //
    """
    wts_dict = {}
    mid_pt = joint_list[int(len(joint_list) / 2)]
    inc_value = 1.0 / (len(joint_list) - (len(joint_list) + 1) / 2)

    wts_dict[mid_pt] = 1.0

    # Start to mid
    i = 0
    inc = 0.0
    while i < len(joint_list) / 2:
        wts_dict[joint_list[i]] = inc
        inc = inc + inc_value
        i = i + 1

    # Mid to end
    i = len(joint_list) / 2
    while i < len(joint_list) - 1:
        wts_dict[joint_list[i]] = inc
        inc = inc - inc_value
        i = i + 1

    wts_dict[joint_list[-1]] = 0.0

    return wts_dict

def add_volume_scale(curve, rig_joints, controls, volumeControl, rig_group="", scaleAxis=['Y','Z']):

    cmds.addAttr(volumeControl, ln="volume", dv=1, min=0, max=1)
    cmds.setAttr("{}.volume".format(volumeControl), k=1, l=0)
    dragonfly.modules.add_metatype(volumeControl, "global_scale_connect")

    cmds.addAttr(volumeControl, ln="volumeMult", dv=1, min=0)
    cmds.setAttr("{}.volumeMult".format(volumeControl), k=1, l=0)

    cmds.addAttr(volumeControl, ln="fatten", dv=1, min=0)
    cmds.setAttr("{}.fatten".format(volumeControl), k=1, l=0)

    normalize_scale_node = "{}_normalizeScale".format(curve)
    all_scale_node = cmds.createNode('multiplyDivide', n='{0}_globalScale_mdn'.format(curve))
    cmds.setAttr('{}.operation'.format(all_scale_node), 2)
    cmds.connectAttr('{}.outputX'.format(normalize_scale_node), '{}.input1X'.format(all_scale_node))
    cmds.connectAttr("{}.globalScale".format(volumeControl), '{}.input2X'.format(all_scale_node))

    #======
    """
    global_scale_mdn = cmds.createNode("multiplyDivide", name="{}_globalScale_mdn".format(volumeControl))
    arc_length = cmds.listConnections("{}.input1X".format(normalize_scale_node), s=True, d=True, plugs=True)[0]
    cmds.connectAttr(arc_length, "{}.input1X".format(global_scale_mdn))
    cmds.connectAttr("{}.globalScale".format(volumeControl), "{}.input2X".format(global_scale_mdn))
    cmds.connectAttr("{}.outputX".format(global_scale_mdn), "{}.input2X".format(normalize_scale_node))
    """
    #======

    # Volume scale node setup
    # volume1Over
    volume1Over = cmds.createNode('multiplyDivide', n='{0}_volume1Over_mdn'.format(curve))
    #cmds.setAttr('{}.input1X'.format(volume1Over), 1)
    cmds.connectAttr("{}.fatten".format(volumeControl), '{}.input1X'.format(volume1Over))
    cmds.setAttr('{}.operation'.format(volume1Over), 2)
    cmds.connectAttr('{}.outputX'.format(all_scale_node), '{}.input2X'.format(volume1Over))

    # volumePower
    volumePower = cmds.createNode('multiplyDivide', n='{0}_volumePower_mdn'.format(curve))
    cmds.setAttr('{}.operation'.format(volumePower), 3)
    cmds.connectAttr('{}.outputX'.format(volume1Over), '{}.input1X'.format(volumePower))
    cmds.connectAttr("{}.volumeMult".format(volumeControl), '{}.input2X'.format(volumePower))

    # volumeBlend
    volumeBlend = cmds.createNode('blendTwoAttr', n='{0}_volume_blend'.format(curve))
    cmds.connectAttr('{}.outputX'.format(volumePower), '{}.input[1]'.format(volumeBlend))
    cmds.setAttr('{}.input[0]'.format(volumeBlend), 1)
    cmds.setAttr('{}.attributesBlender'.format(volumeBlend), 1)
    cmds.connectAttr("{}.volume".format(volumeControl), '{}.attributesBlender'.format(volumeBlend))

    scalers = []
    scaler_weights = get_volume_weights(rig_joints)

    i = 0
    while i < len(rig_joints):
        # volumeDistributeNormalizer
        volumeDistNormalizer = cmds.createNode('plusMinusAverage', n='{0}_volumeDistNrml_pma'.format(rig_joints[i]))
        cmds.connectAttr('{}.output'.format(volumeBlend), '{}.input1D[0]'.format(volumeDistNormalizer))
        cmds.setAttr('{}.input1D[1]'.format(volumeDistNormalizer), -1)

        # scaler - this is where scale bell curve distribution happens
        scaler_tfm = cmds.createNode("transform", name='{0}_scaler_tfm'.format(rig_joints[i]))
        cmds.addAttr(scaler_tfm, ln="scalerWeight", dv=scaler_weights[rig_joints[i]])
        cmds.setAttr("{}.scalerWeight".format(scaler_tfm), k=1, l=0)
        scalers.append(scaler_tfm)
        if rig_group:
            cmds.parent(scaler_tfm, rig_group)

        # volumeDistributer
        volumeDist = cmds.createNode('multiplyDivide', n='{0}_volumeDist_mdn'.format(rig_joints[i]))
        cmds.connectAttr('{}.output1D'.format(volumeDistNormalizer), '{}.input1X'.format(volumeDist))
        cmds.connectAttr("{}.scalerWeight".format(scaler_tfm), '{}.input2X'.format(volumeDist))

        # volumeDistSum
        volumeDistSum = cmds.createNode('plusMinusAverage', n='{0}_volumeDistSum_pma'.format(rig_joints[i]))
        cmds.connectAttr('{}.outputX'.format(volumeDist), '{}.input1D[0]'.format(volumeDistSum))
        #cmds.setAttr('{}.input1D[1]'.format(volumeDistSum), 1)
        cmds.connectAttr("{}.globalScale".format(volumeControl), '{}.input1D[1]'.format(volumeDistSum))

        # global scale mult
        volume_global_scale = cmds.createNode("multiplyDivide", name="{}_volumeGlobalScale".format(rig_joints[i]))
        cmds.connectAttr("{}.output1D".format(volumeDistSum), "{}.input1X".format(volume_global_scale))
        #cmds.connectAttr("{}.globalScale".format(volumeControl), "{}.input2X".format(volume_global_scale))
        cmds.setAttr("{}.operation".format(volume_global_scale), 2)

        # Scale Mult
        scaleMult = cmds.createNode('multiplyDivide', n='{0}_scaleMult_mdn'.format(rig_joints[i]))
        cmds.connectAttr("{}.scale".format(scaler_tfm), "{}.input1".format(scaleMult))
        cmds.connectAttr("{}.outputX".format(volume_global_scale), "{}.input2{}".format(scaleMult, scaleAxis[0]), f=True)
        cmds.connectAttr("{}.outputX".format(volume_global_scale), "{}.input2{}".format(scaleMult, scaleAxis[1]), f=True)

        # Final scale output
        scaleOut = cmds.createNode('blendColors', n='{0}_scaleOutput_blend'.format(rig_joints[i]))
        cmds.connectAttr('{}.output'.format(scaleMult), "{}.color1".format(scaleOut))
        #cmds.connectAttr('{}.outputY'.format(scaleMult), "{}.color1G".format(scaleOut))
        #cmds.connectAttr('{}.outputZ'.format(scaleMult), "{}.color1B".format(scaleOut))

        cmds.connectAttr('{}.output'.format(scaleOut), "{}.scale".format(rig_joints[i]))
        cmds.setAttr('{}.blender'.format(scaleOut), 1)
        cmds.setAttr('{}.color2R'.format(scaleOut), 1)
        cmds.setAttr('{}.color2G'.format(scaleOut), 1)
        cmds.setAttr('{}.color2B'.format(scaleOut), 1)

        i = i + 1

    for ctl, sclr in zip(controls, scalers):
        cmds.scaleConstraint(ctl, sclr)

    return scalers


def attach_to_curve(node, curve, param):
    pci = cmds.createNode('pointOnCurveInfo', n='{0}_pci'.format(node))
    cmds.setAttr('{}.parameter'.format(pci), param)
    curve_shape_node = cmds.listRelatives(curve, s=True)[0]
    cmds.connectAttr('{}.worldSpace'.format(curve_shape_node), '{}.inputCurve'.format(pci))
    cmds.connectAttr('{}.position'.format(pci), '{}.translate'.format(node))


def get_mobject(node):
    sel = om2.MSelectionList()
    sel.add(node)

    return sel.getDependNode(0)


def get_dag_path(node):
    sel = om2.MSelectionList()
    sel.add(node)

    return sel.getDagPath(0)


def get_u_param(point, curve):
    curve_shape = cmds.listRelatives(curve, s=True)[0]
    curve_mobject = get_dag_path(curve_shape)
    m_point = om2.MPoint(point)

    mfn_curve = om2.MFnNurbsCurve(curve_mobject)
    if mfn_curve.isPointOnCurve(m_point):
        parameter = mfn_curve.getParamAtPoint(m_point, space=om2.MSpace.kWorld)
    else:
        closest_point, parameter = mfn_curve.closestPoint(m_point, space=om2.MSpace.kWorld)

    return parameter


def get_node_branch(start_node, end_node):
    nodes = get_all_parents(end_node)
    nodes.reverse()
    nodes = [om2.MFnDependencyNode(x).name() for x in nodes]
    nodes.append(end_node)
    index = nodes.index(start_node)

    return nodes[index:]


def get_all_parents(node):
    parents = []

    mobject = get_mobject(node)

    dag_node = om2.MFnDagNode(mobject)
    node_parent = dag_node.parent(0)

    if node_parent.hasFn(om2.MFn.kTransform):
        parents.append(node_parent)
        parents.extend(get_all_parents(node_parent))

    return parents


def add_stretchy(curve, joints, axis, stretchControl):

    cmds.addAttr(stretchControl, ln="globalScale", dv=1)
    cmds.setAttr("{}.globalScale".format(stretchControl), cb=1, l=0)

    cmds.addAttr(stretchControl, ln="stretch", dv=1, min=0, max=1)
    cmds.setAttr("{}.stretch".format(stretchControl), k=1, l=0)

    cmds.addAttr(stretchControl, ln="retract", dv=0)
    cmds.setAttr("{}.retract".format(stretchControl), k=1, l=0)

    curve_info_node = cmds.createNode('curveInfo', n='{0}_curveInfo'.format(curve))
    cmds.connectAttr('{}.worldSpace'.format(curve), '{}.inputCurve'.format(curve_info_node))

    normalize_scale_node = cmds.createNode('multiplyDivide', n='{0}_normalizeScale'.format(curve))
    cmds.setAttr('{}.input2X'.format(normalize_scale_node), cmds.getAttr('{}.arcLength'.format(curve_info_node)))
    cmds.setAttr('{}.operation'.format(normalize_scale_node), 2)
    cmds.connectAttr('{}.arcLength'.format(curve_info_node), '{}.input1X'.format(normalize_scale_node))

    all_scale_node = cmds.createNode('multiplyDivide', n='{0}_globalScale'.format(curve))
    cmds.setAttr('{}.operation'.format(all_scale_node), 2)
    cmds.connectAttr('{}.outputX'.format(normalize_scale_node), '{}.input1X'.format(all_scale_node))
    cmds.connectAttr("{}.globalScale".format(stretchControl), '{}.input2X'.format(all_scale_node))

    position_locators = []
    for n, jnt in enumerate(joints):
        driver_node = cmds.createNode('joint', n='{0}_driver'.format(jnt))
        position_locators.append(driver_node)

        position = cmds.xform(jnt, q=True, ws=True, t=True)
        cmds.setAttr('{}.translate'.format(driver_node), *position)

        param = get_u_param(position, curve)
        attach_to_curve(driver_node, curve, param)

        if n > 0:
            cmds.addAttr(driver_node, ln='orig_length', at='float')
            orig_length = cmds.getAttr('{}.translate{}'.format(jnt, axis))
            cmds.setAttr('{}.orig_length'.format(driver_node), orig_length)

            parent_locator = position_locators[n - 1]
            distance_node = cmds.createNode('distanceBetween', n='{0}_distance'.format(driver_node))
            cmds.connectAttr('{}.translate'.format(driver_node), '{}.point1'.format(distance_node))
            cmds.connectAttr('{}.translate'.format(parent_locator), '{}.point2'.format(distance_node))

            stretch_global_scale = cmds.createNode("multiplyDivide", name="{}_stretchGlobalScale".format(driver_node))
            cmds.connectAttr("{}.distance".format(distance_node), "{}.input1X".format(stretch_global_scale))
            cmds.connectAttr("{}.globalScale".format(stretchControl), "{}.input2X".format(stretch_global_scale))
            cmds.setAttr("{}.operation".format(stretch_global_scale), 2)

            stretch_factor_node = cmds.createNode('multiplyDivide', n='{0}_stretchFactor'.format(driver_node))
            cmds.setAttr('{}.operation'.format(stretch_factor_node), 2)
            cmds.connectAttr("{}.outputX".format(stretch_global_scale), '{}.input1X'.format(stretch_factor_node))
            #cmds.connectAttr('{}.orig_length'.format(driver_node), '{}.input2X'.format(stretch_factor_node))

            orig_length = cmds.getAttr('{}.orig_length'.format(driver_node))
            cmds.setAttr('{}.input2X'.format(stretch_factor_node), orig_length)

            retract_add = cmds.createNode('addDoubleLinear', n='{0}_retract'.format(driver_node))
            cmds.connectAttr('{}.orig_length'.format(driver_node), '{}.input1'.format(retract_add))
            cmds.connectAttr("{}.retract".format(stretchControl), '{}.input2'.format(retract_add))
            cmds.connectAttr('{}.output'.format(retract_add), '{}.input2X'.format(stretch_factor_node))

            stretch_node = cmds.createNode('multDoubleLinear', n='{}_stretch'.format(driver_node))
            cmds.connectAttr('{}.outputX'.format(stretch_factor_node), '{}.input1'.format(stretch_node))
            cmds.connectAttr('{}.orig_length'.format(driver_node), '{}.input2'.format(stretch_node))

            toggle_stretch_node = cmds.createNode('blendColors', n='{0}_toggleStretchy'.format(driver_node))
            cmds.setAttr('{}.blender'.format(toggle_stretch_node), 1.0)
            cmds.connectAttr("{}.stretch".format(stretchControl), '{}.blender'.format(toggle_stretch_node))
            cmds.connectAttr('{}.output'.format(stretch_node), '{}.color1R'.format(toggle_stretch_node))
            cmds.connectAttr('{}.orig_length'.format(driver_node), '{}.color2R'.format(toggle_stretch_node))

            cmds.connectAttr('{}.outputR'.format(toggle_stretch_node), '{}.translate{}'.format(jnt, axis))

    return position_locators


def cluster_curve(curve, prefix=""):
    curve_shape_node = cmds.listRelatives(curve, s=True)[0]
    mfn_curve = om2.MFnNurbsCurve(get_mobject(curve_shape_node))
    clusters = []
    for i in xrange(mfn_curve.numCVs):
        cv = '{crv}.cv[{index}]'.format(crv=mfn_curve.partialPathName(), index=i)
        shape, handle = cmds.cluster(cv)
        handle = cmds.rename(handle, '{}Cluster{}_hdl'.format(prefix, i))
        clusters.append(handle)

    return clusters


def get_weights(targets, nodes, maxTargets=2, ws=True):
    numTargets = min(len(targets), maxTargets)

    def _getBlend(node):
        piv = om2.MPoint(cmds.xform(node, q=True, ws=ws, rp=True))
        dists = {}
        for target in targets:
            dists[target] = om2.MPoint(piv).distanceTo(om2.MPoint(cmds.xform(target, q=True, ws=ws, rp=True)))

        def _distanceCompare(a, b):
            return cmp(dists[a], dists[b])

        # find closest targets
        closest = sorted(targets, cmp=_distanceCompare)[:numTargets]

        # build ratios dict
        ratios = {}
        distsum = sum([d for t, d in dists.items() if t in closest])
        for t in closest:
            ratios[str(t)] = (distsum - dists[t]) / distsum

        return ratios

    return [_getBlend(n) for n in nodes]


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


def create_curveConnectFromList(nodeList):
    """Creates degree one curve between from ordered list of objects
    sel = cmds.ls(selection=True)
    create_curveConnectFromList(sel)
    """
    i = 0
    while i < len(nodeList) - 1:
        create_curveConnector(nodeList[i], nodeList[i + 1])
        i = i + 1


def create_curveConnector(node1, node2):
    """Creates degree one curve between node1 and node2 objects

    create_curveConnector("lf_tentA7_ctl1", "lf_tentA8_ctl1")
    """
    # Create connection curve, duplicate curve and parent under node1
    crv, crvShp = twoPointCurve(node1, node2)
    crvDup = cmds.duplicate(crv)
    crvDupShp = cmds.listRelatives(crvDup, shapes=True)[0]
    cmds.parent(crvDupShp, crv, r=True, s=True)
    cmds.delete(crvDup)
    cmds.setAttr("{}.inheritsTransform".format(crv), 0)
    cmds.parent(crv, node1)

    # Create leastSquaresModifier and decomposeMatrix nodes
    lsm = cmds.createNode("leastSquaresModifier", name="{}_lsm".format(node1))
    dcm1 = cmds.createNode("decomposeMatrix", name="{}_dcm".format(node1))
    dcm2 = cmds.createNode("decomposeMatrix", name="{}_dcm".format(node2))

    # Connect nodes and curveShapes
    cmds.connectAttr("{}.worldMatrix[0]".format(node1), "{}.inputMatrix".format(dcm1))
    cmds.connectAttr("{}.worldMatrix[0]".format(node2), "{}.inputMatrix".format(dcm2))

    cmds.connectAttr("{}.outputTranslate".format(dcm1), "{}.pointConstraint[0].pointPositionXYZ".format(lsm))
    cmds.connectAttr("{}.outputTranslate".format(dcm2), "{}.pointConstraint[1].pointPositionXYZ".format(lsm))
    cmds.connectAttr("{}.outputNurbsObject".format(lsm), "{}.create".format(crvShp))
    cmds.connectAttr("{}.worldMatrix[0]".format(crvShp), "{}.worldSpaceToObjectSpace".format(lsm))
    cmds.connectAttr("{}.worldSpace[0]".format(crvDupShp), "{}.inputNurbsObject".format(lsm))

    cmds.setAttr("{}.pointConstraint[0].pointConstraintU".format(lsm), 0)
    cmds.setAttr("{}.pointConstraint[1].pointConstraintU".format(lsm), 1)

    cmds.parent(crvShp, crvDupShp, node1, r=True, s=True)
    cmds.hide(crvDupShp)
    cmds.delete(crv)
    return crvShp


def twoPointCurve(node1, node2, degree=1):
    """Creates a degree 3 NURBS curve from two input objects """
    crvCmd = 'cmds.curve(degree=1, p=['
    startEndCtrls = [node1, node2]
    for ctrl in startEndCtrls:
        tfm = cmds.xform(ctrl, query=True, worldSpace=True, translation=True)
        crvCmd += ' ('
        for tfmItem in tfm:
            crvCmd += ' ' + str(tfmItem) + ','
        crvCmd += '),'

    crvCmd += '], k=[0,1])'
    crv = cmds.python(crvCmd)
    if degree > 1:
        cmds.rebuildCurve(crv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=degree, tol=0.01)
    crv = cmds.rename(crv, "{}_crv".format(node1))
    crvShp = cmds.listRelatives(crv, shapes=True)[0]
    return crv, crvShp


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


def getDistance(objA, objB):
    gObjA = cmds.xform(objA, q=True, t=True, ws=True)
    gObjB = cmds.xform(objB, q=True, t=True, ws=True)

    return sqrt(pow(gObjA[0] - gObjB[0], 2) + pow(gObjA[1] - gObjB[1], 2) + pow(gObjA[2] - gObjB[2], 2))


def add_tentacle_sine_deformer(curveNm, aimAxis=[0, -1, 0], upAxis=[1, 0, 0], cvIndexRemove=[0]):
    """Adds sine non-linear deformer to curve for tentacle motion

    Args:
        curveNm - Name of curve to add sine non-linear deformer to.
        aimAxis - Axis that sine handle will aim down the length of the tentacle
        upAxis - Axis that will serve as the up direction for the sine handle
        cvIndexRemove - List of cvs to remove from sine deformer

    add_tentacle_sine_deformer("lf_tentA_crv", aimAxis=[0,-1,0], upAxis=[1,0,0])
    add_tentacle_sine_deformer("lf_tentB_crv", aimAxis=[0,-1,0], upAxis=[1,0,0], cvIndexRemove=[0])
    """
    if cmds.objExists(curveNm):
        # Make sure curve is visible (otherwise sine deformer is not created properly)
        if not cmds.getAttr("{}.v".format(curveNm)):
            cmds.setAttr("{}.v".format(curveNm), 1)

        # Get curve info
        num_cvs = cmds.getAttr("{}.degree".format(curveNm)) + cmds.getAttr("{}.spans".format(curveNm))
        start_pt = "{}.cv[0]".format(curveNm)
        end_pt = "{}.cv[{}]".format(curveNm, num_cvs - 1)

        start_pos = cmds.xform(start_pt, q=True, ws=True, t=True)
        end_pos = cmds.xform(end_pt, q=True, ws=True, t=True)
        end_loc = cmds.spaceLocator()[0]
        dist = getDistance(start_pt, end_pt)
        cmds.setAttr("{}.translate".format(end_loc), end_pos[0], end_pos[1], end_pos[2])

        # Create sine deformer
        cmds.select(curveNm)
        sine_def = cmds.nonLinear(type="sine", highBound=0)
        sine_def[0] = cmds.rename(sine_def[0], "{}_sine_nl".format(curveNm))
        sine_tfm = cmds.rename(sine_def[1], "{}_sine_hdl".format(curveNm))

        # Position/orient sine deformer to curve
        cmds.setAttr("{}.translate".format(sine_tfm), start_pos[0], start_pos[1], start_pos[2])
        cmds.delete(cmds.aimConstraint(end_loc, sine_tfm, aim=aimAxis, u=upAxis, worldUpType="scene"))
        scale_val = cmds.getAttr("{}.scaleX".format(sine_tfm))
        sine_grp = cmds.duplicate(sine_tfm, po=True, name="{}_sine_grp".format(curveNm))
        cmds.parent(sine_tfm, sine_grp)
        cmds.setAttr("{}.scale".format(sine_grp[0]), dist, dist, dist)

        # Set sine deformer attrs
        cmds.setAttr("{}.dropoff".format(sine_def[0]), -1)
        cmds.setAttr("{}.amplitude".format(sine_def[0]), .5)
        #cmds.setAttr("{}.lowBound".format(sine_def[0]), (scale_val * -1))

        # Prune cvs from sine deformer if specified
        if cvIndexRemove:
            sine_set = cmds.listConnections("{}.message".format(sine_def[0]), s=False, d=True, type="objectSet")
            if sine_set:
                for cv in cvIndexRemove:
                    cmds.sets("{}.cv[{}]".format(curveNm, str(cv)), remove=sine_set[0])

        # Cleanup
        cmds.delete(end_loc)
        #cmds.hide(sine_tfm)
        cmds.setAttr("{}.template".format(sine_tfm), 1)

        return sine_def[0], sine_tfm, sine_grp

def add_tentacle_sine_attrs(prefix, control, sine_deformer, sine_tfm, twistAxis="y", master_control=None):
    """Adds anim attrs from sine_handle to control

    add_tentacle_sine_attrs("lf_tentBEnd_ctl", "lf_tentB_crv_sine_nl", "lf_tentB_crv_sine_hdl", master_control=None)
    """

    # all_on_off
    # all_amplitude
    # all_wavelength
    # all_offset

    if cmds.objExists(control):

        if not cmds.attributeQuery("_ALL_SINE_", node=control, exists=True):
            attrs_attributeSeparator(control, '_ALL_SINE_')

        if not cmds.attributeQuery("all_on_off", node=control, exists=True):
            cmds.addAttr(control, ln="all_on_off".format(prefix), dv=1, min=0, max=1)
            cmds.setAttr("{}.all_on_off".format(control, prefix), k=True, l=False)

        if not cmds.attributeQuery("all_amplitude", node=control, exists=True):
            cmds.addAttr(control, ln="all_amplitude".format(prefix), dv=0)
            cmds.setAttr("{}.all_amplitude".format(control, prefix), k=True, l=False)

        if not cmds.attributeQuery("all_wavelength", node=control, exists=True):
            cmds.addAttr(control, ln="all_wavelength".format(prefix), dv=1)
            cmds.setAttr("{}.all_wavelength".format(control, prefix), k=True, l=False)

        if not cmds.attributeQuery("all_offset", node=control, exists=True):
            cmds.addAttr(control, ln="all_offset".format(prefix), dv=0)
            cmds.setAttr("{}.all_offset".format(control, prefix), k=True, l=False)

        attrs_attributeSeparator(control, '_{}_SINE_'.format(prefix))

        # On/Off
        cmds.addAttr(control, ln="{}_on_off".format(prefix), dv=1, min=0, max=1)
        cmds.setAttr("{}.{}_on_off".format(control, prefix), k=True, l=False)
        on_off_mdn = cmds.createNode("multiplyDivide", name="{}_onoff_mdn".format(sine_tfm))
        cmds.connectAttr("{}.all_on_off".format(control, prefix), "{}.input1X".format(on_off_mdn))
        cmds.connectAttr("{}.{}_on_off".format(control, prefix), "{}.input2X".format(on_off_mdn))
        cmds.connectAttr("{}.outputX".format(on_off_mdn), "{}.v".format(sine_tfm))
        #cmds.connectAttr("{}.{}_on_off".format(control, prefix), "{}.v".format(sine_tfm))

        #pma_on_off = cmds.createNode("plusMinusAverage", name="{}_pma".format(sine_deformer))
        mdn_on_off = cmds.createNode("multiplyDivide", name="{}_mdn".format(sine_deformer))
        cmds.connectAttr("{}.{}_on_off".format(control, prefix), "{}.input1X".format(mdn_on_off))
        cmds.connectAttr("{}.all_on_off".format(control, prefix), "{}.input2X".format(mdn_on_off))
        cmds.connectAttr("{}.outputX".format(mdn_on_off), "{}.envelope".format(sine_deformer))
        #cmds.connectAttr("{}.{}_on_off".format(control, prefix), "{}.envelope".format(sine_deformer))

        # Amplitude
        cmds.addAttr(control, ln="{}_amplitude".format(prefix), dv=0)
        cmds.setAttr("{}.{}_amplitude".format(control, prefix), k=True, l=False)
        pma_amp = cmds.createNode("plusMinusAverage", name="{}_amp_pma".format(sine_deformer))
        cmds.connectAttr("{}.{}_amplitude".format(control, prefix), "{}.input1D[0]".format(pma_amp))
        cmds.connectAttr("{}.all_amplitude".format(control, prefix), "{}.input1D[1]".format(pma_amp))
        cmds.connectAttr("{}.output1D".format(pma_amp), "{}.amplitude".format(sine_deformer))
        #cmds.connectAttr("{}.{}_amplitude".format(control, prefix), "{}.amplitude".format(sine_deformer))

        # Wavelength
        cmds.addAttr(control, ln="{}_wavelength".format(prefix), dv=1)
        cmds.setAttr("{}.{}_wavelength".format(control, prefix), k=True, l=False)
        pma_wave = cmds.createNode("plusMinusAverage", name="{}_wave_pma".format(sine_deformer))
        cmds.connectAttr("{}.{}_wavelength".format(control, prefix), "{}.input1D[0]".format(pma_wave))
        cmds.connectAttr("{}.all_wavelength".format(control, prefix), "{}.input1D[1]".format(pma_wave))
        cmds.connectAttr("{}.output1D".format(pma_wave), "{}.wavelength".format(sine_deformer))
        #cmds.connectAttr("{}.{}_wavelength".format(control, prefix), "{}.wavelength".format(sine_deformer))

        # Offset
        cmds.addAttr(control, ln="{}_offset".format(prefix), dv=0)
        cmds.setAttr("{}.{}_offset".format(control, prefix), k=True, l=False)
        pma_off = cmds.createNode("plusMinusAverage", name="{}_offset_pma".format(sine_deformer))
        cmds.connectAttr("{}.{}_offset".format(control, prefix), "{}.input1D[0]".format(pma_off))
        cmds.connectAttr("{}.all_offset".format(control, prefix), "{}.input1D[1]".format(pma_off))
        cmds.connectAttr("{}.output1D".format(pma_off), "{}.offset".format(sine_deformer))
        #cmds.connectAttr("{}.{}_offset".format(control, prefix), "{}.offset".format(sine_deformer))

        # Twist rotation
        cmds.addAttr(control, ln="{}_twist_rot".format(prefix), dv=0)
        cmds.setAttr("{}.{}_twist_rot".format(control, prefix), k=True, l=False)
        cmds.connectAttr("{}.{}_twist_rot".format(control, prefix), "{}.r{}".format(sine_tfm, twistAxis))

        # Dropoff
        cmds.addAttr(control, ln="{}_dropoff".format(prefix), dv=1, min=-1, max=1)
        cmds.setAttr("{}.{}_dropoff".format(control, prefix), k=True, l=False)
        cmds.connectAttr("{}.{}_dropoff".format(control, prefix), "{}.dropoff".format(sine_deformer))

        # Low bound - normalize value going from control to deformer
        cmds.addAttr(control, ln="{}_end_range".format(prefix), dv=1, min=.001)
        cmds.setAttr("{}.{}_end_range".format(control, prefix), k=True, l=False)

        lb_val = cmds.getAttr("{}.lowBound".format(sine_deformer))
        lb_mdn = cmds.createNode("multiplyDivide", name="{}_mdn".format(sine_deformer))
        cmds.connectAttr("{}.{}_end_range".format(control, prefix), "{}.input1X".format(lb_mdn))
        cmds.setAttr("{}.input2X".format(lb_mdn), lb_val)
        cmds.connectAttr("{}.outputX".format(lb_mdn), "{}.lowBound".format(sine_deformer))

        return True
    else:
        print "{} does not exist!".format(control)

def addMessageAttribute(src, tgts, attrName):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        addMessageAttribute("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attrName, exists=True, node=src):
            cmds.addAttr(src, sn=attrName, at='message', m=True)

        i=0
        while i < len(tgts):
            idx = get_next_free_multi_index("{}.{}".format(src, attrName), i)
            cmds.connectAttr("%s.message" % (tgts[i]), "%s.%s[%s]" % (src, attrName, str(idx)), f=True)
            i=i+1

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise


def getMessageAttributeConnections(src, attrName):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        getMessageAttributeConnections("box_fk_ctrl", attrName="pivot_node")
    """
    try:
        if cmds.attributeQuery(attrName, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attrName))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attrName, src))
        raise


def get_next_free_multi_index(attr_name, start_index):
    '''Find the next unconnected multi index starting at the passed in index.'''
    # assume a max of 10 million connections
    while start_index < 10000000:
        if len(cmds.connectionInfo('{}[{}]'.format(attr_name, start_index), sfd=True) or []) == 0:
            return start_index
        start_index += 1

    # No connections means the first index is available
    return 0

'''
def add_tentacle_sine_attrs(control, sine_deformer, sine_tfm, twistAxis="y", master_control=None):
    """Adds anim attrs from sine_handle to control

    add_tentacle_sine_attrs("lf_tentBEnd_ctl", "lf_tentB_crv_sine_nl", "lf_tentB_crv_sine_hdl", master_control=None)
    """

    if cmds.objExists(control):
        attrs_attributeSeparator(control, 'SINE_MOTION')

        # On/Off
        cmds.addAttr(control, ln="on_off", dv=1, min=0, max=1)
        cmds.setAttr("{}.on_off".format(control), k=True, l=False)
        cmds.connectAttr("{}.on_off".format(control), "{}.envelope".format(sine_deformer))

        # Amplitude
        cmds.addAttr(control, ln="amplitude", dv=0)
        cmds.setAttr("{}.amplitude".format(control), k=True, l=False)
        cmds.connectAttr("{}.amplitude".format(control), "{}.amplitude".format(sine_deformer))

        # Wavelength
        cmds.addAttr(control, ln="wavelength", dv=2)
        cmds.setAttr("{}.wavelength".format(control), k=True, l=False)
        cmds.connectAttr("{}.wavelength".format(control), "{}.wavelength".format(sine_deformer))

        # Dropoff
        cmds.addAttr(control, ln="dropoff", dv=1, min=-1, max=1)
        cmds.setAttr("{}.dropoff".format(control), k=True, l=False)
        cmds.connectAttr("{}.dropoff".format(control), "{}.dropoff".format(sine_deformer))

        # Offset
        cmds.addAttr(control, ln="offset", dv=0)
        cmds.setAttr("{}.offset".format(control), k=True, l=False)
        cmds.connectAttr("{}.offset".format(control), "{}.offset".format(sine_deformer))

        # Twist rotation
        cmds.addAttr(control, ln="twist_rot", dv=0)
        cmds.setAttr("{}.twist_rot".format(control), k=True, l=False)
        cmds.connectAttr("{}.twist_rot".format(control), "{}.r{}".format(sine_tfm, twistAxis))

        # Low bound - normalize value going from control to deformer
        cmds.addAttr(control, ln="end_range", dv=1, min=.001)
        cmds.setAttr("{}.end_range".format(control), k=True, l=False)

        lb_val = cmds.getAttr("{}.lowBound".format(sine_deformer))
        lb_mdn = cmds.createNode("multiplyDivide", name="{}_mdn".format(sine_deformer))
        cmds.connectAttr("{}.end_range".format(control), "{}.input1X".format(lb_mdn))
        cmds.setAttr("{}.input2X".format(lb_mdn), lb_val)
        cmds.connectAttr("{}.outputX".format(lb_mdn), "{}.lowBound".format(sine_deformer))

        return True
    else:
        print "{} does not exist!".format(control)
'''

ARROW = {
        "p": [
            [
                0.0,
                0.0,
                0.0
            ],
            [
                -0.5837544798851013,
                0.0,
                -0.000548628275282681
            ],
            [
                0.0,
                0.0,
                1.010573387145996
            ],
            [
                0.5837544798851013,
                0.0,
                -0.000548628275282681
            ],
            [
                0.0,
                0.0,
                0.0
            ],
            [
                0.0,
                0.5837544798851013,
                -0.000548628275282681
            ],
            [
                0.0,
                0.0,
                1.010573387145996
            ],
            [
                0.0,
                -0.5837544798851013,
                -0.000548628275282681
            ],
            [
                0.0,
                0.0,
                0.0
            ]
        ],
        "knots": [
                    0.0,
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                    6.0,
                    7.0,
                    8.0
                ],
        "d": 1,
        "per": False,
        "name": "arrow"
}

