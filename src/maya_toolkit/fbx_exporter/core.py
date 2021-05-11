import os
import ast
import json
import logging
from fbx_exporter.decorator import decorator
#from decorator import decorator

import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om2

import clips


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
MTYPE_RIG = 'dragonfly.rig'


@decorator
def hidesModelPanels(func, *args, **kwargs):
    """Decorator that will hide the model panels while the function is running and
    then restoring the layout when finished. This greatly speeds up operations
    that step through the timeline. When the function is being called, the
    main panel in Maya will go to single view and switch to the outliner. When
    finished, the original layout should be restored.

    To use. decorate the function like this::
        @hidesModelPanels
        def myFunction(arg1, arg2, ...):
            # function body
    """
    mainPane = mel.eval('string $tmpStr = $gMainPane;')
    cmds.panelHistory('mainPanelHistory', e=True, suspend=True)
    # go to single perspective
    cmds.paneLayout(mainPane, e=True, cn='single')
    mainPanels = cmds.paneLayout(mainPane, q=True, childArray=True)

    modelPanel = None
    visiblePanels = cmds.getPanel(vis=True)
    # find a model panel in the main single view panel
    for vp in visiblePanels:
        if cmds.getPanel(typeOf=vp) == 'modelPanel' and vp in mainPanels:
            modelPanel = vp
            break

    outlinerPanel = None
    # if there is no model panel then we don't need to replace it
    if modelPanel:
        # create a new outliner
        outlinerPanel = cmds.outlinerPanel(parent=mainPane)
        cmds.outlinerPanel(outlinerPanel, e=True, rp=modelPanel)

        try:
            return func(*args, **kwargs)
        except:
            pass

        finally:
            # delete the outliner we created and restore the layout
            if outlinerPanel:
                cmds.deleteUI(outlinerPanel, panel=True)

            # restore the previous panel layout
            cmds.panelHistory('mainPanelHistory', e=True, suspend=False)
            cmds.panelHistory('mainPanelHistory', e=True, back=True)


def isolate_selected_nodes(node, state=True):

    mainPane = mel.eval('string $tmpStr = $gMainPane;')
    mainPanels = cmds.paneLayout(mainPane, q=True, childArray=True)
    visiblePanels = cmds.getPanel(vis=True)
    for vp in visiblePanels:
        if cmds.getPanel(typeOf=vp) == 'modelPanel' and vp in mainPanels:
            try:
                modelPanel = vp
                cmds.select(node)
                cmds.isolateSelect(modelPanel, state=state)
            except:
                LOG.error('Unable to isolate selection on: {}'.format(node))
                pass


def hide_rigs():
    all_rigs = get_by_metatype("dragonfly.rig")
    if all_rigs:
        cmds.hide(all_rigs)


def is_propIt_rig(node):
    """Check if rig was made with 'propIt'"""
    if cmds.attributeQuery('metaTypes', node=node, exists=True):
        raw_metatypes = cmds.getAttr('{}.metaTypes'.format(node))
        metatypes = json.loads(raw_metatypes)
        if 'propIt' in metatypes:
            return True
    else:
        LOG.warning("No metaTypes attribute on {}".format(node))
    return


def get_by_metatype(metatype):
    """Returns nodes with a specific metaType

    Args:
        metatype: name string for metaType

    Returns:
        list: Full path node names

    get_by_metatype("dragonfly.rig")
    """
    result = list()

    metatype_attrs = cmds.ls('*.metaTypes', '*:*.metaTypes', long=True)
    for attr in metatype_attrs:
        raw_metatypes = cmds.getAttr(attr)
        metatypes = json.loads(raw_metatypes)
        if metatype in metatypes:
            result.append(attr.split('.')[0])

    return result


def get_node():
    """Create a node that will store persistant fbx data on it.

    Currently responsible for storing:
        - clip data
        - ui settings

    Returns:
        om2.MObject: New network node
    """
    if not cmds.objExists('FBXExporterNode'):
        cmds.createNode('network', n='FBXExporterNode')

    sel = om2.MSelectionList()
    sel.add('FBXExporterNode')

    if not cmds.attributeQuery('clips', node='FBXExporterNode', exists=True):
        clips.add_clips_attr('FBXExporterNode')
    if not cmds.attributeQuery('settings', node='FBXExporterNode', exists=True):
        add_settings_attr('FBXExporterNode')
    if not cmds.attributeQuery('rigs', node='FBXExporterNode', exists=True):
        add_rigs_attr('FBXExporterNode')

    return sel.getDependNode(0)


