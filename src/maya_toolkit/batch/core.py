import os
import subprocess
import tempfile

import utils

STARTUP_CMD = """
import maya.standalone
import maya.cmds as cmds
import maya.api.OpenMaya as om2
maya.standalone.initialize()
"""

OPEN_CMD = """
cmds.file({scenePath}, o=True, f=True)
"""

SAVE_CMD = """
if {0}:
    ext_type = cmds.file({scenePath}, q=True, typ=True)
    cmds.file({scenePath}, s=True, typ=ext_type)
"""

SHUTDOWN_CMD = """
maya.standalone.uninitialize()
"""


def run_python_script(py_script, maya_version=2016.5):
    with open(py_script) as fp:
        script = fp.read()

    script = '\n'.join([STARTUP_CMD, script, SHUTDOWN_CMD])

    script_obj, script_path = tempfile.mkstemp()
    os.write(script_obj, script)

    output = subprocess.check_output([utils.mayapy(maya_version), script_path])

    return output


def run_python_code(code, maya_version=2016.5):
    script = '\n'.join([STARTUP_CMD, code, SHUTDOWN_CMD])

    script_obj, script_path = tempfile.mkstemp()
    os.write(script_obj, script)

    output = subprocess.check_output([utils.mayapy(maya_version), script_path])

    return output


def run_python_on_scene(py_script, scene_path, maya_version=2016.5, save_scene=True):
    if os.path.isfile(py_script):
        with open(py_script) as fp:
            script = fp.read()
    else:
        script = py_script

    script = '\n'.join([STARTUP_CMD, OPEN_CMD.format(scenePath=scene_path), script, SAVE_CMD.format(save_scene), SHUTDOWN_CMD])

    script_obj, script_path = tempfile.mkstemp()
    os.write(script_obj, script)

    output = subprocess.check_output([utils.mayapy(maya_version), script_path])

    return output
