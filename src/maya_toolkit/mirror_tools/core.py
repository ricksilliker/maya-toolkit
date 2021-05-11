# built-ins
import ast
import re
import logging

# third party
import pymel.core as pm

# internal
import mirrorData
import utils

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

MIRROR_THRESHOLD = .0001
MIRROR_STRING_REGEX = {
    'left': [
        # right search regex, left replacement string {right} and {left} will be replaced by opposite string
        ['{right}', 'left'],
        ['{right}', 'Left'],
        ['{right}', 'lft_'],
        ['{right}', 'Lft_'],
        ['(((?<=^)|(?<=_)){right})', 'L_'],  # Only if preceded by _ or at the beginning
        ['(((?<=^)|(?<=_)){right})', 'l_'],  # Only if preceded by _ or at the beginning
        ['(((?<=^)|(?<=_)){right})', 'Lf_'],  # Only if preceded by _ or at the beginning
        ['(((?<=^)|(?<=_)){right})', 'lf_']  # Only if preceded by _ or at the beginning
    ],
    'right': [
        ['{left}', 'right'],
        ['{left}', 'Right'],
        ['{left}', 'rgt_'],
        ['{left}', 'Rgt_'],
        ['((?<=^)|(?<=_)){left}', 'r_'],  # Only if preceded by _ or at the beginning
        ['((?<=^)|(?<=_)){left}', 'R_'],  # Only if preceded by _ or at the beginning
        ['((?<=^)|(?<=_)){left}', 'Rt_'],  # Only if preceded by _ or at the beginning
        ['((?<=^)|(?<=_)){left}', 'rt_']  # Only if preceded by _ or at the beginning
    ]
}

# Compile the auto swap regex
for i, r in enumerate(MIRROR_STRING_REGEX['left']):
    reg = r[0].format(right=MIRROR_STRING_REGEX['right'][i][1])
    MIRROR_STRING_REGEX['left'][i][0] = re.compile(reg)
for i, r in enumerate(MIRROR_STRING_REGEX['right']):
    reg = r[0].format(left=MIRROR_STRING_REGEX['left'][i][1])
    MIRROR_STRING_REGEX['right'][i][0] = re.compile(reg)


def swapMirrorString(input):
    """Swap strings with their mirror equivalent.

    Args:
        input (str): Some string.

    Returns:
        str: String name mirrored.
    """
    if input is None:
        return

    result = input
    for r in MIRROR_STRING_REGEX['left']:
        result = r[0].sub(r[1], result)
    if result == input:
        for r in MIRROR_STRING_REGEX['right']:
            result = r[0].sub(r[1], result)

    return result


def allMirrorNodes(rig=None):
    """Get all nodes that have mirror data.

    Args:
        rig (pm.PyNode): Rig root node, return only mirror nodes related to this rig.

    Returns:
        list
    """
    if rig is not None:
        nodes = list()
        nodes.extend(pm.listRelatives(rig, ad=True))
        return [n.node() for n in nodes if n.hasAttr(mirrorData.MIRROR_DATA_ATTR_NAME)]
    else:
        return [n.node() for n in pm.ls('*.{}'.format(mirrorData.MIRROR_DATA_ATTR_NAME))]


def isMirrorNode(node, validate=True):
    """Check if node is a mirror node already.

    Args:
        node (pm.PyNode): Name of a node.
        validate (bool): Run a validate function, to see if a node has a mirror.

    Returns:
        bool: True if it is a mirror, False if not.
    """
    if not mirrorData.hasMirrorData(node):
        return False
    if validate:
        return validateMirrorNode(node)
    return True


def getMirrorMode(node):
    """Get the mirror mode of the given node.

    Args:
        node (pm.PyNode): Node to check.

    Returns:
        str
    """
    return mirrorData.getMirrorData(node, 'mirrorMode')


def isCustomMirrorNode(node):
    """Check if input node has custom mirror data.

    Args:
        node (pm.PyNode): Node to check.

    Returns:
        bool
    """
    return mirrorData.hasMirrorData(node) and 'customMirror' in mirrorData.getMirrorData(node)


def associate(nodeA, nodeB, force=False):
    """Associate the given nodes as mirrors of each other.

    Args:
        nodeA (pm.PyNode): Name of first node.
        nodeB (pm.PyNode): Name of second node.
        force (bool): Override current association if there is one.

    Returns:
        None
    """
    setMirrorNode(nodeA, nodeB, force)
    setMirrorNode(nodeB, nodeA, force)


def disassociate(node):
    """Disassociate the given mirror node from its counterpart.

    Args:
        node (pm.PyNode): Name of a node to de-link any mirroring associations.

    Returns:
        None
    """
    if not isMirrorNode(node):
        return
    other = getMirrorNode(node, warn=True)
    clearMirrorNode(node)
    clearMirrorNode(other)


