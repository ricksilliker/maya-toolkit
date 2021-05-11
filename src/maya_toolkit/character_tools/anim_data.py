import logging
from collections import OrderedDict

import maya.cmds as cmds
import maya.mel as mel


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def get_maya_version():
    """Get Maya API object.

    Returns:
        int: Maya version
    """
    return cmds.about(api=True)


def get_time(start=None, end=None):
    """Get time slider min/max frames.

    Args:
        start: Override to set start frame to
        end: Override to set end frame to

    Returns:
        list: Start frame, end frame
    """
    if start is None:
        start = cmds.playbackOptions(q=True, min=True)
    if end is None:
        end = cmds.playbackOptions(q=True, max=True)

    return start, end


def get_linear_unit():
    """Get linear unit type.

    Returns:
        str: type name
    """
    return cmds.currentUnit(q=True, linear=True)


def get_angular_unit():
    """Get angular unit type.

    Returns:
        str: type name
    """
    return cmds.currentUnit(q=True, angle=True)


def get_time_unit():
    """Get time unit type.

    Returns:
        str: type name
    """
    return cmds.currentUnit(q=True, time=True)


def get_scene_path():
    """Get full local path to scene.

    Returns:
        str: Path
    """
    return cmds.file(q=True, sn=True)


def get_anim_layers():
    """Get animation layer names.

    Returns:
        list: Animation layer names
    """
    return cmds.ls(typ='animLayer')


def get_anim_layer_data(layer_name):
    """Get animation layer attribute data.

    Args:
        layer_name: Name of a layer to query

    Returns:
        dict: Layer data
    """
    attrs = dict()

    attr_names = ['mute', 'lock', 'solo', 'override', 'passthrough', 'preferred', 'weight', 'rotationAccumulationMode', 'scaleAccumulationMode']
    for attr_name in attr_names:
        attrs[attr_name] = cmds.getAttr('{}.{}'.format(layer_name, attr_name))

    return attrs


def get_node_data(node_name, start_time, end_time):
    """Get node keyframe and attribute data within the given time range.

    Args:
        node_name: Name of the node to query
        start_time: Frame to start at
        end_time: Frame to end at

    Returns:
        dict: key/value pairs for attributes/keys
    """
    result = OrderedDict()

    keyable_attrs = [k for k in cmds.listAttr(node_name, k=True) if not cmds.attributeQuery(k, node=node_name, msg=True)]

    keyed_attrs = get_keyed_attributes(node_name)
    baked_attrs = get_baked_attributes(node_name, start_time, end_time)

    for attr in keyable_attrs:
        if attr in keyed_attrs:
            if attr in baked_attrs:
                data = get_baked_node_data(node_name, attr)
            else:
                data = get_anim_node_data(node_name, attr)
        else:
            data = get_static_node_data(node_name, attr)

        result[attr] = data

    return result


def get_keyed_attributes(node_name):
    """Get keyed attributes by querying if an animation curve node is connected to the keyable channels.

    Args:
        node_name: Node to query

    Returns:
        list: Attribute names
    """
    keyed_attrs = list()

    cons = cmds.listConnections(node_name, c=True)
    attr_pairs = [(cons[x], cons[x + 1]) for x in range(0, len(cons), 2)]

    for pair in attr_pairs:
        if cmds.nodeType(pair[1]).startswith('animCurve'):
            keyed_attrs.append(pair[0].split('.', 1)[1])

    return keyed_attrs


def get_baked_attributes(node_name, start_time, end_time):
    """Get list of attributes with keys at every frame.

    Args:
        node_name: Node to query
        start_time: First frame to check
        end_time: Last frame to check

    Returns:
        list: Attribute names
    """
    start_time, end_time = get_time(start_time, end_time)

    result = []

    attrs = get_keyed_attributes(node_name)
    for attr in attrs:
        keyframes = cmds.keyframe('{0}.{1}'.format(node_name, attr), q=True, time=(start_time, end_time))
        if len(keyframes)-1 == (end_time - start_time):
            result.append(attr)

    return result


