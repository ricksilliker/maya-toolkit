"""


    - Support relative file paths

"""


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

    # loop through each anim data file entry
    for anim_data in params['anim file options']:
        LOG.debug(anim_data)

        valid_anim_file = False

        # Gather option settings for this anim data file import
        file_path = anim_data['filePath']
        file_name = anim_data['fileName']
        import_method = anim_data['importMethod']
        match_method = anim_data['matchMethod']
        search_str = anim_data['search']
        replace_str = anim_data['replace']
        time_range = anim_data['timeRange']

        # Import method to string
        import_method_str = ''
        if import_method:
            import_method_str = 'childrenToo'
        else:
            import_method_str = 'selectedOnly'

        # Match method to string
        match_method_str = ''
        if match_method:
            match_method_str = 'string'
        else:
            match_method_str = 'hierarchy'

        # Resolve file name and check if valid
        full_file_path_name = resolve_file_path(file_path + file_name)

        if os.path.isfile(full_file_path_name):
            if '.atom' in full_file_path_name:
                LOG.info('Vaild ATOM file: {}'.format(full_file_path_name))
                valid_anim_file = True
            else:
                LOG.error('Not an ATOM (.atom) file: {}'.format(full_file_path_name))
        else:
            LOG.error('File is invalid or does not exist: {}'.format(full_file_path_name))

        # If valid animation file, proceed with importing
        if valid_anim_file:
            LOG.info('Importing ATOM animation file: {}'.format(full_file_path_name))

            LOG.info('Anim Import method: {}'.format(import_method_str))
            LOG.info('Anim Match method: {}'.format(match_method_str))
            LOG.info('Anim Search string: {}'.format(search_str))
            LOG.info('Anim Replace string: {}'.format(replace_str))
            LOG.info('Anim Time range: {}'.format(time_range))

            # Gather import options
            file_type = 'atomImport'
            targetTime = '3'
            option = 'scaleReplace'
            match = match_method_str
            selected = import_method_str
            search = search_str
            replace = replace_str
            prefix = ''
            suffix = ''
            mapFile = file_path
            anim_file = full_file_path_name

            option_str = ";;targetTime={};option={};match={};;selected={};search={}:;replace={};prefix={};suffix={};mapFile={};".format(
                targetTime, option, match, selected, search, replace, prefix, suffix, mapFile)

            # Get rig top node
            #top_node = params['rigName']
            top_node = rig['rig']

            # Import animation file
            if cmds.objExists(top_node):
                cmds.select(top_node)
                cmds.file(anim_file, i=True, ra=True, type=file_type, namespace=":", options=option_str)
                LOG.info('Successfully imported animation file: {}'.format(full_file_path_name))
            else:
                LOG.error('Cannot locate rig top node which is required!')


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

