"""

    To Run:

    # Select FK or IK control on limb and run...

    from character_tools import fkik_switch
    reload(fkik_switch)
    fkik_switch.call_fkik_switcher_from_selected(do_bake=False)

    # Select frame range in timeline to bake switch over and run...
    from character_tools import fkik_switch
    reload(fkik_switch)
    fkik_switch.call_fkik_switcher_from_selected(do_bake=True)



    To Do:
        Implement shelf button

        Need to calculate PV vector offset once snapped to elbow (store as a float?)

        Quad legs - account for shoulder aim and foot setup

        Spine/Tail switch
            - IK2FK in progress and working pretty well
            - FK2IK not started (see line 816 of picker.mel)

"""
import logging
LOG = logging.getLogger(__name__)

import dragonfly.modules
reload(dragonfly.modules)

from maya import cmds
from maya import mel


def call_fkik_switcher_from_selected(do_bake=False):
    selected = cmds.ls(selection=True)

    if selected:
        for object in selected:
            fkik_switch = get_message_attribute_connections(object, 'fkik_switch')
            if fkik_switch:

                # Is this a biped, quad fkik switch?
                biped_limb = None
                quad_limb = None
                biped_spine = None
                quad_spine = None

                # Biped
                if dragonfly.modules.check_metatype(fkik_switch[0], 'dragonfly.biped.arm'):  biped_limb = True
                elif dragonfly.modules.check_metatype(fkik_switch[0], 'dragonfly.biped.leg'):  biped_limb = True

                # Quadruped
                if dragonfly.modules.check_metatype(fkik_switch[0], 'dragonfly.quad.arm'):  quad_limb = True
                elif dragonfly.modules.check_metatype(fkik_switch[0], 'dragonfly.quad.leg'):  quad_limb = True

                # Spine

                # Get current FKIK mode
                fkik_mode = cmds.getAttr('{}.FKIKBlend'.format(fkik_switch[0]))

                # Get selected frame range (if any)
                f_range = frameRange(start=None, end=None)

                if biped_limb:
                    # Currently IK, match FK to IK and switch to FK mode
                    if fkik_mode:
                        if do_bake:
                            switch_and_bake(fkik_switch[0], f_range, match_fk_to_ik=True)
                        else:
                            LOG.info('Biped FKIK Switch {} in IK, switching to FK'.format(fkik_switch[0]))
                            switch_biped_limb_fkik(fkik_switch[0], match_fk_to_ik=True)
                    else:
                        if do_bake:
                            switch_and_bake(fkik_switch[0], f_range, match_fk_to_ik=False)
                        else:
                            LOG.info('Biped FKIK Switch {} in FK, switching to IK'.format(fkik_switch[0]))
                            switch_biped_limb_fkik(fkik_switch[0], match_fk_to_ik=False)

                elif quad_limb:
                    # Currently IK, match FK to IK and switch to FK mode
                    if fkik_mode:
                        if do_bake:
                            pass
                        else:
                            LOG.info('Quad FKIK Switch {} in IK, switching to FK'.format(fkik_switch[0]))
                            switch_biped_limb_fkik(fkik_switch[0], match_fk_to_ik=True)
                    else:
                        if do_bake:
                            pass
                        else:
                            LOG.info('Quad FKIK Switch {} in FK, switching to IK'.format(fkik_switch[0]))
                            switch_biped_limb_fkik(fkik_switch[0], match_fk_to_ik=False)
            else:
                LOG.error('Cannot find FKIK Switch from selected: {}'.format(object))
    else:
        LOG.error('Nothing selected, select FK, IK or FKIK switch control and try again')


