"""

TODO: Import onto selected curves only


"""
import os
import json
import logging

import maya.cmds as cmds
import maya.mel as mel

LOG = logging.getLogger(__name__)

def rename_curve_shapes():
    """Renames curve shape nodes after transform name"""
    crvShps = cmds.ls(type='nurbsCurve')
    if crvShps:
        for crv in crvShps:
            par = cmds.listRelatives(crv, parent=True, type="transform")
            if par:
                cmds.rename(crv, "{}Shape#".format(par[0]))

def import_control_curves(filename):
    """Use to import curve data to single json file.

    Args:
        filename:  Full or relative path to json curve data file.
    Returns:
        bool
    """
    file_path = ""
    projPath = cmds.workspace(q=True, rd=True)

    if '.json' in filename:
        file_path = os.path.join('%s' % projPath, '{0}'.format(filename))
    else:
        file_path = os.path.join('%s' % projPath, '{0}.json'.format(filename))

    if not os.path.exists(filename):
        filename = file_path

    if os.path.exists(file_path):
        try:
            fh = open(file_path, 'r')
            curveData = json.load(fh)
            fh.close()

            # create_curve(curveData)
            for dataBlock in curveData:
                create_curve(dataBlock)

            LOG.info('Imported Control Curves to: %s' % file_path)
            return file_path
        except:
            LOG.error('Error importing Control Curves from: %s' % file_path)
            raise
    else:
        LOG.error('Control curve file %s does not exist!' % file_path)
        pass


def call_export_control_curves(exportPath):
    import_cmd = ""
    import_cmd += "#========================================\n"
    import_cmd += "# Use curve control import command below in build\n"
    import_cmd += "#========================================\n"
    import_cmd += "from data_io import curve_io as crv_io \n"

    # Create export directory if it doesn't exist...
    dir_path = os.path.dirname(os.path.abspath(exportPath))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    rel_path = return_relative_path(exportPath)
    export_control_curves(exportPath)
    import_cmd += "crv_io.import_control_curves('{}')\n".format(rel_path)

    return import_cmd


def export_control_curves(filename):
    """Use to export curve data to single json file.

    Args:
        filename:  Full or relative path to json curve data file
    Returns:
        bool
    """
    file_path = ""
    projPath = cmds.workspace(q=True, rd=True)

    if '.json' in filename:
        file_path = os.path.join('%s' % projPath, '{0}'.format(filename))
    else:
        file_path = os.path.join('%s' % projPath, '{0}.json'.format(filename))

    if not os.path.exists(filename):
        filename = file_path

    sel = cmds.ls(selection=True)
    if sel:
        try:
            curveData = dump(curves=sel)

            fh = open(file_path, 'w')
            json.dump(curveData, fh, indent=4)
            fh.close()

            cmds.select(sel)
            LOG.info('Exported Control Curves to: %s' % file_path)
            return file_path
        except:
            LOG.error('Error exporting Control Curves to: %s' % file_path)
            raise
    else:
        LOG.error('No curve controls selected to export!')
        return
    
    
