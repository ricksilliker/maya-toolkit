import maya.cmds as cmds
import maya.api.OpenMaya as om2

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)
DIRECTION = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def run(params, rig):
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
            oc = cmds.orientConstraint(a, orienter, mo=True)

        last_orienter = orienter
        i = i - 1

    handle, effector = cmds.ikHandle(sj=rig_joints[0], ee=rig_joints[-1], sol='ikSplineSolver', c=params['curve'].name(), ccv=False, pcv=False)
    cmds.hide(handle)

    clusters = cluster_curve(params['curve'].name(), prefix=params['baseName'])
    weights = get_weights(controls, clusters)
    for node, weight in reversed(zip(clusters, weights)):
        for target, weight_value in weight.items():
            cmds.parentConstraint(target, node, w=weight_value, mo=True)

    for pointer, orienter, target in zip(rig_joints, orienters, input_joints):
        pc = cmds.pointConstraint(pointer, target, mo=False)
        oc = cmds.orientConstraint(orienter, target, mo=True)
        for axs in ['X','Y','Z']:
            cmds.connectAttr('{}.scale{}'.format(pointer, axs), '{}.scale{}'.format(target, axs))
        if 'noXformGroup' in rig:
            cmds.parent(pc, oc, rig['noXformGroup'])

    organize_grp = cmds.createNode('transform', n='{}IkSpline_grp'.format(params['baseName']))
    if 'rigGroup' in rig:
        cmds.parent(organize_grp, rig['rigGroup'])
    cmds.parent(handle, organize_grp)
    cmds.parent(clusters, organize_grp)
    cmds.parent(rig_joints[0], organize_grp)
    cmds.parent(params['curve'].name(), organize_grp)
    cmds.hide(clusters)

    lib.attrs_attributeSeparator(controls[-1], '___')

    if params['stretchy']:
        axis = ['X', 'Y', 'Z'][params['axisDownBone']]
        stretchy_drivers = add_stretchy(params['curve'].name(), rig_joints, axis, controls[-1])
        cmds.parent(stretchy_drivers, organize_grp)

    if params['volume']:
        if params['stretchy']:
            axis = ['X', 'Y', 'Z']
            axisBone = ['X', 'Y', 'Z'][params['axisDownBone']]
            axis.remove(axisBone)
            axisVolume = axis
            add_volume_scale(params['curve'].name(), rig_joints, controls, controls[-1], scaleAxis=axisVolume)
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


    # Add line connections between controls
    lib.create_curveConnectFromList(controls)

    # Cleanup
    for ctl in controls:
        cmds.setAttr("{}.v".format(ctl), k=False, l=True)


