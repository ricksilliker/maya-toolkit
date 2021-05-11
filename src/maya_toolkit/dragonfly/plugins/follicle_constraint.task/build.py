import maya.cmds as cmds
import maya.api.OpenMaya as om2

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    if not cmds.pluginInfo('matrixNodes', q=True, l=True):
        cmds.loadPlugin('matrixNodes')

    follicle = cmds.createNode('follicle')
    follicle_transform = cmds.listRelatives(follicle, p=True)[0]
    cmds.connectAttr('{}.outRotate'.format(follicle), '{}.rotate'.format(follicle_transform))
    cmds.connectAttr('{}.outTranslate'.format(follicle), '{}.translate'.format(follicle_transform))
    cmds.connectAttr('{}.worldMatrix'.format(params['geometry'].name()), '{}.inputWorldMatrix'.format(follicle))

    cmds.parent(follicle_transform, rig['rigGroup'])

    geometry_dag_path = get_dag_path(params['geometry'].name())
    m_point = om2.MPoint(cmds.xform(params['target'].name(), q=True, ws=True, t=True))
    if geometry_dag_path.hasFn(om2.MFn.kTransform):
        dag_path = om2.MFnDagNode(geometry_dag_path).dagPath()
        dag_path.extendToShape(0)
    else:
        dag_path = geometry_dag_path

    if dag_path.hasFn(om2.MFn.kMesh):
        cmds.connectAttr('{}.worldMesh'.format(dag_path.partialPathName()), '{}.inputMesh'.format(follicle))
        param_u_value, param_v_value, face_id = om2.MFnMesh(dag_path).getUVAtPoint(m_point, om2.MSpace.kWorld)
    elif dag_path.hasFn(om2.MFn.kNurbsSurface):
        cmds.connectAttr('{}.worldSpace'.format(dag_path.partialPathName()), '{}.inputSurface'.format(follicle))
        param_u_value, param_v_value = om2.MFnNurbsSurface(dag_path).getParamAtPoint(m_point, om2.MSpace.kWorld)
    else:
        raise ValueError('`geometry` Parameter should be either a Mesh or Nurbs Surface')

    cmds.setAttr('{}.parameterU'.format(follicle), param_u_value)
    cmds.setAttr('{}.parameterV'.format(follicle), param_v_value)

    pc = cmds.parentConstraint(follicle_transform, params['target'].name(), mo=params['maintainOffset'])
    sc = cmds.scaleConstraint(follicle_transform, params['target'].name(), mo=params['maintainOffset'])
    cmds.parent(pc, sc, rig['noXformGroup'])


def get_mobject(node):
    sel = om2.MSelectionList()
    sel.add(node)

    return sel.getDependNode(0)


def get_dag_path(node):
    sel = om2.MSelectionList()
    sel.add(node)

    return sel.getDagPath(0)