def create_curve(control, transform=None):
    """Create a curve.

    Args:
        control: A data dictionary generated from the dump function.
        transform: A transform node to add curveShape to.

    Returns: 
        Curve name
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
    """
    if cmds.objExists(curve):
        cmds.delete(curve, constructionHistory=True)

        cmds.setAttr('{0}.overrideEnabled'.format(curve), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curve), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curve), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curve), *control['overrideColorRGB'])
        except:
            pass
    """
    if cmds.objExists(curveShape):
        cmds.setAttr('{0}.overrideEnabled'.format(curveShape), control['overrideEnabled'])
        cmds.setAttr('{0}.overrideColor'.format(curveShape), control['overrideColor'])
        try:
            cmds.setAttr('{0}.overrideRGBColors'.format(curveShape), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curveShape), *control['overrideColorRGB'])
        except:
            pass

    return curve


def dump(curves=None):
    """Get a data dictionary representing all the given curves.

    Args:
        curves: Optional list of curves.

    Returns: 
        A json serializable list of dictionaries containing the data required to recreate the curves.
    """
    MAYA_VER = int(mel.eval('getApplicationVersionAsFloat'))
    curves = toList(curves)
    data = []
    for node in curves:
        cmds.delete(node, constructionHistory=True)
        shapes = cmds.listRelatives(node, s=True)
        if not shapes:
            continue
        for shp in shapes:
            if cmds.nodeType(shp) == 'nurbsCurve':
                control = {}
                control = {
                    'name': node,
                    'shape': shp,
                    'cvs': cmds.getAttr('{0}.cv[*]'.format(shp)),
                    'degree': cmds.getAttr('{0}.degree'.format(shp)),
                    'form': cmds.getAttr('{0}.form'.format(shp)),
                    'xform': cmds.xform(node, q=True, ws=True, matrix=True),
                    'knots': get_knots(shp),
                    'pivot': cmds.xform(node, q=True, rp=True),
                    'overrideEnabled': cmds.getAttr('{0}.overrideEnabled'.format(shp)),
                    'overrideColor': cmds.getAttr('{0}.overrideColor'.format(shp)),
                }
                if MAYA_VER > 2015:
                    control['overrideRGBColors'] = cmds.getAttr('{0}.overrideRGBColors'.format(shp))
                    control['overrideColorRGB'] = cmds.getAttr('{0}.overrideColorRGB'.format(shp))[0]
                control['parent'] = cmds.ls(node)[0]
                data.append(control)

    return data


def get_shape(node, intermediate=False):
    """Get the shape node of a transform.
    This is useful if you don't want to have to check if a node is a shape node
    or transform.  You can pass in a shape node or transform and the function
    will return the shape node.

    Args:
        node: The name of the node.
        intermediate: True to get the intermediate shape.

    Returns:
        The name of the shape node.
    """
    returnShapes = []
    if cmds.nodeType(node) == 'transform' or 'joint':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                returnShapes.append(shape)
                # return shape
            elif not intermediate and not is_intermediate:
                returnShapes.append(shape)
                # return shape
        return returnShapes

    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        is_intermediate = cmds.getAttr('%s.intermediateObject' % node)
        if is_intermediate and not intermediate:
            node = cmds.listRelatives(node, parent=True, path=True)[0]
            return get_shape(node)
        else:
            return node
    return None


def get_knots(curve):
    """Gets the list of knots of a curve so it can be recreated.

    Args:
        curve: Curve to query.

    Returns:
        A list of knot values that can be passed into the curve creation command.
    """
    if not 'nurbsCurve' in cmds.nodeType(curve):
        curve = shape.getShape(curve)
    info = cmds.createNode('curveInfo')
    cmds.connectAttr('{0}.worldSpace'.format(curve), '{0}.inputCurve'.format(info))
    knots = cmds.getAttr('{0}.knots[*]'.format(info))
    cmds.delete(info)
    return knots


def toList(input):
    """Takes input and returns it as a list"""
    if isinstance( input, list ):
        return input

    elif isinstance( input, tuple ):
        return list(input)

    return [input]


def return_relative_path(full_path):
    """Returns relative path of input path based on current Maya project"""
    root_dir = cmds.workspace(q=True, rd=True)
    rel_path = os.path.relpath(full_path, root_dir)
    return rel_path.replace('\\','/')


def remove_control(controlTransform):
    """
    Removes any exisiting control curve shapes under the controlTransform

    Args:
        controlTransform: Transform node whose curve shapes are to be removed.
    Returns:
        None.
    Raises:
        Logs error if controlTransform does not exist.

    """
    if cmds.objExists(controlTransform):
        curveShapes = cmds.listRelatives(controlTransform, pa=1, shapes=True, type='nurbsCurve')
        if curveShapes:
            cmds.delete(curveShapes)
            LOG.info('Deleted %s' % curveShapes)
            return True
        else:
            return
    else:
        LOG.error('%s does not exist' % controlTransform)
        return