import os
import json
import logging

import maya.cmds as cmds
import maya.mel as mel

LOG = logging.getLogger(__name__)


def attrValuesToDict(selected_attrs=True, locked_channels=False):
    """Returns attr/value pair dictionary for selected nodes

    Args:
        selected_attrs:  Return for only the selected attrs in the channel box, otherwise just keyable
        locked_channels:  Return locked channel data
    """
    attrDict = {}
    selection = cmds.ls(selection=True)
    if selection:
        for node in selection:
            attrs = getChannelBox(node, selected=selected_attrs, locked=locked_channels)
            if attrs:
                for attr in attrs:
                    attrDict["%s.%s" % (node, attr)] = cmds.getAttr("%s.%s" % (node, attr))

    return attrDict


def import_attributes(filename, setLockedAttrs=False):
    """Imports node, attr, value data from stored json file

    Args:
        filename: Name of file to import, can be relative path to current Maya project

    Example:
        # Importing a "attr" file
        importAttributes("data/finger_rot.attr")

        # Importing a "attr" file
        importAttributes("data/finger_rot.pose")
    """
    projPath = cmds.workspace(q=True, rd=True)
    file_path = os.path.join('%s' % projPath, filename)

    if os.path.exists(file_path):
        try:
            fh = open(file_path, 'r')
            attrData = json.load(fh)
            fh.close()

            for key, value in attrData.iteritems():
                node = key.split(".")[0]
                attr = key.split(".")[1]
                if cmds.objExists(node):
                    if cmds.attributeQuery(attr, node=node, exists=True):
                        isLocked = cmds.getAttr(key, lock=True)
                        isConnected = cmds.listConnections("{}.{}".format(node, attr), s=True, d=False)
                        if isConnected:
                            pass
                        else:
                            if isLocked:
                                if setLockedAttrs:
                                    cmds.setAttr(key, lock=False)
                                    cmds.setAttr(key, value)
                                    cmds.setAttr(key, lock=True)
                                else:
                                    pass
                            else:
                                cmds.setAttr(key, value)

            LOG.info('Imported attr data from: %s' % file_path)
            return file_path
        except:
            LOG.error('Error importing attr data from: %s' % file_path)
            raise
    else:
        LOG.error('Attr data file %s does not exist!' % file_path)
        return


def call_export_attributes(exportPath, selected_attrs=False, locked_channels=False):
    import_cmd = ""
    import_cmd += "#========================================\n"
    import_cmd += "# Use attribute import command below in build\n"
    import_cmd += "#========================================\n"
    import_cmd += "from data_io import attribute_io as attr_io \n"

    selected = cmds.ls(selection=True)
    if selected:
        # Create export directory if it doesn't exist...
        dir_path = os.path.dirname(os.path.abspath(exportPath))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        rel_path = return_relative_path(exportPath)
        export_attributes(exportPath, selected, selected_attrs=selected_attrs, locked_channels=locked_channels)
        import_cmd += "attr_io.import_attributes('{}')\n".format(rel_path)
        return import_cmd
    else:
        LOG.error("Nothing selected, select nodes to export attrs on and try again...")
        return


def export_attributes(filename, nodes, selected_attrs=False, locked_channels=False):
    """Export attribute/value pairs to json.

    Args:
        filename:  Name of json file to save
        nodes: List of nodes to export.
        selected_attrs:  Export only the selected attrs in the channel box
        locked_channels: Export locked channel data

    Returns: NA

    Example:
        # Saving a default "attr" file
        exportAttributes(cmds.ls(selection=True), "data/finger_rot")

        # Saving a "pose" file
        attrs.exportAttributes(cmds.ls(selection=True), "data/finger_rot", fileSuffix='pose')
    """
    cmds.select(nodes)
    attrData = attrValuesToDict(selected_attrs=selected_attrs, locked_channels=locked_channels)

    fh = open(filename, 'w')
    json.dump(attrData, fh, indent=4)
    fh.close()

    LOG.info('Exported attribute file to: %s' % filename)


def return_relative_path(full_path):
    """Returns relative path of input path based on current Maya project"""
    root_dir = cmds.workspace(q=True, rd=True)
    rel_path = os.path.relpath(full_path, root_dir)
    return rel_path.replace('\\','/')


def getChannelBox(node, selected=True, locked=False):
    """Returns a list of all the attrs that are in the channel box
    If locked then only returns the locked CB attrs
    If locked is false then all unlocked CB attrs

    Example:
        from rigging.utils import attribute
        attribute.getChannelBox('transform1', locked=False)
        # Result: [u'visibility',
                     u'translateX',
                     u'translateY',
                     u'translateZ',
                     u'rotateX',
                     u'rotateY',
                     u'rotateZ',
                     u'scaleX',
                     u'scaleY',
                     u'scaleZ'] #

    Args:
        node (str): the maya node you want a list of attrs from:
        selected (bool): Return just the selected attrs in the channel box
        locked (bool): whether or not you want locked attrs or unlocked attrs
    Returns:
        A list of attrs
    """
    # Get all the keyable and or selected attrs
    all_attrs = list()
    if selected:
        all_attrs = mel.eval("selectedChannelBoxAttributes")
    else:
        cb_attrs = cmds.listAttr(node, cb=True)
        key_attrs = cmds.listAttr(node, k=True, scalar=True)
        if cb_attrs:
            all_attrs = cb_attrs
        if key_attrs:
            all_attrs += key_attrs

    # If we don't want locked attrs, remove locked from attrs list
    if not locked:
        locked_attrs = cmds.listAttr(node, l=True)
        if locked_attrs:
            all_attrs = set(all_attrs) - set(locked_attrs)
    return all_attrs