def setMirrorNode(node, mirrorNode, force=False):
    """Set a given node's mirror node.

    Args:
        node (pm.PyNode): Name of the source node.
        mirrorNode (pm.PyNode): Name of the destination node.
        force (bool): Override any mirroring that exists.

    Returns:
        None
    """
    data = mirrorData.getMirrorData(node, 'mirrorNode')

    if mirrorData.hasMirrorData(node):
        if not force and data != mirrorNode and data is not None:
            LOG.warning('{0} is already associated with another node {1}, use force=True to replace with {2}'.format(node, data, mirrorNode))
            return

    mirrorData.setMirrorData(node, key='mirrorNode', value=mirrorNode)
    mirrorData.setMirrorData(node, key='mirrorMode', value='Auto')


def clearMirrorNode(node):
    """Remove mirror node meta data from the given node.

    Args:
        node (pm.PyNode): Name of node to remove data from.

    Returns:
        None
    """
    if mirrorData.hasMirrorData(node):
        pm.deleteAttr(node.attr(mirrorData.MIRROR_DATA_ATTR_NAME))


def validateMirrorNode(node):
    """Check if the given mirror node still has a mirror object.
    Otherwise remove the mirror meta data from the node.

    Args:
        node (pm.PyNode): Name of a node.

    Returns:
        bool: True if the node is a valid mirror node.
    """
    if not mirrorData.hasMirrorData(node):
        return False

    mirrorNode = mirrorData.getMirrorData(node, 'mirrorNode')
    if mirrorNode is None:
        LOG.debug('{0} mirror node was None, clearing mirror node'.format(node))
        clearMirrorNode(node)
        return False

    return True


def getMirrorNode(node, warn=False):
    """Given a mirror node, find the counter part.

    Args:
        node (pm.PyNode): Source node name to get mirror node.
        warn (bool): Warn user if the source has no mirror.

    Returns:
        str: Name of the source node's mirror node.
    """
    if not isMirrorNode(node):
        if warn:
            LOG.warning('{0} is not a mirror node'.format(node))
        return

    return mirrorData.getMirrorData(node, 'mirrorNode')


def isCentered(node, axis=0):
    """Check if a node is at the given center axis.

    Args:
        node (pm.PyNode): Name of a node.
        axis (int): 0, 1, 2 representing x, y, or z axis.
    Returns:
        bool: True if it is centered under the default threshold, False if not.
    """
    axis = utils.getAxis(axis)
    return abs(node.getTranslation(space='world')[axis.index]) < MIRROR_THRESHOLD


def findCenteredParent(node, axis=0):
    """Find the next centered parent node.
    If no parents are centered, uses the highest parent.
    This is used when mirroring joint-hierarchies.

    Args:
        node (pm.PyNode): Node search up from.
        axis (int): Axis to check if centered.

    Returns:
        pm.PyNode: First centered parent.
    """
    if node.getParent() is None:
        return
    # p will be one step ahead
    last = node
    this = node.getParent()
    while this is not None:
        if isCentered(this, axis):
            return this
        last = this
        this = this.getParent()
    return last


def findMirroredParent(node):
    """Find the next parent that is a mirror node or a centered node that can be used as a parent for a new branch.

    Args:
        node (pm.PyNode): Node to trace up from in the hierarchy.

    Returns:
        pm.PyNode
    """
    if node.getParent() is None:
        return
    last = node
    this = node.getParent()
    while this is not None:
        if isMirrorNode(this):
            return this
        last = this
        this = this.getParent()
    return last


def findMirroredOrCenteredParent(node, axis=0):
    """This is used when mirroring joint-chains to preserve a more separated hierarchical structure.

    Args:
        node (pm.PyNode): Node to start search from.
        axis (int): Axis to check if centered.

    Returns:
        pm.PyNode: Logical parent for the node.
    """
    center = findCenteredParent(node, axis)
    mirror = findMirroredParent(node)
    if center is None:
        return mirror
    if mirror is None:
        return center
    if center.hasParent(mirror):
        return center
    if mirror.hasParent(center):
        return mirror
    return center


def determineMirrorMode(a, b):
    """Given two nodes, determine the best mirror mode that describes their current transform relationship.

    Args:
        a (pm.PyNode): First node.
        b (pm.PyNode): Second node.

    Returns:
        str
    """
    awm = utils.getWorldMatrix(a)
    bwm = utils.getWorldMatrix(b)
    aaxes = utils.getBestAxes(awm)
    baxes = utils.getBestAxes(bwm)
    if aaxes == baxes:
        return 'inverse'
    return 'simple'


def cleanup():
    """Remove any mirroring meta data from nodes who are no longer mirrors.

    Args:

    Returns:
        None
    """
    for n in allMirrorNodes():
        validateMirrorNode(n)


