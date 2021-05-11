"""
TODO: Think about rig templates?  Location? Copy to current project? etc.
TODO: Think about workflow with fit and blueprint files

TODO: as_add_faceRig.task
TODO: as_add_ikFingers.task

TODO: Blueprint "templates"
"""
import os
import tempfile
import glob
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules


LOG = py_tasker.tasks.get_task_logger(__name__)
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'dragonfly')
CONTROLS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'controls')

def run(params, rig):

    # Initialize Advanced Skeleton
    init()

    # Check asset name with project name
    asset_name = rig['asset']
    proj_name = asset_from_project()
    if asset_name != proj_name:
        LOG.error('Maya project and asset name do not match, exiting...')
        raise Exception

    # Check if rebuild rig is specified
    rebuild_rig = params['rebuildRig']
    LOG.debug("Rebuild rig = {}".format(rebuild_rig))

    # If importing versioned fit skeleton
    if params['useVersionedFitFile']:
        #build_mocap_rig = params['addMocapOffsetSkeleton']
        LOG.debug("Build mocap rig = {}".format(params['addMocapOffsetSkeleton']))
        fit_file_path = params['fitSkeletonDirectory']
        if fit_file_path:
            #build_base_rig(asset_name, fit_file_path=fit_file_path, rebuild_rig=rebuild_rig, buildMocapRig=build_mocap_rig)
            build_base_rig(asset_name, fit_file_path=fit_file_path, rebuild_rig=rebuild_rig,
                           buildMocapRig=params['addMocapOffsetSkeleton'])
        else:
            LOG.error("No fit skeleton directory specified, set fit skeleton directory in task.")
            raise Exception

    # else use fit skeleton in scene (check if it exists first)
    else:
        if cmds.objExists('FitSkeleton'):
            if rebuild_rig:
                mel.eval("asReBuildAdvancedSkeleton")
            if params['addMocapOffsetSkeleton']:
                add_mocap_skeleton()
        else:
            LOG.error('Cannot find Fit Skeleton node in scene, exiting...')
            raise Exception

    # Parent rig under top node
    try:
        cmds.parent('Main', rig['rigGroup'])
    except:
        cmds.parent("Main", rig['rig'])
    finally:
        pass

    # Parent mocap rig under top node
    if params['addMocapOffsetSkeleton']:
        try:
            cmds.parent(cmds.listRelatives('MoCap', children=True), rig['mocapGroup'])
        except:
            cmds.parent(cmds.listRelatives('MoCap', children=True), rig['rig'])
        finally:
            pass

    # Parent skeleton
    if cmds.objExists(rig['skeletonGroup']):
        cmds.parent(cmds.listRelatives('DeformationSystem', children=True), rig['skeletonGroup'])

    # Delete left over Group created by AS
    if cmds.objExists('Group'):
        cmds.delete('Group')


def init():
    """Sources and calls Advanced Skeleton"""
    try:
        import asRig2.core
        reload(asRig2.core)
        asRig2.core.init()
        LOG.info('Successfully initialized Advanced Skeleton through asRig2')
    except:
        LOG.error('Requires asRig2 to be installed, skipping...')


def asset_from_project():
    """Returns the name of the Maya Project directory to use as the asset variable in the rig build """
    proj_dir = cmds.workspace(q=True, rd=True)
    if proj_dir:
        asset_name = proj_dir.split("/")[-2]
        return asset_name


def build_base_rig(assetName, fit_file_path=None, rebuild_rig=True, buildMocapRig=True):
    """ Imports fit, builds rig, imports model, builds rig hierarchy """
    import_fit_build_rig(assetName, fit_file_path=None, rebuild_rig=rebuild_rig)

    if buildMocapRig:
        add_mocap_skeleton()


