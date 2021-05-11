import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    LOG.debug('Running rig cleanup functions..')

    parentConstraints = params['parentConstraints']
    if parentConstraints:
        if 'noXformGroup' in rig:
            LOG.debug("Parenting constraints under {}".format(rig['noXformGroup']))
            parent_constraint_nodes(rig['noXformGroup'])

    cleanupTopNodes = params['cleanupTopNodes']
    if cleanupTopNodes:
        clean_top_nodes(rig['rig'])

    cleanupProxyNodes = params['cleanupProxyNodes']
    if cleanupProxyNodes:
        clean_proxy_nodes(rig['rig'])

    checkMaxVertSkinInfluences = params['checkMaxVertSkinInfluences']
    if checkMaxVertSkinInfluences:
        mesh_list = get_rig_meshes(rig['rig'], skip_orig=True)
        max_infs = params['maxSkinInfluencesPerVert']
        if mesh_list:
            colorVertsExceedingMaxInfs(mesh_list, max_infs=max_infs, color=True)
    """
    deleteEndJoints = params['pruneNonSkinnedEndJoints']
    if deleteEndJoints:
        skel_grp = rig['skeletonGroup']
        if skel_grp:
            delete_endJointsFromHierarchy(topNodeList=[skel_grp], skipConnected=True, skipSkinned=True)
    """
    curveArnoldAttrRemoval = params['curveArnoldAttrRemoval']
    if curveArnoldAttrRemoval:
        clean_arnold_attr_nodes(rig['rig'])

    skeletonVisibilityFix = params['skeletonVisibilityFix']
    if skeletonVisibilityFix:
        fix_skeleton_visibility()

    rigSkeletonVisibilityFix = params['rigSkeletonVisibilityFix']
    if rigSkeletonVisibilityFix:
        fix_rig_skeleton_visibility()

    lockHideControlVisibility = params['lockHideCtlVisibility']
    if lockHideControlVisibility:
        lock_hide_ctl_visibility()

    createBindPose = params['createBindPose']
    if createBindPose:
        skel_grp = rig['skeletonGroup']
        asset_name = rig['asset']
        create_skeleton_bind_pose(asset_name, skel_grp)


def create_skeleton_bind_pose(asset_name, skeleton_top_node):
    """Creates a single skeleton bind pose for rig in scene

    create_skeleton_bind_pose('Kayah', 'skeleton')
    """
    # Delete existing dagPoses
    dag_poses = cmds.ls(type='dagPose')
    if dag_poses:  cmds.delete(dag_poses)

    # Add new bind pose
    jnts = cmds.listRelatives(skeleton_top_node, ad=True, type='joint')
    if jnts:
        cmds.select(jnts)
        bind_pose = cmds.dagPose(name='{}_bindPose'.format(asset_name), bindPose=True, save=True)
        return bind_pose


def lock_and_hide():
    pass


def hide_vis_attrs(top_node, exception_list=[]):
    """Hides vis attrs on all nodes except top node

    hide_vis_attrs('ORI_CHA_Rhino_Baby_rig', exception_list=[])
    """
    children = cmds.listRelatives(top_node, ad=True)
    if children:
        for child in children:
            if cmds.attributeQuery('visibility', node=child, exists=True):
                cmds.setAttr('{}.visibility'.format(child), lock=True, keyable=False)
                print "processing: {}".format(child)


def clean_top_nodes(rig_node):
    """Deletes any top node that is not the rig or default cameras"""
    scene_default_cams = ["persp", "top", "front", "side"]
    scene_top_nodes = [x for x in cmds.ls("|*") if x not in scene_default_cams]
    scene_top_nodes.remove(rig_node)
    if scene_top_nodes:
        cmds.delete(scene_top_nodes)
        LOG.debug("Deleted non-rig nodes: {nodes}".format(nodes=''.join(scene_top_nodes)))


def clean_proxy_nodes(rig_top_node):
    """Deletes any proxy network nodes left in scene after rig build"""
    proxy_nodes = cmds.ls('proxy_*', type='network')

    if proxy_nodes:
        cmds.delete(proxy_nodes)
        LOG.debug("Deleted proxy nodes: {nodes}".format(nodes=''.join(proxy_nodes)))

    if cmds.objExists('proxy_nodes'):
        print 'Deleting set'
        cmds.delete('proxy_nodes')


def clean_arnold_attr_nodes(rig_node):
    """Lock and Hide any arnold attributes on shapenodes"""
    a = cmds.listRelatives(rig_node, ad=True, f=True)
    if a:
        for shape in a:
            if cmds.attributeQuery('rcurve', n=shape, ex=True):
                lnhattr(shape)

def lnhattr(shape):
    """Lock and Hide any arnold attributes on shapenodes"""

    arnold_nodes = ('rcurve', 'cwdth', 'srate', 'ai_curve_shaderr', 'ai_curve_shaderg', 'ai_curve_shaderb')
    for ar in arnold_nodes:
        cmds.setAttr(shape + "." + ar, l=True, k=False, cb=False)

def parent_constraint_nodes(parent_node):
    """Parents all constraints under parentNode"""
    try:
        # Get all constraints and subtract constraints that are already parented
        cns = []
        cns_all = cmds.ls(type="constraint")
        cns_noXfrm = cmds.listRelatives(parent_node, children=True)

        if cns_noXfrm:
            cns = [x for x in cns_all if x not in cns_noXfrm]
        else:
            cns = cns_all

        if cns and cmds.objExists(parent_node):
            cmds.parent(cns, parent_node)
            LOG.debug("Parented constraints under {}".format(parent_node))
    except:
        LOG.warning("Unable to parent constraints check if {} exists".format(parent_node))


