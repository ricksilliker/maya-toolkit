"""

    TO DO:

    - Add finger spread multiplier attrs


"""
import os
import json

import maya.cmds as cmds
import maya.mel as mel

import py_tasker.tasks
import dragonfly.modules
reload(dragonfly.modules)

LOG = py_tasker.tasks.get_task_logger(__name__)

CONTROLS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'controls')

def run(params, rig):

    for fingerMod in params['fingerMods']:

        do_fingerSpread = fingerMod['fingerSpreadModification']
        if do_fingerSpread:
            cup_ctls = [cup_ctl for cup_ctl in fingerMod['fingerSpreadCupControls'].replace(' ', '').split(",")]
            cup_side = cup_ctls[0].split('_')[-1]
            if cup_ctls and cup_side:
                try:
                    hand_cup_modify(cup_ctls[0], cup_ctls[1], cup_ctls[2], side=cup_side)
                    LOG.info('Added finger spread mod to {}'.format(cup_ctls[2]))
                except:
                    LOG.error('Error adding finger spread mod to {}'.format(cup_ctls[2]))


def hand_cup_modify(middle_cup_ctl, ring_cup_ctl, pinky_cup_ctl, side='R'):
    """Adds single control for the spread of middle, ring and pinky fingers
    Requires that each finger has they're own cup joint

    hand_cup_modify( 'FKMiddleCup_R', 'FKRingCup_R', 'FKPinkyCup_R' )
    """
    mid_off = middle_cup_ctl.replace('FK', 'FKOffset')
    ring_off = ring_cup_ctl.replace('FK', 'FKOffset')
    pinky_off = pinky_cup_ctl.replace('FK', 'FKOffset')

    # Insert transform above existing offset nodes
    mid_zero = insertAsParent(mid_off, name=None, suffix='zero', match=True, nodeType='transform')
    ring_zero = insertAsParent(ring_off, name=None, suffix='zero', match=True, nodeType='transform')
    pinky_zero = insertAsParent(pinky_off, name=None, suffix='zero', match=True, nodeType='transform')

    # Add spread - circle control
    spread_ctl = insertAsParent(pinky_off, name=None, suffix='ctl', match=True, nodeType='transform')
    spread_ctl = cmds.rename(spread_ctl, 'FKFingerCup_{}'.format(side))

    mid_mdn = cmds.createNode('multiplyDivide', name='{}_mdn'.format(mid_off))
    ring_mdn = cmds.createNode('multiplyDivide', name='{}_mdn'.format(ring_off))
    pinky_mdn = cmds.createNode('multiplyDivide', name='{}_mdn'.format(pinky_off))

    cmds.connectAttr('{}.rotate'.format(spread_ctl), '{}.input1'.format(mid_mdn))
    cmds.connectAttr('{}.rotate'.format(spread_ctl), '{}.input1'.format(ring_mdn))
    cmds.connectAttr('{}.rotate'.format(spread_ctl), '{}.input1'.format(pinky_mdn))

    cmds.setAttr('{}.input2X'.format(ring_mdn), .5)
    cmds.setAttr('{}.input2Y'.format(ring_mdn), .5)
    cmds.setAttr('{}.input2Z'.format(ring_mdn), .5)

    cmds.setAttr('{}.input2X'.format(pinky_mdn), .25)
    cmds.setAttr('{}.input2Y'.format(pinky_mdn), .25)
    cmds.setAttr('{}.input2Z'.format(pinky_mdn), .25)

    cmds.connectAttr('{}.output'.format(mid_mdn), '{}.rotate'.format(mid_off))
    cmds.connectAttr('{}.output'.format(ring_mdn), '{}.rotate'.format(ring_off))
    cmds.connectAttr('{}.output'.format(pinky_mdn), '{}.rotate'.format(pinky_off))

    # Add spread multiply attr
    add_vector_attr(spread_ctl, 'mid_spread_mult', xyz_value=[.9, .9, .9])
    add_vector_attr(spread_ctl, 'ring_spread_mult', xyz_value=[.5, .5, .5])
    add_vector_attr(spread_ctl, 'pinky_spread_mult', xyz_value=[.2, .2, .2])

    cmds.connectAttr('{}.mid_spread_mult'.format(spread_ctl), '{}.input2'.format(mid_mdn))
    cmds.connectAttr('{}.ring_spread_mult'.format(spread_ctl), '{}.input2'.format(ring_mdn))
    cmds.connectAttr('{}.pinky_spread_mult'.format(spread_ctl), '{}.input2'.format(pinky_mdn))

    # Add control shape
    ctl_scale = getNodeScale(spread_ctl) / 2
    handle(spread_ctl, ctrlShape='circle', ctrlColor=None, ctrlScale=ctl_scale, ctrlAxis=None)
    modifyShape(spread_ctl, translation=None, rotation=[0, 90, 0], scale=None, world=False)

    # Control color
    if 'R' in side:
        colorControl(spread_ctl, 13)
    elif 'L' in side:
        colorControl(spread_ctl, 6)
    else:
        colorControl(spread_ctl, 17)