def resolveNode(node, other=False):
    """Find a mirror node, if None returns input node.

    Args:
        node (pm.PyNode): Get mirrored node from this one.
        other (bool): If True, resolve the mirrored node.

    Returns:
          pm.PyNode
    """
    if other:
        return getMirrorNode(node)
    return node


class preservedSelection(object):
    """Keeps the current selection for the scope of the given `with` statement.

    Example:
        # >>> pm.polyCube()
        # >>> with preservedSelection() as sel:
        # ...     pm.select(d=1)
        # ...     print pm.selected()
        # Result: []
        # >>> print pm.selected()
        # Result: [nt.Transform(u'pCube1')]
    """

    def __init__(self):
        self.sel = pm.selected()

    def __iter__(self):
        return iter(self.sel)

    def __len__(self):
        return len(self.sel)

    def __getitem__(self, key):
        return self.sel[key]

    def __setitem__(self, key, value):
        self.sel[key] = value

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        valid = [s for s in self.sel if s.exists()]
        pm.select(valid)


class MirrorUtil(object):
    """A basic mirroring util that can duplicate objects,
    mirror their transform matrices, as well as,
    update parenting and hierarchies to match.

    Notes:
        All options are available via the `opts` member.

        The primary methods are:
            `createMirror` -- Handles duplicating nodes and associating them as mirrors, deals with joints.
            `mirrorTransform` -- Handles the actual mirroring and application of matrices between mirror nodes.
            `mirrorParenting` -- Reparent nodes based on their mirror nodes parent, handles joints specially.

        These three operations can be performed together using
        the 'mirror()' method. There are also recursive methods
        available for each of these.
    """

    defaultOptions = dict(
        # global options
        axis=0,
        axisMatrix=None,
        mirrorMode='simple',

        # create mirror options
        replace=False,

        # create and reparent options
        handleJoints=True,

        # mirrorTransform options
        useNodeSettings=True,
        excludedNodeSettings=None,
        mirroredAttrs=[],
        customMirrorAttrExps={},

        # used when getting mirrored matrices
        mirrorTranslate=True,
        mirrorRotate=True,

        # used when applying mirrored matrices
        setTranslate=True,
        setRotate=True,
        setScale=True,
        setAttrs=True,

        # handle colors
        mirrorColor = True,

        # handle shapes
        mirroredCurves = True,

    )

    def __init__(self, **kwargs):
        """Initialize mirroring utility.

        Args:
            **kwargs: Mirror settings.

        Returns:
            None
        """
        self.opts = {}
        self.opts.update(self.defaultOptions)
        self.opts.update(kwargs)

    @property
    def getKwargs(self):
        """Get settings for `getMirrorSettings`."""
        keys = [
            'axis', 'axisMatrix', 'mirrorMode',
            'useNodeSettings', 'excludedNodeSettings',
            'mirroredAttrs', 'customMirrorAttrExps',
        ]
        kwargs = dict([(k, self.opts[k]) for k in keys])
        kwargs['translate'] = self.opts['mirrorTranslate']
        kwargs['rotate'] = self.opts['mirrorRotate']
        kwargs['warn'] = False
        return kwargs

    @property
    def applyKwargs(self):
        """Get settings for `applyMirrorSettings`."""
        return dict(
            translate=self.opts['setTranslate'],
            rotate=self.opts['setRotate'],
            scale=self.opts['setScale'],
            attrs=self.opts['setAttrs'],
        )

    def _recursive(self, arg, fnc, getChildrenFnc, depthLimit=-1):
        """Abstract method for mirroring recursively.

        Args:
            arg: Arguments for the mirroring and getChildren functions.
            fnc: Callable mirroring function.
            getChildrenFnc: Callable to get hierarchy nodes function.
            depthLimit (int): How far down a hierarchy to mirror recursively.

        Returns:
        """
        def f(arg, depth):
            result = [fnc(arg)]
            if depthLimit < 0 or depth < depthLimit:
                for c in getChildrenFnc(arg):
                    result.extend(f(c, depth + 1))
            return result

        return f(arg, 0)

    def _getChildren(self, node):
        """Get all the children that are transforms of a source node.

        Notes:
            Joints will also be returned since they are transforms.

        Args:
            node (pm.PyNode): Node to trace down from.

        Returns:
            list
        """
        return node.listRelatives(typ='transform')

    def mirror(self, sourceNodes, create=True, reparent=True, transform=True):
        """A convenience mirror function.

        Notes:
            Does the following:
                - `createMirror`
                - `mirrorParenting`
                - `mirrorTransform`

        Args:
            sourceNodes (list): Nodes to mirror.
            create (bool): Mirror nodes if they do not exist.
            reparent (bool): Mirror parenting.
            transform (bool): Mirror transforms.

        Returns:
            list: The mirrored node
        """
        sourceNodes = [pm.PyNode(x) for x in utils.asList(sourceNodes)]
        destNodes = []
        if create:
            for n in sourceNodes:
                destNodes.append(self.createMirror(n))
        if reparent:
            for n in sourceNodes:
                self.mirrorParenting(n)
        if transform:
            for n in sourceNodes:
                self.mirrorTransform(n)
        return destNodes

    def mirrorRecursive(self, sourceNodes, create=True, reparent=True, transform=True):
        """A convenience recursive mirror function.

        Notes:
            Does the following:
                - `createMirror`
                - `mirrorParenting`
                - `mirrorTransform`

        Args:
            sourceNodes (list): Nodes to mirror.
            create (bool): Mirroring creation of nodes if they do not exist.
            reparent (bool): Mirroring parenting.
            transform (bool): Mirror transforms.

        Returns:
            list: The mirrored node
        """
        sourceNodes = utils.asList(sourceNodes)
        destNodes = []
        if create:
            for n in sourceNodes:
                destNodes.extend(self.createMirrorRecursive(n))
        if reparent:
            for n in sourceNodes:
                self.mirrorParentingRecursive(n)
        if transform:
            for n in sourceNodes:
                self.mirrorTransformRecursive(n)
        return destNodes

    def createMirror(self, sourceNode):
        """Duplicate the given sourceNode and associate it as a mirror.

        Notes:
            Does not actually mirror the transform matrix of the new node, simply creates an exact duplicate in place.

            `opts` used:
                `replace` -- When False (default) simply returns existing mirror node if one is found.
                `handleJoints` -- Whether to handle joints specially or not, does not mirror centered joints.
                `axis` -- Used when handling joints to determine if they are centered.

        Args:
            sourceNode (pm.PyNode): Node to mirror.

        Returns:
            pm.PyNode
        """
        with preservedSelection():
            destNode = None
            if not self.opts['replace']:
                # look for existing mirror node
                destNode = getMirrorNode(sourceNode)
            if not destNode:

                if self.opts['handleJoints'] and isinstance(sourceNode, pm.nt.Joint) and isCentered(sourceNode, self.opts['axis']):
                    # skip centered joints
                    # TODO: make sure returning None has no ill-effects
                    return

                destNode = pm.duplicate([sourceNode] + sourceNode.getChildren(s=True), po=True)[0]
                # handle error in recent maya versions where extra empty transforms
                # will be included in the duplicate
                extra = destNode.listRelatives(typ='transform')
                if extra:
                    pm.delete(extra)

                destNode.rename(swapMirrorString(sourceNode.nodeName()))

                # associate nodes
                associate(sourceNode, destNode, force=True)

            if self.opts['mirroredCurves']:
                self.mirrorCurveShapes(destNode)

            if self.opts['mirrorColor']:
                self.mirrorColors(sourceNode, destNode)

            return destNode

    def mirrorParenting(self, sourceNode, destNode=None):
        """Parent destNode to match the parenting of the given sourceNode.

        Notes:
            If sourceNode's parent is not a mirror node reparents so that
            the nodes share the same parent, this includes sourceNode
            not having any parent (parent is None).
            This also handles joint parenting, eg. connecting
            inverse scales so that segment scale compensate still works

            `opts` used:
                `handleJoints` -- Whether to handle joints specially or not if True, reparents to next highest centered or mirrored parent.
                `axis` -- Used when handling joints to determine if they are centered.

        Args:
            sourceNode (pm.PyNode): Node to mirror parenting.
            destNode (pm.PyNode): Optional, supply the destination to mirror to.

        Returns:
            None
        """
        with preservedSelection():
            if not destNode:
                destNode = getMirrorNode(sourceNode)
            if not destNode:
                return

            # get parent of source node
            if self.opts['handleJoints'] and isinstance(sourceNode, pm.nt.Joint):
                srcParent = findMirroredOrCenteredParent(sourceNode, self.opts['axis'])
            else:
                srcParent = sourceNode.getParent()

            if srcParent:
                dstParent = getMirrorNode(srcParent)
                if dstParent:
                    destNode.setParent(dstParent)
                else:
                    destNode.setParent(srcParent)
            else:
                destNode.setParent(None)

            # handle joint reparenting
            if isinstance(destNode, pm.nt.Joint):
                p = destNode.getParent()
                if p and isinstance(p, pm.nt.Joint):
                    if not pm.isConnected(p.scale, destNode.inverseScale):
                        p.scale >> destNode.inverseScale

    def mirrorCurveShapes(self, node):
        _axis = utils.getAxis(self.opts['axis'])
        shapes = node.getChildren(s=True)
        for shape in shapes:
            if hasattr(shape, "cv"):
                if self.opts['mirrorMode'] == 'simple':
                    pm.scale(shape.cv, [-1, -1, -1])
                else:
                    s = [1, 1, 1]
                    s[_axis.index] = -1
                    pm.scale(shape.cv, s)

    def mirrorColors(self, sourceNode, destNode=None):
        color = reversed(sourceNode.overrideColorRGB.get())
        destNode.overrideColorRGB.set(*color)

    def mirrorTransform(self, sourceNode, destNode=None):
        """Move a target node to match the given source node.

        Notes:
            See docs for `applyMirrorSettings` and `getMirrorSettings`

            `opts` used when getting a mirrored transform:
                `useNodeSettings`
                `excludedNodeSettings`
                `mirroredAttrs`
                `customMirrorAttrExps`
                `axis`
                `axisMatrix`
                `translate`
                `rotate`
                `mirrorMode`


            `opts` used when applying a mirrored transform:
                `translate`
                `rotate`
                `scale`
                `attrs`

        Args:
            sourceNode (pm.PyNode): Node to use as source transform.
            destNode (pm.PyNode): Optional, supply the destination to mirror to.

        Returns:
            None
        """
        settings = getMirrorSettings(sourceNode, destNode, **self.getKwargs)
        if settings:
            applyMirrorSettings(settings, **self.applyKwargs)

    def createMirrorRecursive(self, sourceNode, depthLimit=-1):
        """Duplicate the supplied sourceNode and associate the duplicate as a mirror.

        Notes:
            Does not actually mirror the sourceNode, simply duplicates.

        Args:
            sourceNode (pm.PyNode): Source node for mirroring.
            depthLimit (int): How many levels to recurse, default is -1 (infinite).

        Returns:
            None
        """
        return self._recursive(sourceNode, self.createMirror, self._getChildren, depthLimit)

    def mirrorParentingRecursive(self, sourceNode, depthLimit=-1):
        """Reparent the mirror nodes of the given source node and all its children to the given depth limit.

        Args:
            sourceNode (pm.PyNode): Source node for mirroring.
            depthLimit (int): How many levels to recurse, default is -1 (infinite).

        Returns:
            None
        """
        return self._recursive(sourceNode, self.mirrorParenting, self._getChildren, depthLimit)

    def mirrorTransformRecursive(self, sourceNode, depthLimit=-1):
        """Mirror the transform matrices of the given node and its children to the given depth limit.

        Args:
            sourceNode (pm.PyNode): Source node for mirroring.
            depthLimit (int): How many levels to recurse, default is -1 (infinite).

        Returns:
            None
        """
        return self._recursive(sourceNode, self.mirrorTransform, self._getChildren, depthLimit)

    def flip(self, sourceNode, destNode=None):
        """Swap transforms between the given two nodes.

        Args:
            sourceNode (pm.PyNode): Node to mirror from.
            destNode (pm.PyNode): Node to mirror to.

        Returns:
            None
        """
        if not destNode:
            destNode = getMirrorNode(sourceNode, warn=True)
            if not destNode:
                return

        sourceSettings = getMirrorSettings(sourceNode, destNode, **self.getKwargs)
        destSettings = getMirrorSettings(destNode, sourceNode, **self.getKwargs)
        if sourceSettings and destSettings:
            applyMirrorSettings(sourceSettings, **self.applyKwargs)
            applyMirrorSettings(destSettings, **self.applyKwargs)

    def flipMultiple(self, sourceNodes, destNodes=None):
        """Swap transforms between the given two node lists.

        Args:
            sourceNodes (list): Nodes to mirror from.
            destNodes (list): Nodes to mirror to.

        Returns:
            None
        """
        if destNodes is None:
            destNodes = [None] * len(sourceNodes)
        # make sure lists are the same length
        if len(sourceNodes) != len(destNodes):
            LOG.warning("Source node list is not the same length as destination node list")
            return
        # get any destination nodes that are None automatically
        for i, source in enumerate(sourceNodes):
            if destNodes[i] is None:
                destNodes[i] = getMirrorNode(source, warn=True)

        allSettings = []

        for i, source in enumerate(sourceNodes):
            if destNodes[i] is not None:
                srcStngs = getMirrorSettings(source, destNodes[i], **self.getKwargs)
                dstStngs = getMirrorSettings(destNodes[i], source, **self.getKwargs)
                allSettings.append((srcStngs, dstStngs))

        for srcStngs, dstStngs in allSettings:
            applyMirrorSettings(srcStngs, **self.applyKwargs)
            applyMirrorSettings(dstStngs, **self.applyKwargs)

    def flipCenter(self, sourceNodes):
        """Given a list of non-mirror nodes, flip them in place.

        Notes:
            Nodes must be given in order of dependency, where parents are first,
            followed by children in hierarchical order.

        Args:
            sourceNodes (list): Nodes to flip.

        Returns:
            None
        """
        stngs = []
        # get all at once
        for n in sourceNodes:
            kwargs = self.getKwargs
            kwargs['mirrorMode'] = 'inverse'
            kwargs['excludedNodeSettings'] = ['mirrorMode']
            s = getMirrorSettings(n, n, **kwargs)
            stngs.append(s)
        # set all at once
        # assumes selection is in parent -> child order
        for s in stngs:
            applyMirrorSettings(s, **self.applyKwargs)


