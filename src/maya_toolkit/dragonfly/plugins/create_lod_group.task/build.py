import os
import tempfile

import maya.cmds as cmds

import py_tasker.tasks
import collections

LOG = py_tasker.tasks.get_task_logger(__name__)
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'dragonfly')


def run(params, rig):

    rig_name = rig['rig']
    geo_grp = rig['geoGroup']
    lod_dict = collections.OrderedDict()

    for lod in params['lods']:
        name_lod = lod['lodName']
        geo_lod = [cmds.ls(x, long=False)[0] for x in lod['geo']]
        lod_dict[name_lod] = geo_lod

    if lod_dict:
        lod_grp = create_lod_groups(lod_dict)
        if cmds.objExists(geo_grp):
            if not cmds.listRelatives(lod_grp, parent=True):
                cmds.parent(lod_grp, geo_grp)


def create_lod_groups(lod_dict, name='LOD_grp'):
    """Creates lod group and subgroups from dictionary data

    Args:
        lod_dict = <LOD_name> : [<mesh_list>]
        name = Name of main LOD group

    Returns:
        Main LOD top group

    Example:
        my_lod_dict = collections.OrderedDict()
        my_lod_dict['LOD0'] = ['CH_MoorishIdol_LOD0_SM', 'CH_MoorishIdolFin_LOD0_SM']
        my_lod_dict['LOD1'] = ['CH_MoorishIdol_LOD1_SM', 'CH_MoorishIdolFin_LOD1_SM']
        create_lod_groups(my_lod_dict)
    """
    geo_lod_list = list()
    cmds.select(clear=True)
    for lod, lod_geo in lod_dict.items():
        for geo in lod_geo:
            if cmds.listRelatives(geo, parent=True):
                cmds.parent(geo, world=True)
        geo_lod_list.append(lod_geo[0])

    if geo_lod_list:
        cmds.select(geo_lod_list)
        cmds.LevelOfDetailGroup()
        lod_grp = cmds.rename(cmds.ls(selection=True)[0], name)
        for lod, lod_geo in lod_dict.items():
            if len(lod_geo) > 1:
                lod_parent = cmds.listRelatives(lod_geo[0], parent=True)
                if lod_parent:
                    cmds.parent(lod_geo[1:], lod_parent[0])
        return lod_grp
