import maya.cmds as cmds

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    LOG.debug('Running rig rename functions..')

    advancedSkeletonToMLRigRename = params['advancedSkeletonToMLRigRename']
    if advancedSkeletonToMLRigRename:
        # Store Name History
        top_node = rig['rig']
        addNameHistoryAttrToNodeHierarchy(top_node)
        do_advancedSkeletonToMLRigRename()




NAMES_AS = {
    "TWIST": "Part",
    "COLLAR": "Scapula",
    "UPARM": "Shoulder",
    "LOARM": "Elbow",
    "WRIST": "Wrist",
    "UPLEG": "Hip",
    "LOLEG": "Knee",
    "FOOT": "Ankle",
    "TOE": "Toes",
}

NAMES_NEW = {
    "TWIST": "Twist",
    "COLLAR": "clavicle",
    "UPARM": "shoulder",
    "LOARM": "elbow",
    "WRIST": "hand",
    "UPLEG": "hip",
    "LOLEG": "knee",
    "FOOT": "ankle",
    "TOE": "toes",
}

# ADVANCED SKELETON SIDES
LEFT_AS = '_L'
RIGHT_AS = '_R'
CENTER_AS = '_M'
MIDDLE_AS = '_M'
BACK_AS = '_BK'
FRONT_AS = '_FT'
TOP_AS = '_TP'
BOT_AS = '_BT'
IN_AS = '_IN'
OUT_AS = '_OT'
UP_AS = '_UP'
DOWN_AS = '_DN'
SIDES_AS = {'left': LEFT_AS, 'right': RIGHT_AS, 'center': CENTER_AS, 'middle': MIDDLE_AS,
            'back': BACK_AS, 'front': FRONT_AS, 'top': TOP_AS, 'bottom': BOT_AS,
            'in': IN_AS, 'out': OUT_AS, 'up': UP_AS, 'down': DOWN_AS}

# RENAME SIDES
LEFT = 'lf_'
RIGHT = 'rt_'
CENTER = 'cn_'
MIDDLE = 'cn_'
BACK = 'bk_'
FRONT = 'ft_'
TOP = 'tp_'
BOT = 'bt_'
IN = 'in_'
OUT = 'ot_'
UP = 'up_'
DOWN = 'dn_'
SIDES = {'left': LEFT, 'right': RIGHT, 'center': CENTER, 'middle': MIDDLE,
         'back': BACK, 'front': FRONT, 'top': TOP, 'bottom': BOT,
         'in': IN, 'out': OUT, 'up': UP, 'down': DOWN}

# Controls and hierarchies
ROOT = '_zero'
GRP = '_grp'
CTRL = '_ctl'
POLEVECTOR = '_pv'
GMBL = '_gmbl'
HUB = '_hub'
CTRLTAG = CTRL.replace('_', '').capitalize()
CTRLSGRP = CTRL.replace('_', '') + '_shapes_grp'
EXP = '_export'
DUP = '_duplicate'
SHAPEGRP = 'controlShapes'
CRV = '_crv'
SPACER = '_spacer'

# FK IK
FK = '_fk'
IK = '_ik'
IKH = '_ikh'
BLEND = '_blend'
FKIK = '_fkik'
SWITCH = 'ik'

# Joints
JNT = '_jnt'
TWIST = '_twist'
DEF = '_def'
RIG = '_rig'

# Pairs of existing names (key), and new name to replace with (value)
TOP_NODE_RENAME = {
    'RootExtraX_M':'cn_body_ctl',
    'RootX_M':'cn_cog_ctl',
    'Main':'cn_masterOffset_ctl',
}
"""
TOP_NODE_RENAME = {
    'RootExtraX_M':'cn_body_ctl',
    'RootX_M':'cn_cog_ctl',
    'Cn_spineBase_jnt': 'Cn_body_jnt',
    'Cn_master': 'Cn_master_ctrl',
    'main_ctrl': 'Cn_masterOffset_ctrl',
    'Cn_rootX_ctrl': 'Cn_cog_ctrl',
    'Cn_rootExtraX_ctrl': 'Cn_body_ctrl',
    'Cn_hipSwinger_ctrl': 'Cn_pelvis_ctrl',

    'Lf_iKArm_fk_ctrl': 'lf_FKIKArm_switch_ctrl',
    'Rt_iKArm_fk_ctrl': 'rt_FKIKArm_switch_ctrl',
    'Lf_iKLeg_fk_ctrl': 'lf_FKIKLeg_switch_ctrl',
    'Rt_iKLeg_fk_ctrl': 'rt_FKIKLeg_switch_ctrl',
    'Cn_iKSpine_fk_ctrl': 'cn_FKIKSpine_switch_ctrl',
    'Cn_iKSpline_fk_ctrl': 'cn_FKIKNeck_switch_ctrl',
    'Cn_iKSplineTail_fk_ctrl': 'cn_FKIKTail_switch_ctrl',
}
"""


def do_advancedSkeletonToMLRigRename():
    """ Calls rename functions to rename rig nodes """
    try:
        topNodeRename(TOP_NODE_RENAME)
        toLowerCase()
        sideRenameSuffixToPrefix()
        jointRename()
        controlRename()
        nodeTypeRename()
        asNodeRename()
        #topNodeRename(TOP_NODE_RENAME)
    except:
        pass