def getMirrorSettings(sourceNode, destNode=None, useNodeSettings=True, excludedNodeSettings=None, warn=True, **kwargs):
    """Get mirror settings for mirroring from the given source node to destination node.

    Args:
        sourceNode (pm.PyNode): The node to get matrix and other settings from.
        destNode (pm.PyNode): The node that will have mirrored settings applied.
        useNodeSettings (bool): Whether to load custom settings from the node or not.
        excludedNodeSettings: A list of settings to exclude when loading from node.
        warn (bool): Whether to warn if the node is not a mirror node.
        **kwargs: Used between 3 mirroring stages:
            See 'getMirroredMatrices' for a list of kwargs that can be given.
                `mirroredAttrs` -- A list list of custom attribute names that will be included when mirroring.
                `customMirrorAttrExps` -- A dictionary of {attr: expression} that are evaluated using the given sourceNode, destNode to determine custom mirroring behaviour for any attributes.

    Returns:
        dict
    """
    result = {}

    LOG.debug("Getting Mirror Settings: {0}".format(sourceNode))
    if not destNode:
        destNode = getMirrorNode(sourceNode, warn=warn)

    if not destNode:
        return

    # if enabled, pull some custom mirroring settings from the node,
    # these are stored in a string attr as a python dict
    if useNodeSettings and isCustomMirrorNode(sourceNode):
        LOG.debug("Custom Mirror Node")
        nodeStngs = loadCustomMirrorSettings(sourceNode)
        LOG.debug("Settings: {0}".format(nodeStngs))
        if excludedNodeSettings is None:
            kwargs.update(nodeStngs)
        else:
            for k in nodeStngs:
                if k not in excludedNodeSettings:
                    kwargs[k] = nodeStngs[k]

    # pull some kwargs used for getMirroredMatrices
    matrixKwargs = dict([(k, v) for k, v in kwargs.items() if k in ('axis', 'axisMatrix', 'translate', 'rotate', 'mirrorMode')])
    result['matrices'] = getMirroredMatrices(sourceNode, **matrixKwargs)

    # add list of mirrored attributes as designated by kwargs
    mirAttrKwargs = dict([(a, getattr(sourceNode, a).get()) for a in kwargs.get('mirroredAttrs', [])])
    result.setdefault('mirroredAttrs', {}).update(mirAttrKwargs)

    for attr, exp in kwargs.get('customMirrorAttrExps', {}).items():
        if exp:
            LOG.debug("Attr: {0}".format(attr))
            LOG.debug("Exp:\n{0}".format(exp))
            val = evalCustomMirrorAttrExp(sourceNode, destNode, attr, exp)
            LOG.debug("Result: {0}".format(val))
            # Eval from the mirror to the dest
            result['mirroredAttrs'][attr] = val

        LOG.debug("Mirrored Attrs: {0}".format(result['mirroredAttrs']))

    # Save additional variables
    result['sourceNode'] = sourceNode
    result['destNode'] = destNode

    return result