def add_volume_scale(curve, rig_joints, controls, volumeControl, scaleAxis=['Y','Z']):
    cmds.addAttr(volumeControl, ln="volume", dv=1, min=0, max=1)
    cmds.setAttr("{}.volume".format(volumeControl), k=1, l=0)

    cmds.addAttr(volumeControl, ln="volumeMult", dv=1, min=0)
    cmds.setAttr("{}.volumeMult".format(volumeControl), k=1, l=0)

    crvShp = cmds.listRelatives(curve, shapes=True)
    crvArcLen = cmds.listConnections("{}.worldSpace[0]".format(crvShp[0]), s=False, d=True, type="curveInfo")
    crvNrml = cmds.listConnections("{}.arcLength".format(crvArcLen[0]), s=False, d=True, type="multiplyDivide")[0]

    for jnt, ctl in zip(rig_joints, controls):
        output_volume = cmds.createNode('plusMinusAverage', name='{}_volumeOutput_pma'.format(jnt))

        # Overall volume squash/stretch
        mdn = cmds.createNode('multiplyDivide', name='{}_volume_mdn'.format(jnt))
        cmds.setAttr('{}.input1X'.format(mdn), 1)
        cmds.setAttr('{}.operation'.format(mdn), 2)

        blend_volume_node = cmds.createNode('blendColors', n='{0}_blendVolume'.format(jnt))
        cmds.connectAttr('{}.outputX'.format(crvNrml), '{}.color1R'.format(blend_volume_node))
        cmds.setAttr('{}.color2R'.format(blend_volume_node), 1.0)
        cmds.connectAttr('{}.outputR'.format(blend_volume_node), '{}.input2X'.format(mdn))
        cmds.connectAttr("{}.volume".format(volumeControl), '{}.blender'.format(blend_volume_node))
        cmds.setAttr('{}.input3D[0].input3Dx'.format(output_volume), 1)
        cmds.setAttr('{}.input3D[0].input3Dy'.format(output_volume), 1)
        cmds.setAttr('{}.input3D[0].input3Dz'.format(output_volume), 1)
        for axs in scaleAxis:
            cmds.connectAttr('{}.outputX'.format(mdn), '{}.input3D[0].input3D{}'.format(output_volume, axs.lower()))

        # Control Scale - Connect each control's scale attrs to '{}.input3D[1].input3D{}'.format(output_volume)
        for ax in ['X','Y','Z']:
            cmds.connectAttr('{}.scale{}'.format(ctl, ax), '{}.input3D[1].input3D{}'.format(output_volume, ax.lower()))

        # Final output volume to jnt
        mdn_sum = cmds.createNode('multiplyDivide', name='{}_volumeSum_mdn'.format(ctl))
        cmds.connectAttr("{}.output3D".format(output_volume), '{}.input1'.format(mdn_sum))
        cmds.setAttr('{}.operation'.format(mdn_sum), 2)
        for ax in ['X', 'Y', 'Z']:
            cmds.setAttr('{}.input2{}'.format(mdn_sum, ax), 2)
        cmds.connectAttr("{}.output".format(mdn_sum), '{}.scale'.format(jnt))

        """ORIGINAL VOLUME
        mdn = cmds.createNode('multiplyDivide', name='{}_volume_mdn'.format(jnt))
        cmds.setAttr('{}.input1X'.format(mdn), 1)
        cmds.setAttr('{}.operation'.format(mdn), 2)

        blend_volume_node = cmds.createNode('blendColors', n='{0}_blendVolume'.format(jnt))
        cmds.connectAttr('{}.outputX'.format(crvNrml), '{}.color1R'.format(blend_volume_node))
        cmds.setAttr('{}.color2R'.format(blend_volume_node), 1.0)
        cmds.connectAttr('{}.outputR'.format(blend_volume_node), '{}.input2X'.format(mdn))
        cmds.connectAttr("{}.volume".format(volumeControl), '{}.blender'.format(blend_volume_node))

        for axs in scaleAxis:
            cmds.connectAttr('{}.outputX'.format(mdn), '{}.scale{}'.format(jnt, axs))
        """


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
    cmds.addAttr(stretchControl, ln="stretch", dv=1, min=0, max=1)
    cmds.setAttr("{}.stretch".format(stretchControl), k=1, l=0)

    curve_info_node = cmds.createNode('curveInfo', n='{0}_curveInfo'.format(curve))
    cmds.connectAttr('{}.worldSpace'.format(curve), '{}.inputCurve'.format(curve_info_node))

    normalize_scale_node = cmds.createNode('multiplyDivide', n='{0}_normalizeScale'.format(curve))
    cmds.setAttr('{}.input2X'.format(normalize_scale_node), cmds.getAttr('{}.arcLength'.format(curve_info_node)))
    cmds.setAttr('{}.operation'.format(normalize_scale_node), 2)
    cmds.connectAttr('{}.arcLength'.format(curve_info_node), '{}.input1X'.format(normalize_scale_node))

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

            stretch_factor_node = cmds.createNode('multiplyDivide', n='{0}_stretchFactor'.format(driver_node))
            cmds.setAttr('{}.operation'.format(stretch_factor_node), 2)
            cmds.connectAttr('{}.distance'.format(distance_node), '{}.input1X'.format(stretch_factor_node))
            cmds.connectAttr('{}.orig_length'.format(driver_node), '{}.input2X'.format(stretch_factor_node))

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