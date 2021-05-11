import logging
LOG = logging.getLogger(__name__)

import maya.cmds as cmds


def addMessageAttribute(src, tgts, attrName):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        addMessageAttr("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attrName, exists=True, node=src):
            cmds.addAttr(src, sn=attrName, at='message', m=True)

        i=0
        while i < len(tgts):
            idx = get_next_free_multi_index("{}.{}".format(src, attrName), i)
            cmds.connectAttr("%s.message" % (tgts[i]), "%s.%s[%s]" % (src, attrName, str(idx)), f=True)
            i=i+1

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise


def getMessageAttributeConnections(src, attrName):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        getMessageAttributeConnections("box_fk_ctrl", attrName="pivot_node")
    """
    try:
        if cmds.attributeQuery(attrName, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attrName))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attrName, src))
        raise


def get_next_free_multi_index(attr_name, start_index):
    '''Find the next unconnected multi index starting at the passed in index.'''
    # assume a max of 10 million connections
    while start_index < 10000000:
        if len(cmds.connectionInfo('{}[{}]'.format(attr_name, start_index), sfd=True) or []) == 0:
            return start_index
        start_index += 1

    # No connections means the first index is available
    return 0
