# built-ins
import os
import logging
import json
import tempfile
import re

# third party
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2


LOG = logging.getLogger(__name__)
XML_IMPORT_METHOD = ['index', 'nearest', 'barycentric', 'bilinear', 'over']
WEIGHT_FILE_TYPE = ['json', 'binary', 'xml']


def get_weights_directory():
    """Get the `weights` directory based on the current scene file path.

    Returns:
        str: Full directory path
    """
    scene_path = cmds.file(q=True, sn=True)
    if not scene_path:
        LOG.exception('No weights directory')
        return

    scene_dir = os.path.abspath(scene_path).rsplit(os.path.sep, 1)[0]
    if not os.path.exists(os.path.join(scene_dir, 'weights')):
        LOG.exception('No weights directory')
        return

    return os.path.join(scene_dir, 'weights')


def export_weights(file_name, nodes=None, export_type=0, **kwargs):
    """Saved skin cluster weights to a file.

    Args:
        file_name: Name to give the output file
        nodes: Optionally designate the nodes with skin clusters to be exported
        export_type: An enumeration [0=JSON, 1=Maya Binary, 2=XML]
        **kwargs: Extra keyword arguments for JSON exporting

    Returns:
        None
    """
    if nodes is None:
        nodes = cmds.ls(sl=True, fl=True)

    skins = {node: get_skin(node) for node in nodes}

    kw = dict()
    kw['skins'] = skins
    kw.update(kwargs)

    result = None
    if export_type == 0:
        result = export_json_weights(file_name, **kw)
    elif export_type == 1:
        pass
    elif export_type == 2:
        result = export_xml_weights(file_name, skins)
    else:
        raise ValueError('Export type does not exist, {}'.format(export_type))

    LOG.info('Skin weights exported: {}'.format(result))


def import_weights(file_path, nodes=None, **kwargs):
    """Import skin weights from a given file.

    Args:
        file_path: Full path to a weight file
        nodes: Optionally designate nodes to import weights onto
        **kwargs: Extra keyword arguments for importing JSON or XML weights

    Returns:
        None
    """
    if nodes is None:
        nodes = cmds.ls(sl=True, fl=True)

    skins = [get_skin(n) for n in nodes]

    if file_path.endswith('.xml'):
        for skin in skins:
            import_xml_weights(file_path, skin, **kwargs)
    elif file_path.endswith('.json'):
        for num, skin in enumerate(skins):
            import_json_weights(file_path, skin, nodes[num], **kwargs)
    elif file_path.endswith('.mb'):
        raise NotImplementedError
    else:
        raise ValueError('File is not a valid weight data file, must be a JSON, XML, or Maya Binary type')


def import_xml_weights(file_path, skin, method=0, **kwargs):
    """Import xml file skin weights.

    Args:
        file_path: Full file path to the XML weight file
        skin: Skin cluster node to apply the weights to
        method: Import method for cmds.deformerWeights [0='index', 1='nearest', 2='barycentric', 3='bilinear', 4='over']
        **kwargs: Keyword arguments for cmds.deformerWeights command

    Returns:
        None
    """
    cmds.deformerWeights(file_path, im=True, method=XML_IMPORT_METHOD[method], deformer=skin, **kwargs)


def export_xml_weights(file_name, skins):
    """Save out skin weights to an XML file.

    Args:
        file_name: Name for output file
        skins: Skin clusters to gather skin weights from

    Returns:
        str: File path to output weights file
    """
    weights_dir = get_weights_directory()

    if not os.path.exists(weights_dir):
        os.makedirs(weights_dir)

    output_file_name = '{}.xml'.format(file_name)

    skin_names = [oma2.MFnSkinCluster(v).name() for k, v in skins.items()]
    output_path = cmds.deformerWeights(output_file_name, p=weights_dir, ex=True, vc=True, deformer=skin_names)

    return output_path


def export_binary_weights(file_name, skins):
    """Save out skin weights as a Maya Binary file.

    Args:
        file_name: Name for output file
        skins: Skin clusters to gather skin weights from

    Returns:
        str: File path to output weights file
    """
    weights_dir = get_weights_directory()
    output_path = os.path.join(weights_dir, '{}.mb'.format(file_name))
    cmds.file(output_path, ea=True, type='mayaBinary')

    return output_path