def add_settings_attr(node_name):
    """Add a string type attribute to the given node, this attribute is used to store the UI settings.

    Args:
        node_name(str): Name of a maya dependency node

    Returns:
        None
    """
    cmds.addAttr(node_name, ln='settings', dt='string', k=True)
    cmds.setAttr('{0}.settings'.format(node_name), '{}', type='string')


def add_rigs_attr(node_name):
    """Add a string type attribute to the given node, this attribute is used to store the UI settings.

    Args:
        node_name(str): Name of a maya dependency node

    Returns:
        None
    """
    cmds.addAttr(node_name, ln='rigs', dt='string', k=True)
    cmds.setAttr('{0}.rigs'.format(node_name), '{}', type='string')


def save_ui_settings(settings, fn_node=None):
    fn_node = get_node()
    node_name = om2.MFnDependencyNode(fn_node).name()
    attr = '{0}.settings'.format(node_name)
    serialized_settings = json.dumps(settings)
    cmds.setAttr(attr, serialized_settings, type='string')

def save_rig_settings(rig_settings, fn_node=None):
    fn_node = get_node()
    node_name = om2.MFnDependencyNode(fn_node).name()
    attr = '{0}.rigs'.format(node_name)
    serialized_settings = json.dumps(rig_settings)
    cmds.setAttr(attr, serialized_settings, type='string')

def load_ui_settings():
    fn_node = get_node()
    node_name = om2.MFnDependencyNode(fn_node).name()
    attr = '{0}.settings'.format(node_name)
    serialized_settings = cmds.getAttr(attr)

    return json.loads(serialized_settings)

def load_rig_settings():
    fn_node = get_node()
    node_name = om2.MFnDependencyNode(fn_node).name()
    attr = '{0}.rigs'.format(node_name)
    serialized_settings = cmds.getAttr(attr)

    return json.loads(serialized_settings)

def get_current_range():
    """Get the time range in the current Maya scene.

    Returns:
        list: Frames for start and end
    """
    return [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]


def get_scene():
    """Get the scene path of the current Maya scene.

    Returns:
        str: Full file path
    """
    return cmds.file(q=True, sn=True)


def remap_anim(amount):
    """Move all animation keys/curves by a set amount.

    Args:
        amount (int): Amount of keyframes to adjust all animation curves

    Returns:
        None
    """
    anim_curves = cmds.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
    for each in anim_curves:
        cmds.keyframe(each, edit=True, relative=True, timeChange=amount)


def get_scene_directory(path=None):
    """Get the directory of the given path or get the current Maya scene directory.

    Args:
        path: Optional path to a file

    Returns:
        str: Directory where the input scene exists
    """
    if path is None:
        path = get_scene()

    return os.path.dirname(path)


def get_asset(rig_node):
    """Returns asset name from rig data stored on rig node, if that rig data
    does not exist (ie., older rig), then it tries to use the top node name.

    Args:
        rig_node: Top rig group node of rig as MObject

    Returns:
        str: Name of asset as string
    """
    rig_top_node = om2.MFnDependencyNode(rig_node).name()
    if cmds.attributeQuery('rig_data', node=rig_top_node, exists=True):
        asset_name = attr_to_py('{}.rig_data'.format(rig_top_node), 'asset')
    else:
        rig_name = rig_top_node.rsplit(':', 1)[-1]
        if "_rig" in rig_name:
            asset_name = rig_name.rsplit(':', 1)[-1].split('_rig')[0]
        else:
            asset_name = rig_name

    return asset_name


def resolve_scene_path(scene_path=None):
    """Make sure the scene exists, and has been saved atleast once.

    Args:
        scene_path: Optional scene path to resolve

    Returns:
        str: The scene path if it exists.
    """
    if scene_path is None:
        scene_path = cmds.file(q=True, sn=True)
    if not scene_path:
        raise ValueError('Current scene has no name, save the current file before exporting an FBX')

    return scene_path