def applyMirrorSettings(mirrorSettings, translate=True, rotate=True, scale=True, attrs=True):
    """Set mirror transformations and attributes on the source and destination nodes.

    Notes:
        Mirror Settings should include:
            - source and destination nodes to mirror from/to
            - mirror matrices used to mirror transforms
            - mirror attribute values used to mirror attributes

    Args:
        mirrorSettings (dict): All the information needed to mirror.
        translate (bool): Mirror position.
        rotate (bool): Mirror rotation.
        scale (bool): Mirror scale.
        attrs (bool): Mirror other attributes.

    Returns:
        None
    """

    """
    Apply mirror settings created from getMirrorSettings
    """
    LOG.debug("Applying Mirror Settings: {0}".format(mirrorSettings['destNode']))

    settings = mirrorSettings
    if any([translate, rotate, scale]):
        setMirroredMatrices(settings['destNode'], settings['matrices'], translate=translate, rotate=rotate, scale=scale)

    if attrs:
        LOG.debug("Applying Mirrored Attrs")
        for attrName, val in mirrorSettings.get('mirroredAttrs', {}).items():
            LOG.debug("{0} -> {1}".format(attrName, val))
            attr = settings['destNode'].attr(attrName)
            attr.set(val)


def loadCustomMirrorSettings(node):
    """Get custom mirror data from a node.

    Args:
        node (pm.PyNode): Node to find mirror options on.

    Returns:
        dict
    """
    result = {}
    if not isCustomMirrorNode(node):
        return result

    data = mirrorData.getMirrorData(node)

    if 'customMirror' not in data or 'settings' not in data['customMirror']:
        raise KeyError("Custom Mirror node missing settings")

    settingsStr = data['customMirror']['settings']
    result = ast.literal_eval(settingsStr)

    # Put in a translation layer to allow more flexibility in butterfly rigs between versions
    mirrorMode = result.get('mirrorMode', None)

    # backwards compatibility
    if mirrorMode is None:
        mirrorMode = 'simple' if result.get('axesMirrored', True) else 'inverse'

    settings = {
        'mirrorMode': mirrorMode,
        'customMirrorAttrExps': dict([(attr, data['exp']) for attr, data in result.get('customMirrorAttrs', {}).items()]),
    }

    return settings


