"""
Auxillary functions used to mirror nodes.

These functions are not necessarily limited to mirror nodes.

This module uses PyMEL.
"""

import pymel.core as pm


def asList(value):
    """Take some value and convert to a list.

    Args:
        value: Something

    Returns:
        list: Convert other data types into a list.
    """
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        value = [value]
    return value


def getAxis(value):
    """Get a pm.dt.Vector representation of an axis.

    Notes:
        Accepts 0, 1, 2, 3, x, y, z, w and Axis objects

    Args:
        value: Some axis describer.

    Returns:
        A pm.dt.Vector.Axis enum for the given value
    """
    if isinstance(value, pm.util.EnumValue) and value.enumtype == pm.dt.Vector.Axis:
        return value
    elif isinstance(value, int):
        return pm.dt.Vector.Axis[value]
    elif isinstance(value, basestring):
        for k in pm.dt.Vector.Axis.keys():
            if k.startswith(value):
                return getattr(pm.dt.Vector.Axis, k)


def getWorldMatrix(node, negateRotateAxis=True):
    """Get a given node's worldMatrix value.

    Args:
        node (str/pm.PyNode): Node to retrieve worldMatrix attribute value from.
        negateRotateAxis (bool): Remove the rotate axis matrix from the output.

    Returns:
        pm.dt.Matrix
    """
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)
    if isinstance(node, pm.nt.Transform):
        wm = pm.dt.TransformationMatrix(node.wm.get())
        if negateRotateAxis:
            r = pm.dt.EulerRotation(pm.cmds.xform(node.longName(), q=True, ws=True, ro=True))
            wm.setRotation(r, node.getRotationOrder())
        return wm
    else:
        return pm.dt.TransformationMatrix()


def getBestAxis(matrix, axis=0):
    """

    Args:
        matrix (pm.dt.Matrix): Get best axis that matches this matrix.
        axis (int): [x, y, z] index.

    Returns:
        (int, int)
    """
    bestval = None
    bestaxis = None
    for a in range(3):
        val = matrix[a][axis]
        if bestval is None or abs(val) > abs(bestval):
            bestval = val
            bestaxis = a
    return getAxis(bestaxis), cmp(bestval, 0)


def getBestAxes(matrix):
    """Get whether each axis matches a matrix and which direction its pointing.

    Args:
        matrix (pm.dt.Matrix): Matrix to match against.

    Returns:
        (int, int, int), (int, int, int)
    """
    x, xsign = getBestAxis(matrix, 0)
    y, ysign = getBestAxis(matrix, 1)
    z, zsign = getBestAxis(matrix, 2)
    return (x, y, z), (xsign, ysign, zsign)


def getJointMatrices(jnt):
    """Get matrices that represent a joint transform.

    Args:
        jnt (pm.PyNode): A joint node.

    Returns:
        pm.dt.Matrix, pm.dt.EulerRotation, pm.dt.EulerRotation, pm.dt.EulerRotation
    """
    r = pm.dt.EulerRotation(jnt.r.get()).asMatrix()
    ra = pm.dt.EulerRotation(jnt.ra.get()).asMatrix()
    jo = pm.dt.EulerRotation(jnt.jo.get()).asMatrix() * jnt.pm.get()
    return jnt.wm.get(), r, ra, jo


def setJointMatrices(jnt, matrix, r, ra, jo, translate=True, rotate=True):
    """Set a joint transform.

    Notes:
        Does not support scale.

    Args:
        jnt (pm.PyNode):
        matrix (pm.dt.Matrix): A world matrix.
        r (pm.dt.EulerRotation): A rotation matrix.
        ra (pm.dt.EulerRotation): A rotate axis matrix.
        jo (pm.dt.EulerRotation): A joint orient matrix
        translate (bool): Apply to translate.
        rotate (bool): Apply to rotate.

    Returns:
        None
    """
    matrix = matrix * jnt.pim.get()
    if rotate:
        jo = jo * jnt.pim.get()
        rEuler = pm.dt.TransformationMatrix(r).euler
        raEuler = pm.dt.TransformationMatrix(ra).euler
        joEuler = pm.dt.TransformationMatrix(jo).euler
        rEuler.unit = raEuler.unit = joEuler.unit = 'degrees'
        pm.cmds.setAttr(jnt + '.r', *rEuler)
        pm.cmds.setAttr(jnt + '.ra', *raEuler)
        pm.cmds.setAttr(jnt + '.jo', *joEuler)
    if translate:
        pm.cmds.setAttr(jnt + '.t', *matrix[3][:3])


