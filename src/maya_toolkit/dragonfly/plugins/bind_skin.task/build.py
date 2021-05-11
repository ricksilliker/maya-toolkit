import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.modules


LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    bind_kwargs = dict(omi=params['maintainMaxInfluence'],
                       dr=8.0, mi=params['maxInfluences'], nw=1, rui=False,
                       bm=1, sm=0, tsb=True, wd=1)

    for msh in params['geometry']:
        skin = cmds.skinCluster(msh.name(), [jnt.name() for jnt in params['joints']], **bind_kwargs)
        cmds.rename(skin, '{0}_skcl'.format(msh.name()))

    dragonfly.modules.import_weights(file_path=params['weightsFile'].absolute_path(), nodes=[x.name() for x in params['geometry']])