def switch_biped_limb_fkik(fkik_switch, match_fk_to_ik=True, keyframe=False):
    # Current mode is IK, matching FK and switching to FK mode
    if match_fk_to_ik:
        ik_jnts = get_message_attribute_connections(fkik_switch, 'ik_jnts')
        fk_ctls = get_message_attribute_connections(fkik_switch, 'fk_ctls')
        for src, tgt in zip(ik_jnts, fk_ctls):
            match_orientation(src, tgt)
        cmds.setAttr('{}.FKIKBlend'.format(fkik_switch), 0)

        if keyframe:
            cmds.setKeyframe(fk_ctls)

    # Current mode is FK, matching IK and switching to IK mode
    else:
        ik_ctl = get_message_attribute_connections(fkik_switch, 'ik_ctl')
        pv_ctl = get_message_attribute_connections(fkik_switch, 'ik_pv')
        ik_align = get_message_attribute_connections(fkik_switch, 'ik_ctl_align')
        fk_ctls = get_message_attribute_connections(fkik_switch, 'fk_ctls')
        ik_local = get_message_attribute_connections(fkik_switch, 'ik_local')

        if ik_ctl and pv_ctl:
            cmds.xform(ik_ctl[0], t=cmds.xform(ik_align[0], t=1, q=1, ws=1), ws=1)
            match_orientation(ik_align[0], ik_ctl[0])
            cmds.xform(pv_ctl[0], t=cmds.xform(fk_ctls[1], t=1, q=1, ws=1), ws=1)

            if ik_local:
                match_orientation(fk_ctls[2], ik_local[0])

            # Zero IK foot attrs and match toe
            if cmds.attributeQuery('ik_toe_align', node=fkik_switch, exists=True):
                cmds.setAttr('{}.heelBall'.format(ik_ctl[0]), 0)
                cmds.setAttr('{}.footTilt'.format(ik_ctl[0]), 0)
                cmds.setAttr('{}.ballSwivel'.format(ik_ctl[0]), 0)
                cmds.setAttr('{}.heelSwivel'.format(ik_ctl[0]), 0)
                fk_toe_rot = cmds.getAttr('{}.rotate'.format(fk_ctls[3]))
                cmds.setAttr('{}.toesUpDn'.format(ik_ctl[0]), -(fk_toe_rot[0][2]))

            cmds.setAttr('{}.FKIKBlend'.format(fkik_switch), 1)

            if keyframe:
                cmds.setKeyframe(ik_ctl[0], pv_ctl[0])


def switch_and_bake(fkik_switch, frame_range, match_fk_to_ik=True):

    start_frame = frame_range[0]
    end_frame = frame_range[1]

    for i in range(int(start_frame), int(end_frame+1)):
        switch_biped_limb_fkik(fkik_switch, match_fk_to_ik=match_fk_to_ik, keyframe=True)
        cmds.currentTime(i)
        #cmds.refresh()


def match_orientation(source, target):

    ''' This works for IK to FK'''
    if source.__contains__("IKX") == True:
        print '            '
        print 'Switching from Ik to Fk'
        dummy = cmds.duplicate(target, po=True)[0]
        cmds.delete(cmds.orientConstraint(source, dummy))
        cmds.delete(cmds.orientConstraint(dummy, target))
        cmds.delete(dummy)
    
    ''' This works for FK to IK'''
    if source.__contains__("AlignIK") == True:
        print '            '
        print 'Switching from fk to ik'
        cmds.duplicate(source, po=True)[0]
        dummy = cmds.duplicate(source, po=True)[0]
        cmds.delete(cmds.orientConstraint(dummy, target, o=[-180,0,0]))
        cmds.delete(dummy)

    if source.__contains__("lf_AlignIKToankle") == True:
        cmds.duplicate(source, po=True)[0]
        dummy = cmds.duplicate(source, po=True)[0]
        cmds.delete(cmds.orientConstraint(dummy, target))
        cmds.delete(dummy)


