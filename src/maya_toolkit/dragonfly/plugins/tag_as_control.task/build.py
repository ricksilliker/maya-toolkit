import py_tasker.tasks
import dragonfly.modules
import dragonfly.meta_types

import maya.cmds as cmds


LOG = py_tasker.tasks.get_task_logger(__name__)
BUF = "buf"
CTL = "ctl"


def setUp(params, spec):
    pass


def run(params, rig):
    for node in params['nodes']:
        dragonfly.modules.add_metatype(node.name(), dragonfly.meta_types.MTYPE_CTL)

    if params['freezeScale']:
        with TempParentToWorld(params['nodes']):
            with KeepPoints(params['nodes']):
                for node in params['nodes']:
                    # Store the rotations and rotate axes that will be lost
                    # when we freeze the scale
                    rotateAxis_attr = '{}.rotateAxis'.format(node.name())
                    rotate_attr = '{}.rotate'.format(node.name())
                    ra = cmds.getAttr(rotateAxis_attr)[0]
                    r = cmds.getAttr(rotate_attr)[0]
                    # reset scale
                    cmds.makeIdentity(node.name(), apply=True, s=True, r=False, t=False)
                    # Restore rotations and rotate axis
                    cmds.setAttr(rotateAxis_attr, *ra)
                    cmds.setAttr(rotate_attr, *r)

    if params['createOffset']:
        for node in params['nodes']:
            buffer = ""
            if CTL in node.name():
                buffer = cmds.createNode('transform', n='{0}{1}'.format(node.name().replace(CTL, ""), BUF))
            else:
                buffer = cmds.createNode('transform', n='{0}_{1}'.format(node.name(), BUF))
            node_position = cmds.xform(node.name(), q=True, ws=True, t=True)
            node_rotation = cmds.xform(node.name(), q=True, ws=True, ro=True)

            cmds.xform(buffer, ws=True, t=node_position)
            cmds.xform(buffer, ws=True, ro=node_rotation)

            node_parent = cmds.listRelatives(node.name(), p=True)
            if node_parent:
                cmds.parent(buffer, node_parent[0])
            cmds.parent(node.name(), buffer)

    if params['hiddenAttrs']:
        hiddenAttrs = [attr for attr in params['hiddenAttrs'].replace(' ', '').split(",")]

        for attr in hiddenAttrs:
            for node in params['nodes']:
                if not cmds.attributeQuery(attr, node=node.name(), exists=True):
                    LOG.warning('Could not find attribute: {0}.{1}'.format(node.name(), attr))
                    continue

                cmds.setAttr('{}.{}'.format(node.name(), attr), cb=False, k=False)

    if params['lockedAttrs']:
        lockedAttrs = [attr for attr in params['lockedAttrs'].replace(' ', '').split(",")]

        for attr in lockedAttrs:
            for node in params['nodes']:
                if not cmds.attributeQuery(attr, node=node.name(), exists=True):
                    LOG.warning('Could not find attribute: {0}.{1}'.format(node.name(), attr))
                    continue

                cmds.setAttr('{}.{}'.format(node.name(), attr), l=True)


class TempParentToWorld(object):
    def __init__(self, nodes):
        self.nodes = list()
        for node in nodes:
            info = dict()
            info['node'] = node.name()
            info['children'] = cmds.listRelatives(node.name(), children=True, type='transform')
            info['parent'] = cmds.listRelatives(node.name(), parent=True)
            self.nodes.append(info)

    def __enter__(self):
        for nodeInfo in self.nodes:
            if cmds.listRelatives(nodeInfo['node'], p=True):
                cmds.parent(nodeInfo['node'], w=True)

            if nodeInfo.get('children'):
                for c in nodeInfo['children']:
                    if cmds.listRelatives(c, p=True):
                        cmds.parent(c, w=True)
        return self

    def __exit__(self, type, value, traceback):
        for nodeInfo in self.nodes:
            if cmds.listRelatives(nodeInfo['node'], p=True) != nodeInfo['parent']:
                cmds.parent(nodeInfo['node'], nodeInfo['parent'][0])

            if nodeInfo.get('children'):
                for c in nodeInfo['children']:
                    if cmds.listRelatives(c, p=True) != [nodeInfo['node']]:
                        cmds.parent(c, nodeInfo['node'])


class KeepPoints(object):
    def __init__(self, nodes):
        self.nodes = list()
        for node in nodes:
            info = dict()
            info['node'] = node.name()
            info['cvData'] = [storeCVPositions(shp) for shp in cmds.listRelatives(node.name(), s=True) if cmds.nodeType(node.name()) == 'nurbsCurve']
            info['vtxData'] = [storeVTXPositions(shp) for shp in cmds.listRelatives(node.name(), s=True) if cmds.nodeType(node.name()) == 'mesh']
            self.nodes.append(info)

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        for info in self.nodes:
            for data in info['cvData']:
                restoreCVPositions(data)
            for data in info['vtxData']:
                restoreVTXPositions(data)


def storeCVPositions(node):
    result = {}
    if cmds.nodeType(node) == 'transform':
        shapes = cmds.listRelatives(node, sh=True)
    else:
        shapes = [node]
    for shp in shapes:
        cv_length = len(cmds.getAttr('{}.cv[:]'.format(shp)))
        shpPos = [(i, cmds.xform('{}.cv[{}]'.format(shp, i), q=True, ws=True, t=True)) for i in range(cv_length)]
        result[shp] = shpPos
    return result


def restoreCVPositions(positionData):
    for shp, posData in positionData.items():
        for i, pos in posData:
            cmds.xform(cmds.xform('{}.cv[{}]'.format(shp, i)), ws=True, t=pos)


def storeVTXPositions(node):
    result = {}
    if cmds.nodeType(node) == 'transform':
        shapes = cmds.listRelatives(node, sh=True)
    else:
        shapes = [node]
    for shp in shapes:
        vtx_length = len(cmds.getAttr('{}.vtx[:]'.format(shp)))
        shpPos = [(i, cmds.xform('{}.vtx[{}]'.format(shp, i), q=True, ws=True, t=True)) for i in range(vtx_length)]
        result[shp] = shpPos
    return result


def restoreVTXPositions(positionData):
    for shp, posData in positionData.items():
        for i, pos in posData:
            cmds.xform(cmds.xform('{}.vtx[{}]'.format(shp, i)), ws=True, t=pos)