def import_fit_build_rig(assetName, fit_file_path=None, rebuild_rig=True):
    """Builds Advanced Skeleton rig from latest "fit" file in current Maya Project's fit directory
    or from the passed in path

    Args:
        assetName:  Name of asset
        fit_file_path:  File path to fit skeleton file.
        rebuild_rig:  Rebuild the rig after importing the fit file.

    Returns:
        True if rig built successfully
    """
    try:
        if not fit_file_path:
            fit_file_path = get_project_file_by_type(type="fit")

        if os.path.exists(fit_file_path):
            cmds.file("%s" % fit_file_path, i=True, dns=True, mergeNamespacesOnClash=False, pr=True, ignoreVersion=True)
            cmds.viewFit()
            if rebuild_rig:
                mel.eval("asReBuildAdvancedSkeleton")

            # Store original names in case rig needs to be renamed later
            name_history_attribute()

            LOG.info('Built rig from fit file: %s' % fit_file_path)
            return True
        else:
            LOG.error('File does not exist: %s' % fit_file_path)
            return
    except:
        LOG.error('Failed to build rig from fit file')
        raise
    
    
def get_project_file_by_type(type="fit", importFile=False, openFile=False, fileSuffix="ma"):
    """ get_project_file_by_type(type="fit", importFile=False, openFile=False, fileSuffix="ma") """
    projPath = cmds.workspace(query=True, rd=True)
    typePath = "%s%s/" % (projPath, type)
    assetName = projPath.split('/')[-2]
    versions = len(glob.glob('%s%s_%s_v*.%s' % (typePath, assetName, type, fileSuffix)))
    currentFile = "%s%s_%s_v%s.%s" % (typePath, assetName, type, versions, fileSuffix)

    if os.path.exists(currentFile):
        try:
            if versions:
                if openFile:
                    cmds.file(currentFile, open=True, force=True)
                    LOG.info("Opened file: %s" % currentFile)

                elif importFile:
                    cmds.file("%s%s_%s_v%s.%s" % (typePath, assetName, type, versions, fileSuffix), i=True, force=True)
                    LOG.info("Imported file: %s" % currentFile)

                return currentFile
        except:
            LOG.error('Unable to open/find file')
            return
    else:
        LOG.error("File doesn't exist for %s" % currentFile)
        
        
def add_mocap_skeleton():
    """ Calls asCreateMocap to add mocap offset rig """
    try:
        mel.eval("asCreateMoCap()")
        rename_mocap_skeleton()
        delete_mocap_helper_joints()

        # Move mocap root connection to offset node
        cmds.disconnectAttr("SpineBase_M_mocap_pma.output3D", "RootExtraX_M.translate")
        cmds.connectAttr("SpineBase_M_mocap_pma.output3D", "RootOffsetX_M.translate")

        LOG.debug('Added mocap offset rig...')
        return True

    except:
        LOG.error('Unable to add mocap offset rig')
        raise
    
    
