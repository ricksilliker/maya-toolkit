import maya.cmds as cmds

import py_tasker.tasks
import dragonfly.meta_types
import dragonfly.modules

import ast
import getpass
import datetime

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):

    top_node = params['rigName']
    rig['asset'] = params['rigName']

    if cmds.objExists(top_node):
        LOG.warning("Top node exists: {}".format(top_node))
    if not cmds.objExists(top_node):
        top_node = cmds.createNode('transform', name='{baseName}_rig'.format(baseName=params['rigName']))

    dragonfly.modules.add_metatype(top_node, dragonfly.meta_types.MTYPE_RIG)
    dragonfly.modules.add_metatype(top_node, 'rig_info')

    rig['rig'] = top_node
    for attr_name in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
        cmds.setAttr('{}.{}'.format(top_node, attr_name), l=True, k=False, cb=False)

    # Add rig data to top node
    rig_data = {}
    rig_data['asset'] = params['rigName']
    rig_data['rigger'] = getpass.getuser()
    rig_data['data_time'] = datetime.date.today().strftime("%B %d, %Y")
    pyToAttr('{baseName}_rig.rig_data'.format(baseName=params['rigName']), rig_data)


def pyToAttr(objAttr, data, lock=True):
    """Write Python data to the given Maya obj.attr.	This data can later be read back via attrToPy().

    Args:
        objAttr: A valid object.attribute name in the scene.
                    If the object exists, but the attribute doesn't, the attribute will be added.
                    If the attribute already exists, it must be of type 'string', so the Python data can be written to it.
        data:   Some Python data, data that will be added to the attribute in question.
        lock:   Lock the attribute to prevent accidental editing

    Examples:
        dictData = {'asset':'YellowButterfly'}# dictionary data
        pyToAttr('YellowButterfly_rig.rig_data', dictData)# stores dictData dictionary to "rig_data" attr
        attrToPy('YellowButterfly_rig.rig_data', 'asset')# retrieves dictionary's "asset" key from "rig_data" attr

        listData = [1,2,3,"this", "is"]
        pyToAttr('YellowButterfly_rig.list_data', listData)
        my_list = attrToPy('YellowButterfly_rig.list_data', None)
    """
    obj, attr = objAttr.split('.')
    if not cmds.objExists(objAttr):
        cmds.addAttr(obj, longName=attr, dataType='string')
    if cmds.getAttr(objAttr, type=True) != 'string':
        raise Exception("Object '%s' already has an attribute called '%s', but it isn't type 'string'"%(obj,attr))

    stringData = data
    cmds.setAttr(objAttr, stringData, type='string')
    if lock:
        cmds.setAttr(objAttr, lock=True)


def attrToPy(objAttr, key):
    """Take previously stored data on a Maya attribute (put there via pyToAttr() ) and read it back to valid Python values.

    Args:
        objAttr:    A valid object.attribute name in the scene.	And of course, it must have already had valid Python data pickled to it.
        key:        Optional key to specify

    Examples:
        See above pyToAttr
    """
    if cmds.objExists(objAttr):
        stringAttrData = str(cmds.getAttr(objAttr))
        data_dict = ast.literal_eval(stringAttrData)
        if key:
            return data_dict[key]
        else:
            return data_dict
    else:
        return None
