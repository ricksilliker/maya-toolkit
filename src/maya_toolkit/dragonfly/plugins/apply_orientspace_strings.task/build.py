import py_tasker.tasks

import maya.cmds as cmds

LOG = py_tasker.tasks.get_task_logger(__name__)
VERSION = '1.0.0'


def run(params, rig):
    for cat in params['spaces']:
        target = cat['target']

        space_names = cat['spaces'].replace(' ', '')
        space_names = space_names.split(',')

        if 'world' in space_names:
            world_space_node = None

            for x in cmds.ls('*.spaceName'):
                if cmds.getAttr(x) == 'world':
                    world_space_node = x.split('.', 1)[0]

            if world_space_node is None:
                world_space_node = cmds.createNode('transform', n='world')
                world_space_op = CreateSpace()
                world_space_op.name = 'world'
                world_space_op.target = world_space_node
                world_space_op.run()
                cmds.parent(world_space_node, rig['spacesGroup'])

        space_nodes = [x for x in cmds.ls('*.spaceName') if cmds.getAttr(x) in space_names]
        space_nodes.sort(key=lambda x: space_names.index(cmds.getAttr(x)))
        space_nodes = [x.split('.', 1)[0] for x in space_nodes]

        # Add "parent" space
        space_names.insert(0, "parent")
        space_nodes.insert(0, cat['targetParentNode'])

        cmds.addAttr(target, ln='spaces', at='enum', en=':'.join(space_names), k=True)

        # create offset node above `target`
        apply_space_node = cmds.createNode('transform', n='{0}_applySpace'.format(target))
        cmds.addAttr(apply_space_node, ln='spaceTarget', at='message')
        target_position = cmds.xform(target, q=True, ws=True, t=True)
        cmds.xform(apply_space_node, ws=True, t=target_position)
        cmds.delete(cmds.orientConstraint(target, apply_space_node))

        cmds.parent(apply_space_node, cmds.listRelatives(target, p=True)[0])
        cmds.parent(target, apply_space_node)

        cmds.addAttr(target, ln='applySpaceNode', at='message')
        cmds.connectAttr('{}.applySpaceNode'.format(target), '{}.spaceTarget'.format(apply_space_node))

        # create constraints that handle transformation changes
        cnst = cmds.orientConstraint(space_nodes, apply_space_node, mo=True)[0]
        sc = cmds.scaleConstraint(space_nodes, apply_space_node, mo=True)[0]
        weightList = cmds.orientConstraint(cnst, query=True, weightAliasList=True)

        for index, spaceNode in enumerate(weightList):
            # create condition node to handle target weight toggle for `spaces` attribute
            condition_node = cmds.createNode('condition')
            cmds.setAttr('{}.secondTerm'.format(condition_node), index)
            cmds.setAttr('{}.operation'.format(condition_node), 0)
            cmds.setAttr('{}.colorIfTrue'.format(condition_node), 1, 1, 1)
            cmds.setAttr('{}.colorIfFalse'.format(condition_node), 0, 0, 0)

            cmds.connectAttr('{}.spaces'.format(target), '{}.firstTerm'.format(condition_node))
            cmds.connectAttr('{}.outColorR'.format(condition_node), '{}.{}'.format(cnst, weightList[index]), force=True)
            cmds.connectAttr('{}.outColorR'.format(condition_node), '{}.{}'.format(sc, weightList[index]), force=True)

        cmds.setAttr('{}.spaces'.format(target), 0)
        cmds.setAttr('{}.offset'.format(cnst), 0,0,0)


class CreateSpace(object):
    name = 'world'
    target = None
    delegates = []

    def run(self):
        cmds.addAttr(self.target, ln='spaceName', dt='string')
        cmds.setAttr('{}.spaceName'.format(self.target), self.name, type='string')

        cmds.addAttr(self.target, ln='spaceDelegates', at='message')
        if self.delegates:
            for node in self.delegates:
                cmds.addAttr(node, ln='spaceRoot', at='message')
                cmds.connectAttr('{}.spaceDelegates'.format(self.target), '{}.spaceRoot'.format(node))