def add_vector_attr(node, attr_name, xyz_value=[0,0,0]):
    """
    add_vector_attr('Fingers_R', 'test', xyz_value=[0,0,0])
    """
    cmds.addAttr(node, ln=attr_name, at='double3')
    cmds.addAttr(node, ln='{}X'.format(attr_name), p=attr_name, min=0.0, max=1.0)
    cmds.addAttr(node, ln='{}Y'.format(attr_name), p=attr_name, min=0.0, max=1.0)
    cmds.addAttr(node, ln='{}Z'.format(attr_name), p=attr_name, min=0.0, max=1.0)

    cmds.setAttr('{}.{}'.format(node, attr_name), xyz_value[0], xyz_value[1], xyz_value[2])
    cmds.setAttr('{}.{}X'.format(node, attr_name), k=True, l=False)
    cmds.setAttr('{}.{}Y'.format(node, attr_name), k=True, l=False)
    cmds.setAttr('{}.{}Z'.format(node, attr_name), k=True, l=False)

    return True



def create_control(curve_data, transform):
    """Uses dictionary of curve data to create curve and properly rename curve shape node"""
    try:
        crv = cmds.curve(**curve_data)
        crvShp = cmds.listRelatives(crv, shapes=True)[0]
        cmds.parent(crvShp, transform, r=True, s=True)
        cmds.rename(crvShp, "{}Shape".format(transform))
        cmds.delete(crv)
        return True
    except:
        LOG.error("Unable to add pivot curve to {}".format(transform))
        raise


def matchPose(src, dst, poseType='pose'):
    """Match dst transform to src transform (follows maya constraint argument order: src, dst)"""
    if (poseType == 'position'):
        position = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        cmds.xform(dst, worldSpace=True, translation=position)

    elif (poseType == 'rotation'):
        rotation = cmds.xform(src, query=True, worldSpace=True, rotation=True)
        cmds.xform(dst, worldSpace=True, rotation=rotation)

    elif (poseType == 'scale'):
        scale = cmds.xform(src, query=True, worldSpace=True, scale=True)
        cmds.xform(dst, worldSpace=True, scale=scale)

    elif (poseType == 'pose'):
        pivot = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        matrix = cmds.xform(src, query=True, worldSpace=True, matrix=True)
        matrix[12] = pivot[0]
        matrix[13] = pivot[1]
        matrix[14] = pivot[2]
        cmds.xform(dst, worldSpace=True, matrix=matrix)


def getParent(node, recursive=False, breakNode=None):
    """Get parent node, if recursive get topnode in heirarchy """
    parents = cmds.listRelatives(node, parent=True)
    if not parents:
        return None
    parent = parents[0]

    if recursive:
        recursiveParents = [parent]
        while parent:
            parents = cmds.listRelatives(parent, parent=True)
            if parents:
                parent = parents[0]
                if parent == breakNode:
                    break
                else:
                    recursiveParents.append(parent)
            else:
                break
        return recursiveParents
    else:
        return parent


def insertAsParent(node, name=None, suffix=None, match=True, nodeType='transform'):
    """Insert parent node"""
    # Get node parent
    parent = getParent(node)

    # Resolve name
    if not name:
        if suffix:
            name = node + '_' + suffix
        else:
            name = node + '_grp'

    # Create new node under parent
    insert = cmds.createNode(nodeType, name=name, parent=parent)

    # Match node
    if match:
        matchPose(node, insert)
    else:
        matchPose(parent, insert)

    # Parent node under insert
    cmds.parent(node, insert)

    return insert


