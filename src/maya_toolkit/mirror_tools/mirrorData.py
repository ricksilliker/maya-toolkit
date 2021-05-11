"""
Parse and serialize information needed to mirror nodes.

In this module you can..

- check if a node has mirror data on it
- set/get mirror data to a node
- serialize/parse python/string data from/to nodes

This module uses PyMEL.
"""

import json
import logging
import re

import pymel.core as pm

LOG = logging.getLogger(__name__)

MIRROR_DATA_ATTR_NAME = 'mirrorData'


def hasMirrorData(node):
    """Check if a node has the `mirrorData` attribute.

    Args:
        node (pm.PyNode): Node to check.

    Returns:
        bool: True/False if an attribute exists on node.
    """
    if isinstance(node, basestring):
        node = pm.PyNode(node)

    return node.hasAttr(MIRROR_DATA_ATTR_NAME)


def getMirrorData(node, key=None):
    """Get mirror information from a node.

    Args:
        node (pm.PyNode): Node to grab mirror info.
        key (str): Optional key to retrieve from mirror data dict.

    Returns:
        Parse data from a node under the `mirrorData` attribute.
    """
    node = pm.PyNode(node)

    if not node.hasAttr(MIRROR_DATA_ATTR_NAME):
        return {}

    fullData = json.loads(node.attr(MIRROR_DATA_ATTR_NAME).get())

    if key is not None and key in fullData:
        return parseMirrorData(fullData[key])
    else:
        return parseMirrorData(fullData)


def setMirrorData(node, key, value):
    """Set some mirror information on a given node.

    Args:
        node (pm.PyNode): Maya node to store mirrorData on.
        key (str): Dict key to store value in.
        value: Some python data that is serialized.

    Returns:
        Serialize data onto a node under the `mirrorData` attribute.
    """
    node = pm.PyNode(node)

    if not node.hasAttr(MIRROR_DATA_ATTR_NAME):
        node.addAttr(MIRROR_DATA_ATTR_NAME, dt='string')
        node.attr(MIRROR_DATA_ATTR_NAME).set('{}')

    fullData = json.loads(node.attr(MIRROR_DATA_ATTR_NAME).get())
    data = serializeMirrorData(value)
    fullData[key] = data
    encodedData = json.dumps(fullData)
    node.attr(MIRROR_DATA_ATTR_NAME).set(encodedData)


def serializeMirrorData(value):
    """Convert python values to string data.

    Args:
        value: Some data to serialize.

    Returns:
        Some data to convert to its string representation.
    """
    if isinstance(value, dict):
        data = {}
        for k, v in value.iteritems():
            data[k] = serializeMirrorData(v)
    elif isinstance(value, (list, tuple)):
        data = []
        for v in value:
            data.append(serializeMirrorData(v))
    elif isinstance(value, pm.nt.DependNode):
        data = value.__apimfn__().uuid().asString()
    else:
        data = value

    return data


def parseMirrorData(value):
    """Convert string data to python values.

    Args:
        value: Some data to parse from json values to python values.

    Returns:
        Some value, Uuid's are converted to valid PyNodes.
    """
    if isinstance(value, dict):
        data = {}
        for k, v in value.iteritems():
            data[k] = parseMirrorData(v)
    elif isinstance(value, (list, tuple)):
        data = []
        for v in value:
            data.append(parseMirrorData(v))
    elif isUuid(value):
        try:
            data = pm.PyNode(pm.cmds.ls(value)[0])
        except:
            data = {}
            LOG.error('Could not parse node metadata for uuid `{}`'.format(value))
    else:
        data = value

    return data


def isUuid(value):
    """Check if a given string is a valid Maya Uuid.

    Args:
        value: Some node uuid.

    Returns:
        bool: True/False if it is a match.
    """
    uuidPattern = re.compile('^[A-F0-9]{8}-([A-F0-9]{4}-){3}[A-F0-9]{12}$')
    return isinstance(value, basestring) and uuidPattern.match(value)