def get_static_node_data(node_name, attr_name):
    """Get node channel data that has no keys and has not been baked, just set values.

    Args:
        node_name: Node to query
        attr_name: Attribute to query

    Returns:
        dict: Value data
    """
    value = cmds.getAttr('{}.{}'.format(node_name, attr_name))

    result = OrderedDict()
    result['value'] = value
    result['static'] = True

    return result


def get_anim_node_data(node_name, attr_name):
    """Get animation curve data.

    Args:
        node_name: Node to query
        attr_name: Attribute to query

    Returns:
        dict: Value data
    """
    attr = '{0}.{1}'.format(node_name, attr_name)

    anim_curve = cmds.listConnections(attr, c=True, t='animCurve')[1]

    result = OrderedDict()
    result['anim'] = True
    result['weighted'] = cmds.keyTangent(attr, q=True, weightedTangents=True)[0]
    result['preInfinity'] = cmds.getAttr('{0}.preInfinity'.format(anim_curve))
    result['postInfinity'] = cmds.getAttr('{0}.postInfinity'.format(anim_curve))
    result['keys'] = get_node_keyframes(node_name, attr_name)

    return result


def get_baked_node_data(node_name, attr_name):
    """Get all keyframe time and value data for a node's attribute.

    Args:
        node_name: Node to query
        attr_name: Attribute to query

    Returns:
        dict: Value data
    """
    attr = '{0}.{1}'.format(node_name, attr_name)

    result = OrderedDict()
    result['baked'] = True
    result['value'] = [cmds.keyframe(attr, q=True, time=(i, i), eval=True)[0] for i in cmds.keyframe(attr, q=True)]

    return result


def get_node_keyframes(node_name, attr_name):
    """Get keyframe data.

    Args:
        node_name: Node to query
        attr_name: Attribute to query

    Returns:
        list: Keyframe value data
    """
    result = list()

    attr = '{0}.{1}'.format(node_name, attr_name)
    keyframe_indices = cmds.keyframe(attr, q=True)
    for index in keyframe_indices:
        key = dict()
        key['time'] = index
        key['value'] = cmds.keyframe(attr, q=True, time=(index, index), eval=True)[0]
        key['lock'] = cmds.keyTangent(attr, t=(index, index), q=True, l=True)[0]
        key['inTanType'] = mel.eval('keyTangent -time {0} -q -inTangentType "{1}";'.format(index, attr))[0]
        key['inTangent'] = [cmds.keyTangent(attr, t=(index, index), q=True, ix=True)[0],
                            cmds.keyTangent(attr, t=(index, index), q=True, iy=True)[0]]
        key['inTanAngle'] = cmds.keyTangent(attr, t=(index, index), q=True, inAngle=True)[0]
        key['inTanWeight'] = cmds.keyTangent(attr, t=(index, index), q=True, inWeight=True)[0]
        key['outTanType'] = mel.eval('keyTangent -time {0} -q -inTangentType "{1}";'.format(index, attr))[0]
        key['outTangent'] = [cmds.keyTangent(attr, t=(index, index), q=True, ox=True)[0],
                             cmds.keyTangent(attr, t=(index, index), q=True, oy=True)[0]]
        key['outTanAngle'] = cmds.keyTangent(attr, t=(index, index), q=True, outAngle=True)[0]
        key['outTanWeight'] = cmds.keyTangent(attr, t=(index, index), q=True, outWeight=True)[0]

        result.append(key)

    return result


def set_node_keyframes(node_name, attr_name, key_data):
    """Set keyframe data.

    Args:
        node_name: Node
        attr_name: Attribute
        key_data: Data to set
    """
    attr = '{0}.{1}'.format(node_name, attr_name)
    for elem in key_data:
        range = (elem['time'], elem['time'])
        cmds.setKeyframe(node_name, attribute=attr_name, time=range, value=elem['value'])

        cmds.keyTangent(attr, t=range, edit=True, inTangentType=elem['inTanType'], outTangentType=elem['outTanType'])

        cmds.keyTangent(attr, t=range, edit=True, absolute=True, lock=elem['lock'],
                        inAngle=elem['inTanAngle'],
                        inWeight=elem['inTanWeight'])

        cmds.keyTangent(attr, t=range, edit=True, absolute=True, lock=elem['lock'],
                        outAngle=elem['outTanAngle'],
                        outWeight=elem['outTanWeight'])