def get_message_attribute_connections(src, attr_name):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        get_message_attribute_connections("box_fk_ctrl", attr_name="pivot_node")
    """
    try:
        if cmds.attributeQuery(attr_name, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attr_name))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attr_name, src))
        raise


def frameRange(start=None, end=None):
    """Returns the frame range based on the highlighted timeslider,
    or otherwise the playback range.
    """
    if not start and not end:
        gPlayBackSlider = mel.eval('$temp=$gPlayBackSlider')
        if cmds.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            frameRange = cmds.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            start = frameRange[0]
            end = frameRange[1]
        else:
            start = cmds.playbackOptions(query=True, min=True)
            end = cmds.playbackOptions(query=True, max=True)

    return start,end


"""
SPINE SWITCHER IN PROGRESS
# Align Biped Spine
fk_spine_ctls = ['cn_root_fk_ctl', 'cn_spine1_fk_ctl', 'cn_spine2_fk_ctl', 'cn_spine3_fk_ctl', 'cn_chest_fk_ctl']

# Align IK to FK
num_ik_ctls = 3
ik_ctls = ['cn_spine1_ik_ctl', 'cn_spine2_ik_ctl', 'cn_spine3_ik_ctl']
spine_ik_start = 'cn_spine1_ik_ctl'
spine_ik_mid = 'cn_spine2_ik_ctl'
spine_ik_end = 'cn_spine3_ik_ctl'

start_pos = cmds.xform('cn_AlignIKToRoot', q=True, ws=True, t=True)
start_ori = cmds.xform('cn_AlignIKToRoot', q=True, ws=True, ro=True)
start_ro = cmds.xform('cn_AlignIKToRoot', q=True, ws=True, roo=True)

cmds.xform(spine_ik_start, ws=True, t=start_pos)
cmds.xform(spine_ik_start, ws=True, roo=start_ro, ro=start_ori)

# Run this at end
end_pos = cmds.xform('cn_AlignIKToChest', q=True, ws=True, t=True)
end_ori = cmds.xform('cn_AlignIKToChest', q=True, ws=True, ro=True)
end_ro = cmds.xform('cn_AlignIKToChest', q=True, ws=True, roo=True)

cmds.xform(spine_ik_end, ws=True, t=end_pos)
cmds.xform(spine_ik_end, ws=True, roo=end_ro, ro=end_ori)


# Align middle control
curve_pts = list()
i=0
while i < len(fk_spine_ctls):
    pos = cmds.xform(fk_spine_ctls[i], q=True, ws=True, t=True)
    curve_pts.append((pos[0], pos[1], pos[2]))
    i=i+1

cmds.curve(name="FK2IKCurve", p=curve_pts)
cmds.rebuildCurve("FK2IKCurve", ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=0, d=3, tol=0.01)
if cmds.objExists('TempPointOnCurveInfo'): cmds.delete('TempPointOnCurveInfo')
poci = cmds.createNode('pointOnCurveInfo', name='TempPointOnCurveInfo')
cmds.setAttr('{}.turnOnPercentage'.format(poci), 1)
cmds.connectAttr('FK2IKCurve.worldSpace', '{}.inputCurve'.format(poci))

# Align "in-between" controls
i=2
while i < (len(ik_ctls)):
    print ((i-1.0)/(num_ik_ctls-1.0))
    cmds.setAttr('{}.parameter'.format(poci), ((i-1.0)/(num_ik_ctls-1.0)))
    pos = cmds.getAttr('{}.position'.format(poci))
    print pos
    cmds.xform(ik_ctls[i], ws=True, t=pos[0])
    i=i+1
    
cmds.delete(poci, "FK2IKCurve")

end_pos = cmds.xform('cn_AlignIKToChest', q=True, ws=True, t=True)
end_ori = cmds.xform('cn_AlignIKToChest', q=True, ws=True, ro=True)
end_ro = cmds.xform('cn_AlignIKToChest', q=True, ws=True, roo=True)

cmds.xform(spine_ik_end, ws=True, t=end_pos)
cmds.xform(spine_ik_end, ws=True, roo=end_ro, ro=end_ori)


# Then do CV controls
i=0
while i < len(fk_ctls):
    pos = cmds.xform(fk_ctls[i], q=True, ws=True, t=True)
    cmds.xform(?, ws=True, t=True)


"""