def scaleControl(node, scaleVector):
    """Scale controlCurve by [x, y, z].
    Adjust controlCurve size of selected transform nodes.

    Args:
        node: Transform node.
        scaleVector: Scale vector.
        ocp: Object Center Pivot.
    Returns:
        None.
    Raises:
        Logs warning if node does not exist.
        Logs warning if node is not tranform type.
        Logs warning if scaleVector is not a list of three.
    """
    if not cmds.objExists(node):
        LOG.warning(node + ' does not exist.')
        return
    elif not (cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint')):
        LOG.warning('Input node requires transform or joint type.')
        return
    elif len(scaleVector) != 3:
        LOG.warning('Input scaleVector requires a list of three.')
        return

    shapeList = get_shape(node)
    for shape in shapeList:
        cmds.select(cl=1)
        cmds.select(shape + '.cv[:]')

        # Get center pivot of CVs
        cls = cmds.cluster()
        cp = cmds.xform(cls[1], q=True, ws=True, piv=True)
        cmds.delete(cls)

        cmds.select(shape + '.cv[:]')
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, p=(cp[0], cp[1], cp[2]))


def colorControl(node, index):
    """Drawing overrides selected

    Args:
        node: Transform node or nurbsCurve.
        index: Color index.
    Returns:
        None.
    Raises:
        None.
    """
    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.setAttr("{0}.overrideEnabled".format(node), True)
        cmds.setAttr("{0}.overrideColor".format(node), index)

    elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
        shapeList = cmds.listRelatives(node, shapes=True)
        for shape in shapeList:
            cmds.setAttr("{0}.overrideEnabled".format(shape), True)
            cmds.setAttr("{0}.overrideColor".format(shape), index)


def getNodeScale(node):
    """Returns bbox scale of node as vector """
    bBox = cmds.exactWorldBoundingBox(node)
    gScale = min(bBox[3] - bBox[0], bBox[4] - bBox[1], bBox[5] - bBox[2])
    return gScale


def handle(ctrl, ctrlShape='circle', ctrlColor=None, ctrlScale=None, ctrlAxis=None):
    """Add valid ctrl shape (handle) to ctrl node. Rename to ctrlShape format.
    If ctrl has curve shapes, they will be deleted.

    Args:
        ctrl: Target control.
        ctrlShape: The control shape name.
        ctrlColor: The maya color of the control. Takes int or string.
        ctrlScale: The scale of the control.
        ctrlAxis: The normal axis name of the control, such as 'x', or '-z'.

    Returns: List of the added shape.
    """
    # check if ctrl exists
    if not cmds.objExists(ctrl):
        LOG.info('control.handle: "' + ctrl + '" node does not exist, skipping...')
        return (None)

    # load and add control shapes from json file
    filepath = os.path.join(CONTROLS_DIRECTORY, ctrlShape + '.json')
    if os.path.exists(filepath):
        importShapesFromJson(filepath, ctrl)
    else:
        LOG.error('Control shape file %s does not exist! You lose... (said in Schwarzenegger voice)' % ctrlShape)
        return (None)

    # Add color
    controlShapes = cmds.listRelatives(ctrl, s=True)
    if ctrlColor:
        # setColor(ctrl, ctrlColor)
        if controlShapes:
            for ctrlShp in controlShapes:
                setColor(ctrlShp, ctrlColor)

    # Get ctrl info
    ctrlCenter = cmds.xform(ctrl, q=True, ws=True, t=True)
    pts = []
    if controlShapes:
        for s in controlShapes:
            pts = pts + cmds.ls(s + '.cp[*]')

    # Orient
    orientAxes = {"x": [0, 0, -90], "y": [0, 0, 0], "z": [90, 0, 0],
                  "-x": [0, 0, 90], "-y": [0, 0, 180], "-z": [-90, 0, 0]}
    if ctrlAxis:
        axis = orientAxes[ctrlAxis]
        cmds.rotate(axis[0], axis[1], axis[2], pts, p=ctrlCenter, r=True, os=True)

    # Scale
    if ctrlScale:
        cmds.scale(ctrlScale, ctrlScale, ctrlScale, pts, p=ctrlCenter, r=True)

    # rename
    controlShapes = cmds.listRelatives(ctrl, s=True)
    for s in controlShapes:
        cmds.rename(s, ctrl + 'Shape')

    return (controlShapes)


