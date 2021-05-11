# built-ins
import re
import logging

# third party
import maya.cmds as cmds
import maya.api.OpenMaya as om2


LOG = logging.getLogger(__name__)


class dfNode(object):
    @staticmethod
    def fromName(name):
        """Create a new dfNode instance from a node name.

        Args:
            name: Name of an existing node

        Returns:
            dfNode: New instance
        """
        uuid = cmds.ls(name, uuid=True, dep=True)
        return dfNode(uuid[0])

    @staticmethod
    def fromList(node_names):
        """Create a list of new dfNode instances from a list of node names.

        Args:
            node_names: List of node names short or long

        Returns:
            list: dfNode objects
        """
        result = list()

        for n in node_names:
            uuid = cmds.ls(n, uuid=True, dep=True)
            if uuid:
                result.append(dfNode(uuid[0]))

        return result

    @staticmethod
    def fromSelection():
        """Create a list of new dfNode instances from the current active selection.

        Returns:
            list: dfNode objects
        """
        result = list()

        for n in cmds.ls(sl=True, dep=True):
            uuid = cmds.ls(n, uuid=True)
            result.append(dfNode(uuid[0]))

        return result

    def __init__(self, uuid):
        self._uuid = uuid

    def exists(self):
        """Check if the node this dfNode references exists in the current Maya scene.

        Returns:
            bool: Node exists or not
        """
        if cmds.ls(self._uuid):
            return True
        return False

    def name(self):
        """Get this node's short name.

        Returns:
            str: Name at node
        """
        n = cmds.ls(self._uuid)
        if self.exists():
            return n[0]
        return

    def full_path(self):
        """Get this node's full DAG path.

        Returns:
            str: DAG path
        """
        return cmds.ls(self._uuid, long=True)[0]

    def mobject(self):
        """Get this node's api object.

        Returns:
            om2.MObject: Maya Python API 2.0 object
        """
        sel = om2.MSelectionList()
        sel.add(self.name())

        return sel.getDependNode(0)

    def uuid(self):
        """Get this node's internal UUID.

        Returns:
            str: Node uuid
        """
        return str(self._uuid)

    def __str__(self):
        return self._uuid

    def __repr__(self):
        return "dfNode({})".format(self._uuid)


def is_uuid(value):
    """Check if a given value is most likely a UUID string.

    Args:
        value (str): Data

    Returns:
        bool: Whether or not the value is a valid UUID
    """
    uuidPattern = re.compile('^[A-F0-9]{8}-([A-F0-9]{4}-){3}[A-F0-9]{12}$')
    return isinstance(value, basestring) and uuidPattern.match(value)


def yaml_representer(dumper, dfnode):
    """Custom YAML Dumper for dfNode object.

    Args:
        dumper: YAML Dumper object
        dfnode: dfNode object

    Returns:
        str: dfNode tagged YAML data
    """
    value = '{name} | {uuid}'.format(name=dfnode.name(), uuid=dfnode.uuid())
    return dumper.represent_scalar('!dfNode', value)


def yaml_constructor(loader, dfnode):
    """Custom a YAML Loader constructor for dfNode object.

    Args:
        loader: YAML Loader object
        dfnode: dfNode object yaml data

    Returns:
        dfNode: yaml data converted to a dfNode instance
    """
    value = loader.construct_scalar(dfnode)
    uuid = value.replace(' ', '').split('|')[1]
    return dfNode(uuid)