def import_json_weights(file_path, skin, mesh_key, **kwargs):
    """Apply skin weights from a json file to specified geometry.

    Args:
        file_path: Full file path to the JSON skin weights file
        skin: Skin clusters to apply weight data to
        mesh_key: Mesh name to evaluate and apply data to
        **kwargs: Currently unavailable

    Returns:
        None
    """
    with open(file_path, 'r') as fp:
        weight_data = json.load(fp)

    mesh_vert_count = cmds.polyEvaluate(mesh_key, v=True)
    file_vert_count = len(weight_data[mesh_key])
    if mesh_vert_count != file_vert_count:
        LOG.warning('Weight file has a different point count than the current geometry: {0}--{1}:{2}'.format(mesh_key, mesh_vert_count, file_vert_count))
        return

    skin_influences = set([x.fullPathName() for x in oma2.MFnSkinCluster(skin).influenceObjects()])
    file_influences = set([y[0] for x in weight_data[mesh_key] for y in x[1]])
    if skin_influences != file_influences:
        missing_in_file = skin_influences.difference(file_influences)
        missing_in_skin = file_influences.difference(skin_influences)
        if missing_in_skin:
            LOG.warning('Skin is missing influences: {}'.format(*missing_in_skin))
        elif missing_in_file:
            LOG.warning('Weight file is missing influences: {}'.format(*missing_in_file))

    set_weights(skin, weight_data[mesh_key])


def export_json_weights(file_name, skins, prune=True, use_influence_names=True):
    """Save out skin weights to a JSON file.

    Args:
        file_name: Name to give output file
        skins: Skin clusters to export skin data from
        prune: Remove influences with zero weights
        use_influence_names: Use names instead of UUID in output file

    Returns:
        str: Output file path
    """
    weight_data = dict()
    for k, v in skins.items():
        weight_data[k] = get_weights(v, prune, use_influence_names)

    weights_dir = get_weights_directory()

    if not os.path.exists(weights_dir):
        os.makedirs(weights_dir)

    output_path = '{}.json'.format(os.path.join(weights_dir, file_name))

    with open(output_path, 'w') as fp:
        json.dump(weight_data, fp, indent=2)

    return output_path


def get_skin_influences(skin):
    """Get a skin clusters influence list.

    Args:
        skin: Skin cluster name or mobject

    Returns:
        dict: A map where keys are the logical index and values are the names of the influences
    """
    influences = dict()

    sel = om2.MSelectionList()
    sel.add(skin)
    skin_mobject = sel.getDependNode(0)
    mfn_skin = oma2.MFnSkinCluster(skin_mobject)

    mfn_influences = mfn_skin.influenceObjects()

    for num in range(len(mfn_influences)):
        influence_idx = om2.MFnDependencyNode(mfn_influences[num].node()).uuid().asString()
        logical_index = mfn_skin.indexForInfluenceObject(mfn_influences[num])
        influences[int(logical_index)] = influence_idx

    return influences


def get_skin(node):
    """Get a geometry's skin cluster.

    Args:
        node: Node name or mobject

    Returns:
        om2.MObject: Maya API object representing the skin cluster node
    """
    sel = om2.MSelectionList()
    sel.add(node)
    node_mobject = sel.getDependNode(0)

    if any([node_mobject.hasFn(x) for x in (om2.MFn.kMesh, om2.MFn.kNurbsSurface, om2.MFn.kNurbsCurve)]):
        shape_mobject = node_mobject
    else:
        node_dag_path = sel.getDagPath(0)
        shape_mobject = node_dag_path.extendToShape(0).node()

    skin_mobject = None

    dg = om2.MItDependencyGraph(shape_mobject, om2.MFn.kSkinClusterFilter, om2.MItDependencyGraph.kUpstream)
    while not dg.isDone():
        current_node = dg.currentNode()
        if not current_node.isNull() and current_node.hasFn(om2.MFn.kSkinClusterFilter):
            skin_mobject = current_node
            break

    return skin_mobject


