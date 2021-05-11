import logging
LOG = logging.getLogger(__name__)

import maya.cmds as cmds


# Copy tentacle pose
def getAllTentaclesFromSelected():
    sel = cmds.ls(selection=True)
    if sel:
        ctl = sel[0]
        main_ctl = ""
        if cmds.attributeQuery("space_network", node=ctl, exists=True):
            main_ctl = ctl
        else:
            cxns = cmds.listConnections("{}.message".format(ctl), s=False, d=True)
            if cxns:
                for cxn in cxns:
                    if cmds.attributeQuery("space_network", node=cxn, exists=True):
                        main_ctl = cxn
        if main_ctl:
            ctl_list_all = cmds.listConnections("{}.space_network".format(main_ctl))
            ctl_list = list(set(ctl_list_all))
        return ctl_list


def mirrorTentaclePose(src_tent_controls):
    """
    selTents = getAllTentaclesFromSelected()
    mirTents = mirrorTentaclePose(selTents)
    """
    tgt_tent_controls = list()
    src_side = ""
    tgt_side = ""
    for src_ctl in src_tent_controls:
        if "lf" in src_ctl:
            src_side = "lf"
            tgt_side = "rt"
        elif "rt" in src_ctl:
            src_side = "rt"
            tgt_side = "lf"
        else:
            print "Cannot determine side from selection!"
            return
        tgt_ctl = src_ctl.replace(src_side, tgt_side)
        if cmds.objExists(tgt_ctl):
            tgt_tent_controls.append(tgt_ctl)

    if tgt_tent_controls:
        for src, tgt in zip(src_tent_controls, tgt_tent_controls):
            copyPastePose(src, tgt)


def copyTentaclePose():
    sel = cmds.ls(selection=True)

    if len(sel) == 2:
        src_ctl = sel[0]
        tgt_ctl = sel[1]

        cmds.select(src_ctl)
        src_tents = sorted(getAllTentaclesFromSelected())

        cmds.select(tgt_ctl)
        tgt_tents = sorted(getAllTentaclesFromSelected())

        if src_tents and tgt_tents:
            for src, tgt in zip(src_tents, tgt_tents):
                copyPastePose(src, tgt)
                print src, tgt

        cmds.select(sel)


def copyPastePose(src, tgt):
    """
    copyPastePose("lf_tentB4_ctl", "lf_tentC4_ctl")
    """
    attrs = cmds.listAttr(src, k=True)
    if attrs:
        for attr in attrs:
            if cmds.attributeQuery(attr, node=src, exists=True):
                copyPasteAttr(src, tgt, attr)


def copyPasteAttr(src, tgt, attr):
    attr_type = cmds.getAttr("{}.{}".format(src, attr), type=True)
    if not "message" in attr_type:
        attr_val = cmds.getAttr("{}.{}".format(src, attr))
        cmds.setAttr("{}.{}".format(tgt, attr), attr_val)