import logging
from collections import OrderedDict

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om2
import yaml

import anim_data


LOG = logging.getLogger(__name__)


def get_selection():
    """Get user selection.

    Returns:
        list: Maya API objects
    """
    result = list()

    selection = om2.MGlobal.getActiveSelectionList()
    for x in range(selection.length()):
        dep_node = selection.getDependNode(x)
        if dep_node.hasFn(om2.MFn.kDagNode):
            result.append(dep_node)

    return result


def get_common_spaces(nodes):
    """Get list of common spaces between all nodes.

    Args:
        nodes: Input nodes to query space list

    Returns:
        list: Common list of space names
    """
    common_spaces = list()

    for node in nodes:
        dep_node = om2.MFnDependencyNode(node)
        if dep_node.hasAttribute('spaces'):
            attr = om2.MFnEnumAttribute(dep_node.attribute('spaces'))
            space_names = list()
            for x in range(attr.getMax()+1):
                space_names.append(attr.fieldName(x))
            common_spaces.append(space_names)

    sets = [set(sublist) for sublist in common_spaces]
    if sets:
        return sets[0].intersection(*sets[1:])
    else:
        return []


def set_space(nodes, space_name):
    """Set the given nodes to the given existing space.

    Args:
        nodes: Maya API objects to set to given space
        space_name: space name to switch nodes into
    """
    for node in nodes:
        dep_node = om2.MFnDependencyNode(node)
        node_full_name = dep_node.absoluteName()
        attr = om2.MFnEnumAttribute(dep_node.attribute('spaces'))
        space_index = attr.fieldValue(space_name)

        world_position = cmds.xform(node_full_name, q=True, ws=True, t=True)
        world_rotation = cmds.xform(node_full_name, q=True, ws=True, ro=True)

        dep_node.findPlug('spaces', True).setInt(space_index)
        cmds.setAttr('{0}.spaces'.format(node_full_name), space_index)

        cmds.xform(node_full_name, ws=True, t=world_position)
        cmds.xform(node_full_name, ws=True, ro=world_rotation)


def add_selection_callback(func):
    """Create a new selection change callback event to a given callable.

    Args:
        func: Callable object

    Returns:
        long: Callback ID for new event added
    """
    return om2.MEventMessage.addEventCallback('SelectionChanged', func)


def remove_callbacks(ids):
    """Remove callbacks.

    Args:
        ids: List of callback IDs
    """
    om2.MMessage.removeCallbacks(ids)


def get_range_selection(control=None):
    """Get the selected range or the min/max of the timeline.

    Args:
        control: timeControl UI object to query

    Returns:
        list: Start and end frame
    """
    if control is None:
        control = mel.eval('global string $gPlayBackSlider; $temp=$gPlayBackSlider;')
    if cmds.timeControl(control, q=True, rv=True):
        raw_value = cmds.timeControl(control, q=True, rng=True)
        start_frame, end_frame = raw_value.strip('"').split(':')
    else:
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

    return int(start_frame), int(end_frame)


def get_channelbox_selection(control=None):
    """Get the selected attributes or all keyable for the selected nodes.

    Args:
        control: Channel Box UI object to query

    Returns:
        list: Attribute names
    """
    if control is None:
        control = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')

    return cmds.channelBox(control, q=True, sma=True) or []


def cut_keys():
    """Get the keyframe data then clear for the selected objects.

    Returns:
        dict: Attribute name keys with values of keyframe data
    """
    nodes = cmds.ls(sl=True, l=True)
    frame_range = get_range_selection()
    data = copy_keys()
    for node in nodes:
        cmds.cutKey(node, time=frame_range, cl=True)

    return data


def copy_keys():
    """Get the keyframe data for the selected objects.

    Returns:
        dict: Attribute name keys with values of keyframe data
    """
    nodes = cmds.ls(sl=True, l=True)
    if not nodes:
        raise ValueError('No objects selected, select an object with keyframes')
    if len(nodes) != 1:
        raise ValueError('Can only copy one object at a time, select a single object')

    attrs = get_channelbox_selection() or cmds.listAttr(nodes[0], keyable=True)
    frame_range = get_range_selection()
    frame_range = range(frame_range[0], frame_range[1] + 1)
    result = dict()
    for attr in attrs:
        out_data = list()
        raw_data = anim_data.get_node_keyframes(nodes[0], attr)
        for elem in raw_data:
            if elem['time'] in frame_range:
                out_data.append(elem)
        result[attr] = out_data

    LOG.info(result)

    return result