def get_weights(skin, prune=False, use_influence_names=False):
    """Given a skin cluster node, gather all the weight data in sequential vertex order.

    Args:
        skin: Skin cluster name or mobject
        prune: Remove skin weight data that is zero
        use_influence_names: Use node names instead of node UUIDs

    Returns:
        list: Skin weights nested by vertex order, then influence order
    """
    data = list()

    mfn_skin = oma2.MFnSkinCluster(skin)
    influences = get_skin_influences(skin)

    if use_influence_names:
        influences = {k: cmds.ls(v, long=True)[0] for k, v in influences.items()}

    weight_list_attr = mfn_skin.findPlug('weightList', False)
    vertices = weight_list_attr.getExistingArrayAttributeIndices()

    weight_list_attr.evaluateNumElements()

    for vert in vertices:
        weights = list()
        weight_list_index_attr = weight_list_attr.elementByLogicalIndex(vert)
        weights_attr = weight_list_index_attr.child(0)
        influence_ids = weights_attr.getExistingArrayAttributeIndices()

        infPlug = om2.MPlug(weights_attr)

        for index in influence_ids:
            infPlug.selectAncestorLogicalIndex(index, weights_attr.attribute())
            influence = influences[index]
            value = infPlug.asDouble()
            if prune and value <= 0.0:
                continue
            weights.append([influence, value])
        data.append([vert, weights])

    return data


def set_weights(skin, data, prune=False):
    """Set an skin cluster with weight data.

    Args:
        skin: Skin cluster node or mobject
        data: Weight data specifically in the format `get_weights` returns
        prune: Remove unused influences from the skin cluster

    Returns:
        None
    """
    influences = get_skin_influences(skin)
    influences_remapped = {v: k for k, v in influences.items()}
    mfn_skin = oma2.MFnSkinCluster(skin)
    for vert, weights in data:
        weight_list_index_attr = '{skincluster}.weightList[{vertId}]'.format(skincluster=mfn_skin.name(), vertId=vert)
        for influence, weight_value in weights:
            influence_logical_index = influences_remapped[influence]
            weights_attr = '.weights[{influenceId}]'.format(influenceId=influence_logical_index)
            cmds.setAttr(weight_list_index_attr + weights_attr, weight_value)
    if prune:
        skin_name = om2.MFnDependencyNode(skin).name()
        skin_geo = om2.MFnDependencyNode(oma2.MFnGeometryFilter(skin).getOutputGeometry()[0]).name()
        cmds.skinPercent(skin_name, skin_geo, nrm=False, prw=0)


def get_uuid(node_name):
    """Get a node's unique identifier in Maya.

    Args:
        node_name: short or long node name

    Returns:
        str: Node UUID
    """
    sel = om2.MSelectionList()
    sel.add(node_name)
    mobject = sel.getDependNode(0)
    depend_node = om2.MFnDependencyNode(mobject)

    return depend_node.uuid().asString()


def name_from_uuid(uuid):
    """Returns node's name from given uuid

    Args:
        uuid: valid uuid of existing node in scene

    Returns:
        str: Node name
    """
    uuidPattern = re.compile('^[A-F0-9]{8}-([A-F0-9]{4}-){3}[A-F0-9]{12}$')
    if isinstance(uuid, basestring) and uuidPattern.match(uuid):
        try:
            node_str = str(cmds.ls(uuid)[0])
            return node_str
        except:
            raise Exception("Not a valid UUID value")


def add_metatype_attribute(node):
    """Add a special attribute named `metaTypes` to a node.

    This attributes allows a user to mark nodes for a specific purpose, that can be easily looked up later.

    Args:
        node: Node name or mobject

    Returns:
        None
    """
    if isinstance(node, om2.MObject):
        node = om2.MFnDependencyNode(node).name()
    if not cmds.attributeQuery('metaTypes', node=node, exists=True):
        cmds.addAttr(node, ln='metaTypes', dt='string')
        cmds.setAttr('{}.metaTypes'.format(node), '[]', type='string')


def add_metatype(node, metatype):
    """Add a new metaType to a node.

    Args:
        node: Node name or mobject
        metatype: Unique string that represents the metaType value

    Returns:
        None
    """
    add_metatype_attribute(node)
    attr = '{}.metaTypes'.format(node)
    value = json.loads(cmds.getAttr(attr))
    value.append(metatype)
    value = json.dumps(value)
    cmds.setAttr(attr, value, type='string')


