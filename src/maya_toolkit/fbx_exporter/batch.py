import os

from maya import cmds
import fbx_exporter.view
import fbx_exporter.core as fbx_core
import fbx_exporter.clips as fbx_clips


def fbx_batch_export_folders(folder_list, output_dir, delete_static_channels=False):
    """Opens each Maya file found in each folder in the "folder_list" and exports fbx file for each
    clip into the "destination_folder"

    Currently uses whatever the min/max frame range is set in the Maya file as the export range
    (ie., it does not currently use the clip information defined in the FBX exporter)

    """
    # New file
    cmds.file(new=True, f=True)

    for input_dir in folder_list:
        # List files in directory
        src_files = os.listdir(input_dir)

        if src_files:
            for src_file in src_files:
                if '.ma' or '.mb' in src_file:

                    # Load file
                    cmds.file('{}\\{}'.format(input_dir, src_file), o=True, f=True)
                    print "SOURCE: {}\\{}".format(input_dir, src_file)

                    # Extract export filename
                    ns = src_file.split('_')
                    fbx_file = 'CH_{}_{}_AN.fbx'.format(ns[1], ns[2])

                    # Find rigs
                    rigs = fbx_core.get_rigs()
                    if rigs:
                        for rig in rigs:
                            if cmds.objExists('FBXExporterNode'):  cmds.delete('FBXExporterNode')
                            fbx_node = fbx_core.get_node()
                            fbx_clips.add_clip('FBXExporterNode')
                            min_f = cmds.playbackOptions(q=True, minTime=True)
                            max_f = cmds.playbackOptions(q=True, maxTime=True)
                            cmds.setAttr("FBXExporterNode.clips",
                                         "[[\"{}\", {}, {}, true]]".format(ns[2], min_f, max_f), type='string')

                            # Create output directory if it doesn't exist
                            if not os.path.exists(output_dir):
                                os.makedirs(output_dir)

                            # Export and save FBX anim file
                            kw = dict()
                            kw['user_filename'] = fbx_file
                            rig_node = fbx_core.get_rig_mobject(rig)
                            kw['only_selection'] = False
                            kw['output_path'] = output_dir
                            kw['DeleteStaticChannels'] = delete_static_channels
                            kw['FBXExportShapes'] = False
                            kw['ExportMeshes'] = False
                            kw['FBXExportFileVersion'] = 'FBX201800'
                            fbx_core.export_rigs([rig_node], fbx_clips.get_clips('FBXExporterNode'), **kw)

                    # Load next file...
                    print "EXPORTED: {}\\{}".format(output_dir, fbx_file)


def fbx_batch_export_files(file_list, output_dir, delete_static_channels=False):
    """Opens each Maya file found in "file_list" and exports fbx file for each
    clip into the "destination_folder"

    Currently uses whatever the min/max frame range is set in the Maya file as the export range
    (ie., it does not currently use the clip information defined in the FBX exporter)

    """
    # New file
    cmds.file(new=True, f=True)

    src_files = file_list

    if src_files:
        for src_file in src_files:
            if '.ma' or '.mb' in src_file:

                # Load file
                cmds.file('{}'.format(src_file), o=True, f=True)
                print "SOURCE: {}".format(src_file)

                # Extract export filename
                ns = src_file.split('_')
                fbx_file = 'CH_{}_{}_AN.fbx'.format(ns[1], ns[2])

                # Find rigs
                rigs = fbx_core.get_rigs()
                if rigs:
                    for rig in rigs:
                        if cmds.objExists('FBXExporterNode'):  cmds.delete('FBXExporterNode')
                        fbx_node = fbx_core.get_node()
                        fbx_clips.add_clip('FBXExporterNode')
                        min_f = cmds.playbackOptions(q=True, minTime=True)
                        max_f = cmds.playbackOptions(q=True, maxTime=True)
                        cmds.setAttr("FBXExporterNode.clips", "[[\"{}\", {}, {}, true]]".format(ns[2], min_f, max_f),
                                     type='string')

                        # Create output directory if it doesn't exist
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)

                        # Export and save FBX anim file
                        kw = dict()
                        kw['user_filename'] = fbx_file
                        rig_node = fbx_core.get_rig_mobject(rig)
                        kw['only_selection'] = False
                        kw['output_path'] = output_dir
                        kw['DeleteStaticChannels'] = delete_static_channels
                        kw['FBXExportShapes'] = False
                        kw['ExportMeshes'] = False
                        kw['FBXExportFileVersion'] = 'FBX201800'
                        fbx_core.export_rigs([rig_node], fbx_clips.get_clips('FBXExporterNode'), **kw)

                # Load next file...
                print "EXPORTED: {}\\{}".format(output_dir, fbx_file)






