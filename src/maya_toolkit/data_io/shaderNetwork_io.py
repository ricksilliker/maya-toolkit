"""

    Test shader assignment to model?
    Add per file export

    # Example of writing out shader network data for two shaders
    from data_io import shaderNetwork_io
    reload(shaderNetwork_io)

    shaders = ['Ch_Pufferfish_01_body_SMSG', 'Ch_Pufferfish_01_fins_SMSG']
    shader_path = 'D:\\dev\\reef\\SourceArt\\Characters\\Pufferfish\\Rig\\work\\Pufferfish\\data\\Pufferfish_shaders.json'
    shaderNetwork_io.export(shader_path, shaders)

    # Example for reading shader data file into scene

"""
# Read and write(export) the shader networks to custom data format
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import json
import logging
import pprint
import os

LOG = logging.getLogger(__name__)

defaultShadingEngines = ['initialParticleSE', 'initialShadingGroup']  # default shading engines

# write (export) multiple shader networks
# shadingEngineNodes = ['Body_VRayMtlSG', ''Teeth_VRayMtol_ShaderSG']
# shadingEngineNodes = ['Body_VRayMtlSG']
# write (export) all shader networks
# shadingEngineNodes = pm.ls(type='shadingEngine')

def export(exportPath, shadingEngineNodes, per_file=False):
    """Exports all shader network nodes, attr and connection data for given shadingEngineNodes to json file
    
    Args:
        exportPath: 
        shadingEngineNodes: 
        per_file:
        
    Returns:
         Output shader data file
         
    Examples:
        # write (export) multiple shader networks
        # shadingEngineNodes = ['Body_VRayMtlSG', ''Teeth_VRayMtol_ShaderSG']
        # shadingEngineNodes = ['Body_VRayMtlSG']
        # write (export) all shader networks
        # shadingEngineNodes = pm.ls(type='shadingEngine')
    """
    shaderNetworkData = {}
    mesh_list = list()
    for eachShadingEngine in shadingEngineNodes:
        pyNode = pm.PyNode(eachShadingEngine)
        historyList = pyNode.listHistory(pdo=True)
        historyListMesh = pyNode.listHistory(pdo=False)
        mesh_list = set(historyListMesh) - set(historyList)

        if pyNode.name() in defaultShadingEngines:
            continue
    
        nodes = {}
        attributes = {}
        connections = {}
        geometries = []
        geometries_connect = {}
    
        for eachNode in historyList:
            # get node a nd node type
            nodes.setdefault(eachNode.name(), eachNode.type())
    
            # get node attribute and attribute value
            attributeList = eachNode.listAttr(r=True, w=True, u=True, m=True, hd=True)
            attributeValue = {}
    
            if not attributeList:
                continue
    
            for eachAttribute in attributeList:
                if eachAttribute.type() == 'attributeAlias':
                    continue
    
                currentValue = eachAttribute.get()

                if currentValue == None:
                    currentValue = 'None'
                else:
                    if type(currentValue) == bool:
                        currentValue = int(currentValue)

                    attributeValue.setdefault(eachAttribute.name(), currentValue)
            attributes.setdefault(eachNode.name(), attributeValue)
            """
                if currentValue == None:
                    currentValue = 'None'
    
                if type(currentValue) == bool:
                    currentValue = int(currentValue)
    
                attributeValue.setdefault(eachAttribute.name(), currentValue)
            attributes.setdefault(eachNode.name(), attributeValue)
            """
    
            # get node connections 
            connectionList = eachNode.listConnections(s=False, d=True, p=True)
            sourceConnections = {}
            if not connectionList:
                continue
            for eachConnection in connectionList:
                if not "hyperShadePrimaryNodeEditorSavedTabsInfo" in eachConnection.name():
                    sourceAttribute = eachConnection.listConnections(s=True, d=False, p=True)
                    if not sourceAttribute:
                        continue
                    sourceConnections.setdefault(sourceAttribute[0].name(), []).append(eachConnection.name())
            connections.setdefault(eachNode.name(), sourceConnections)
    
        # get shader assign geometries
        cmds.select(pyNode.name())
        mel.eval('hyperShade -smn ""')
        mat_nodes = cmds.ls(selection=True)
        if mat_nodes:
            for mat_node in mat_nodes:
                cmds.select(mat_node)
                mel.eval('hyperShade -objects ""')
                assigned_geo = cmds.ls(selection=True)
                if assigned_geo:
                    geometries.append(assigned_geo)

        # This conncets the mesh shape to the shder
        # from Ch_Pufferfish_01_SMShape.instObjGroups[0] to SG's Ch_Pufferfish_01_body_SMSG.dagSetMembers[0]
        """
        if mesh_list:
            for mesh_object in mesh_list:
                # Find dag connections to shadingEngine
                dag_cxns = cmds.listConnections('{}.dagSetMembers'.format(eachShadingEngine), s=True, d=False, p=True)
                if dag_cxns:
                    for dag_cxn in dag_cxns:
                        src_dag_cxn = cmds.listConnections(dag_cxn, s=False, d=True, p=True)[0]
                        geometries_connect[dag_cxn] = src_dag_cxn
        """
        #dag_set_dict = {}
        #dag_set_dict['Ch_Pufferfish_01_SMShape.instObjGroups[0]'] = 'Ch_Pufferfish_01_body_SMSG.dagSetMembers[0]'
        #networks['connections'].update("Ch_Pufferfish_01_body_SMSG" : dag_set_dict)
        # Final data
        networks = {}
        networks['nodes'] = nodes
        networks['attributes'] = attributes
        networks['connections'] = connections
        networks['geometries'] = geometries
        #networks['geometries_connect'] = geometries_connect
        # pprint.pprint (networks)
        #networks['connections'].update({"Ch_Pufferfish_01_body_SMSG": dag_set_dict})
        """
        "Ch_Pufferfish_01_body_SMSG": {
                                          "Ch_Pufferfish_01_SMShape.instObjGroups[0]": [
                                              "Ch_Pufferfish_01_body_SMSG.dagSetMembers[0]"
                                          ]
                                      },
        """
        shaderNetworkData.setdefault(pyNode.name(), networks)

    # write data
    with open(exportPath, 'w') as outfile:
        try:
            json.dump(shaderNetworkData, outfile, sort_keys=True, indent=4)
            LOG.info('Exported shaderData for {} to {}'.format(eachShadingEngine, exportPath))
        except:
            LOG.error('Unable to export skinWeight data to {0}.'.format(exportPath))