def get_rig_meshes(rig_top_node, skip_orig=True):
    """Returns all meshes under rig top node"""
    mshs = cmds.listRelatives(rig_top_node, ad=True, type="mesh")
    if mshs:
        if skip_orig:
            for msh in mshs:
                if "Orig" in msh:
                    mshs.remove(msh)
        return mshs


def getSkinCluster(src):
    """
    Given a source (geometry or skincluster) return skincluster.
    """

    if cmds.nodeType(src) == "skinCluster":
        srcSkin = src
    else:
        srcSkin = mel.eval('findRelatedSkinCluster("' + src + '")')

    return srcSkin


def colorVertsExceedingMaxInfs(mesh_list, max_infs=8, color=True):
    """
    meshes = ["Octopus_LOD0_mesh"]
    colorVertsExceedingMaxInfs(meshes, max_infs=8)
    """
    vert_list = list()
    for mesh in mesh_list:
        vc = (cmds.polyEvaluate(mesh, v=1)) + 1
        sc = getSkinCluster(mesh)

        if sc:
            for i in range(1, vc):
                vtx = "%s.vtx[%s]" % (mesh, i)
                vtx_jnts = cmds.skinPercent(sc, vtx, ignoreBelow=.001, q=1, t=None)
                if vtx_jnts:
                    if len(vtx_jnts) > max_infs:
                        vert_list.append(vtx)

    if vert_list:
        cmds.select(vert_list)
        cmds.sets(name="Vertices_Exceeding_Max_Skin_Influences")
        LOG.warning("WARNING: Meshes in scene have vertices with more than {} influences!".format(str(max_infs)))

        if color:
            cmds.polyColorPerVertex(rgb=(1, 0, 0), cdo=1)
            cmds.select(vert_list)
    else:
        LOG.info("All meshes in scene are within max skin influence per vertex range of {}".format(str(max_infs)))
        
        
def delete_endJointsFromHierarchy(topNodeList=[], skipConnected=True, skipSkinned=True):
    """Find and delete all end joints in hierarchy found beneath topNode. You can have it skip joints with connections
    or skin influence

    Args:
        topNodeList:  Top node whose children will be checked for end joints to prune.
        skipConnected:  If true, if an end joint is connected, do not delete it.
        skipSkinned:  If true, if an end joint is a skin influence, do not delete it.

    Returns:
        True

    Example:
        delete_endJointsFromHierarchy(topNodeList=['skeleton'])
    """
    for topNode in topNodeList:
        endJnts = []
        jntsToDelete = []
        skinnedJoints = []
        connectedJoints = []

        jntList = cmds.listRelatives(topNode, ad=True, type='joint')
        if jntList:
            scNodes = cmds.ls(type='skinCluster')
            for jnt in jntList:
                hasChild = cmds.listRelatives(jnt, children=True)
                if not hasChild:
                    if not 'root' or not 'Root' in cmds.listRelatives(jnt, parent=True)[0]:

                        # Check if joint is a skinCluster influence
                        if not skipSkinned:
                            if scNodes:
                                for sc in scNodes:
                                    skinInf = skinCluster.isSkinInfluence(sc, influence=jnt)
                                    if skinInf:
                                        skinnedJoints.append(jnt)

                        # Check if joint is connected
                        if not skipConnected:
                            for attr in cmds.listAttr(jnt, keyable=True):
                                cxns = cmds.listConnections('%s.%s' % (jnt, attr))
                                if cxns:
                                    connectedJoints.append(jnt)

                        endJnts.append(jnt)

            skinnedJoints = list(set(skinnedJoints))
            connectedJoints = list(set(connectedJoints))
            skipJoints = list(set(skinnedJoints + connectedJoints))
            jntsToDelete = list(set(endJnts).difference(skipJoints))

        if jntsToDelete:
            cmds.delete(jntsToDelete)
            LOG.info('Deleted end joints %s' % jntsToDelete)
            return True

def fix_skeleton_visibility():
    """
    Verify drawing override is turned off on COG joint
    """
    if cmds.objExists('cn_cog_jnt'):
        LOG.info('Cog Joint found, toggling display type')
        if cmds.objExists('jointLayer'):
            LOG.info('Delete jointLayer')
            cmds.delete('jointLayer')
        cmds.setAttr('cn_cog_jnt' + '.overrideEnabled', 0)
    else:
        LOG.info('No COG Joint found skipping this step')

def fix_rig_skeleton_visibility():
    """
    Toggle drawStyle on rig joints
    """
    LOG.info('Toggling drawStyle for joints under Rig group')
    rig_joints = cmds.listRelatives('rig', ad=True, type='joint')
    if rig_joints:
        for rig_jnt in rig_joints:
            cmds.setAttr(rig_jnt + '.drawStyle', 2)

def lock_hide_ctl_visibility():
    """
    Locks & Hides visibility of controls in the rig
    """
    LOG.info('Locking and Hiding Controls Visibility Attribute')
    ctls = cmds.ls('*_ctl*')
    ctls = [str(r) for r in ctls]
    for ctl in ctls:
        if "transform" in cmds.nodeType(str(ctl)):
            cmds.setAttr(str(ctl) + '.v', l=True, k=False, cb=False)