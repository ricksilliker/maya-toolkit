import os

import maya.cmds as cmds

def get_scene_directory(path=None):
    """Get the directory of the given path or get the current Maya scene directory.

    Args:
        path: Optional path to a file

    Returns:
        str: Directory where the input scene exists
    """
    if path is None:
        path = get_scene()

    return os.path.dirname(path)

def get_scene():
    """Get the scene path of the current Maya scene.

    Returns:
        str: Full file path
    """
    return cmds.file(q=True, sn=True)