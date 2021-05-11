import logging
LOG = logging.getLogger(__name__)

import re
import json

from Qt import QtGui, QtWidgets, QtCore
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel




def toList(input):
    """
    takes input and returns it as a list
    """

    if isinstance( input, list ):
        return input

    elif isinstance( input, tuple ):
        return list(input)

    return [input]
	
	
def getSkinCluster(src):
    """
    Given a source (geometry or skincluster) return skincluster.
    """

    if cmds.nodeType(src) == "skinCluster":
        srcSkin = src
    else:
        srcSkin = mel.eval('findRelatedSkinCluster("' + src + '")')

    return srcSkin
	
	
def create(geom, infs, name=None, proxyJnts=True, nw=2, bm=0, sm=0, mi=4):
    infs = toList(infs)

    if not name:
        name = geom + '_skinCluster'

    if not cmds.objExists(geom):
        print('nodecast.createSkinCluster: could not find mesh: "' + geom + '", skipping...')
        return
    infsDup = []
    for inf in infs:
        if not cmds.objExists(inf) and proxyJnts:
            # create a proxy influence so we can still apply weights
            print('nodecast.createSkinCluster: could not find influence: "' + inf + '", creating a proxy...')
            if not cmds.objExists(PROXYGRP):
                cmds.createNode('transform', n=PROXYGRP)
            infShortName = inf.split('|')[-1]
            cmds.select(PROXYGRP)
            infName = cmds.joint(n=infShortName)
            infsDup.append(infName)
        else:
            infsDup.append(inf)

    skin = cmds.skinCluster(infsDup, geom, n=name, tsb=True, lw=False, nw=nw, bm=bm, sm=sm, mi=mi)[0]

    return skin
	
	
def xfer(srcGeom, dstGeom, smooth=False, uv=False, rui=False):
    srcSkin = mel.eval('findRelatedSkinCluster("' + srcGeom + '")')
    if cmds.objExists(srcSkin):
        srcInfs = cmds.skinCluster(srcSkin, q=True, inf=True)
        dstSkin = mel.eval('findRelatedSkinCluster("' + dstGeom + '")')
        if dstSkin:
            cmds.delete(dstSkin)
        dstSkin = cmds.skinCluster(srcInfs, dstGeom, n=dstGeom + '_skinCluster', tsb=True)[0]
        
        cmds.copySkinWeights(ss=srcSkin, ds=dstSkin, sa='closestPoint', ia='oneToOne', nm=True, sm=smooth)

        cmds.connectAttr(srcSkin + '.skinningMethod', dstSkin + '.skinningMethod', f=True)
        cmds.disconnectAttr(srcSkin + '.skinningMethod', dstSkin + '.skinningMethod')

        return (dstSkin)
    else:

        return (None)
	
	