def paste_keys(data):
    """Set keyframe data exactly onto the selected objects.

    Args:
        data: Keyframe data from copy/cut functions
    """
    nodes = cmds.ls(sl=True, l=True)
    for node in nodes:
        for attr, values in data.items():
            LOG.debug('Setting keyframe on {0}.{1}'.format(node, attr))
            anim_data.set_node_keyframes(node, attr, values)


class AnimUtil(object):
    """Utility to manipulate animation data across objects and scenes.

    Attributes:
        default_opts: Default options that can be configured for the object.
    """
    default_opts = dict(
        startTime=None,
        endTime=None
    )

    def __init__(self, **kwargs):
        """Initialize.

        Args:
            **kwargs: key/value pairs to override attribute `default_opts`
        """
        self.opts = dict()
        self.opts.update(self.default_opts)
        self.opts.update(kwargs)

    def _dict_representer(self, dumper, data):
        """Add a Dumper representer for OrderedDict.

        Args:
            dumper: YAML Dumper object to add representer to
            data: Data for representer

        Returns:
            data reconfigured
        """
        return dumper.represent_dict(data.items())

    def set_data(self, data, nodes, scene=True, layers=True, animation=True):
        """Not Implemented"""
        pass

    def get_data(self, nodes, scene=True, layers=True, animation=True):
        """Create a valid output object for export function.

        Args:
            nodes: Nodes to store output for
            scene: Save scene info data
            layers: Save animation layer data
            animation: Save keyframe and attribute data

        Returns:
            dict: A valid yaml dump object
        """
        out_data = OrderedDict()
        if scene:
            self.set_header(out_data)
        if layers:
            self.set_anim_layers(out_data)
        if animation:
            self.set_body(out_data, nodes)

        return out_data

    def export(self, nodes, output_path, scene=True, layers=True, animation=True):
        """Export animation data to a yaml file.

        Args:
            nodes: Nodes to output keyframe and attribute data for
            output_path: Path to save output object
            scene: Save header data
            layers: Save anim layer data
            animation: Save body data
        """
        yaml.Dumper.add_representer(OrderedDict, self._dict_representer)
        yaml.Dumper.add_representer(str, yaml.representer.SafeRepresenter.represent_str)
        yaml.Dumper.add_representer(unicode, yaml.representer.SafeRepresenter.represent_unicode)

        out_data = self.get_data(nodes, scene, layers, animation)

        with open(output_path, 'w') as fp:
            yaml.dump(out_data, fp, Dumper=yaml.Dumper, default_flow_style=False)

        LOG.info('Animation exported successfully: {0}'.format(output_path))

    def set_header(self, out_data):
        """Save scene data to an output object.

        Args:
            out_data: Output object to store data in
        """
        out_data['mayaVersion'] = anim_data.get_maya_version()
        out_data['sceneFile'] = anim_data.get_scene_path()
        out_data['timeUnit'] = anim_data.get_time_unit()
        out_data['linearUnit'] = anim_data.get_linear_unit()
        out_data['angularUnit'] = anim_data.get_angular_unit()
        time_start, time_end = anim_data.get_time(self.opts['startTime'], self.opts['endTime'])
        out_data['startTime'] = time_start
        out_data['endTime'] = time_end

    def set_anim_layers(self, out_data):
        """Save the animation layer data to an output object.

        Args:
            out_data: Output object to store data in
        """
        existing_anim_layers = anim_data.get_anim_layers()
        out_data['animLayers'] = {k: anim_data.get_anim_layer_data(k) for k in existing_anim_layers}

    def set_body(self, out_data, nodes):
        """Save the attribute and keyframe data to an output object.

        Args:
            out_data:
            nodes: Objects to query keyframe data for
        """
        for node in nodes:
            out_data[node] = anim_data.get_node_data(node, self.opts['startTime'], self.opts['endTime'])

