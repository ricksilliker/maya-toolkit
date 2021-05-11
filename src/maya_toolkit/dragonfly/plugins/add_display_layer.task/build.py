import py_tasker.tasks

import maya.cmds as cmds
import maya.api.OpenMaya as om2

LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '1.0.0'


def run(params, rig):
    for num, element in enumerate(params['layers']):
        nodes = [x.name() for x in element['objects']]
        if not cmds.objExists(element['name']):
            display_layer = cmds.createDisplayLayer(nodes, n=element['name'])
        else:
            cmds.editDisplayLayerMembers(element['name'], nodes)
            display_layer = element['name']

        cmds.setAttr('{}.visibility'.format(display_layer), element['visible'])
        for attr in ('displayType', 'shading', 'texturing', 'playback'):
            attr_name = '{}.{}'.format(display_layer, attr)
            cmds.setAttr(attr_name, element[attr])