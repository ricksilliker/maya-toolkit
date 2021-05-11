"""
    Various python functions for editing rig LODs.

    # lodTools Shelf:
        WeightJumper
        InfluenceChecker
        PruneLowestInfluenceOnSelectedVertices
        PruneSmallWeights
        LockUnlockSkinInfluences
        Return Number of Skin Influences
        Normalize Skin Weights
        SmoothSkinWeightsBrush
        ngSkinTools?

    # Launch InfluenceChecker ui:
    from rig_utils import lod
    lod.influenceCheckerUI()

    # Launch Component Editor
    mel.eval("ComponentEditor;")

"""

import logging
LOG = logging.getLogger(__name__)

import maya.cmds as cmds
import maya.mel as mel

from maya import OpenMaya as om
import maya.OpenMayaAnim as omAnim


def influenceCheckerUI():
    WinName = ("InfluenceChecker")
    if (cmds.window(WinName, ex=1)):
        cmds.deleteUI(WinName)

    cmds.window(WinName, w=200, s=0)
    cmds.columnLayout()
    cmds.rowColumnLayout(nc=1)
    cmds.setParent('..')
    cmds.separator(style='in', w=200)
    cmds.rowColumnLayout(nc=2)
    cmds.text('Max Number of Influences')
    cmds.intField('maxcountfield', min=1, max=99, v=8, w=70)
    cmds.setParent('..')
    cmds.rowColumnLayout(nc=3)
    cmds.separator(style='in', w=30)
    cmds.button(l='Show Over Max Influences', c=DoIt)
    cmds.separator(style='in', w=30)

    cmds.separator(style='in')
    cmds.separator(style='in')
    cmds.separator(style='in')

    cmds.separator(style='out', w=30)
    cmds.button(l='Remove Color', c=RemoveColor)
    cmds.separator(style='out', w=30)

    cmds.separator(style='out', w=30)
    cmds.separator(style='out', w=30)
    cmds.separator(style='out', w=30)

    cmds.separator(style='out', w=30)
    cmds.button(l='Prune Weights', c=pruneWeights)
    cmds.separator(style='out', w=30)

    cmds.showWindow(WinName)


ColorMe = []
Skin = []


def DoIt(*args):
    global ColorMe
    ColorMe = []
    global Skin
    Skin = []

    MaxCount = cmds.intField('maxcountfield', q=1, v=1)

    selected = cmds.ls(sl=1)
    if cmds.objExists('polyColorPerVertex*'):
        selectNode = cmds.select('polyColorPerVertex*')
        cmds.delete()

    for sel in selected:
        VertCount = cmds.polyEvaluate(sel, v=1)
        VertCountAdded = VertCount + 1

        # get attached skin cluster
        Skin = cmds.listHistory(sel, il=1)[1]
        print Skin

        for i in range(1, VertCountAdded):
            vertexName = "%s.vtx[%s]" % (sel, i)

            vertJoints = cmds.skinPercent(Skin, vertexName,
                                          ignoreBelow=.001, q=1, t=None)
            if len(vertJoints) > MaxCount:
                ColorMe.append(vertexName)

        # print ColorMe
        if len(ColorMe) <= 0:
            print "None to color, Good Job"
        else:
            cmds.select(ColorMe)
            cmds.polyColorPerVertex(rgb=(1, 0, 0), cdo=1)
            #cmds.select(cl=1)
            cmds.select(ColorMe)
            print "Color has been applied"


def RemoveColor(*args):
    try:
        sel = cmds.ls(selection=True)
        if sel:
            selectNode = cmds.select('polyColorPerVertex*')
            cmds.delete()
            if sel:
                cmds.select(sel)
            print "Color was removed"
        else:
            print "Select mesh to remove vertex color from!"
    except ValueError:
        cmds.error("Looks like there isnt any color to remove")


def pruneWeights(*args):
    global ColorMe
    # print ColorMe
    sel = cmds.ls(sl=1)
    MaxCount = cmds.intField('maxcountfield', q=1, v=1)

    if len(ColorMe) >= 0:
        for ea in ColorMe:
            vertexName = ea
            selected = cmds.ls(sl=1)
            influenceJoints = cmds.skinPercent(Skin, vertexName, q=1,
                                               t=None, ignoreBelow=0.00000000001)
            influenceValue1 = cmds.skinPercent(Skin, vertexName, q=1, v=1,
                                               ignoreBelow=0.00000000001)
            influenceValue2 = sorted(influenceValue1, reverse=True)
            lowestValue = influenceValue2[MaxCount - 1]
            cmds.skinPercent(Skin, vertexName, prw=lowestValue)
        print "Weights Have been pruned on necessary verts"
    else:
        print '''either run the "Show Over Max Influences button,
			or there is nothing to prune'''


def lockSkinInfluences():
    src = cmds.ls(selection=True)
    if src:
        infs = getInfluences(src[0])
        if infs:
            for inf in infs:
                cmds.setAttr("{}.liw".format(inf), 1)


def getInfluences(src):
    """
    Given a source (geometry or skincluster) return the influences for it.
    """
    srcSkin = getSkinCluster(src)

    if cmds.objExists(srcSkin):
        return cmds.skinCluster(srcSkin, q=1, inf=1)
    else:
        return None


def getSkinCluster(src):
    """
    Given a source (geometry or skincluster) return skincluster.
    """
    if cmds.nodeType(src) == "skinCluster":
        srcSkin = src
    else:
        srcSkin = mel.eval('findRelatedSkinCluster("' + src + '")')
    return srcSkin


