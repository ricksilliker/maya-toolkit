"""
    # FKIK fingers
    rig.fingerFKIKSetup(fingerNames=["Index", "Middle", "Ring", "Pinky", "Thumb"], sides=["L", "R"])

    # Rig control modifications
    modify.masterControl(controlScale=1.0)
    modify.bodyControl(controlScale=1.0)
    modify.cogControl(controlScale=1.0)
    modify.hipSwinger(controlScale=1.0)
    modify.fkikControls(controlScale=1.0)
    modify.curveControlColors()


    # FOOT MOD
# IK Foot Modification - Use attributes to control foot pivots instead of controls
foot_ctl = 'lf_leg_ik_ctl'

# Add attrs
foot_attrs = [ 'footTilt', 'heelBall', 'heelBallAngle', 'toesUpDn', 'ballSwivel', 'heelSwivel', ]

for foot_attr in foot_attrs:
    cmds.addAttr(foot_ctl, ln=foot_attr, dv=0, at='double')
    cmds.setAttr('{}.{}'.format(foot_ctl, foot_attr), k=True, l=False)

cmds.setAttr('{}.heelBallAngle'.format(foot_ctl), 25)

# Connect foot attrs
cmds.connectAttr( '{}.footTilt'.format(foot_ctl), '{}.rock'.format(foot_ctl) )
cmds.connectAttr( '{}.heelBall'.format(foot_ctl), '{}.roll'.format(foot_ctl) )
cmds.connectAttr( '{}.heelBallAngle'.format(foot_ctl), '{}.rollAngle'.format(foot_ctl) )
cmds.connectAttr( '{}.toesUpDn'.format(foot_ctl), 'lf_toes_ik_ctl.rx'.format(foot_ctl) )
#cmds.connectAttr( '{}.ballSwivel'.format(foot_ctl), '{}.roll'.format(foot_ctl) )
cmds.connectAttr( '{}.heelSwivel'.format(foot_ctl), 'lf_heelSwing_ctl.ry'.format(foot_ctl) )

# Hide existing attrs
foot_attrs_hide = ['swivel', 'roll', 'rollAngle', 'rock']
for foot_attr_hide in foot_attrs_hide:
    cmds.setAttr('{}.{}'.format(foot_ctl, foot_attr_hide), k=False, l=False)

# Hide existing controls
cmds.hide('lf_IKOffsettoes', 'lf_heelSwing_ctl', 'lf_rollHeel_ctlShape')


FootTilt = Existing "Rock" attr
HeelBall = Existing "Roll" attr
ToesUpDn = 'lf_toes_ik_ctl.rx'
BallSwivel =
HeelSwivel = Existing "Swivel" attr
ToeCtl = lf_rolltoesEnd_ctl

"""

import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)
MAYA_VER = int(mel.eval('getApplicationVersionAsFloat'))
CONTROLS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'controls')


def run(params, rig):

    for footIK in params['footIKControls']:

        footIK_ctl = footIK['footIKControl']

        LOG.info('Modifying footIK pivot controls on {}'.format(footIK_ctl))

        # Get controls
        toe_ctl = return_foot_node(footIK_ctl, search_str='IKToes_')

        # Add attr separator
        attributeSeparator(footIK_ctl, "FootPivots")

        # Add new foot attrs
        foot_attrs = ['footTilt', 'heelBall', 'heelBallAngle', 'toesUpDn', 'ballSwivel', 'heelSwivel', ]

        for foot_attr in foot_attrs:
            cmds.addAttr(footIK_ctl, ln=foot_attr, dv=0, at='double')
            cmds.setAttr('{}.{}'.format(footIK_ctl, foot_attr), k=True, l=False)

        cmds.setAttr('{}.heelBallAngle'.format(footIK_ctl), 25)

        # Connect new foot attrs to existing foot attrs
        cmds.connectAttr('{}.footTilt'.format(footIK_ctl), '{}.rock'.format(footIK_ctl))
        cmds.connectAttr('{}.heelBall'.format(footIK_ctl), '{}.roll'.format(footIK_ctl))
        cmds.connectAttr('{}.heelBallAngle'.format(footIK_ctl), '{}.rollAngle'.format(footIK_ctl))
        if toe_ctl:
            cmds.connectAttr('{}.toesUpDn'.format(footIK_ctl), '{}.rx'.format(toe_ctl))
        ball_pivot = add_ball_pivot_node(footIK_ctl)
        cmds.connectAttr( '{}.ballSwivel'.format(footIK_ctl), '{}.ry'.format(ball_pivot) )
        heel_pivot = add_heel_pivot_node(footIK_ctl)
        cmds.connectAttr('{}.heelSwivel'.format(footIK_ctl), '{}.ry'.format(heel_pivot))


        # Hide existing attrs
        foot_attrs_hide = ['swivel', 'roll', 'rollAngle', 'rock']
        for foot_attr_hide in foot_attrs_hide:
            cmds.setAttr('{}.{}'.format(footIK_ctl, foot_attr_hide), k=False, l=False)

        # Hide existing controls
        ctls_to_hide = cmds.listRelatives(footIK_ctl, ad=True, type='nurbsCurve')

        if 'Front' in footIK_ctl:
            hide_strings = ['IKFrontPaw', 'IKOffsetFrontPaw', 'RollfrontHeel', 'RollToe', 'HeelSwing', 'RollPaws']
        elif 'Back' in footIK_ctl:
            hide_strings = ['IKBackPaw', 'IKOffsetBackPaw', 'RollbackHeel', 'RollToe', 'HeelSwing', 'RollPaw']
        else:
            hide_strings = ['IKToes', 'IKOffsettoes', 'RollHeel', 'RollToes', 'HeelSwing']

        for ctl in ctls_to_hide:
            for hide_str in hide_strings:
                if hide_str in ctl:
                    cmds.hide(ctl)

        # Show specific controls
        show_strings = ['RollToesEnd']
        for ctl in ctls_to_hide:
            for show_str in show_strings:
                if show_str in ctl:
                    cmds.showHidden(ctl)


        LOG.info('Successfully modified footIK pivot controls on {}'.format(footIK_ctl))