def get_metatype(metatype):
    """Get nodes with a specific metaType

    Args:
        metatype: name string for metaType

    Returns:
        list: Full path node names
    """
    result = list()

    metatype_attrs = cmds.ls('*.metaTypes', long=True)
    for attr in metatype_attrs:
        raw_metatypes = cmds.getAttr(attr)
        metatypes = json.loads(raw_metatypes)
        if metatype in metatypes:
            result.append(attr.split('.')[0])

    return result


def check_metatype(node, metatype):
    """Check if node has meta_type

    Args:
        node:  Node to check existence of metatype
        metatype:  Name of metaType to check for

    Example:
        # Check if rig node is a propIt metaType
        check_metatype('cone:cone_rig', 'propIt')
    """
    if cmds.attributeQuery('metaTypes', node=node, exists=True):
        raw_metatypes = cmds.getAttr('{}.metaTypes'.format(node))
        metatypes = json.loads(raw_metatypes)
        if metatype in metatypes:
            return True
    return


def export_lod_fbx(rig_node, output_path, meshes, skeleton_root, fbx_version='2015', triangulate=False, disconnect_joints=True):
    """Save out a rig's deformation skeleton_root and meshes.

    Args:
        rig_node: Rig root/top node
        output_path: Full path where the FBX will be located
        meshes: List of meshes to export
        skeleton_root:  skeleton_root root joint to export

    Returns:
        None
    """
    export_nodes = list()
    export_nodes.extend(meshes)
    export_nodes.extend([skeleton_root])

    # Delete constraints on joints first
    skeleton_root_joints = cmds.listRelatives(skeleton_root, ad=True, type="joint")
    if skeleton_root_joints:
        cmds.select(skeleton_root, skeleton_root_joints)
        cmds.delete(constraints=True)

    # Break any connections to keyable attrs on joints
    if disconnect_joints:
        break_input_connections(skeleton_root, hierarchy=True, children=True, allDescendants=True)

    try:
        cmds.parent(export_nodes, w=True)
    except:
        pass

    cmds.delete(rig_node)

    #export_nodes.extend([x for node in export_nodes for x in cmds.listRelatives(node, ad=True)])
    cmds.select(clear=True)
    cmds.select(export_nodes)

    if not cmds.pluginInfo('fbxmaya', q=True, l=True):
        cmds.loadPlugin('fbxmaya')

    # export as fbx rig
    mel.eval('FBXExportFileVersion "FBX{}00"'.format(fbx_version))
    #mel.eval('FBXExportFileVersion "FBX201600"')
    # Geometry
    mel.eval("FBXExportSmoothingGroups -v true")
    mel.eval("FBXExportHardEdges -v false")
    mel.eval("FBXExportTangents -v false")
    mel.eval("FBXExportSmoothMesh -v true")
    mel.eval("FBXExportInstances -v false")
    mel.eval("FBXExportReferencedAssetsContent -v false")
    if triangulate:
        mel.eval("FBXExportTriangulate -v true")
    else:
        mel.eval("FBXExportTriangulate -v false")
    # Animation
    mel.eval("FBXExportBakeComplexAnimation -v false")
    mel.eval("FBXExportUseSceneName -v false")
    mel.eval("FBXExportQuaternion -v euler")
    mel.eval("FBXExportShapes -v true")
    mel.eval("FBXExportSkins -v true")
    # Constraints
    mel.eval("FBXExportConstraints -v false")
    # Cameras
    mel.eval("FBXExportCameras -v false")
    # Lights
    mel.eval("FBXExportLights -v false")
    # Embed Media
    mel.eval("FBXExportEmbeddedTextures -v false")
    # Connections
    mel.eval("FBXExportInputConnections -v false")
    # Axis Conversion
    mel.eval("FBXExportUpAxis y")

    cmd = 'FBXExport -f "{0}" -s'.format(output_path)
    mel.eval(cmd)