CUSTOM_EXP_FMT = """\
def exp():
    {body}return {lastLine}
result = exp()
"""


def evalCustomMirrorAttrExp(sourceNode, destNode, attr, exp):
    """Get mirrored values for a given attribute that exists on both a source and destination node.
    Uses a math expression that dictates how to mirror the value.

    Notes:
        Does not set attr values.

    Args:
        sourceNode (pm.PyNode): Node that sends value to be mirrored.
        destNode (pm.PyNode): Node that receives mirrored attribute.
        attr (str): Attribute name to evaluate mirrored value for.
        exp (str): Math expression that describes how to mirror an attribute.

    Returns:
        dict
    """
    result = {}

    LOG.debug("Raw Exp: {0}".format(repr(exp)))
    _globals = {}
    _globals['node'] = sourceNode
    _globals['dest_node'] = destNode
    if hasattr(sourceNode, attr):
        _globals['value'] = getattr(sourceNode, attr).get()
    else:
        raise KeyError("{0} missing mirrored attr {1}".format(sourceNode, attr))
    if hasattr(destNode, attr):
        _globals['dest_value'] = getattr(destNode, attr).get()
    else:
        raise KeyError("{0} missing mirrored attr {1}".format(sourceNode, attr))

    # Add a return to the last line of the expression
    # so we can treat it as a function
    body = [l for l in exp.strip().split('\n') if l]
    lastLine = body.pop(-1)
    _exp = CUSTOM_EXP_FMT.format(body='\n\t'.join(body + ['']), lastLine=lastLine)
    LOG.debug("Modified Exp:\n{0}".format(_exp))  # TESTING
    LOG.debug("Globals:\n{0}".format(_globals))  # TESTING

    exec (_exp, _globals)
    result = _globals['result']
    LOG.debug("Exp Result: {0}".format(result))  # TESTING

    return result