def load(filePath):

    #filePath = os.path.join(os.environ['temp'], 'myTestShader.shader')
    shaderData = open(filePath, 'r')
    shaderNetworkData = json.load(shaderData)
    shaderData.close()

    # pprint.pprint(shaderNetworkData)

    shaderList = pm.listNodeTypes('shader')
    textureList = pm.listNodeTypes('texture')
    utilityList = pm.listNodeTypes('utility')

    for eachShaderNetwork in shaderNetworkData:
        # print eachShaderNetwork
        nodes = shaderNetworkData[eachShaderNetwork]['nodes']
        attributes = shaderNetworkData[eachShaderNetwork]['attributes']
        connections = shaderNetworkData[eachShaderNetwork]['connections']
        geometries = shaderNetworkData[eachShaderNetwork]['geometries']
        #geometries_connect = shaderNetworkData[eachShaderNetwork]['geometries_connect']

        updateNode = {}

        # create nodes
        for eachNode in nodes:
            nodeType = nodes[eachNode]

            # =======================================================================
            # if pm.objExists(eachNode):
            #     pm.delete(eachNode)
            #     print 'node removed\t-', eachNode
            # =======================================================================

            if nodeType in shaderList:
                currentNode = pm.shadingNode(nodeType, asShader=True, n=eachNode)
            elif nodeType in textureList:
                currentNode = pm.shadingNode(nodeType, asTexture=True, n=eachNode)
            elif nodeType in utilityList:
                currentNode = pm.shadingNode(nodeType, asUtility=True, n=eachNode)
            else:
                currentNode = pm.createNode(nodeType, n=eachNode)

            updateNode.setdefault(eachNode, currentNode.name())

        # set attribute values
        for eachNode in attributes:
            for eachAttribute in attributes[eachNode]:
                if not pm.objExists(eachAttribute):
                    continue
                currentAttribute = eachAttribute.replace(eachNode, updateNode[eachNode])
                pyAttribute = pm.PyNode(currentAttribute)
                currentValue = attributes[eachNode][eachAttribute]
                try:
                    pyAttribute.set(currentValue)
                except Exception as result:
                    print 'set attribute warning', eachAttribute, '\t-   ', result

        # connect attribute
        for eachNode in connections:
            for eachAttribute in connections[eachNode]:
                currentSourceAttribute = eachAttribute.replace(eachNode, updateNode[eachNode])
                pySourceAttribute = pm.PyNode(currentSourceAttribute)
                for eachConnection in connections[eachNode][eachAttribute]:
                    try:
                        print eachAttribute, eachConnection
                        cmds.connectAttr(eachAttribute, eachConnection, f=True)
                        """
                        targetNode = eachConnection.split('.')[0]
                        currentTargetAttribute = eachConnection.replace(targetNode, updateNode[targetNode])
                        pyTargetAttribute = pm.PyNode(currentTargetAttribute)
                        pySourceAttribute.connect(pyTargetAttribute, force=True)

                        print 'connect\t', pySourceAttribute, 'to\t', pyTargetAttribute
                        """
                    except:
                        #print 'connection warning', eachAttribute, '\t-   ', result
                        pass
        '''
        # connect geometry connections
        for eachNode in geometries_connect:
            for eachAttribute in geometries_connect[eachNode]:
                currentSourceAttribute = eachAttribute.replace(eachNode, updateNode[eachNode])
                pySourceAttribute = pm.PyNode(currentSourceAttribute)
                for eachConnection in connections[eachNode][eachAttribute]:
                    try:
                        # cmds.connectAttr("Ch_Pufferfish_01_SMShape.instObjGroups[0]", "Ch_Pufferfish_01_body_SMSG.dagSetMembers[0]")
                        #print eachAttribute, eachConnection
                        #cmds.connectAttr(eachAttribute, eachConnection, f=True)

                        targetNode = eachConnection.split('.')[0]
                        currentTargetAttribute = eachConnection.replace(targetNode, updateNode[targetNode])
                        pyTargetAttribute = pm.PyNode(currentTargetAttribute)
                        pySourceAttribute.connect(pyTargetAttribute, force=True)

                        print 'connect\t', pySourceAttribute, 'to\t', pyTargetAttribute

                    except:
                        print 'connection warning', eachAttribute, '\t-   ', result
        '''