def importShapesFromJson(filepath, transform=None):
    """
    Import control shape to node.

    Args:
        filepath: The absolute filepath to a json file.
        transform: Target node.

    Returns: Filepath if succeeds. None if fails.

    """
    if os.path.exists(filepath):

        fh = open(filepath, 'r')
        curveData = json.load(fh)
        fh.close()

        # make sure it's a list - some control jason files are dicts in a list some are just dicts
        # this deals with that issue
        if type(curveData) != list:
            curveData = [curveData]

        # if the transform already has shapes delete them and create new ones
        if transform:
            shapes = cmds.listRelatives(transform, s=True)
            if shapes:
                for s in shapes:
                    cmds.delete(s)
                    # create_curve(curveData)
        for dataBlock in curveData:
            create_curve(dataBlock, transform)

        LOG.debug('Imported Control Curves from: %s' % filepath)
        return filepath
    else:
        LOG.error('Control curve file %s does not exist!' % filepath)
        return None


def create_curve(control, transform=None):
    """Create a curve.

    Args:
        control: A data dictionary generated from the dump function.
        transform: A transform node to add curveShape to.

    Returns:
        Curve name.
    """
    curve = control['name']
    curveShape = control['shape']

    periodic = control['form'] == 2
    degree = control['degree']
    points = control['cvs']

    if periodic and not cmds.objExists(curveShape):
        points = points + points[:degree]

    if cmds.objExists(curveShape):
        i = 0
        while i < len(points):
            cmds.move(points[i][0], points[i][1], points[i][2], '%s.cv[%s]' % (curveShape, i), os=True)
            i = i + 1

    else:
        if cmds.objExists(curve):
            curve = cmds.curve(degree=degree, p=points, n="TEMP" + control['name'], per=periodic, k=control['knots'])
        else:
            curve = cmds.curve(degree=degree, p=points, n=control['name'], per=periodic, k=control['knots'])
        curveShape = cmds.rename(cmds.listRelatives(curve, shapes=True)[0], curveShape)

        if 'parent' in control:
            if cmds.objExists(control['parent']):
                if control['parent'] != cmds.listRelatives(curveShape, parent=True)[0]:
                    try:
                        cmds.parent(curveShape, control['parent'], relative=True, shape=True)
                        cmds.delete(curve)
                    except:
                        pass

    # parenting
    if (transform and (transform is not cmds.listRelatives(curveShape, p=True, type='transform')[0])):
        try:
            cmds.parent(curveShape, transform, s=1, r=1)
            cmds.delete(curve)
        except:
            pass

    if cmds.objExists(curve):
        cmds.delete(curve, constructionHistory=True)

        cmds.setAttr('{0}.overrideEnabled'.format(curve), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curve), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curve), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curve), *control['overrideColorRGB'])
        except:
            pass

    if cmds.objExists(curveShape):
        cmds.setAttr('{0}.overrideEnabled'.format(curveShape), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curveShape), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curveShape), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curveShape), *control['overrideColorRGB'])
        except:
            pass

    return curve


def modifyShape(ctrl, translation=None, rotation=None, scale=None, world=False):
    """
    Modify transform of shapes.

    Args:
        ctrl: Target control node.
        translation: Translation value of [x, y, z]
        rotation: Rotation value of [x, y, z]
        scale: Scale value of [x, y, z]
        world: True to operate in world space. False to operate in object space.

    Returns: NA
    """
    ctrlShapes = cmds.listRelatives(ctrl, shapes=True)
    pts = list()
    for shape in ctrlShapes:
        pts = pts + cmds.ls(shape + '.cp[*]', fl=True)

    if translation:
        if world:
            cmds.move(translation[0], translation[1], translation[2], pts, r=True, ws=True)
        else:
            cmds.move(translation[0], translation[1], translation[2], pts, r=True, os=True)

    if rotation:
        cmds.rotate(rotation[0], rotation[1], rotation[2], pts, r=True, os=True)

    if scale:
        cmds.scale(scale[0], scale[1], scale[2], pts, r=True)