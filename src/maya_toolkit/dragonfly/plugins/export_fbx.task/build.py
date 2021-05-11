import os
import tempfile

import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules

LOG = py_tasker.tasks.get_task_logger(__name__)
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'dragonfly')


def run(params, rig):
    scene_path = cmds.file(q=True, sn=True)

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    cmds.file(rn=os.path.join(TEMP_DIR, 'fbx_input.ma'))
    cmds.file(s=True, f=True, typ='mayaAscii')

    rig_name = rig['rig']
    if not params['outputPath']:
        scene_path = cmds.file(q=True, sn=True)
        output_dir = scene_path.rsplit(os.path.sep, 1)[0]
        output_path = os.path.join(output_dir, '{}_exported.fbx'.format(rig_name))
    else:
        output_path = os.path.join(params['outputPath'], '{}_exported.fbx'.format(rig_name))

    LOG.debug('Exporting rig FBX..')

    if 'skeletonGroup' in rig and 'meshesGroup' in rig:
        meshes = cmds.listRelatives(rig['meshesGroup'], c=True)
        skeleton = cmds.listRelatives(rig['skeletonGroup'], c=True)
        if skeleton and meshes:
            dragonfly.modules.export_fbx(rig_node=rig, output_path=output_path)

    cmds.file(os.path.join(TEMP_DIR, 'fbx_input.ma'), o=True, f=True, pmt=False)
    cmds.file(rn=scene_path)