def getSkinPercentWeights(vtx, skin, min_weight=0.0001):
    cmd = 'skinPercent  -ib %f -q -t %s %s'
    cmd = cmd % (min_weight, skin, vtx)
    vtxInf = mel.eval(cmd)
    vtxWeights = cmds.skinPercent(skin, vtx, ib=min_weight, q=1, v=1)
    dictWeights = dict()
    for i in range(len(vtxInf)):
        dictWeights[vtxInf[i]] = vtxWeights[i]
    return (dictWeights)


def returnHighLowSkinInfs(vtx, skin):
    """Returns influences with highest and lowest weight for vertex
    pruneLowestInf("Bellum_mesh.vtx[10658]", "Bellum_mesh_skinCluster")
    """
    wts_dict = getSkinPercentWeights(vtx, skin)
    hiInf = ""
    lowInf = ""
    hiWt = 0.0
    lowWt = 1.0
    for inf, wt in wts_dict.iteritems():
        if wt > hiWt:
            hiWt = wt
            hiInf = inf
        if wt < lowWt:
            lowWt = wt
            lowInf = inf
    return lowInf, hiInf, skin


def pruneLowestInfsOnSelected():
    """Loops through selected vertices and moves smallest weighted
    skin influence to highest (used for reducing the number of infs per vertex)
    """
    selVerts = cmds.ls(selection=True, flatten=True)
    if selVerts:
        for vtx in selVerts:
            meshNm = vtx.split(".")[0]
            sc = getSkinCluster(meshNm)
            if sc:
                cmds.select(clear=True)
                cmds.select(vtx)

                hiLowInfs = returnHighLowSkinInfs(vtx, sc)
                weightJumper(hiLowInfs[2], jointSource=hiLowInfs[0], jointTarget=hiLowInfs[0], selVerts=True, percent=100)
                cmds.skinPercent(hiLowInfs[2], normalize=True)
                LOG.info("Pruned lowest inf {} to {}".format(hiLowInfs[0], hiLowInfs[1]))
        cmds.select(selVerts)


def weightJumper(skin, jointSource="", jointTarget="", selVerts=False, percent=100):
    """Transfers skin weighting from jointSource to jointTarget

    Args:
        skin: The skinCluster to affect.
        jointSource: Influence currently holding the weight values.
        jointTarget: Influence where the weights will be transferred (added) to.
        selVerts: Boolean for transferring entire influence or only affecting selected vertices.
        percent: Int 0 to 100 for the percentage of weights to transfer.
    Returns:
        None
    """
    if not jointSource:
        jointSource = cmds.ls(sl=1)[0]
    if not jointTarget:
        jointTarget = cmds.ls(sl=1)[1]

    normalVal = cmds.getAttr("%s.normalizeWeights" % skin)
    cmds.setAttr("%s.normalizeWeights" % skin, 0)

    # Query skinCluster object
    selectionList = om.MSelectionList()
    selectionList.add(skin)
    node = om.MObject()
    selectionList.getDependNode(0, node)
    skinClusterNode = omAnim.MFnSkinCluster(node)

    # Use magic to find the components
    mfnSet = om.MFnSet(skinClusterNode.deformerSet())
    mfnSetMembers = om.MSelectionList()
    mfnSet.getMembers(mfnSetMembers, False)
    dgPath = om.MDagPath()
    components = om.MObject()
    mfnSetMembers.getDagPath(0, dgPath, components)

    if selVerts:
        # Get selected verts
        vertSelList = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(vertSelList)
        selection_iter = om.MItSelectionList(vertSelList, om.MFn.kMeshVertComponent)
        selection_DagPath = om.MDagPath()
        componentSel = om.MObject()

        selection_iter.getDagPath(selection_DagPath, componentSel)
        finalComponents = componentSel
    else:
        finalComponents = components

    transPercent = percent * .01
    keepPercent = (100 - percent) * .01

    # Get the number of influences that affect the skinCluster
    infs = om.MDagPathArray()
    numInfs = skinClusterNode.influenceObjects(infs)

    # Get dagPath for the skinCluster at index 0
    skinPath = om.MDagPath()
    index = 0
    skinClusterNode.indexForOutputConnection(index)
    skinClusterNode.getPathAtIndex(index, skinPath)

    # Find joints
    myCountIndex = 0
    myWinIndex = 0
    for counter in range(0, numInfs, 1):
        infName = infs[counter].partialPathName()
        if infName == jointSource:
            myCountIndex = counter
        elif infName == jointTarget:
            myWinIndex = counter

    # Find current weights
    myInflArray = om.MIntArray(1, myWinIndex)
    myOtherInflArray = om.MIntArray(1, myCountIndex)

    jointSourceWeights = om.MDoubleArray()
    skinClusterNode.getWeights(skinPath, finalComponents, myOtherInflArray, jointSourceWeights)

    jointDestWeights = om.MDoubleArray()
    skinClusterNode.getWeights(skinPath, finalComponents, myInflArray, jointDestWeights)

    jointTargetFinalWeights = om.MDoubleArray(len(jointDestWeights))
    bigOldWeightList = [(x * transPercent) + y for x, y in zip(jointSourceWeights, jointDestWeights)]

    for i in xrange(len(jointDestWeights)):
        jointTargetFinalWeights.set(bigOldWeightList[i], i)

    jointSourceNewWeights = om.MDoubleArray(len(jointDestWeights))
    if percent != 100:
        keepWeightList = [x * keepPercent for x in jointSourceWeights]
        for i in xrange(len(jointDestWeights)):
            jointSourceNewWeights.set(keepWeightList[i], i)

    # Set new weights
    skinClusterNode.setWeights(skinPath, finalComponents, myInflArray, jointTargetFinalWeights, False)
    skinClusterNode.setWeights(skinPath, finalComponents, myOtherInflArray, jointSourceNewWeights, False)

    cmds.setAttr("%s.normalizeWeights" % skin, normalVal) 