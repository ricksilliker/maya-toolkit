import re
import logging

import maya.cmds as cmds
import maya.api.OpenMaya as om2


LOG = logging.getLogger(__name__)
ATTR_REGEX = re.compile('^[a-zA-Z_]*$')


def getPlusMinusOutput(plug):
    node = plug.split('.', 1)[0]
    # node = om2.MFnDependencyNode(plug.node()).name()
    plug = get_mplug(plug)

    if cmds.nodeType(node) != 'plusMinusAverage':
        raise ValueError('Expected plusMinusAverage node, got {0}'.format(cmds.nodeType(node)))

    if plug.isCompound:
        cmplen = plug.numChildren()
    elif plug.isChild:
        cmplen = plug.parent().numChildren()
    else:
        cmplen = 0

    if cmplen > 0:
        cmpattr = '{}.output{}D'.format(node, cmplen)
        if plug.isChild:
            index = [plug.parent().child(x) for x in range(plug.parent().numChildren())].index(plug)
            return get_mplug(cmpattr).child([index]).partialName(includeNodeName=True, useLongNames=True)
        else:
            return cmpattr

    return '{}.output1D'.format(node)


_OUTPUTS = {
    'addDoubleLinear': 'output',
    'multiplyDivide': 'output',
    'vectorProduct': 'output',
    'blendColors': 'output',
    'reverse': 'output',
    'clamp': 'output',

    'condition': 'outColor',
    'setRange': 'outValue',
    'distanceBetween': 'distance',

    'plusMinusAverage': getPlusMinusOutput,
}


def isAttribute(value):
    # if isinstance(value, NodeExpr):
    #     return True
    # elif cmds.objExists(value):
    #     return True
    # else:
    #     return False
    return isinstance(value, NodeExpr)


def get_mplug(value):
    if isinstance(value, (basestring, om2.MObject)):
        sel = om2.MSelectionList()
        sel.add(value)
        return sel.getPlug(0)


def dimension(plug):
    if not isinstance(plug, om2.MPlug):
        plug = get_mplug(plug)
        if plug is None:
            return 1

    if plug.isCompound:
        return plug.numChildren()
    elif plug.isArray:
        return plug.numElements()
    else:
        return 1


def getUtilityInput(plug, attr, connections=False):
    # if not isAttribute(attr):
    #     raise ValueError('Cannot find correct input plugs for non-attribute: {0}'.format(attr))

    attrdim = dimension(attr)

    if isinstance(plug, (list, tuple)):
        if len(plug) == 0:
            return []
        if len(plug) == 1:
            plug = plug[0]

    indim = dimension(plug)

    def _return(inputs, attrs):
        if connections:
            return zip(inputs, attrs)
        else:
            return attrs

    def _child(obj, index):
        if dimension(obj) == 1:
            return obj
        # elif isAttribute(obj):
        plug = get_mplug(obj)
        if plug.isCompound:
            out_plug = plug.child(index)
            return out_plug.partialName(includeNodeName=True, useLongNames=True)
        elif plug.isArray:
            out_plug = plug.elementByLogicalIndex(index)
            return out_plug.partialName(includeNodeName=True, useLongNames=True)
        else:
            return obj[index]
        # else:
        #     return obj[index]

    if indim == attrdim:
        return _return([plug], [attr])
    else:
        dim = min(indim, attrdim)
        ins = [_child(plug, i) for i in range(dim)]
        ats = [_child(attr, i) for i in range(dim)]
        return _return(ins, ats)


def getUtilityOutput(plug):
    node = plug.split('.', 1)[0]
    type_ = cmds.nodeType(plug)
    if type_ not in _OUTPUTS:
        LOG.warning("No output found for utility type '{0}'".format(type_))
        return None

    output = _OUTPUTS[type_]

    if callable(output):
        return output(plug)
    elif get_mplug('{}.{}'.format(node, output)).isCompound:
        attr = get_mplug(plug)
        if attr.isChild:
            index = [attr.parent().child(x) for x in range(attr.parent().numChildren())].index(attr)
            out_plug = get_mplug('{}.{}'.format(node, output))
            output_children = [out_plug.child(x) for x in range(out_plug.numChildren())]
            return output_children[index].partialName(includeNodeName=True, useLongNames=True)
    return '{}.{}'.format(node, output)


def getBestUtilityOutput(*inputs):
    if len(inputs) == 0:
        return []
    outs = [getUtilityOutput(i) for i in inputs]
    best = outs[0]
    for out in outs:
        if dimension(out) > dimension(best):
            best = out
    return best


def getBestUtilityOutputForInputs(*inputpairs):
    inputs = []
    for pair in inputpairs:
        inputs.extend(getUtilityInput(*pair))
    return getBestUtilityOutput(*inputs)


def setOrConnect(input, attr):
    cons = getUtilityInput(input, attr, connections=True)
    for i, a in cons:
        setOrConnectAttr(i, a)


def setOrConnectAttr(value, attr):
    if cmds.objExists(value):
        cmds.connectAttr(value, attr, force=True)
    else:
        cmds.setAttr(attr, value)
    # if isAttribute(value):
    #     value.connect(attr)
    # else:
    #     attr.set(value)


