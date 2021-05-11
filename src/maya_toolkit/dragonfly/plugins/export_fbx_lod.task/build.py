import os
import tempfile

import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules


LOG = py_tasker.tasks.get_task_logger(__name__)
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'dragonfly')


def run(params, rig):

    rig_name = rig['rig']

    scene_path = cmds.file(q=True, sn=True)

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    cmds.file(rn=os.path.join(TEMP_DIR, 'fbx_input.ma'))
    cmds.file(s=True, f=True, typ='mayaAscii')

    # loop through each LOD entry
    for lod in params['lods']:
        LOG.debug(lod)

        cmds.file(os.path.join(TEMP_DIR, 'fbx_input.ma'), o=True, f=True, pmt=False)

        # For each lod gather export data
        name_lod = lod['lodName']

        # Filenaming - we can add more "rules" as needed for different projects
        fbx_file_name = params['filename']

        if '.fbx' in  fbx_file_name:
            fbx_file_name = fbx_file_name.replace('.fbx', '')

        if '<asset>' in fbx_file_name:
            fbx_file_name = fbx_file_name.replace('<asset>', rig['asset'])

        if '<LOD>' in fbx_file_name:
            fbx_file_name = fbx_file_name.replace('<LOD>', name_lod)

        file_path = None
        if lod['filePath']:
            file_path = resolve_file_path(lod['filePath'])
            file_path = os.path.join(file_path, '{}.fbx'.format(fbx_file_name))
            #file_path = os.path.join(lod['filePath'], '{}.fbx'.format(fbx_file_name))
            file_path = os.path.realpath(file_path)
            file_path = file_path.replace('\\', '/')

        else:
            scene_path = cmds.file(q=True, sn=True)
            output_dir = scene_path.rsplit(os.path.sep, 1)[0]
            file_path = os.path.join(lod['filePath'], '{}.fbx'.format(fbx_file_name))
            file_path = os.path.realpath(file_path)
            file_path = file_path.replace('\\', '/')


        geo_lod = list()
        ver_lod = lod['fbxVersion']
        tri_lod = lod['triangulateOutput']
        useLodGrp_lod = lod['useGeoLodGroup']

        if useLodGrp_lod:
            if cmds.objExists('LOD_grp'):
                geo_lod.append('LOD_grp')
        else:
            geo_lod = [cmds.ls(x, long=False)[0] for x in lod['geo']]

        root_lod = [cmds.ls(x, long=False)[0] for x in lod['skeletonRoot']]
        if not root_lod:
            root_lod = cmds.listRelatives( rig['skeletonGroup'], children=True, type='joint' )

        # Check if root lod is a proxy node
        if 'proxy' in root_lod[0]:
            root_lod[0] = root_lod[0].replace('proxy_', '')
            if not cmds.objExists(root_lod[0]):
                root_lod = ''

        prune_lod = lod['jointPruneList']

        disconnect_skeleton_connections(root_lod[0])

        # Check if export data is valid
        if name_lod and geo_lod and root_lod:
            LOG.debug("Lod name: {}".format(name_lod))
            LOG.debug("\tLod filepath: {}".format(file_path))
            LOG.debug("\tLod fbx version: {}".format(ver_lod))
            LOG.debug("\tLod triangulate: {}".format(tri_lod))
            LOG.debug("\tLod geo: {}".format(''.join(geo_lod)))
            LOG.debug("\tLod root: {}".format(''.join(root_lod)))

            LOG.info("LOD name: {}".format(name_lod))
            LOG.info("LOD filepath: {}".format(file_path))

            try:
                if prune_lod:
                    for prune_jnt in prune_lod:
                        try:
                            if cmds.objExists(prune_jnt.name()):
                                cmds.delete(prune_jnt.name())
                        except:
                            pass
                dragonfly.modules.export_lod_fbx(rig_name, file_path, geo_lod, root_lod[0], fbx_version='2018', triangulate=tri_lod)
                LOG.debug("Fbx exported rig to: {}".format(file_path))
            except:
                LOG.warning("Fbx export failed for: {}".format(file_path))

        else:
            LOG.warning("Fbx Export LOD parameters incomplete, skipping export!")

    cmds.file(os.path.join(TEMP_DIR, 'fbx_input.ma'), o=True, f=True, pmt=False)
    cmds.file(rn=scene_path)


def disconnect_skeleton_connections(root_joint):
    """Cleanly disconnects all incoming connections to skeleton hierarchy

    disconnect_skeleton_connections("Cn_root_jnt")
    """
    if cmds.objExists(root_joint):
        all_joints = cmds.listRelatives(root_joint, ad=True, type="joint")
        all_joints.append(root_joint)
        if all_joints:
            delete_node_list = list()
            for jnt in all_joints:
                attrs = ['tx','ty','tz','translate',
                         'rx','ry','rz','rotate',
                         'sx','sy','sz','scale',
                         'visibility']
                for attr in attrs:
                    incoming_connection = cmds.listConnections("{}.{}".format(jnt, attr), source=True,
                                                               destination=False, plugs=True)
                    if incoming_connection:
                        cmds.disconnectAttr(incoming_connection[0], "{}.{}".format(jnt, attr))
            LOG.info("Deleted incoming skeleton connections for: {}".format(root_joint))


def return_relative_path(full_path):
    """Returns relative path of input path based on current Maya project"""
    root_dir = cmds.workspace(q=True, rd=True)
    rel_path = os.path.relpath(full_path, root_dir)
    return rel_path.replace('\\','/')


def resolve_file_path(file_path):
    """Returns full path from full or relative input file path

    resolve_file_path('deform/skinClusters/Octopus_LOD0_Mesh.skin')
    """
    if file_path:
        if os.path.exists(file_path):
            return file_path
        else:
            proj_path = cmds.workspace(q=True, rd=True)
            return "{}{}".format(proj_path, file_path)
    else:
        LOG.error('No file path specified!')