def exportSkinWeight(exportPath, meshes, namespace=False):
    '''
    Args:
        exportPath: The file path where a json file is saved.
        meshes: A list of mesh nodes.
        namespace: True to export with namespace. False to export without namespace.

    Returns: True if export succeeds. False if export fails.
    '''
    data = {}
    if not meshes:
        LOG.error('Meshes input {0} is not valid.'.format(meshes))
        return False

    for mesh in meshes:
        skinCluster = getSkinCluster(mesh)
        skinNorm = cmds.getAttr('%s.normalizeWeights' % skinCluster)

        # get the MFnSkinCluster for clusterName
        selList = om.MSelectionList()
        selList.add(skinCluster)
        clusterNode = om.MObject()
        selList.getDependNode(0, clusterNode)
        skinFn = oma.MFnSkinCluster(clusterNode)

        # get the MDagPath for all influence
        infDags = om.MDagPathArray()
        skinFn.influenceObjects(infDags)

        # {
        #     "mesh_name": {
        #         "weights": {
        #             "vert id": {
        #                 "influence id": weight,
        #                 "influence id": weight
        #             }
        #         },
        #         "infs": [inf1, inf2, inf3, inf4, ...],
        #         "skinCluster": skinCluster_name
        #     }
        # }

        infIds = {}
        infs = []
        unique = True
        for i in xrange(infDags.length()):
            infPath = infDags[i].partialPathName()
            if '|' in infPath:
                LOG.warning('Influence of {}: "{}" is not have a unique name.'.format(mesh, infDags[i].fullPathName()))
                unique = False
            infId = int(skinFn.indexForInfluenceObject(infDags[i]))
            infIds[infId] = i
            infs.append(infPath)
        if not unique:
            LOG.warning(
                '{} skincluster export is skipped. Please make sure all influence names are unique'.format(mesh))
            continue

        # get the MPlug for the weightList and weights attributes
        wlPlug = skinFn.findPlug('weightList')
        wPlug = skinFn.findPlug('weights')
        wlAttr = wlPlug.attribute()
        wAttr = wPlug.attribute()
        wInfIds = om.MIntArray()

        # progressBar visualization
        total = wlPlug.numElements()
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMinimumSize(QtCore.QSize(450, 40))
        progressBar.setMinimum(1)
        progressBar.setMaximum(total)
        progressBar.setWindowTitle('Exporting skincluster: {}'.format(mesh))
        progressBar.show()
        completed = 0

        weights = {}
        for vId in xrange(wlPlug.numElements()):
            vWeights = {}
            # tell the weights attribute which vertex id it represents
            wPlug.selectAncestorLogicalIndex(vId, wlAttr)

            # get the indice of all non-zero weights for this vert
            wPlug.getExistingArrayAttributeIndices(wInfIds)

            # create a copy of the current wPlug
            infPlug = om.MPlug(wPlug)

            completed += 1
            progressBar.setValue(completed)
            for infId in wInfIds:
                # tell the infPlug it represents the current influence id
                infPlug.selectAncestorLogicalIndex(infId, wAttr)

                # add this influence and its weight to this verts weights
                try:
                    vWeights[infIds[infId]] = infPlug.asDouble()
                except KeyError:
                    # assumes a removed influence
                    pass
            weights[vId] = vWeights

        if namespace:
            meshName = mesh
        else:
            meshName = mesh.split(':')[-1]

        data[meshName] = {'weights': weights, 'infs': infs, 'skinCluster': skinCluster, 'nw': skinNorm}

    with open(exportPath, 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
            LOG.info('Exported skin weights for mesh {0}.'.format(meshes))
            return True
        except:
            LOG.error('Unable to export skinWeight data to {0}.'.format(exportPath))
            return False


def importSkinWeight(importPath, meshes, namespace=False):
    '''Import skinWeight from a json file, to a list of meshes.
    To a whole mesh, or selected vertices.

    Args:
        filepath: The file path where a json file is loaded.
        meshes: A list of mesh nodes. If [], import all available meshes.
        namespace: True to respect imported namespace data. False to ignore any namespaces.

    Returns: True if import succeeds. False if import fails.
    '''
    with open(importPath) as infile:
        try:
            data = json.load(infile)
            LOG.info('Loaded skinWeight data from {0}.'.format(importPath))
        except:
            LOG.error('Unable to load skinWeight data from {0}.'.format(importPath))
            return False

    if not meshes:
        meshes = data.keys()

    for mesh in meshes:
        selectedIndice = []
        selectedVerts = [v.split('.vtx')[-1] for v in cmds.ls(sl=1, fl=1) if (('.vtx' in v) and (mesh in v))]
        for v in selectedVerts:
            id = re.findall('\\d+', v)[0]
            selectedIndice.append(id)

        if namespace:
            if not (mesh in data):
                LOG.warning('Unable to find mesh data for "{0}"'.format(mesh))
                continue
            meshName = mesh
        else:
            shortName = mesh.split(':')[-1]
            meshName = ''
            for m in data.keys():
                if m.split(':')[-1] == shortName:
                    meshName = m
            if not meshName:
                LOG.warning('Unable to find mesh data for "{0}"'.format(shortName))
                continue

        # if mesh is not in current scene, skip
        if not cmds.objExists(meshName):
            continue

        weights = data[meshName]['weights']
        infs = data[meshName]['infs']
        skinClusterName = data[meshName]['skinCluster']
        skinNorm = data[meshName]['nw']

        if cmds.polyEvaluate(mesh, v=1) != len(weights.keys()):
            LOG.warning('Mesh "{0}": Vertex number does not match with the imported skinCluster "{1}"'.format(
                mesh, skinClusterName))

        # progressBar visualization
        total = len(weights.items())
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMinimumSize(QtCore.QSize(450, 40))
        progressBar.setMinimum(1)
        progressBar.setMaximum(total)
        progressBar.setWindowTitle('Importing skincluster: {}'.format(mesh))
        progressBar.show()
        completed = 0

        # vertices selection
        if selectedIndice:
            # get skinCluster
            currentName = getSkinCluster(mesh)
            # check if skinCluster exists
            if not currentName:
                LOG.error('Mesh "{0}": SkinCluster missing selected vertices'.format(mesh))
                return False
            # check the name of skinCluster
            elif currentName != skinClusterName:
                LOG.warning(
                    'SkinCluster "{0}": Name does not match with the imported skinCluster "{1}"'.format(currentName,
                                                                                                        skinClusterName))

            # check the number of influences
            currentInfs = cmds.skinCluster(currentName, q=1, inf=1)
            if len(currentInfs) != len(infs):
                LOG.warning(
                    'SkinCluster "{0}": Influence number does not match with the imported skinCluster "{1}"'.format(
                        currentName, skinClusterName))

            # unlock influences used by skincluster
            for inf in infs:
                if not cmds.objExists(inf):
                    LOG.warning('Unable to find influence "{0}"]'.format(inf))
                    continue
                cmds.setAttr('%s.liw' % inf, 0)

            for vertId in selectedIndice:
                if not (vertId in weights):
                    LOG.info('Unable to find weight data for {0}.vtx[{1}]'.format(mesh, vertId))
                    continue
                    # TODO
                    # deal with vertices with missing weight data: missing data for vertId
                    # currently acting awkward
                weightData = weights[vertId]
                wlAttr = '%s.weightList[%s]' % (currentName, vertId)
                completed += 1
                progressBar.setValue(completed)
                for infId, infValue in weightData.items():
                    wAttr = '.weights[%s]' % infId
                    cmds.setAttr(wlAttr + wAttr, infValue)
            return True

        # get skinCluster
        if getSkinCluster(mesh):
            cmds.delete(getSkinCluster(mesh))
        create(mesh, infs, name=skinClusterName, nw=skinNorm)

        # normalize needs turned off for the prune to work
        if skinNorm != 0:
            cmds.setAttr('%s.normalizeWeights' % skinClusterName, 0)
        try:
            cmds.skinPercent(skinClusterName, mesh, nrm=False, prw=100)
        except:
            LOG.info("Error on %s" % skinClusterName)
            raise

        # restore normalize setting
        cmds.setAttr('%s.normalizeWeights' % skinClusterName, skinNorm)

        # apply weights
        for vertId, weightData in weights.items():
            wlAttr = '%s.weightList[%s]' % (skinClusterName, vertId)
            completed += 1
            progressBar.setValue(completed)
            for infId, infValue in weightData.items():
                wAttr = '.weights[%s]' % infId
                cmds.setAttr(wlAttr + wAttr, infValue)

    return True