def add_heel_pivot_node(foot_ik_ctl):
    """Adds a pivot transform at ball of foot

    Example:
        add_heel_pivot_node('IKLeg_L')
    """
    # Create new transform
    cmds.select(clear=True)
    heel_pivot = cmds.group(name='{}_heel_pivot'.format(foot_ik_ctl), empty=True)

    if 'Front' in foot_ik_ctl:
        match_pivot = return_foot_node(foot_ik_ctl, search_str='RollOffsetfrontHeel_')
    elif 'Back' in foot_ik_ctl:
        match_pivot = return_foot_node(foot_ik_ctl, search_str='RollOffsetbackHeel_')
    else:
        match_pivot = return_foot_node(foot_ik_ctl, search_str='RollOffsetHeel_')

    cmds.delete(cmds.pointConstraint(match_pivot, heel_pivot))
    ik_child = cmds.listRelatives(foot_ik_ctl, children=True, type='transform')
    cmds.parent(heel_pivot, foot_ik_ctl)
    cmds.parent(ik_child, heel_pivot)
    return heel_pivot


def add_ball_pivot_node(foot_ik_ctl):
    """Adds a pivot transform at ball of foot

    Example:
        add_ball_pivot_node('IKLeg_L')
    """
    # Create new transform
    cmds.select(clear=True)
    ball_pivot = cmds.group(name='{}_ball_pivot'.format(foot_ik_ctl), empty=True)
    inner_pivot = return_foot_node(foot_ik_ctl, search_str='RockInnerPivot_')
    outer_pivot = return_foot_node(foot_ik_ctl, search_str='RockOuterPivot_')
    cmds.delete(cmds.pointConstraint(inner_pivot, outer_pivot, ball_pivot))
    ik_child = cmds.listRelatives(foot_ik_ctl, children=True, type='transform')
    cmds.parent(ball_pivot, foot_ik_ctl)
    cmds.parent(ik_child, ball_pivot)
    return ball_pivot


def return_foot_node(foot_ik_ctl, search_str=""):
    """Simple function to help find foot nodes in a footIK ctl hiearchy

    return_foot_node( 'IKLeg_L', search_str='IKToes_')
    """
    foot_nodes = cmds.listRelatives(foot_ik_ctl, ad=True, type='transform')
    for foot_node in foot_nodes:
        if search_str in foot_node:
            return foot_node


def attributeSeparator(control, attr):
    """Create a separator attribute on the specified control object

    Args:
        control: The control to add the separator attribute to
        attr: The separator attribute name

    Returns:
        string: control.attr

    Example:
        attributeSeparator('Lf_arm_ctrl', '___')
    """
    # Check control
    if not cmds.objExists(control):
        raise Exception('Control object "' + control + '" does not exist!')

    # Check attribute
    if cmds.objExists(control + '.' + attr):
        raise Exception('Control attribute "' + control + '.' + attr + '" already exists!')

    # Create attribute
    cmds.addAttr(control, ln=attr, at='enum', en=':-:')
    cmds.setAttr(control + '.' + attr, cb=True)
    cmds.setAttr(control + '.' + attr, l=True)

    # Return result
    return (control + '.' + attr)