def toLowerCase():
    if cmds.objExists("Root_M"):
        try:
            cmds.sets("Root_M", edit=True, add="AllSet")
        except:
            pass

    if cmds.objExists("AllSet"):
        ctl_nodes = cmds.sets("ControlSet", q=True)
        dfm_nodes = cmds.sets("DeformSet", q=True)
        all_nodes = ctl_nodes + dfm_nodes
        if all_nodes:
            for node in all_nodes:
                newNm = node[0].lower() + node[1:]
                try:
                    cmds.rename(node, newNm)
                except:
                    pass


def sideRenameSuffixToPrefix():
    """ Replaces side suffix with side prefix """
    for side, asSide in SIDES_AS.iteritems():
        nodesSide = cmds.ls('*%s' % asSide, '*%s_*' % asSide)
        if nodesSide:
            for node in nodesSide:
                if not '_MoCap_' in node:
                    try:
                        nodeNm = node.replace('%s' % asSide, '')
                        cmds.rename(node, '%s%s' % (SIDES[side], nodeNm))
                        LOG.debug("Renamed %s to %s%s" % (node, SIDES[side], nodeNm))
                    except:
                        LOG.error("Error renaming %s" % node)


def jointRename():
    """ Adds joint suffix to all joints in scene """
    jointList = cmds.ls(type='joint')
    if jointList:
        for jnt in jointList:
            if not "_jnt" in jnt:
                try:
                    if not JNT in jnt:
                        cmds.rename(jnt, '%s%s' % (jnt, JNT))
                except:
                    LOG.error("Error renaming %s" % jnt)


def controlRename():
    """ Adds control naming suffix to all controls under ControlSet """
    if cmds.objExists('ControlSet'):
        controlList = cmds.sets('ControlSet', query=True)
        if controlList:
            for ctrl in controlList:
                if not CTRL in ctrl:
                    cmds.rename(ctrl, '%s%s' % (ctrl, CTRL))


def nodeTypeRename():
    """ Adds nodeType suffix to nodes in scene """
    # typeDict = {'FK': FK, 'IK': IK}
    typeDict = {'fK': FK, 'iK': IK}
    for asType, newType in typeDict.iteritems():
        for asType, newType in typeDict.iteritems():
            allType = cmds.ls('*_%s*' % asType)
            if allType:
                for nodeNm in allType:
                    try:
                        descStr = nodeNm.split('_')[1]
                        descStrNew = '%s%s' % (descStr.replace(asType, ''), newType)
                        descStrNewLowerCase = descStrNew[0].lower() + descStrNew[1:]
                        cmds.rename(nodeNm, nodeNm.replace(descStr, descStrNewLowerCase))
                    except:
                        pass


def asNodeRename():
    """ Specific Advanced Skeleton node naming replacement """
    # First rename preset rename dictionaries
    for nameKey, asName in NAMES_AS.iteritems():
        for asNameCase in ["upper", "lower"]:
            if "lower" in asNameCase:
                asName = asName.lower()

            nodeNames = cmds.ls("*%s*" % asName)
            if nodeNames:
                for node in nodeNames:
                    try:
                        newNm = node.replace(asName, NAMES_NEW[nameKey])
                        cmds.rename(node, newNm)
                        LOG.debug('Renamed %s to --->>> %s' % (node, newNm))
                    except:
                        pass


def topNodeRename(renameDict=TOP_NODE_RENAME):
    """ Explicit top node renaming """
    for origName, newName in renameDict.iteritems():
        if cmds.objExists(origName):
            cmds.rename(origName, newName)


def addNameHistoryAttrToNodeHierarchy(topNode):
    '''
    Stores the original name of nodes under the topNode hierarchy to a nameHistory attribute

    addNameHistoryAttrToNodeHierarchy('MotusMan')
    '''
    nodeList = cmds.listRelatives(topNode, ad=True, f=True, shapes=False)
    nodeList.append(topNode)
    if nodeList:
        for node in nodeList:
            if cmds.objExists(node):
                if not cmds.attributeQuery('nameHistory', node=node, exists=True):
                    cmds.addAttr(node, longName='nameHistory', dataType='string')
                cmds.setAttr('%s.nameHistory' % node, lock=False)
                cmds.setAttr('%s.nameHistory' % node, node.split('|')[-1], type='string')
                cmds.setAttr('%s.nameHistory' % node, lock=True)


def nameHistoryToggle(topNode):
    ''' Toggles name of nodes under the topNode group according to their nameHistory attrubute '''

    if cmds.objExists(topNode):
        allNodes = cmds.listRelatives(topNode, ad=True)
        for node in allNodes:
            if cmds.attributeQuery('nameHistory', node=node, exists=True):
                oldName = cmds.getAttr('%s.nameHistory' % node)
                try:
                    if not node in oldName:
                        cmds.rename(node, oldName)
                        cmds.setAttr('%s.nameHistory' % oldName, lock=False)
                        cmds.setAttr('%s.nameHistory' % oldName, node, type='string')
                        cmds.setAttr('%s.nameHistory' % oldName, lock=True)
                        LOG.info('Renamed %s ---> %s' % (node, oldName))
                except:
                    LOG.info('Unable to rename %s ---> %s' % (node, oldName))


def stripNameHistoryAttr(node):
    '''
    Removes nameHistory attr, useful if a node has been duplicated with an existing nameHistory attr
    stripNameHistoryAttr('Knee_L1')
    '''
    if cmds.attributeQuery('nameHistory', node=node, exists=True):
        cmds.setAttr('%s.nameHistory' % node, lock=False)
        cmds.deleteAttr(node, at='nameHistory')
        return True