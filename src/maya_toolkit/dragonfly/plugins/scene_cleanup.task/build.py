
import maya.cmds as cmds
import collections

import py_tasker.tasks

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    LOG.debug('Running rig cleanup functions..')

    renderLayers = params['renderLayers']
    if renderLayers:
        clean_render_layers()

    deleteTurtle = params['deleteTurtle']
    if deleteTurtle:
        delete_turtle()

    deleteNamespaces = params['deleteAllNamespaces']
    if deleteNamespaces:
        del_namspace()

    deleteUnknown = params['deleteUnknownNodes']
    if deleteUnknown:
        ml_delUnknown()

    deleteOrphanRefNodes = params['deleteOrphanedReferanceNodes']
    if deleteOrphanRefNodes:
        delete_orphan_ref_nodes()

    deleteUnknownPlugins = params['deleteUnknownPlugins']
    if deleteUnknownPlugins:
        del_unknown_plugins()

    deleteUnusedShaders = params['deleteUnusedShaders']
    if deleteUnusedShaders:
        delete_unused_shaders()

    layerCleanup = params['deleteLayers']
    if layerCleanup:
        delete_layers()


def delete_unused_shaders():
    as_shdrs = cmds.ls('as*', type=['lambert', 'shadingEngine'])
    if as_shdrs:
        cmds.delete(as_shdrs)



def clean_render_layers():
    """Deletes outdated renderLayer nodes"""
    if cmds.ls(type="renderLayer"):
        for rl in cmds.ls(type="renderLayer"):
            if rl != 'defaultRenderLayer':
                cmds.delete(rl)


def delete_turtle():
    """Deletes Turtle Node from the scene"""
    if cmds.objExists('TurtleDefaultBakeLayer'):
        try:
            cmds.lockNode('TurtleBakeLayerManager', lock=False  )
            cmds.delete( 'TurtleBakeLayerManager')

            cmds.lockNode('TurtleDefaultBakeLayer', lock=False  )
            cmds.delete( 'TurtleDefaultBakeLayer')

            cmds.lockNode('TurtleRenderOptions', lock=False  )
            cmds.delete( 'TurtleRenderOptions')

            cmds.lockNode('TurtleUIOptions', lock=False  )
            cmds.delete('TurtleUIOptions')
            print "Done deleting Turtle"
        except Exception,e:
            print str(e)


def get_namespc():
    """Gather existing namespaces"""
    ttl_nmspc = {}
    nmspc = list(set(cmds.ls(showNamespace =1)))
    for nm in nmspc:
        if (nm.count(':')>0) and (nm!=':'):
            the_count = nm.split(':')
            if len(the_count) > 0:
                the_count.pop()
                if the_count:
                    for item, count in collections.Counter(the_count).items():
                        if item not in ttl_nmspc:
                            ttl_nmspc[item] = count
                        else:
                            if ttl_nmspc[item] < count:
                                ttl_nmspc[item] = count
    return ttl_nmspc


def del_namspace():
    """Delete gathered namespaces"""
    all_nmspc = get_namespc()
    for nm in all_nmspc.keys():
        for i in range(all_nmspc[nm]):
            try:
                cmds.namespace( removeNamespace=nm, mergeNamespaceWithRoot=1)
            except Exception,e:
                pass
    print "Done deleting namespace"


def ml_delUnknown():
    """Delete Unknown Nodes"""
    unknown_nodes = cmds.ls(type='unknown')
    print "Found Unknown Nodes:", unknown_nodes
    if unknown_nodes:
        for n in unknown_nodes:
            try:
                cmds.lockNode(n , l=False)
                cmds.delete(n)
            except:
                print 'Could not delete unknown node: {}'.format(n)
                pass
    print "Done deleting Unknown Nodes"


def delete_orphan_ref_nodes():
    """Delete Orphaned Referance Nodes"""
    RN_nodes = cmds.ls(references=1)
    for rf in RN_nodes:
        try:
            filename = cmds.referenceQuery( rf,filename=True )
        except Exception, e:
            cmds.lockNode(rf, lock = 0)
            cmds.delete(rf)
            continue


def del_unknown_plugins():
    """Delete Unknown Plugins"""
    unknown_plugins = cmds.unknownPlugin(q=True, list=True)
    print "Unknown Plugins Found :",unknown_plugins
    deleted_plugs = []
    if unknown_plugins:
        for plugin in unknown_plugins:
            try:
                cmds.unknownPlugin(plugin, remove=True)
                deleted_plugs.append(plugin)
            except Exception,e:
                print '\nEXCEPTION occured:',e
                continue
    if deleted_plugs:
        print "Cleaned Plugins: %s"%(' '.join(deleted_plugs) )
    else:
        print "No Plugins cleaned"

def delete_layers():
    """Delete any leftover layers"""
    layer = cmds.ls(type='displayLayer')
    d = 'defaultLayer'
    for a in layer:
        if a == d:
            continue
        cmds.setAttr(a + '.displayType', 0)
        cmds.setAttr(a + '.playback', 1)
        cmds.setAttr(a + '.visibility', 1)
        cmds.delete(a)