def export_fbx(rig_node, output_path):
    """Save out a rig's deformation skeleton and meshes.

    Args:
        rig_node: Rig root/top node
        output_path: Full path where the FBX will be located

    Returns:
        None
    """
    export_nodes = list()

    meshes = cmds.listRelatives(rig_node['meshesGroup'], c=True)
    export_nodes.extend(meshes)

    skeleton = cmds.listRelatives(rig_node['skeletonGroup'], c=True)
    export_nodes.extend(skeleton)

    cmds.parent(export_nodes, w=True)

    cmds.delete(rig_node['rig'])

    export_nodes.extend([x for node in export_nodes for x in cmds.listRelatives(node, ad=True)])
    cmds.select(export_nodes, r=True)

    if not cmds.pluginInfo('fbxmaya', q=True, l=True):
        cmds.loadPlugin('fbxmaya')

    # export as fbx rig
    mel.eval('FBXExportFileVersion "FBX201600"')
    # Geometry
    mel.eval("FBXExportSmoothingGroups -v false")
    mel.eval("FBXExportHardEdges -v false")
    mel.eval("FBXExportTangents -v false")
    mel.eval("FBXExportSmoothMesh -v true")
    mel.eval("FBXExportInstances -v false")
    mel.eval("FBXExportReferencedAssetsContent -v false")
    # Animation
    mel.eval("FBXExportBakeComplexAnimation -v false")
    mel.eval("FBXExportUseSceneName -v false")
    mel.eval("FBXExportQuaternion -v euler")
    mel.eval("FBXExportShapes -v true")
    mel.eval("FBXExportSkins -v true")
    # Constraints
    mel.eval("FBXExportConstraints -v false")
    # Cameras
    mel.eval("FBXExportCameras -v false")
    # Lights
    mel.eval("FBXExportLights -v false")
    # Embed Media
    mel.eval("FBXExportEmbeddedTextures -v false")
    # Connections
    mel.eval("FBXExportInputConnections -v false")
    # Axis Conversion
    mel.eval("FBXExportUpAxis y")

    cmd = 'FBXExport -f "{0}" -s'.format(output_path)
    mel.eval(cmd)


def export_rig(rig_node, output_path):
    """Process a rig file by creating a temp version of the rig, then exporting it as a FBX.

    Args:
        rig_node: Rig root/top node
        output_path: Full path to the output location

    Returns:
        None
    """
    file_name = cmds.file(q=True, sn=True, shn=True)
    if not file_name:
        file_name = 'rig'
    else:
        file_name = file_name.split('.')[0]
    temp_path = os.path.join(tempfile.gettempdir(), '{}_exported_rig.mb'.format(file_name))
    scene_name = cmds.file(q=True, sn=True)
    cmds.select(rig_node['rig'], r=True)
    cmds.file(temp_path, es=True, typ='mayaBinary', f=True)
    export_fbx(rig_node, output_path)
    cmds.file(scene_name, o=True, f=True)
    cmds.file(rn=scene_name)


def remove_namespaces(empty_first=True, defaults=('UI', 'shared')):
    """Remove namespaces from the current Maya scene.

    Args:
        empty_first: Remove nodes from the namespace before deleting it
        defaults: Namespaces to keep

    Returns:
        None
    """
    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
    namespaces.sort(key=lambda ns: ns.count(':'), reverse=True)
    for ns in namespaces:
        try:
            cmds.namespace(rm=ns, mnr=empty_first)
            LOG.debug('Removed namespace: `{0}`'.format(ns))
        except RuntimeError as e:
            LOG.exception('Could not remove namespace, it might not be empty: {}'.format(e))


def break_input_connections(node, hierarchy=True, children=True, allDescendants=True):
    """Use to disconnect attr connections to nodes"""
    node_list = list()
    node_list.append(node)
    if hierarchy:
        children = cmds.listRelatives(node, children=children, ad=allDescendants)
        if children:
            for child in children:
                node_list.append(child)

    for node in node_list:
        attrs = cmds.listAttr(node, k=True)
        if attrs:
            for attr in attrs:
                cxn = cmds.listConnections('{}.{}'.format(node, attr), s=True, d=False, plugs=True)
                if cxn:
                    cmds.disconnectAttr(cxn[0], '{}.{}'.format(node, attr))

    return node_list


def resolve_file_path(file_path):
    """Returns full path from full or relative input file path

    resolve_file_path('deform/skinClusters/Octopus_LOD0_Mesh.skin')
    """
    if file_path:
        if os.path.exists(file_path):
            return file_path
        else:
            proj_path = cmds.workspace(q=True, rd=True)
            return "{}{}".format(proj_path, file_path)
    else:
        LOG.error('No file path specified!')
