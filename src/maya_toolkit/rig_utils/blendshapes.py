import logging
LOG = logging.getLogger(__name__)
import os

import maya.cmds as cmds
import maya.mel as mel


def importBlendshape(geometry, filename=''):
    """ Imports blendshape deformer (used for scripted rig builds)

    Args:
        geometry:  Name of object to import blendshape to
        filename:  Name of .shp blendshape data file

    Returns:
        File path of imported blendshape file.
    Example:
        importBlendshape('ray_cn_body', filename='deform/blendshapes/ray_cn_body__ray_cn_body_bs.shp')
    """
    projDir = cmds.workspace(query=True, rd=True)
    blendshapesDir = '%s/%s' % (projDir, filename)
    if not '.shp' in blendshapesDir:
        blendshapesDir = '%s.shp' % blendshapesDir

    if not os.path.exists(blendshapesDir):
        LOG.error('Blendshape file does not exist...' % filename)
        return

    else:
        # Do blendshapes import
        shpDir = os.path.dirname(os.path.abspath(blendshapesDir)) + "\\"
        shpDir = shpDir.replace("\\", "/")
        shpFullFilename = blendshapesDir.split('/')[-1]
        shpFilename = shpFullFilename.split('.')[0]
        bsName = shpFilename.split('__')[1]

        try:
            # Create blendshape deformer first
            cmds.blendShape(geometry, foc=True, name=bsName)
            mel.eval('blendShape -edit -import "%s" "%s";' % (blendshapesDir, bsName))

            if os.path.isfile(blendshapesDir):
                cmds.deformerWeights("%s.xml" % shpFilename, im=True, deformer=bsName, method="index", path=shpDir)

            # Set each target attr to zero, coming in set to 1 otherwise.
            tgts = cmds.listAttr(bsName, m=True, st="weight")
            if tgts:
                for tgt in tgts:
                    cmds.setAttr("%s.%s" % (bsName, tgt), 0)

            LOG.info('Imported %s' % blendshapesDir)
            return blendshapesDir

        except:
            LOG.error('Could not import blendshape file %s...' % blendshapesDir)
            return


def exportBlendshape(filename='', blendshapeName='', exportWeightFile=True):
    """ Exports blendshape deformer

    Args:
        filename:  Name of .shp blendshape data file
        blendshapeName:  Blendshape node name

    Returns:
        Path to exported blendshape file.
    Example:
        exportBlendshape(filename='ray_cn_body', blendshapeName='ray_cn_body_bs')
    """
    projDir = cmds.workspace(query=True, rd=True)
    deformDir = '%s/deform' % projDir
    blendshapesDir = '%s/deform/blendshapes' % projDir

    # Check for blendshape export directories under current Maya project
    if not os.path.isdir(deformDir):
        try:
            LOG.info('%s does not exist, creating...' % deformDir)
            os.mkdir(deformDir)
        except:
            LOG.error('Could not create directory % for export...' % deformDir)
            return

    if not os.path.isdir(blendshapesDir):
        try:
            LOG.info('%s does not exist, creating...' % blendshapesDir)
            os.mkdir(blendshapesDir)
        except:
            LOG.error('Could not create directory % for export...' % blendshapesDir)
            return

    # Do blendshapes export
    try:
        if cmds.objExists(blendshapeName):
            
            try:
                filename = '%s__%s' % (filename, blendshapeName)
                cmds.blendShape(blendshapeName, edit=True, export='%s/%s.shp' % (blendshapesDir, filename))
    
                if exportWeightFile:
                    cmds.deformerWeights("%s.xml" % filename, ex=True, deformer=blendshapeName, method="index",
                                       path=blendshapesDir)
    
                LOG.info('Exported blendshape deformer: %s/%s.shp' % (blendshapesDir, filename))
                return '%s/%s.shp' % (blendshapesDir, filename)
            
            except:
                LOG.error('Could not export psd blendshape %s...' % filename)
                return
            
    except:
        LOG.error('Blendshape does not exist to export %s...' % blendshapeName)
        return