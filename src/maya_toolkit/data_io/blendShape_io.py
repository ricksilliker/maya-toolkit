"""
TODO: Export connection data with blendshape?
TODO: SHAPES export for PSDs?
"""
import os
import json
import logging
import maya.cmds as cmds
import maya.mel as mm

LOG = logging.getLogger(__name__)


def import_blendshape(filePath):
    """ Imports blendshape deformer from file onto specified mesh

    Args:
        filePath:  Full file path to
        mesh:  Name of the mesh to import blendshape onto

    Returns:
        True/False

    Example:
        import_blendshape('deform/blendshapes/Ch_Pufferfish_LOD0_SM__Ch_Pufferfish_LOD0_SM_bs.json')
    """
    resolved_path = resolve_file_path(filePath)
    import_dir = os.path.dirname(resolved_path)
    import_filename = os.path.basename(resolved_path)

    if not os.path.isfile(resolved_path):
        LOG.error('File does not exist: {}'.format(resolved_path))
        return False

    with open(resolved_path) as infile:
        try:
            data = json.load(infile)
            LOG.info('Loaded blendShape data from {0}.'.format(filePath))
        except:
            LOG.error('Unable to load blendShape data from {0}.'.format(filePath))
            return False

    # Check mesh exists
    mesh = data['mesh'][0]
    if not cmds.objExists(mesh):
        LOG.error('Mesh {} does not exist in scene'.format(mesh))
        return

    # If blendshape exists, delete
    if cmds.objExists(data['blendshape_node']):
        cmds.delete(data['blendshape_node'])

    try:
        cmds.blendShape(mesh, foc=True, name=data['blendshape_node'])
        mm.eval('blendShape -edit -import "%s/%s" "%s";' % (import_dir, data['blendshape_file'], data['blendshape_node']))
        cmds.deformerWeights(data['blendshape_weights'], im=True, deformer=data['blendshape_node'], method="index",
                             path=import_dir)

        # Set each target attr to zero, coming in set to 1 otherwise.
        tgts = cmds.listAttr(data['blendshape_node'], m=True, st="weight")
        if tgts:
            for tgt in tgts:
                cmds.setAttr("%s.%s" % (data['blendshape_node'], tgt), 0)
        return True

    except:
        LOG.error('Unable to create blendshape {} from file {}'.format(data['blendshape_node'], import_filename))
        return False


def call_export_blendshape(exportPath, mesh, blendshape_node=''):
    import_cmd = ""
    import_cmd += "#========================================\n"
    import_cmd += "# Use blendshape import command below in build\n"
    import_cmd += "#========================================\n"
    import_cmd += "from data_io import blendShape_io as bs \n"

    # Create export directory if it doesn't exist...
    dir_path = os.path.dirname(os.path.abspath(exportPath))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    rel_path = return_relative_path(exportPath)
    export_blendshape(exportPath, blendshape_node)
    import_cmd += "bs.import_blendshape('{}')\n".format(rel_path)

    return import_cmd


def export_blendshape(export_file_path, blendshape_node):
    """Exports blendshape deformer to file

    Args:
        export_file_path: Full file path for exported blendshape data
        blendshape_node:  Blendshape node to export

    Returns:
        Blendshape import command

    Example:
        bs_file_path = 'deform/blendshapes/Ch_Pufferfish_LOD0_SM__Ch_Pufferfish_LOD0_SM_bs.json'
        export_blendshape(bs_file_path, 'Ch_Pufferfish_LOD0_SM_bs')
    """
    resolved_path = resolve_file_path(export_file_path)
    export_dir = os.path.dirname(resolved_path)
    export_filename = os.path.basename(resolved_path)
    #export_filename_no_ext = export_filename.split('.')[0]

    # Check blendshape
    if not cmds.objExists(blendshape_node):
        LOG.error('Blendshape node {0} does not exist.'.format(blendshape_node))
        return False

    # Check directory path, create directory if it doesn't exist
    if not os.path.isdir(export_dir):
        try:
            LOG.info('{} does not exist, creating...'.format(export_dir))
            os.mkdir(export_dir)
        except:
            LOG.error('Could not create directory {} for export...'.format(export_dir))
            return

    # Do blendshape export
    try:
        # filename = '{}__{}'.format(export_filename_no_ext, blendshape_node)
        cmds.blendShape(blendshape_node, edit=True, export='{}/{}.bshp'.format(export_dir, blendshape_node))
        cmds.deformerWeights("{}.xml".format(blendshape_node), ex=True, deformer=blendshape_node, method="index",
                             path=export_dir)

        bs_data = {}
        bs_data['blendshape_file'] = '{}.bshp'.format(blendshape_node)
        bs_data['blendshape_weights'] = '{}.xml'.format(blendshape_node)
        bs_data['blendshape_node'] = blendshape_node
        bs_data['mesh'] = get_geo_from_blendshape(blendshape_node)

        with open(resolved_path, 'w') as outfile:
            json.dump(bs_data, outfile, sort_keys=True, indent=4)

        LOG.info('Exported blendshape node {} to {}'.format(blendshape_node, export_file_path))
        return "Blendshape export data..."
    except:
        LOG.error('Blendshape does not exist to export {}...'.format(blendshape_node))
        return


def get_selected_blendshape():
    """Returns selected blendshapes from channel box

    """
    selection = cmds.ls(selection=True)
    blendshape_nodes = list()

    if selection:
        for item in selection:
            if "blendShape" in cmds.nodeType(item):
                blendshape_nodes.append(item)
        return blendshape_nodes
    else:
        print "No blendshape nodes selected"
        return


def return_blendshape_from_mesh(mesh_name=""):
    """

    return_blendshape_from_mesh(mesh_name="Ch_Pufferfish_LOD0_SM")
    """
    selection = cmds.ls(selection=True)
    blendshape_nodes = list()

    if selection:
        for item in selection:
            shp = cmds.listRelatives(item, shapes=True)
            if shp:
                his = cmds.listHistory(shp[0])
                if his:
                    for node in his:
                        if "blendShape" in cmds.nodeType(node):
                            blendshape_nodes.append(node)
        return blendshape_nodes
    else:
        print "No blendshapes found connected to {}".format(mesh_name)
        return


def get_geo_from_blendshape(blendshape_node):
    """

    get_geo_from_blendshape("Ch_Pufferfish_LOD0_SM_bs")
    """
    bs_set = cmds.listConnections("{}.message".format(blendshape_node), s=False, d=True, type='objectSet')
    if bs_set:
        geo = cmds.listConnections("{}.dagSetMembers".format(bs_set[0]), s=True, d=False)
        if geo:
            return geo


def return_relative_path(full_path):
    """Returns relative path of input path based on current Maya project"""
    root_dir = cmds.workspace(q=True, rd=True)
    rel_path = os.path.relpath(full_path, root_dir)
    return rel_path.replace('\\','/')


def resolve_file_path(file_path):
    """Returns full path from full or relative input file path

    resolve_file_path('deform/skinClusters/Ch_YellowButterfly_LOD0_SM_skin.json')
    """
    if file_path:
        if os.path.exists(file_path):
            return file_path
        elif os.path.exists(os.path.dirname(file_path)):
            return file_path
        else:
            proj_path = cmds.workspace(q=True, rd=True)
            return "{}{}".format(proj_path, file_path)
    else:
        LOG.error('No file path specified!')