def getMirroredMatrices(node, axis=0, axisMatrix=None, translate=True, rotate=True, mirrorMode='simple'):
    """Get the mirrored matrix or matrices for the given node

    Notes:
        Handles joints and regular transforms differences.

    Args:
        node (pm.PyNode): Node to mirror data from.
        axis: The axis about which to mirror.
        axisMatrix (pm.dt.Matrix): The matrix in which we should mirror.
        translate (bool): If False, the matrix will not be moved.
        rotate (bool): If False, the matrix will not be rotated.
        mirrorMode (str): What type of mirroring should be performed, 'simple' or 'inverse'.

    Returns:
        dict
    """
    # build kwargs for both commands
    kwargs = dict(
        axis=axis,
        axisMatrix=axisMatrix,
        translate=translate,
        rotate=rotate,
        mirrorMode=mirrorMode,
    )
    result = {}
    if isinstance(node, pm.nt.Joint):
        result['type'] = 'joint'
        jmatrices = utils.getJointMatrices(node)
        result['matrices'] = getMirroredJointMatrices(*jmatrices, **kwargs)
    else:
        result['type'] = 'node'
        result['matrices'] = [getMirroredTransformMatrix(utils.getWorldMatrix(node), **kwargs)]
    return result


def setMirroredMatrices(node, mirroredMatrices, translate=True, rotate=True, scale=True):
    """Set the world matrix for the given node using the given mirrored matrices.

    Notes:
        Handles joints and regular transforms differences.

    Args:
        node (pm.PyNode): Node to mirror.
        mirroredMatrices (list): Matrices needed to mirror a node.
        translate (bool): Mirror Position.
        rotate (bool): Mirror Rotation.
        scale (bool): Mirror scale.

    Returns:
        None
    """
    if mirroredMatrices['type'] == 'joint':
        LOG.debug("Applying Joint Matrices")
        utils.setJointMatrices(node, *mirroredMatrices['matrices'], translate=translate, rotate=rotate)
    else:
        LOG.debug("Applying Transform Matrix")
        utils.setWorldMatrix(node, *mirroredMatrices['matrices'], translate=translate, rotate=rotate, scale=scale)