def plusMinusAverage(in_plugs, operation):
    a = cmds.createNode('plusMinusAverage')
    cmds.setAttr('{}.operation'.format(a), operation)

    if dimension(in_plugs[0]) == 1:
        attr = '{}.input1D'.format(a)
    elif dimension(in_plugs[0]) == 2:
        attr = '{}.input2D'.format(a)
    elif dimension(in_plugs[0]) == 3:
        attr = '{}.input3D'.format(a)
    else:
        raise ValueError('plusMinusAverage node can only handle input lengths of 1, 2 or 3')

    for i, plug in enumerate(in_plugs):
        # plug_name = plug.partialName(includeNodeName=True, useLongNames=True)
        # plug1 = NodeExpr(plug_name)
        setOrConnect(plug, '{}[{}]'.format(attr, i))

    return getUtilityOutput(attr)


def add(*inputs):
    return plusMinusAverage(inputs, 1)


def subtract(*inputs):
    return plusMinusAverage(inputs, 2)


def rsubtract(a, b):
    return subtract(b, a)


def average(*inputs):
    return plusMinusAverage(inputs, 3)


def multiply(a, b):
    return multiplyDivide(a, b, 1)


def divide(a, b):
    return multiplyDivide(a, b, 2)


def rdivide(a, b):
    return divide(b, a)


def pow(a, b):
    return multiplyDivide(a, b, 3)


def sqrt(a):
    return multiplyDivide(a, 0.5, 3)


def multiplyDivide(input1, input2, operation=1):
    nodetype = 'multiplyDivide'
    n = utilityNode(**locals())
    return getBestUtilityOutputForInputs((input1, '{}.input1'.format(n)), (input2, '{}.input2'.format(n)))


def utilityNode(nodetype, **kwargs):
    """
    Create and return a utility node.
    Sets or connects any attributes represented by kwargs.
    """
    node = cmds.createNode(nodetype)
    for key, value in kwargs.items():
        setOrConnect(value, '{}.{}'.format(node, key))
    return node


_fncs = [
    add, subtract, rsubtract, average,
    multiply, divide, rdivide, pow, sqrt
]

allfncs = _fncs[:]


class NodeExpr(object):
    def __init__(self, attr):
        if not cmds.objExists(attr):
            raise ValueError('Attribute does not exist')

        self.attr = attr

        for fnc in _fncs:
            setattr(self, fnc.__name__, self._makefnc(fnc))

    def __getattr__(self, attr):
        if hasattr(self.attr, attr):
            return getattr(self.attr, attr)

    def _makefnc(self, fnc):
        def new(*args, **kwargs):
            args = [self.attr] + list(args)
            for i in range(len(args)):
                if isinstance(args[i], NodeExpr):
                    args[i] = args[i].attr
            return NodeExpr(fnc(*args, **kwargs))
        new.__name__ = fnc.__name__
        new.__doc__ = fnc.__doc__

        return new

    def __repr__(self):
        return 'A({0!r})'.format(self.attr)

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.subtract(other)

    def __rsub__(self, other):
        return self.rsubtract(other)

    def __div__(self, other):
        return self.divide(other)

    def __rdiv__(self, other):
        return self.rdivide(other)

    def __mul__(self, other):
        return self.multiply(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pos__(self):
        return self

    def __neg__(self):
        return self * -1

    @property
    def output(self):
        return getBestUtilityOutput(self.attr)

    def set(self, value):
        cmds.setAttr(self.attr, value)

    def connect(self, other, force=False):
        cmds.connectAttr(self.attr, other.attr, force=force)


def evaluate(expression, **kwargs):
    if not isinstance(expression, basestring):
        raise ValueError('Can only evaluate a string not {}'.format(type(expression)))

    # get node map
    nodeMap = dict()
    nodeMap.update(kwargs)

    if nodeMap:
        build_equation(expression, nodeMap)


def build_equation(equation, nodeMap):
    # split equation
    expFull = subAttrExpression(equation, nodeMap)
    eqsplit = [x.strip() for x in expFull.split('=')]
    env = getEvalEnvironment()
    results = list()
    for eq in eqsplit:
        results.append(eval(eq, env))
    if len(results) == 2:
        setOrConnectAttr(results[1].attr, results[0].attr)


def subAttrExpression(exp, nodeMap):
    newExp = exp
    for k, v in nodeMap.items():
        regex = re.compile('([^\w]?){0}([\.)]\w*)'.format(k))
        newExp = regex.sub('\\1 A(\'{0}\\2\')'.format(v), newExp)
    return newExp


def getEvalEnvironment():
    env = dict(
        cmds=cmds,
        A=NodeExpr
    )
    # add all linker functions
    for fnc in getAttrFuncs():
        env[fnc.__name__] = fnc
    return env


def getAttrFuncs():
    fncs = []
    for fnc in allfncs:
        def wrapFunc(fnc):
            def wrapped(*args, **kwargs):
                return NodeExpr(fnc(*args, **kwargs))
            wrapped.__name__ = fnc.__name__
            wrapped.__doc__ = fnc.__doc__
            return wrapped
        fncs.append(wrapFunc(fnc))
    return fncs