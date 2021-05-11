import logging
LOG = logging.getLogger(__name__)

import os
import json

import maya.cmds as cmds


TRS = ['t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz', 's', 'sx', 'sy', 'sz']
TRS9 = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
TRSV = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
TR = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
SV = ['sx', 'sy', 'sz', 'v']


def attrs_keyable(attrs, node=None):
    """Make an attr or a list of attrs keyable"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), keyable=True)


def attrs_show(attrs, node=None):
    """Show a hidden attribute in the channel box and make it keyable and unlocked"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), keyable=True)
        cmds.setAttr('{}.{}'.format(node, a), lock=False)

def attrs_hide(attrs, node=None):
    """Hide attribute in the channel box and make it not keyable and locked"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), keyable=False, channelBox=False)


def attrs_lock(attrs, node=None):
    """Lock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), lock=True)


def attrs_lock_hide(attrs, node=None):
    """Lock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), lock=True)
        cmds.setAttr('{}.{}'.format(node, a), keyable=False)

def attrs_unlock(attrs, node=None):
    """Unlock an attribute or a list of attributes"""
    for a in attrs:
        cmds.setAttr('{}.{}'.format(node,a), lock=False)


def attrs_add_message(src, tgts, attrName):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        attrs_add_message("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attrName, exists=True, node=src):
            cmds.addAttr(src, sn=attrName, at='message')

        for tgt in tgts:
            cmds.connectAttr("%s.message" % (tgt), "%s.%s" % (src, attrName))
        return True

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise


def attrs_get_message(src, attrName):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        attrs_get_message("box_fk_ctrl", attrName="pivot_node")
    """
    try:
        if cmds.attributeQuery(attrName, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attrName))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attrName, src))
        raise
    
def attrs_attributeSeparator(control, attr):
    """Create a separator attribute on the specified control object

    Args:
        control: The control to add the separator attribute to
        attr: The separator attribute name

    Returns:

    Example:
        attributeSeparator('Lf_arm_ctrl', '___')
    """
    # Check control
    if not cmds.objExists(control):
        raise Exception('Control object "'+control+'" does not exist!')

    # Check attribute
    if cmds.objExists(control+'.'+attr):
        raise Exception('Control attribute "'+control+'.'+attr+'" already exists!')

    # Create attribute
    cmds.addAttr(control,ln=attr,at='enum',en=':-:')
    cmds.setAttr(control+'.'+attr,cb=True)
    cmds.setAttr(control+'.'+attr,l=True)

    # Return result
    return (control+'.'+attr)


def importAttributes(filename):
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
                        if isLocked:
                            cmds.setAttr(key, lock=False)
                        cmds.setAttr(key, value)
                        if isLocked:
                            cmds.setAttr(key, lock=True)

            LOG.info('Imported attr data from: %s' % file_path)
            return file_path
        except:
            LOG.error('Error importing attr data from: %s' % file_path)
            raise
    else:
        LOG.error('Attr data file %s does not exist!' % file_path)
        return


def exportAttributes(nodes, filename="", selectedChannels=False, lockedChannels=False, fileSuffix='attr'):
    """
    Export attribute/value pairs to json.

    Args:
        nodes: One of a list of nodes to export.
        filepath: Absolute filepath to export to.

    Returns: NA

    Example:
        # Saving a default "attr" file
        exportAttributes(cmds.ls(selection=True), "data/finger_rot")

        # Saving a "pose" file
        attrs.exportAttributes(cmds.ls(selection=True), "data/finger_rot", fileSuffix='pose')
    """
    projPath = cmds.workspace(q=True, rd=True)
    if '.{}'.format(fileSuffix) in filename:
        file_path = os.path.join('%s' % projPath, '{0}'.format(filename))
    else:
        file_path = os.path.join('%s' % projPath, '{}.{}'.format(filename, fileSuffix))

    cmds.select(nodes)
    attrData = attrValuesToDict(selectedChannels=selectedChannels, lockedChannels=lockedChannels)

    fh = open(file_path, 'w')
    json.dump(attrData, fh, indent=4)
    fh.close()

    LOG.info('Exported attribute file to: %s' % file_path)


def getChannelBox(node, selected=True, locked=False):
    """
    Returns a list of all the attrs that are in the channel box
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
    if selected:
        cbattrs = mm.eval("selectedChannelBoxAttributes")
    else:
        cbattrs = cmds.listAttr(node, scalar=True, k=True, l=locked)
    if locked:
        cbattrs = cmds.listAttr(node, scalar=True, l=locked)

    return cbattrs


def attrValuesToDict(selectedChannels=True, lockedChannels=False):
    """Returns attr/value pair dictionary for selected nodes

    Args:
        selectedChannels:  Return for only the selected attrs in the channel box, otherwise just keyable
        lockedChannels:  Return locked channel data
    """
    attrDict = {}
    selection = cmds.ls(selection=True)
    if selection:
        for node in selection:
            attrs = getChannelBox(node, selected=selectedChannels, locked=lockedChannels)
            if attrs:
                for attr in attrs:
                    attrDict["%s.%s" % (node, attr)] = cmds.getAttr("%s.%s" % (node, attr))

    return attrDict