def rename_mocap_skeleton(mocapSkeletonOffset=[0,0,0]):
    """Renames AdvSkeleton Mocap joints (ie., Spine2_MoCap_M -> Spine2_M_mocap)"""

    mocapJnts = cmds.ls('*_MoCap_*', type='joint')

    if mocapJnts:
        for mocapJnt in mocapJnts:
            splitNm = mocapJnt.split('_')
            newNm = '%s_%s_mocap' % (splitNm[0], splitNm[2])
            cmds.rename(mocapJnt, newNm)

        charHeight = -(cmds.getAttr('Main.height'))

        # Add another mocap top node to constrain to master
        cmds.disconnectAttr('Root_M_mocap.translate', 'RootExtraX_M.translate')
        cmds.parent('Root_M_mocap', world=True)
        cmds.rename('CenterOffset', 'MocapRigLocalOffset')
        cmds.group('MocapRigLocalOffset', name='MocapRigWorldOffset')

        cmds.setAttr('MocapRigWorldOffset.translate', 0,0,0)
        cmds.setAttr('MocapRigLocalOffset.translate', 0, 0, 0)
        cmds.setAttr('MoCap.translate', 0, 0, 0)

        cmds.parentConstraint("Main", "MocapRigWorldOffset", mo=True)
        cmds.scaleConstraint("Main", "MocapRigWorldOffset")
        originLoc = cmds.spaceLocator()[0]
        cmds.pointConstraint(originLoc, 'MocapRigLocalOffset')

        # Rename root mocap joint
        cmds.rename('Root_M_mocap', 'SpineBase_M_mocap')

        # Create new root mocap joint
        cmds.select(clear=True)
        cmds.joint(name='Root_M_mocap')
        cmds.parent('Root_M_mocap', 'MocapRigLocalOffset')
        cmds.setAttr('Root_M_mocap.translate', 0, 0, 0)
        cmds.delete(cmds.pointConstraint('Root_M', 'SpineBase_M_mocap'))
        cmds.parent('SpineBase_M_mocap', 'Root_M_mocap')

        # Create offset connection from mocap joint back to RootExtraX_M
        spineBasePos = cmds.getAttr('SpineBase_M_mocap.translate')[0]
        pma = cmds.createNode('plusMinusAverage', name='SpineBase_M_mocap_pma')
        cmds.connectAttr('SpineBase_M_mocap.translate', '%s.input3D[0]' % pma)
        cmds.setAttr('%s.input3D[1].input3Dx' % pma, spineBasePos[0] * -1)
        cmds.setAttr('%s.input3D[1].input3Dy' % pma, spineBasePos[1] * -1)
        cmds.setAttr('%s.input3D[1].input3Dz' % pma, spineBasePos[2] * -1)
        cmds.connectAttr('%s.output3D' % pma, 'RootExtraX_M.translate')

        # Create mocap control
        handle('MocapRigLocalOffset', ctrlShape='four_arrow_circle', ctrlColor=18, ctrlScale=(charHeight / 20), ctrlAxis=None)
        cmds.delete(originLoc)

        # Offset skeleton behind character
        cmds.setAttr("MocapRigLocalOffset.translate", mocapSkeletonOffset[0], mocapSkeletonOffset[1], mocapSkeletonOffset[2])

        return True
    else:
        return


def delete_mocap_helper_joints(helperSearchString="Hlpr"):
    """Delete helper joints that are not needed in mocap skeleton

    Args:
        helperSearchString:  Search string in helper joint name to search for

    Returns:
        True
    """
    if cmds.objExists("MoCap"):
        mcHlprJnts = []
        mcJnts = cmds.listRelatives("MoCap", ad=True, type="joint")
        for mcJnt in mcJnts:
            if helperSearchString in mcJnt:
                mcHlprJnts.append(mcJnt)
        if mcHlprJnts:
            cmds.delete(mcHlprJnts)
            return True

        
def name_history_attribute(topNode="Group"):
    """ Stores the original name of nodes under the topNode hierarchy to a nameHistory attribute

    Args:
        topNode:  Top node name whose children will have nameHistory attribute added.

    Returns:
        None
    """
    try:
        nodeList = cmds.listRelatives(topNode, ad=True, f=True, shapes=False)
        nodeList.append(topNode)
        if nodeList:
            for node in nodeList:
                if cmds.objExists(node):
                    if not cmds.attributeQuery('nameHistory', node=node, exists=True):
                        cmds.addAttr(node, longName='nameHistory', dataType='string')
                    cmds.setAttr('%s.nameHistory' % node, lock=False)
                    cmds.setAttr('%s.nameHistory' % node, node.split('|')[-1], type='string')
                    cmds.setAttr('%s.nameHistory' % node, lock=True)
        LOG.debug("Successfully added nameHistory attr to nodes in hierarchy")
    except:
        LOG.error("Error adding nameHistory attr to nodes in hierarchy")
        raise


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


def importShapesFromJson(filepath, transform=None):
    """Import control shape to node.

    Args:
        filepath: The absolute filepath to a json file.
        transform: Target node.

    Returns:
        Filepath if succeeds. None if fails.
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


def setColor(node, colorInt):
    """Sets the maya color on a node like a control or transform

    Args:
        node:  Node in scene to color
        colorInt: color index value
    """
    cmds.setAttr(node+'.overrideEnabled', 1)
    cmds.setAttr(node+'.overrideShading', 0)
    cmds.setAttr(node+'.overrideColor', colorInt)