def resolve_output_path(output_path, scene_path=None):
    """Make sure an output path is a valid path to save as.

    If output_path is None

    Args:
        output_path: Path to resolve
        scene_path:

    Returns:
        str: The output path
    """
    if output_path is None:
        scene_path = resolve_scene_path(scene_path)
        output_dir = os.path.dirname(scene_path)
        file_name = '{0}.fbx'.format(os.path.basename(scene_path).split('.')[0])
        output_path = os.path.join(output_dir, file_name)

    return output_path


#@hidesModelPanels
def export_rigs(nodes, clip_data, **kwargs):
    """Bake and export the given rigs as FBX animated skeletons.

    Args:
        nodes: Valid rig nodes
        clip_data: list of clip type data
        **kwargs: keyword arguments for `export_rig`

    Returns:
        None
    """
    if not nodes:
        raise ValueError('Could not run FBX export, needs atleast 1 rig')
    # If clips, we're doing an animation export
    LOG.info(clip_data)
    if clip_data:
        for clip in clip_data:
            if not clip[3]:
                continue
            for node in nodes:
                LOG.info("FBX Animation Export: {}".format(node))
                kw = dict()
                kw.update(kwargs)
                kw['clipName'] = clip[0]
                remap_anim(-clip[1]+1)
                kw['bake_start'] = 1
                kw['bake_end'] = clip[2] - (clip[1] - 1)
                fbx_name = kw['user_filename']
                kw['output_path'] = os.path.abspath(os.path.join(kw['output_path'], fbx_name))
                kw['output_path'] = kw['output_path'].replace('\\', '/')
                kw['DeleteStaticChannels'] = kwargs['DeleteStaticChannels']

                # Check if this rig is a propIt rig
                if is_propIt_rig(node):
                    kw['ExportMeshes'] = True
                    kw['FBXExportSkins'] = True

                # Export optimizations for faster baking
                # hide all other rigs and isolateSelection
                hide_rigs()
                cmds.showHidden(node)
                cmds.refresh(suspend=True)
                # isolate select rig to export
                isolate_selected_nodes(node, state=True)

                # Turn parallel evaluation on
                current_eval_state = cmds.evaluationManager(query=True, mode=True)[0]
                cmds.evaluationManager(mode="off")
                cmds.evaluationManager(mode="parallel")

                # Do export
                export_rig(node, **kw)

                # Turn isolate select off
                isolate_selected_nodes(node, state=False)

                # Set evaluation mode back to original state
                cmds.evaluationManager(mode=current_eval_state)
                cmds.refresh(suspend=False)
    else:
        for node in nodes:
            LOG.info("FBX Rig Export: {}".format(node))
            kw = dict()
            kw.update(kwargs)
            kw['clipName'] = 'rig'
            kw['bake_start'] = 1
            kw['bake_end'] = 1
            fbx_name = kw['user_filename']
            kw['output_path'] = os.path.abspath(os.path.join(kw['output_path'], fbx_name))
            kw['output_path'] = kw['output_path'].replace('\\', '/')
            kw['DeleteStaticChannels'] = kwargs['DeleteStaticChannels']
            export_rig(node, **kw)