def getMirroredTransformMatrix(matrix, axis=0, axisMatrix=None, translate=True, rotate=True, mirrorMode='simple'):
    """Get the mirrored version of the given matrix.

    Args:
        matrix (pm.dt.Matrix): Matrix to mirror.
        axis: The axis about which to mirror.
        axisMatrix (pm.dt.Matrix): The matrix in which we should mirror.
        translate (bool): If False, the matrix will not be moved.
        rotate (bool): If False, the matrix will not be rotated.
        mirrorMode (str): Type of mirroring that should be performed, `simple` or `inverse`.

    Returns:
        pm.dt.Matrix
    """
    axis = utils.getAxis(axis)
    if axisMatrix is not None:
        # remove scale from the axisMatrix
        axisMatrix = utils.getScaleMatrix(axisMatrix).inverse() * axisMatrix
        matrix = matrix * axisMatrix.inverse()
    s = utils.getScaleMatrix(matrix)
    r = utils.getRotationMatrix(matrix)
    t = matrix[3]
    if translate:
        # negate translate vector
        t[axis.index] = -t[axis.index]
    if rotate:
        r = utils.invertOtherAxes(r, axis)
        if mirrorMode == 'inverse':
            LOG.debug("Counter Rotating because mirror mode is inverse")
            r = counterRotateForNonMirrored(r, axis)
    mirror = s * r
    mirror[3] = t
    if axisMatrix is not None:
        mirror = mirror * axisMatrix
    return mirror


def getMirroredJointMatrices(matrix, r, ra, jo, axis=0, axisMatrix=None, translate=True, rotate=True, mirrorMode='simple'):
    """Get the mirrored matrices based off the given matrices.

    Args:
        matrix (pm.dt.Matrix): Source node matrix.
        r (pm.dt.Matrix): Source node rotation matrix.
        ra (pm.dt.Matrix): Source node rotateAxis matrix.
        jo (pm.dt.Matrix): Source node jointOrient matrix.
        axis: The axis about which to mirror.
        axisMatrix (pm.dt.Matrix): The matrix in which we should mirror.
        translate (bool): If False, the matrix will not be moved.
        rotate (bool): If False, the matrix will not be rotated.
        mirrorMode (str): What type of mirroring should be performed, eg. 'simple' or 'inverse.

    Returns:
        list: [pm.dt.Matrix, pm.dt.Matrix, pm.dt.Matrix, pm.dt.Matrix]
    """
    LOG.debug("Getting Mirrored Joint Matrices")
    # matches transform orientation
    mirror = getMirroredTransformMatrix(matrix, axis, axisMatrix, translate, rotate)
    if rotate:
        if axisMatrix is not None:
            # matches orientation with jo
            axisMatrix = utils.getScaleMatrix(axisMatrix).inverse() * axisMatrix
            jo = jo * axisMatrix.inverse()
        if mirrorMode == 'simple':
            # flips orientation
            jo = utils.invertOtherAxes(jo, axis)
        if mirrorMode == 'inverse':
            LOG.debug("Counter Rotating because mirror mode is inverse")
            # changes orientation to inverted world
            jo = utils.invertAxis(jo, axis)
            jo = counterRotateForMirroredJoint(jo, axis)
        if axisMatrix is not None:
            # doesnt seem to do anything
            jo = jo.inverse() * axisMatrix
    return mirror, r, ra, jo


def counterRotateForNonMirrored(matrix, axis=0):
    """Essentially rotates 180 on the given axis,
    this is used to create mirroring when
    ctls are setup to not be mirrored at rest pose.

    Args:
        matrix (list): A 4x4 list/array object or pm.dt.Matrix.
        axis: A descriptor for an axis.

    Returns:
        pm.dt.Matrix
    """
    axis = utils.getAxis(axis)
    others = [o.index for o in utils.getOtherAxes(axis)]
    x, y, z = matrix[:3]
    for i, row in enumerate((x, y, z)):
        if i in others:
            for col in range(3):
                row[col] *= -1
    return pm.dt.Matrix(x, y, z)


def counterRotateForMirroredJoint(matrix, axis=0):
    """Essentially rotates 180 on the given axis,
    this is used to create mirroring when
    ctls are setup to not be mirrored at rest pose.

    Args:
        matrix (list): A 4x4 list/array object or pm.dt.Matrix.
        axis: A descriptor for an axis.

    Returns:
        pm.dt.Matrix
    """
    axis = utils.getAxis(axis)
    others = [o.index for o in utils.getOtherAxes(axis)]
    x, y, z = matrix[:3]
    for i, row in enumerate((x, y, z)):
        if i not in others:
            for col in range(3):
                row[col] *= -1
    return pm.dt.Matrix(x, y, z)


