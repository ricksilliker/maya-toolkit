import json
import logging

import maya.cmds as cmds


LOG = logging.getLogger(__name__)


def add_clips_attr(node):
    cmds.addAttr(node, ln='clips', dt='string', k=True)
    cmds.setAttr('{0}.clips'.format(node), '[]', type='string')


def get_clips(node):
    clip_data = cmds.getAttr('{0}.clips'.format(node))
    return json.loads(clip_data)


def get_clip(node, index):
    return get_clips(node)[index]


def set_clip(node, index, value):
    clip = get_clip(node, index)
    for num, val in enumerate(value):
        clip.pop(num)
        clip.insert(num, val)


def set_clips(node, *data):
    serialized_data = json.dumps(data)
    cmds.setAttr('{0}.clips'.format(node), serialized_data, type='string')


def delete_clip(node, index):
    clips = get_clips(node)
    clips.pop(index)
    serialized_data = json.dumps(clips)
    cmds.setAttr('{0}.clips'.format(node), serialized_data, type='string')


def add_clip(node):
    data = get_clips(node)
    data.append(['', 0, 0, True])
    serialized_data = json.dumps(data)
    cmds.setAttr('{0}.clips'.format(node), serialized_data, type='string')