@hidesModelPanels
def export_rig(node, scene_path=None, output_path=None, bake_start=None, bake_end=None, snap_to_origin=False, **kwargs):
    """Bake and export the given rigs as FBX animated skeletons.

    Args:
        node: Valid rig node
        scene_path: Scene path of the rig node
        output_path: File path to save out the FBX to
        bake_start: Start frame for bake
        bake_end: End frame for bake
        snap_to_origin: Move root of the skeleton to the origin and then bake
        **kwargs: keyword arguments for `export_fbx`

    Returns:
        None
    """
    cmds.refresh()

    # make sure input node is a rig
    if isinstance(node, basestring):
        node = get_rig_mobject(node)

    if not is_rig(node):
        return

    # resolve paths
    LOG.info('Resolving paths..')
    scene_path = resolve_scene_path(scene_path)
    output_path = resolve_output_path(output_path)

    # fill rig namespace, rig name
    LOG.info('Get rig info..')
    kw = dict()
    kw['namespace'] = get_rig_namespace(node)
    kw['rig'] = get_rig_name(node)
    kw['asset'] = get_asset(node)
    kw['clip'] = kwargs['clipName']
    kw.update(kwargs)

    output_path = str(output_path).format(**kw)

    # From the bake node list, find any meshes and related blendshapes (if any)
    bake_meshes = list()
    blendshape_nodes = list()

    # for bake_node in skeleton:
    for bake_node in get_bake_nodes(node):
        bake_dag = om2.MFnDagNode(bake_node)
        if is_mesh(bake_dag.fullPathName()):
            bake_meshes.append(bake_dag.fullPathName())
            bs_nodes = get_blendshapes(mesh=bake_dag.fullPathName())
            if bs_nodes:
                for bs in bs_nodes:
                    blendshape_nodes.append(bs)
                # Only if blendShape exist do we export mesh
                bake_meshes.append(bake_dag.fullPathName())

    # Process any meshes and blendshapes found
    if bake_meshes:
        # If blendshapes are checked regardless of meshes being checked AND this is not a rig export...
        if kwargs['FBXExportShapes'] and 'rig' not in kw['clipName']:
            if blendshape_nodes:
                LOG.info('Baking blendshapes: {}'.format(''.join(bs_nodes)))
                bake_blendshapes(blendshape_nodes=blendshape_nodes, bake_start=bake_start, bake_end=bake_end)

            # In the case where if no blendshape nodes are found
            elif not blendshape_nodes and not kw['ExportMeshes']:
                for bake_mesh in bake_meshes:
                    LOG.info('No blendshape found and meshes set not to export, pruning: {}'.format(bake_mesh))
                    remove_node_from_bake_node(bake_mesh)

        # do not export meshes at all = skeletons only
        elif not kw['ExportMeshes'] and not kwargs['FBXExportShapes']:
            for bake_mesh in bake_meshes:
                LOG.info('PRUNING MESHES FROM BAKE NODES: {}'.format(bake_mesh))
                remove_node_from_bake_node(bake_mesh)
    else:
        LOG.info(bake_meshes)

    # bake rigs, strip out the skeletons
    LOG.info('Baking skeleton..')
    skip_bake = False
    if 'rig' in kw['clipName']:
        skip_bake = True
    if kwargs['DeleteStaticChannels']:
        LOG.info('Deleting static channels')
    skeleton = bake_rig(node,
                        bake_start,
                        bake_end,
                        skip_bake=skip_bake,
                        delete_static_channels=kwargs['DeleteStaticChannels'])

    # optimize scene
    LOG.info('Optimizing scene..')
    cleanup(keep_nodes=skeleton)

    # enable snap
    if snap_to_origin:
        LOG.info('Snap enabled baking at origin...')
        # snap object
        transform = om2.MFnDependencyNode().create('transform')
        transform_name = om2.MFnDagNode(transform).fullPathName()
        roots = list()
        # constrain new transform to skeleton roots
        for obj in skeleton:
            obj_name = om2.MFnDagNode(obj).fullPathName()
            cmds.parentConstraint(transform_name, obj_name, mo=False)
            roots.append(obj_name)
        # bake new animation with roots at origin
        LOG.info('Baking nodes: {0}'.format(roots))
        cmds.bakeResults(roots, t=(bake_start, bake_end), sm=True, sb=1, dic=True, pok=False)
        # removes transform and associated constraints
        cmds.delete(transform_name)

    # export skeleton fbx
    LOG.info('Exporting..')
    export_fbx(output_path, fbx_version=kw['FBXExportFileVersion'], **kwargs)
    LOG.info('Export Successful: {0}'.format(output_path))

    # reopen original file
    cmds.file(scene_path, o=True, f=True)


def is_rig(mobject):
    """Validate that the given node is a rig.

    Args:
        mobject: om2.MObject instance of the rig node

    Returns:
        bool: True if a rig, False if not
    """
    if not isinstance(mobject, om2.MObject):
        mobject = get_rig_mobject(mobject)

    rig_node = om2.MFnDependencyNode(mobject)
    if rig_node.hasAttribute('metaTypes'):
        raw_metatypes = om2.MPlug(mobject, rig_node.attribute('metaTypes')).asString()
        metatypes = json.loads(raw_metatypes)
        if MTYPE_RIG in metatypes:
            return True

    return False


