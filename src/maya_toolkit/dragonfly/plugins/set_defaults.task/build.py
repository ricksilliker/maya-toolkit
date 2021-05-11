import json
import ast

import maya.cmds as cmds

import py_tasker.tasks


LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    for ctl in params['controls']:
        defaults_attr = add_default_attr(ctl.name())
        values = dict()
        for attr in cmds.listAnimatable(ctl.name()):
            attrName = attr.split('.')[-1]
            values[attrName] = cmds.getAttr(attr)

        for override in params['overrideAttributes']:
            override_long_name = cmds.attributeQuery(override['attrName'], n=ctl.name(), ln=True)
            values[override_long_name] = ast.literal_eval(override['attrValue'])

        cmds.setAttr(defaults_attr, json.dumps(values), type='string')


def add_default_attr(node):
    if not cmds.attributeQuery('defaults', n=node, ex=True):
        cmds.addAttr(node, ln='defaults', dt='string')

    return '{0}.defaults'.format(node)