def getEulerForMtx(mtx):
    """Get a rotation in degrees.

    Args:
        mtx (pm.dt.Matrix): A matrix.

    Returns:
        pm.dt.EulerRotation
    """
    if not isinstance(mtx, pm.dt.TransformationMatrix):
        mtx = pm.dt.TransformationMatrix(mtx)
    rEuler = mtx.getRotation()
    rEuler.setDisplayUnit('degrees')
    return rEuler


def setWorldMatrix(node, matrix, translate=True, rotate=True, scale=True, matchAxes=False):
    """Set the transform of a give node in world space.

    Args:
        node (str/pm.PyNode): Object in Maya.
        matrix (pm.dt.Matrix): A matrix used to transform the given node.
        translate (bool): Apply to translate.
        rotate (bool): Apply to rotate.
        scale (bool): Apply to scale.
        matchAxes (bool): Exactly match the rotation of the given matrix.

    Returns:
        None
    """
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)

    if not isinstance(matrix, pm.dt.TransformationMatrix):
        matrix = pm.dt.TransformationMatrix(matrix)

    # Conver the rotation order
    ro = node.getRotationOrder()
    if ro != matrix.rotationOrder():
        matrix.reorderRotation(ro)

    if translate:
        pm.cmds.xform(node.longName(), ws=True, t=matrix.getTranslation('world'))
    if rotate:
        if matchAxes and any(node.ra.get()):
            # Get the source's rotation matrix
            source_rotMtx = pm.dt.TransformationMatrix(getEulerForMtx(matrix).asMatrix())
            # Get the target transform's inverse rotation matrix
            target_invRaMtx = pm.dt.EulerRotation(node.ra.get()).asMatrix().inverse()
            # Multiply the source's rotaiton matrix by the inverse of the
            # target's rotation axis to get just the difference in rotation
            target_rotMtx = target_invRaMtx * source_rotMtx
            # Get the new rotation value as a Euler in the correct rotation order
            target_rotation = getEulerForMtx(target_rotMtx)
            rotation = target_rotation.reorder(node.getRotationOrder())
            rotation.setDisplayUnit('degrees')
        else:
            rotation = getEulerForMtx(matrix)
        pm.cmds.xform(node.longName(), ws=True, ro=rotation)
    if scale:
        localScaleMatrix = matrix * node.pim.get()
        pm.cmds.xform(node.longName(), s=localScaleMatrix.getScale('world'))


def getScaleMatrix(matrix):
    """The scale matrix of the given matrix.
    Args:
        matrix (list): Some 4x4 list/array.
    Returns:
        pm.dt.Matrix
    """
    s = pm.dt.TransformationMatrix(matrix).getScale('world')
    return pm.dt.Matrix((s[0], 0, 0), (0, s[1], 0), (0, 0, s[2]))


def getRotationMatrix(matrix):
    """The rotation matrix of the given matrix.
    Args:
        matrix (list): Some 4x4 list/array.
    Returns:
        pm.dt.Matrix
    """
    return pm.dt.TransformationMatrix(matrix).euler.asMatrix()


def getOtherAxes(value, includeW=False):
    """Get the other pm.dt.Vector values that are not the given axis.

    Args:
        value: Some pm.dt.Vector axis description.
        includeW: Add W axis to the output.

    Returns:
        list
    """
    axis = getAxis(value)
    if axis is not None:
        skip = [axis.index] + ([] if includeW else [3])
        return [a for a in pm.dt.Vector.Axis.values() if a.index not in skip]


def invertOtherAxes(matrix, axis=0):
    """Inverts the other axes of the given rotation matrix based on rows of the matrix.

    Args:
        matrix (list): Some 4x4 list/array.
        axis: Some pm.dt.Vector axis description.

    Returns:
        pm.dt.Matrix
    """
    axis = getAxis(axis)
    others = getOtherAxes(axis)
    x, y, z = matrix[:3]
    for v in (x, y, z):
        for a in others:
            v[a.index] *= -1
    return pm.dt.Matrix(x, y, z)


def invertAxis(matrix, axis=0):
    """Inverts the other axes of the given rotation matrix based on rows of the matrix.

    Args:
        matrix (list): Some 4x4 list/array.
        axis: Some pm.dt.Vector axis description.

    Returns:
        pm.dt.Matrix
    """
    axis = getAxis(axis)
    x, y, z = matrix[:3]
    for v in (x, y, z):
        v[axis.index] *= -1
    return pm.dt.Matrix(x, y, z)