def get_rig_mobject(rig_path):
    """Get the om2.MObject instance of a given rig DAG path.

    Args:
        rig_path: Full path or unique name given to a node

    Returns:
        om2.MObject: Instance object for the rig name
    """
    sel = om2.MSelectionList()
    sel.add(rig_path)
    return sel.getDependNode(0)


def get_rig_name(rig_mobject):
    """Get the short name of a given rig.

    Args:
        rig_mobject: om2.MObject instance of the rig

    Returns:
        str: Name of the rig top node
    """
    return om2.MFnDependencyNode(rig_mobject).name().rsplit(':', 1)[-1]


def get_rig_namespace(rig_mobject):
    """Get the namespace of a node.

    Args:
        rig_mobject: om2.MObject instance of the rig

    Returns:
        str: Namespace name
    """
    return om2.MFnDependencyNode(rig_mobject).namespace


def get_rigs():
    """Get all the rigs in the current Maya scene

    Returns:
        list: Full path names to all the rigs
    """
    result = list()
    attrs = cmds.ls('*.metaTypes', long=True, r=True)
    result.extend([attr.split('.', 1)[0] for attr in attrs if MTYPE_RIG in json.loads(cmds.getAttr(attr))])

    return result


def bake_rigs(rig_nodes, bake_start, bake_end):
    """Bake animation on all the given rigs.

    Args:
        rig_nodes: om2.MObject instances with the rig metaType
        bake_start: Frame to start bake
        bake_end: Frame to stop bake

    Returns:
        list: All baked node root objects from the input rigs
    """
    nodes = list()
    for node in rig_nodes:
        skeleton = bake_rig(node, bake_start, bake_end)
        nodes.append(skeleton)

    return nodes


def bake_rig(rig_mobject, bake_start=None, bake_end=None, skip_bake=False, delete_static_channels=False):
    """Bake animation on a given rig

    Args:
        rig_mobject: om2.MObject instance with the rig metaType
        bake_start: Frame to start bake
        bake_end: Frame to end bake
        skip_bake: Get bake nodes but do not perform actual bake, for rig exports
        delete_static_channels: Delete ranges of keyframes with no value or tangent changes

    Returns:
        list: baked node root objects
    """
    LOG.info('Get bake times..')
    if bake_start is None:
        bake_start = cmds.playbackOptions(q=True, min=True)
    if bake_end is None:
        bake_end = cmds.playbackOptions(q=True, max=True)

    LOG.info('Get rig node..')
    rig_dep_node = om2.MFnDependencyNode(rig_mobject)

    if not rig_dep_node.hasAttribute('bakeNodes'):
        raise ValueError('Missing `bakeNodes` attribute, add a make_bakeable task to the rig blueprint')

    LOG.info('Get bake nodes..')
    nodes = list()
    metatypes_plug = om2.MPlug(rig_mobject, rig_dep_node.attribute('bakeNodes'))
    for x in range(metatypes_plug.numElements()):
        elem_plug = metatypes_plug.elementByLogicalIndex(x)
        elem_mobject = elem_plug.source().node()
        elem_dag = om2.MFnDagNode(elem_mobject)
        nodes.append(elem_dag.fullPathName())

    if skip_bake:
        LOG.info('Skipping bake, disconnecting skeleton..')
        # Cleanly disconnect skeleton
        root_joint = ""
        for node in nodes:
            if "joint" in cmds.nodeType(node):
                root_joint = get_root_joint(joint=node)
            if root_joint:
                disconnect_skeleton_connections(root_joint)
                break
        LOG.info('Disconnecting skeleton from root joint: {}'.format(root_joint))
    else:
        LOG.info('Baking keyframes..')
        cmds.bakeResults(nodes, t=(bake_start, bake_end), sm=True, sb=1, dic=True, pok=False)
        LOG.info('Baked animation on {0} joint(s) from frame {1} to {2}'.format(len(nodes), bake_start, bake_end))

    # Delete static channels if specified
    if delete_static_channels:
        cmds.select(nodes)
        cmds.delete(staticChannels=True)

    skeleton = get_bake_nodes(rig_mobject)

    return skeleton


