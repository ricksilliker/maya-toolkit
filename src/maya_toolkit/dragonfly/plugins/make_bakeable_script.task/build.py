import os
import imp

import maya.cmds as cmds

import py_tasker.tasks


LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    scene_name = cmds.file(q=True, sn=True)
    rig_dir = os.path.abspath(os.path.dirname(scene_name))
    scripts_dir = os.path.join(rig_dir, 'scripts')

    if len(params['code']) > 0:
        _globals = dict()
        _globals['rig'] = rig

        for child in params['inputs']:
            _globals[child['variable']] = child['node']

        if os.path.exists(scripts_dir):
            python_modules = [os.path.join(scripts_dir, file_name) for file_name in os.listdir(scripts_dir) if
                              file_name.endswith('.py')]
            for mod in python_modules:
                mod_name = file_name.split('.')[0]
                _globals[mod_name] = imp.load_source(mod_name, mod)

        exec(params['code'], _globals)