def get_bake_nodes(rig_mobject):
    """Get the nodes connected to the rig node's `bakeNodes` attribute.

    Args:
        rig_mobject: Input rig node

    Returns:
        list: All root nodes from the `bakeNodes` attribute on the rig node
    """
    rig_dep_node = om2.MFnDependencyNode(rig_mobject)

    nodes = list()
    metatypes_plug = om2.MPlug(rig_mobject, rig_dep_node.attribute('bakeNodes'))
    for x in range(metatypes_plug.numElements()):
        elem_plug = metatypes_plug.elementByLogicalIndex(x)
        nodes.append(elem_plug.source().node())

    roots = get_roots_from_nodes(nodes)

    return roots


def get_rig_mobjects():
    """Get all rigs in the current Maya scene as om2.MObject instances.

    Returns:
        list: om2.MObject instances
    """
    rig_paths = get_rigs()

    return [get_rig_mobject(path) for path in rig_paths]


def get_children(mobject, recursive=True):
    """Get all the child nodes of a given node

    Args:
        mobject: Input node that is an om2.MObject instance
        recursive: Get all grandchildren as well as children

    Returns:
        list: om2.MObject instances that are children to the given node
    """
    children = list()
    dag_node = om2.MFnDagNode(mobject)
    for index in range(dag_node.childCount()):
        child_mobject = dag_node.child(index)
        children.append(child_mobject)
        if recursive:
            children.extend(get_children(child_mobject))

    return children


def export_fbx(output_path, fbx_version='FBX201600', only_selection=False, **kwargs):
    """Save opened Maya scene as an FBX.

    Args:
        output_path: Full path where the FBX will be located
        fbx_version: FBX version number to export as
        only_selection: Add the `export selection` flag so only selection exports and not an entire scene
        **kwargs: Keyword arguments for the fbx settings, keys should be the mel command for a specific settings toggle

    Returns:
        str: Output path where the fbx file was saved
    """
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')

    defaults = {
        'FBXExportGenerateLog': 'false',
        'FBXExportSmoothingGroups': 'true',
        'FBXExportHardEdges': 'false',
        'FBXExportTangents': 'false',
        'FBXExportSmoothMesh': 'true',
        'FBXExportInstances': 'false',
        'FBXExportReferencedAssetsContent': 'false',
        'FBXExportBakeComplexAnimation': 'false',
        'FBXExportUseSceneName': 'false',
        'FBXExportQuaternion': 'euler',
        'FBXExportShapes': 'false',
        'FBXExportSkins': 'false',
        'FBXExportConstraints': 'false',
        'FBXExportCameras': 'false',
        'FBXExportLights': 'false',
        'FBXExportEmbeddedTextures': 'false',
        'FBXExportInputConnections': 'false',
        'FBXExportInAscii': 'false',
    }

    # export as fbx rig
    mel.eval('FBXExportFileVersion "{fbx}"'.format(fbx=fbx_version))
    mel.eval('FBXExportUpAxis {0}'.format(kwargs.pop('FBXExportUpAxis', 'y')))

    for k, v in defaults.items():
        if k in kwargs:
            mel.eval('{0} -v {1}'.format(k, str(kwargs[k]).lower()))
        else:
            mel.eval('{0} -v {1}'.format(k, v))

    LOG.info('output path {0}'.format(output_path))
    cmd = 'FBXExport -f "{0}" '.format(output_path)
    if only_selection:
        cmd += '-s'
    mel.eval(cmd)

    return output_path


def get_parents(mobject):
    """Get all the parent nodes of a given node.

    Args:
        mobject: om2.MObject instance

    Returns:
        list: om2.MObject instances that are parents of the given node
    """
    result = list()
    while mobject is not None:
        dag_node = om2.MFnDagNode(mobject)
        LOG.debug('{0} > type {1}'.format(dag_node.fullPathName(), mobject.apiTypeStr))
        parent_mobject = dag_node.parent(0)

        if parent_mobject.hasFn(om2.MFn.kWorld):
            break

        result.append(parent_mobject)
        mobject = parent_mobject

    return result


def get_roots_from_nodes(mobjects):
    """Get the top level nodes from an input list of nodes.

    Args:
        mobjects: list of om2.MObject instances

    Returns:
        list: om2.MObject instances
    """
    result = []

    for n in mobjects:
        if any([p in mobjects for p in get_parents(n)]):
            continue
        result.append(n)

    return result


def delete_nodes(keep_nodes=None):
    """Delete all nodes, except those explicitly given.

    Args:
        keep_nodes: List of nodes not to delete

    Returns:
        None
    """
    cameras = ['|persp', '|top', '|front', '|side']
    dag_nodes = om2.MItDag(om2.MItDag.kBreadthFirst)
    top_nodes = list()

    while not dag_nodes.isDone():
        dag_nodes.next()

        current_obj = dag_nodes.currentItem()
        # skip camera nodes
        # if current_obj.hasFn(om2.MFn.kCamera):
        #     continue
        if dag_nodes.fullPathName() in cameras:
            continue
        # skip world node
        if current_obj.hasFn(om2.MFn.kWorld):
            continue
        # skip non-top level nodes
        if dag_nodes.depth() > 1:
            break
        # skip explicit nodes
        if dag_nodes.currentItem() in keep_nodes:
            continue

        top_nodes.append(dag_nodes.currentItem())

    node_names = [om2.MFnDagNode(x).fullPathName() for x in top_nodes]
    LOG.debug(node_names)
    cmds.delete(node_names)


def cleanup(keep_nodes):
    """Optimize the current scene for FBX export.

    Does the following:
    - imports all referenced files
    - removes all namespaces
    - removes all nodes not to keep, and makes all keep nodes top level items in the DAG

    Args:
        keep_nodes: DAG node list of things not to delete

    Returns:
        None
    """
    # make sure no references
    import_all_references()
    # move nodes out of any hierarchy
    for obj in keep_nodes:
        dag_obj = om2.MFnDagNode(obj)
        if not dag_obj.parent(0).hasFn(om2.MFn.kWorld):
            cmds.parent(dag_obj.fullPathName(), w=True)
    # delete other nodes
    delete_nodes(keep_nodes)
    # remove namespaces
    remove_namespaces()


def import_all_references():
    """Import every referenced file in the current Maya scene.

    Returns:
        None
    """
    refs = cmds.file(q=True, r=True)
    for ref in refs:
        if cmds.referenceQuery(ref, il=True):
            LOG.debug('Importing Reference {0}'.format(ref))
            cmds.file(ref, ir=True)


def remove_namespaces(empty_first=True, defaults=('UI', 'shared')):
    """Remove namespaces from the current Maya scene.

    Args:
        empty_first: Remove nodes from the namespace before deleting it
        defaults: Namespaces to keep

    Returns:
        None
    """
    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
    namespaces.sort(key=lambda x: ns.count(':'), reverse=True)
    for ns in namespaces:
        try:
            cmds.namespace(rm=ns, mnr=empty_first)
        except RuntimeError as e:
            LOG.exception('Could not remove namespace, it might not be empty: {}'.format(e))


def get_blendshapes(mesh=None):
    """Returns list of blendshapes in mesh's history

    Args:
        mesh: Name of mesh's transform to query blendshapes

    Returns:
        list: blendshapes connected to mesh

    Example:
        get_blendshapes_from_mesh(mesh="CH_Pufferfish_01_SK_LOD0:Ch_Pufferfish_01_SM")
        // Result: [u'CH_Pufferfish_01_SK_LOD0:blendShape1'] //
    """
    mesh_shp = cmds.listRelatives(mesh, shapes=True)
    if mesh_shp:
        bs_nodes = list()
        mesh_his = cmds.listHistory(mesh_shp[0])
        for node in mesh_his:
            if "blendShape" in cmds.nodeType(node):
                bs_nodes.append(node)
        return bs_nodes


def bake_blendshapes(blendshape_nodes=None, bake_start=None, bake_end=None):
    """Bakes all blendshape attrs on input blendshapes

    Args:
        blendshape_nodes: List of blendshape nodes
        bake_start: Start frame number
        bake_end: End frame number

    Returns:
        None

    Example:
        bs = ['CH_Pufferfish_01_SK_LOD0:blendShape1']
        bake_blendshapes(blendshape_nodes=bs, bake_start=1, bake_end=100)
    """
    if blendshape_nodes:
        try:
            cmds.bakeResults(blendshape_nodes, t=(bake_start, bake_end), sm=True, sb=1, dic=True, pok=False)
            return True
        except Exception:
            raise Exception('Error baking blendshape attributes')


def is_mesh(mesh):
    """Check if the specified object is a polygon mesh or transform parent of a mesh

    Args:
        mesh: Object to query

    Returns:
        True/False
    """
    # Check Object Exists
    if not cmds.objExists(mesh):
        return False

    # Check Shape
    if 'transform' in cmds.nodeType(mesh, i=True):
        mesh_shape = cmds.ls(cmds.listRelatives(mesh, s=True, ni=True, pa=True) or [], type='mesh')
        if not mesh_shape:
            return False
        mesh = mesh_shape[0]

    # Check Mesh
    if cmds.objectType(mesh) != 'mesh':
        return False

    # Return Result
    return True


def remove_node_from_bake_node(node):
    """Used to remove node from rig's bake node list, for example, remove a mesh if meshes are not to be exported

    Args:
        node: Object to remove from bakeNodes list of rig node

    Returns:
        None
    """
    if cmds.objExists(node):
        cxns = cmds.listConnections("{}.message".format(node), s=False, d=True, plugs=True)
        if cxns:
            for cxn in cxns:
                if 'bakeNodes' in cxn:
                    cmds.disconnectAttr("{}.message".format(node), cxn)
                    cmds.removeMultiInstance(cxn)


def disconnect_skeleton_connections(root_joint):
    """Cleanly disconnects all incoming connections to skeleton hierarchy

    Args:
        Joiint to traverse down from and disconnect all transform attrs from

    Returns:
        None

    Example:
        disconnect_skeleton_connections("Cn_root_jnt")
    """
    if cmds.objExists(root_joint):
        all_joints = cmds.listRelatives(root_joint, ad=True, type="joint")
        all_joints.append(root_joint)
        if all_joints:
            for jnt in all_joints:
                attrs = ['tx', 'ty', 'tz', 'translate',
                         'rx', 'ry', 'rz', 'rotate',
                         'sx', 'sy', 'sz', 'scale',
                         'visibility']
                for attr in attrs:
                    incoming_connection = cmds.listConnections("{}.{}".format(jnt, attr), source=True,
                                                               destination=False, plugs=True)
                    if incoming_connection:
                        cmds.disconnectAttr(incoming_connection[0], "{}.{}".format(jnt, attr))
            LOG.info("Deleted incoming skeleton connections for: {}".format(root_joint))


def get_root_joint(joint=""):
    """Function to find the top parent joint node from the given 'joint' maya node
        Example:
            topParentJoint = get_root_joint(joint="LShoulder")

    Args:
        joint (string) : name of the maya joint to traverse from

    Returns:
        A string name of the top parent joint traversed from 'joint'
    """
    # Search through the root_joint's top most joint parent node
    root_joint = joint

    while True:
        parent = cmds.listRelatives(root_joint, parent=True, type='joint')
        if not parent:
            break
        root_joint = parent[0]

    return root_joint


def attr_to_py(attr, key):
    """Take previously stored data on a Maya attribute (put there via py_to_attr()),
    and read it back to valid Python values.

    Args:
        attr: An existing attribute name in the scene with pickled data
        key: Optional key to specify

    Examples:
        See above pyToAttr
    """
    if cmds.objExists(attr):
        string_data = str(cmds.getAttr(attr))
        data_dict = ast.literal_eval(string_data)
        if key:
            return data_dict[key]
        else:
            return data_dict
    else:
        return None


def get_current_playback_settings():
    """Get the playback settings from the current time slider.

    Returns:
        dict: min, max, animation start and end frames.
    """
    result = dict()
    result['min'] = cmds.playbackOptions(q=True, min=True)
    result['max'] = cmds.playbackOptions(q=True, max=True)
    result['ast'] = cmds.playbackOptions(q=True, ast=True)
    result['aet'] = cmds.playbackOptions(q=True, aet=True)

    return result
