"""
    import setdrivenkey as sdk

    PROJ_DIR = cmds.workspace(q=True, rd=True)
    sdkFile = '{}/data/hood_sdk.json'.format(PROJ_DIR)
    sdk.writeSetDrivenKeyDataToFile( ['cn_extraHood_fk_ctl'], sdkFile )

    # Read sdkData from file
    sdk.readSetDrivenKeyDataFromFile(sdkFile)

    #######################
    To Do
    #######################
    mirrorSetDrivenKeys
    read/write does not support 'weighted' tangents at this time

"""
import logging
LOG = logging.getLogger(__name__)

import re, math
import json

import maya.cmds as mc
import maya.mel as mm


def lockUnlockSDKAnimCurves(lock=False):
    ''' lockUnlockSDKAnimCurves() '''
    try:
        animCurveTypes = ("animCurveUL", "animCurveUU", "animCurveUA", "animCurveUT")
        sdkCurves = mc.ls(type=animCurveTypes)

        if sdkCurves:
            for sdkCurve in sdkCurves:
                mc.setAttr('%s.keyTimeValue' % sdkCurve, lock=lock)
        return True

    except:
        pass


def lockSetDrivenKeyCurve(sdkCurve):
    if mc.objExists(sdkCurve):
        mc.setAttr('%s.keyTimeValue' % sdkCurve, lock=True)
        return True
    else:
        return


def readSetDrivenKeyDataFromFile(filePath, lock=False):
    '''
    Reads and reconstructs setDrivenKeyfraomes from json file exported from writeSetDrivenKeyDataToFile()
    sdkFile = 'Z:/users/tcoleman/code/temp_sdk_data.json'
    readSetDrivenKeyDataFromFile(sdkFile)
    '''
    fh = open(filePath, 'r')
    sdkDataDict = json.load(fh)
    fh.close()

    # iterate through dict keys
    for sdkCurve, sdkDict in sdkDataDict.iteritems():

        driver = sdkDict['driver']
        driven = sdkDict['driven']
        driverKeys = sdkDict['driverKeys']
        drivenKeys = sdkDict['drivenKeys']
        itt = sdkDict['itt']
        ott = sdkDict['ott']
        pri = sdkDict['pri']
        poi = sdkDict['poi']

        if mc.objExists(driver) and mc.objExists(driven):

            i = 0
            for driverKey, drivenKey in zip(driverKeys, drivenKeys):
                # Create setDrivenKeyframes
                mc.setDrivenKeyframe(driven, cd=driver, dv=driverKey, value=drivenKey)
                LOG.debug('SetDrivenKeyframe:  Driver=%s.%s, Driven=%s.%s' % (driver, driven, driverKey, drivenKey))

                # Set keyframe tangents
                mc.selectKey(sdkCurve, add=True, k=True, f=(driverKey, driverKey))
                mc.keyTangent(itt=itt[i], ott=ott[i])

                i = i + 1

            # Set pre/post infinity
            mc.selectKey(sdkCurve, add=True, k=True, f=(driverKeys[0], driverKeys[0]))
            mc.setInfinity(pri=pri)

            mc.selectKey(clear=True)
            mc.selectKey(sdkCurve, add=True, k=True, f=(driverKeys[-1], driverKeys[-1]))
            mc.setInfinity(poi=poi)

            # Lock setDrivenKeyframes if specified
            if lock:
                mc.setAttr('%s.keyTimeValue' % sdkCurve, lock=True)

        mc.refresh()
    LOG.info('SetDrivenKeyframe Data read from %s' % filePath)


def writeSetDrivenKeyDataToFile(objectList, filePath):
    '''
    Writes setDrivenKeyframe dats to json file in order to import with readSetDrivenKeyDataFromFile()

    import rigUtils.utils.setDrivenKey as sdk
    reload(sdk)

    helperJnts = ['Rt_elbow_jnt_transRot_helper']
    writeSetDrivenKeyDataToFile(helperJnts, 'Z:/users/tcoleman/code/temp_sdk_data.json')
    '''
    sdkDataDict = {}

    for obj in objectList:

        if mc.objExists(obj):

            LOG.debug('Object exists: %s' % obj)

            # Gather sdk animation curves
            sdkCurves = returnSetDrivenKeyCurvesFromObject(obj)

            # For each sdk curve gather data
            if sdkCurves:
                for sdkCurve in sdkCurves:
                    LOG.debug('sdkCurve: %s' % sdkCurve)
                    sdkData = returnSetDrivenKeyData(sdkCurve)
                    sdkDataDict[sdkCurve] = sdkData

    # Write out sdk data to json file
    if sdkDataDict:
        fh = open(filePath, 'w')
        json.dump(sdkDataDict, fh, indent=4)
        fh.close()
        LOG.info('SetDrivenKeyframe Data written to %s' % filePath)


def returnSetDrivenKeyData(sdkAnimCurve):
    '''
    Returns setDrivenKey command from input sdkAnimCurve

    returnSetDrivenKeyData('Rt_elbow_jnt_transRot_helper_offsetX')
    '''
    LOG.debug('Working on sdkCurve: %s' % sdkAnimCurve)

    if mc.objExists(sdkAnimCurve):
        LOG.debug('sdkCurve exists: %s' % sdkAnimCurve)

        # Find driver and driven objects
        driver = mc.listConnections('%s.input' % sdkAnimCurve, scn=True, source=True, destination=False, plugs=True)
        driven = mc.listConnections('%s.output' % sdkAnimCurve, source=False, destination=True, plugs=True)

        # Find keyframes and values
        driverKeys = mc.keyframe(sdkAnimCurve, q=True, floatChange=True)
        drivenKeys = mc.keyframe(sdkAnimCurve, q=True, valueChange=True)

        # Get animCurve tangent types
        itt = mm.eval("keyTangent -query -itt %s ;" % sdkAnimCurve)
        ott = mm.eval("keyTangent -query -ott %s ;" % sdkAnimCurve)

        # Get animCurve pre/post infinity
        mc.selectKey(sdkAnimCurve, add=True, k=True, f=(driverKeys[0], driverKeys[0]))
        pri = mc.setInfinity(q=True, pri=True)[0]

        mc.selectKey(clear=True)
        mc.selectKey(sdkAnimCurve, add=True, k=True, f=(driverKeys[-1], driverKeys[-1]))
        poi = mc.setInfinity(q=True, poi=True)[0]

        # Return sdk data
        sdkDict = {}
        sdkDict['driver'] = driver[0]
        sdkDict['driven'] = driven[0]
        sdkDict['driverKeys'] = driverKeys
        sdkDict['drivenKeys'] = drivenKeys
        sdkDict['itt'] = itt
        sdkDict['ott'] = ott
        sdkDict['pri'] = pri
        sdkDict['poi'] = poi

        return sdkDict


def returnSetDrivenKeyCurvesFromObject(inputObject):
    '''
    Returns any setDrivenKey curves connected to inputObject's keyable attributes

    returnSetDrivenKeyCurvesFromObject( 'Rt_elbow_jnt_transRot_helper' )
    '''
    sdkCurves = list()
    keyAttrs = list()
    sourceObject = inputObject


    if 'blendShape' in mc.nodeType(sourceObject):
        keyAttrs = mc.listAttr(sourceObject, m=True, st="weight")
    elif 'follicle' in mc.nodeType(sourceObject):
        keyAttrs = ['parameterU', 'parameterV']
    else:
        keyAttrs = mc.listAttr(sourceObject, keyable=True)

    for attr in keyAttrs:
        cxns = mc.listConnections('%s.%s' % (sourceObject, attr), s=True, d=False)
        if cxns:
            currentAnimCurveType = mc.nodeType(cxns[0])
            animCurveTypes = ("animCurveUL", "animCurveUU", "animCurveUA", "animCurveUT")
            for animCurveType in animCurveTypes:
                if currentAnimCurveType in animCurveType:
                    sdkCurves.append(cxns[0])

    return sdkCurves


def mirrorSDKSelected(search='Rt_', replace='Lf_'):
    ''' mirrorSDKSelected() '''
    sel = mc.ls(selection=True)

    if sel:
        for item in sel:
            mirrorItem = item.replace(search, replace)
            attrs = returnSetDrivenKeyAttrsFromObject(item)

            if mc.objExists(mirrorItem):
                if attrs:
                    copySDK(curAttrs=attrs, mirrorAttrs=attrs, source=item, targets=[mirrorItem], search=search,
                            replace=replace, specialIter=[], sort=False, mode='driven', drAttrSearch='',
                            drAttrReplace='', createDriverAttr=False)
                else:
                    print '%s has no sdk keyable attributes' % item
            else:
                print '%s does not exist, skipping' % mirrorItem
    else:
        print 'Nothing selected to mirror'


def returnSetDrivenKeyAttrsFromObject(inputObject):
    '''
    Returns any setDrivenKey curves connected to inputObhect's keyable attributes

    returnSetDrivenKeyAttrsFromObject( 'Rt_middleFinger1_jnt_outerTransRot_helper_jnt' )
    '''

    sourceObject = inputObject
    keyAttrs = mc.listAttr(sourceObject, keyable=True)
    sdkAttrs = []

    for attr in keyAttrs:
        cxns = mc.listConnections('%s.%s' % (sourceObject, attr), s=True, d=False)
        if cxns:
            currentAnimCurveType = mc.nodeType(cxns[0])
            animCurveTypes = ("animCurveUL", "animCurveUU", "animCurveUA", "animCurveUT")
            for animCurveType in animCurveTypes:
                if currentAnimCurveType in animCurveType:
                    sdkAttrs.append(attr)

    return sdkAttrs


def setSetDrivenKeyframe(driver='', driverValue=0, driven='', drivenValue=1, setInitialSetDriveKeyframe=False):
    '''
    Set driven keyframe "wrapper"

    setSetDrivenKeyframe( driver='Rt_indexFinger2_jnt.ry', driverValue=90, driven='Rt_indexFinger2_bulge_helper.tz', drivenValue=-.08, setInitialSetDriveKeyframe=True )
    '''
    if mc.objExists(driver) and mc.objExists(driven):

        if setInitialSetDriveKeyframe:
            mc.setDrivenKeyframe(driven, cd=driver)

        mc.setDrivenKeyframe(driven, cd=driver, value=drivenValue, driverValue=driverValue)
        LOG.debug('Set setDrivenKeyframe for %s:%s --> %s:%s' % (driver, driverValue, driven, drivenValue))

    else:

        LOG.warning('Driver %s or driven %s not found, skipping...' % (driver, driven))


def setSetDrivenKeyframeList(driver='', driverValueList=[], drivenList=[], drivenValueList=[]):
    '''
    Set driven keyframe "wrapper" for multiple driven objects and/or multiple dirver/driven keys

    setSetDrivenKeyframeList( driver='Rt_indexFinger2_jnt.ry', driverValueList=[0,45,90], drivenList=['Rt_indexFinger2_bulge_helper.tz'], drivenValueList=[0,0,-.08] )
    '''
    if mc.objExists(driver):

        for driven in drivenList:

            if mc.objExists(driven):

                for driverValue, drivenValue in zip(driverValueList, drivenValueList):
                    mc.setDrivenKeyframe(driven, cd=driver, value=drivenValue, driverValue=driverValue)
                    LOG.debug('Set setDrivenKeyframe for %s:%s --> %s:%s' % (driver, driverValue, driven, drivenValue))

    else:

        LOG.warning('Driver %s not found, skipping...' % driver)


# copySDK, 20110109
#
# Python definitions to mirror SDK setups to single/multiple objects.
# isoparmB
#
# - updated 20110117
#   Added 'driver' mode
#   Corrected mirror key behaviour for angular units
#
# - updated 20130916
#   Added moveSDK function
#   Added ability to rename target driver attributes
#   Added ability to create driver attribute if non-existant (createDriverAttr)
#   Added mirrorSelectedChannels convenience function
#   Format changes
#
# for questions or suggestions, email me at martinik24@gmail.com

###############################################################################

ANIM_CURVE_TYPES = ('animCurveUL', 'animCurveUA', 'animCurveUU',
                    'animCurveTL', 'animCurveTA', 'animCurveTU')


def copySDK(curAttrs=[], mirrorAttrs=[], source='', targets=[],
            search='', replace='', specialIter=[], sort=False, mode='driven',
            drAttrSearch='', drAttrReplace='', createDriverAttr=False):
    '''This definition is used to copy SDK setups from one node
to another node/s in Maya.  With no declarations, the script works by getting
the selection list. The first selected object is the source, everything else
is a target. The script will copy SDKs from the source and replicate it
on the targets.   SDKs will be linked to the original source driver by default.


Node and attribute options

curAttrs    - string or string list     - is for explicitly declaring
                        which attributes to copy SDKs from.  If you
                        don't declare it, the script will search for SDKs
                        on all keyable attributes of the source.

mirrorAttrs - string or string list     - is to tell the script
                        which attributes on the source object will receive
                        a negative value in their keyframes.

source      - string                    - is to explicitly declare
                        the source node to copy.  If this is declared, targets
                        must also be declared. If not declared, the selection
                        list is used and the first selected object
                        is the source.
                                        - if mode is set to driven, source
                        represents the source driven node, when mode is set
                        to driver, source represents the source driver node.

targets     - string or string list     - is to explicitly declare target nodes
                        to apply SDKs to.  If this is declared, source
                        must also be declared. If not declared, the selection
                        list is used and all other objects other than the first
                        comprise the targets list.
                                        - if mode is set to driven, targets
                        represents the destination driven node/s, when mode
                        is set to driver, targets represents the destination
                        driver node/s.



String search options for driver nodes:

search      - string                    - when mode is set to Driven, is used
                        for pattern searching in Driver names.  search
                        and replace both have to be declared. If not declared,
                        the SDK's are connected to the original driver node
                        attributes.  This attribute accepts regex
                        search strings.
                                        - when mode is set to Driver, this is
                        used instead to search for Driven object names. search
                        and replace MUST be declared in case of Driver-centric
                        operations.

replace     - string                    - when mode is set to Driven, is used
                        for pattern searching in Driver names, to look for
                        alternate Driver nodes. This provides the
                        replace string to use when looking for Driver nodes.
                        The replace string can use the special %s character
                        to provide more flexibility with choosing different
                        Drivers for multiple Driven nodes.
                                        - when mode is set to Driver, this
                        is used instead to search for Driven object names.
                        search and replace MUST be declared in case of
                        Driver-centric operations.

specialIter - int or string list or list of lists  - is used when you want to
                        provide a list or an iteratable object to use when you
                        want more flexibility in naming your driver object.
                        Your replace variable must contain a replace string
                        with %s, and that will get swapped by what you
                        enter here.
                                        - You can use a single list
                        ['a', 'b', 'c'], lists within lists for multiple %s's
                        [['a', 'b', 'c'], [1, 2, 3]], or python techniques
                        such as range e.g., range(0,12).
                                        - The only rule is that the lists
                        have to be as long as the number of targets.

sort        - boolean                   - Sort the target list alphabetically.
                        Helps to reorganize the targets list if you're using
                        the specialIter function.

mode        - string 'driver', 'driven' or 'guess' - Decides whether the script
                        operates via selecting a driven node, or a driver node.
                        Default is set to driven, meaning you have to select
                        the driven object you want to mirror over as your
                        first selection.  Options are either 'driver',
                        'driven', or 'guess' (if set to guess, will find
                        whether it has more outgoing or incomming
                        sdk keyframes), and the default is driven.
                                        - In driven mode, script wil find the
                        original driver from the driven node and seek out
                        alternate driver names via the search and replace
                        variables if declared, else it will use
                        the original driver/s.
                                        - In driver mode, script will seek out
                        all driven nodes and search for the alternate driven
                        node names based off the search and replace variables.
                        In driver mode, search and replace declaration
                        is required.

drAttrSearch  - string                  - If declared, search for this string
                        component in a source driver attribute, for
                        the purpose of replacing this string in
                        a target driver attribute.

drAttrReplace - string                  - If declared, use this string
                        to replace a found attrSearch component in a source
                        driver attr when looking for a target driver attr.

createDriverAttr - boolean              - Create the driver attribute on
                        a found target node if it did not already exist,
                        Default is False.  This only works in 'driver' mode.



Mirror SDK curves example:

    sys.path.append('//ml-store-smb.magicleap.ds/fl/Users/MAGICLEAP/tcoleman/code') # DEV
    import rigUtils.utils.setDrivenKey as sdk
    reload(sdk)

    # Mirror SDK curves
    src = 'Rt_elbow_jnt_outerTransRot_helper_jnt'
    tgts = ['Lf_elbow_jnt_outerTransRot_helper_jnt']
    attrs = ['offsetX', 'offsetY']

    sdk.copySDK(curAttrs=attrs, mirrorAttrs=attrs, source=src, targets=tgts,
                search='', replace='', specialIter=[], sort=False, mode='driven',
                drAttrSearch='', drAttrReplace='', createDriverAttr=False)

'''
    # Make sure all variables are correct
    if not source.strip() or not targets:
        curlist = mc.ls(sl=True, ap=True)
        if not curlist or len(curlist) < 2:
            print ('\nPlease select at least two objects.')
            return 1
        source = curlist[0]
        targets = curlist[1:]
    elif isinstance(targets, str) and targets.strip():
        targets = [targets]
    if sort:
        targets.sort()
    if curAttrs:

        if isinstance(curAttrs, str) and curAttrs.strip():
            curAttrs = [curAttrs]

        attrs = [mc.attributeQuery(x, node=source, ln=True) for x in curAttrs
                 if mc.attributeQuery(x, node=source, ex=True)]
        if not attrs:
            print ('Specified attributes %s, do not exist on driver %s .'
                   % (', '.join(attrs), source))
            return 1
    else:
        attrs = mc.listAttr(source, k=True)

    if mirrorAttrs:
        if isinstance(mirrorAttrs, str):
            mirrorAttrs = [mirrorAttrs]
        tempMirrorAttrs = []
        for attr in mirrorAttrs:
            if not mc.attributeQuery(attr, node=source, ex=True):
                continue
            tempMirrorAttrs.append(mc.attributeQuery(attr, node=source, ln=True))
        tempMirrorAttrs = list(set(tempMirrorAttrs))
        if tempMirrorAttrs:
            mirrorAttrs = tempMirrorAttrs
        else:
            print ('Specified attributes to be mirrored %s, do not exist '
                   'on source node %s .' % (', '.join(mirrorAttrs), source))
            mirrorAttrs = []

    if mode.strip().lower() == 'driven':
        mode = True
    elif mode.strip().lower() == 'driver':
        mode = False
    elif mode.lower() == 'guess':
        driverNodes = []
        drivenNodes = []

        drivenNodes, blendWeightedNodes = \
            findSDKNodes(mirrorAttrs, source, attrs, True)
        if blendWeightedNodes:
            for node in blendWeightedNodes:
                SDKN2, SKN, ON = searchBWNodes(node)
                if SDKN2:
                    a = set(drivenNodes + SDKN2)
                    drivenNodes = list(a)
        driverNodes, blendWeightedNodes = \
            findSDKNodes(mirrorAttrs, source, attrs, False)

        if len(drivenNodes) >= len(driverNodes):
            mode = True
        else:
            mode = False
    else:
        print ('\nUnrecognized mode argument: "' + str(mode) +
               '", use either "driver", "driven", or "guess".')
        return 1

    # Determine special iteration parameters if there is a %s in the replace
    # variable. Used for complex Driver name searching, if each of your targets
    # has a different driver object.
    SDKResults = []
    BWNResults = []
    iterExec = None
    if (not search or not replace) and mode:
        search = None
        replace = None
    elif (not search or not replace) and not mode:
        print ('\nPlease "declare" search and "replace" variables '
               'when in driver mode.')
        return 1
    elif replace.count('%s') and not specialIter:
        print ('\nWhen using the "%s" character, you must declare '
               'a specialIter list')
        return 1
    elif replace.count('%s'):
        if (isinstance(specialIter[0], list) or
                isinstance(specialIter[0], tuple)):
            numArgs = len(specialIter)
            iterExec = 'feeder = ('
            iterScratch = []
            for x in range(0, numArgs):
                if len(specialIter[x]) != len(targets):
                    print ('\nspecialIter item ' + str(x) + ' length (' +
                           str(len(specialIter[x])) + ') must be the same as target'
                                                      ' length (' + str(len(targets)) + ') .')
                    return 1
                iterScratch.append('specialIter[%s][i]' % str(x))

            iterExec += ', '.join(iterScratch) + ' )'
        else:
            if len(specialIter) != len(targets):
                print ('\nspecialIter length (' + str(len(specialIter)) +
                       ') must be the same as target length (' +
                       str(len(targets)) + ') .')
                return 1
            iterExec = 'feeder = specialIter[i]'

    # Acquire SDK and blendweighted nodes from source
    SDKnodes, blendWeightedNodes = \
        findSDKNodes(mirrorAttrs, source, attrs, mode)

    # Go through all the targets and mirror SDK nodes and
    # blendWeighted nodes with SDK from source.
    i = 0
    for target in targets:
        if SDKnodes:
            doSDKs(SDKnodes, target, search, replace, i, iterExec, specialIter,
                   SDKResults, BWNResults, mode, createDriverAttr,
                   drAttrSearch, drAttrReplace)

        if blendWeightedNodes and mode:
            for node in blendWeightedNodes:

                SDKnodes2, SKnodes, otherNodes = searchBWNodes(node)

                if SDKnodes2:
                    newBlendNode = mc.duplicate(node[0])[0]
                    doSDKs(SDKnodes2, newBlendNode, search, replace, i,
                           iterExec, specialIter, SDKResults, BWNResults,
                           True, createDriverAttr,
                           drAttrSearch, drAttrReplace)
                    if SKnodes:
                        for node2 in SKnodes:
                            newKeyNode = mc.duplicate(node2[0])[0]
                            if node2[2]:
                                mirrorKeys(newKeyNode)
                            mc.connectAttr('%s.output' % newKeyNode,
                                           '%s.%s' % (newBlendNode, node2[1]), f=True)
                    mc.connectAttr('%s.output' % newBlendNode,
                                   '%s.%s' % (target, node[1]), f=True)
                    BWNResults.append('Connected Blend Weighted node '
                                      '%s.output to Driven node %s.%s' %
                                      (newBlendNode, target, node[1]))
                else:
                    print ('\nNo SDK nodes connected to blendWeighted node '
                           + node[0] + ', skipping...')
        i += 1

    return 0


def moveSDK(source=None, destination=None, curAttrs=[],
            drAttrSearch='', drAttrReplace='', deleteOldAttrs=False):
    ''' Move the specified set driven key attributes from once source driver
    attr to one target destination driver attr.
    '''

    if not source or not destination:
        source, destination = mc.ls(sl=True)

    if not all((mc.objExists(source), mc.objExists(destination))):
        print ('One of the nodes does not exist, '
               'please check: %s, %s' % (source, destination))
        return 1

    if curAttrs:

        if isinstance(curAttrs, str) and curAttrs.strip():
            curAttrs = [curAttrs]

        attrs = [mc.attributeQuery(x, node=source, ln=True) for x in curAttrs
                 if mc.attributeQuery(x, node=source, ex=True)]
        if not attrs:
            print ('Specified attributes %s, do not exist on driver %s .'
                   % (', '.join(attrs), source))
            return 1
    else:
        attrs = mc.listAttr(source, k=True)

    # Get the SDK's and any blendwheighted nodes with SDKs.
    driverNodes, blendWeightedNodes = findSDKNodes((), source, attrs, False)

    # Connect all the old connections from the source to the new attr
    # on the destinationn attribute.
    for nodeList in (driverNodes, blendWeightedNodes):
        for node in nodeList:
            # Create the new driver attr if it does not already exist.
            createDriverAttrFunc(source, destination, node[1].split('[')[0],
                                 drAttrSearch, drAttrReplace)

            mc.connectAttr('%s.%s' % (destination,
                                      node[1].replace(drAttrSearch, drAttrReplace)),
                           '%s.%s' % (node[0], node[3]), f=True)

    # If specified, delete the old driver attr.
    if not deleteOldAttrs:
        return
    userDefinedAttrs = mc.listAttr(source, ud=True)
    for attr in attrs:
        if attr in userDefinedAttrs and \
                not mc.listConnections('%s.%s' % (source, attr),
                                       scn=True, d=True, s=True, p=False):
            mc.deleteAttr('%s.%s' % (source, attr))


def findSDKNodes(mirrorAttrs, source, attrs, mode):
    '''Searches for SDK nodes or blendWeighted nodes on a given node.
    Mode determines whether to search for incomming or outgoing connections
    (True is incommingm False is outgoing).

    Will return a list of found SDK nodes and blendWeighted nodes.'''

    SDKN = []
    BWN = []

    if mode:
        listConLambda = lambda source, attr: mc.listConnections(
            '%s.%s' % (source, attr), scn=True, d=False, s=True, p=True)
    else:
        listConLambda = lambda source, attr: mc.listConnections(
            '%s.%s' % (source, attr), scn=True, d=True, s=False, p=True)

    for attr in attrs:
        conns = listConLambda(source, attr)
        if conns:
            for conn in conns:
                conn, targetAttr = conn.split('.')[0], \
                                   '.'.join(conn.split('.')[1:])
                nodeType = mc.ls(conn, st=True)[1]
                mirrorAttr = False
                if attr in mirrorAttrs:
                    mirrorAttr = True
                if nodeType in ('animCurveUL', 'animCurveUA', 'animCurveUU'):
                    SDKN.append((conn, attr, mirrorAttr, targetAttr))
                elif nodeType == 'blendWeighted' and mode:
                    BWN.append((conn, attr, mirrorAttr, targetAttr))
    return SDKN, BWN


def searchBWNodes(node):
    '''Searches for SDK nodes, keyframe nodes and other connections on
    a blendWeighted node. Will return a list of found SDK nodes,
    keyframe nodes and any other node connection types.'''

    SDKN2 = []
    SKN = []
    ON = []
    attrs = mc.listAttr('%s.input' % node[0], multi=True)
    if not attrs:
        print ('\nNo SDK nodes connected to blendWeighted node %s'
               ', skipping...' % node[0])
        return [], [], []

    for attr in attrs:
        conn = mc.listConnections(
            '%s.%s' % (node[0], attr), scn=True, d=False, s=True, p=True)
        if conn:
            nodetype = mc.ls(conn[0].split('.')[0], st=True)[1]
            mirrorAttr = node[2]
            if nodetype in ('animCurveUL', 'animCurveUA', 'animCurveUU'):
                SDKN2.append((conn[0].split('.')[0], attr, mirrorAttr))
            elif nodetype in ('animCurveTL', 'animCurveTA', 'animCurveTU'):
                SKN.append((conn[0].split('.')[0], attr, mirrorAttr))
            else:
                ON.append((conn[0], attr, mirrorAttr))

    return SDKN2, SKN, ON


def connectToConn(replace, iterExec, curNode, curNode2,
                  repPattern, mode, newKeyNode, origBW):
    ''' Connect the newKeyNode based on the search/replace
    parameters specified.
    '''

    errorCheck = False
    if replace.count('%s'):
        currentRep = replace
        exec (iterExec) in locals()
        currentRep = currentRep % feeder
        newConn = curNode2.split('.')[0].replace(repPattern, currentRep)
    else:
        newConn = curNode2.split('.')[0].replace(repPattern, replace)

    if mc.objExists(newConn) and \
            mc.attributeQuery(
                '.'.join(curNode2.split('.')[1:]), node=newConn, ex=True) and \
            mode:
        mc.connectAttr(
            '%s.%s' % (newConn, '.'.join(curNode2.split('.')[1:])),
            '%s.input' % newKeyNode, f=True)

    # In driver mode, check for blendWeighted nodes. If the target
    # has a blendWeighted node, check to see if it has the same number
    # of input multi attrs, otherwise make a new one.
    elif mc.objExists(newConn) and (
                mc.attributeQuery(
                    '.'.join(curNode2.split('.')[1:]), node=newConn, ex=True) or
                mc.attributeQuery(
                    curNode2.split('.')[1].split('[')[0], node=newConn, ex=True)) \
            and not mode:

        targetCon = mc.listConnections(
            '%s.%s' % (newConn, '.'.join(curNode2.split('.')[1:])),
            s=True, d=False, p=True, scn=True)
        makeNewBW = False
        if targetCon:
            nodeType = mc.ls(targetCon[0].split('.')[0], st=True)[1]
            if nodeType == 'blendWeighted':
                targetBWInSize = len(mc.listAttr(
                    '%s.input' % targetCon[0].split('.')[0], multi=True))
                origBWInSize = len(mc.listAttr(
                    '%s.input' % origBW.split('.')[0], multi=True))
                if targetBWInSize == origBWInSize:
                    mc.connectAttr('%s.output' % newKeyNode,
                                   '%s.%s' % (targetCon[0].split('.')[0],
                                              '.'.join(curNode.split('.')[1:])), f=True)
                else:
                    makeNewBW = True
            else:
                makeNewBW = True
        else:
            makeNewBW = True

        if makeNewBW and origBW:
            newBW = mc.duplicate(origBW.split('.')[0])[0]
            mc.connectAttr('%s.output' % newKeyNode,
                           '%s.%s' % (newBW, '.'.join(curNode.split('.')[1:])), f=True)
            mc.connectAttr('%s.output' % newBW,
                           '%s.%s' % (newConn, '.'.join(curNode2.split('.')[1:])), f=True)
        else:
            mc.connectAttr('%s.output' % newKeyNode,
                           '%s.%s' % (newConn, '.'.join(curNode2.split('.')[1:])), f=True)

    elif mode and mc.objExists(newConn) and \
            not mc.attributeQuery(
                '.'.join(curNode2.split('.')[1:]), node=newConn, ex=True):
        print ('\nDriver node %s does not have the attribute %s .'
               % (newConn, '.'.join(curNode2.split('.')[1:])))
        mc.delete(newKeyNode)

    else:
        errorCheck = True

    return errorCheck, newConn


def createDriverAttrFunc(sourceDriver, targetDriver, origAttr,
                         drAttrSearch, drAttrReplace, skipRecursion=False):
    ''' Recursive function that takes an attribute on one node and replicates
    it on another.  Will handle compound attributes.
    '''

    sourceNodeAttr = '%s.%s' % (sourceDriver, origAttr)

    # If we're dealing with a compound attr like a double3,
    # create the parent first.
    parentAttr = mc.addAttr(sourceNodeAttr, **{'q': True, 'parent': True})
    targetParentAttr = None
    if parentAttr and parentAttr != origAttr:
        targetParentAttr = parentAttr.replace(drAttrSearch, drAttrReplace)
        if not skipRecursion:
            createDriverAttrFunc(sourceDriver, targetDriver, parentAttr,
                                 drAttrSearch, drAttrReplace)

    targetNodeAttr = '%s.%s' % (targetDriver,
                                origAttr.replace(drAttrSearch, drAttrReplace))
    targetAttr = origAttr.replace(drAttrSearch, drAttrReplace)
    if mc.attributeQuery(targetAttr, node=targetDriver, ex=True):
        return

    attrDict = {}
    keyable = mc.getAttr("%s.%s" % (sourceDriver, origAttr), k=True)
    attrDict['ln'] = targetAttr
    attrDict['at'] = mc.getAttr(sourceNodeAttr, type=True)
    if attrDict['at'] in ('double', 'long', 'float'):
        for curAttr in ('min', 'max', 'dv'):
            if isinstance(mc.addAttr(
                    sourceNodeAttr, **{'q': True, curAttr: True}),
                    type(None)):
                continue
            attrDict[curAttr] = mc.addAttr(
                sourceNodeAttr, **{'q': True, curAttr: True})

    if mc.addAttr(sourceNodeAttr, **{'q': True, 'dt': True})[0] == 'string':
        attrDict['dt'] = 'string'
    if targetParentAttr:
        attrDict['p'] = targetParentAttr

    mc.addAttr(targetDriver, **attrDict)
    for childAttr in \
                    mc.attributeQuery(origAttr, node=sourceDriver, lc=True) or []:
        createDriverAttrFunc(sourceDriver, targetDriver, childAttr,
                             drAttrSearch, drAttrReplace, skipRecursion=True)
    for childAttr in \
                    mc.attributeQuery(origAttr, node=sourceDriver, lc=True) or []:
        childKeyable = mc.getAttr(
            "%s.%s" % (sourceDriver, childAttr), k=True)
        if childKeyable:
            try:
                mc.setAttr("%s.%s" % (targetDriver,
                                      childAttr.replace(drAttrSearch, drAttrReplace)),
                           e=True, keyable=True)
            except:
                pass

    if keyable:
        try:
            mc.setAttr(targetNodeAttr, e=True, keyable=True)
        except:
            pass


def doSDKs(SDKnodes, target, search, replace, i, iterExec, specialIter,
           SDKResults, BWNResults, mode, createDriverAttr,
           drAttrSearch, drAttrReplace):
    ''' This is the procedure that actually performs the SDK replication
    '''

    # Declare search direction of connectionInfo command, based of tool mode.
    if mode:
        conInfoLambda = lambda node: mc.listConnections(
            '%s.input' % node[0], d=False, s=True, p=True, scn=True)
    else:
        conInfoLambda = lambda node: mc.listConnections(
            '%s.output' % node[0], d=True, s=False, p=True, scn=True)

    for node in SDKnodes:

        # Check what's connected to SDK nodes and see if the target nodes
        # have the same attributes as the source node, if no reults or
        # no matching attributes, continue.
        connections = conInfoLambda(node)
        if not connections or (not createDriverAttr and (
                    not mc.attributeQuery(
                        node[1].replace(drAttrSearch, drAttrReplace),
                        node=target, ex=True) and
                    not mc.attributeQuery(
                        node[1].split('[')[0].replace(drAttrSearch, drAttrReplace),
                        node=target, ex=True))):
            print 'CONTINUED', node  # delete me
            continue

        # If createDriverAttr is set to True and the driver attribute
        # doesn't exist, try to create it on the new driver.
        elif (not mc.attributeQuery(
                node[1].replace(drAttrSearch, drAttrReplace),
                node=target, ex=True) and
                  not mc.attributeQuery(
                      node[1].split('[')[0].replace(drAttrSearch, drAttrReplace),
                      node=target, ex=True)):
            if mode or not createDriverAttr:
                continue
            sourceDriver = mc.listConnections(
                '%s.input' % node[0],
                d=False, s=True, p=False, scn=True)[0]
            createDriverAttrFunc(sourceDriver, target, node[1].split('[')[0],
                                 drAttrSearch, drAttrReplace)

        if isinstance(connections, str):
            connections = [connections]

        # Duplicate keyframe node and mirror if asked.
        newKeyNode = mc.duplicate(node[0])[0]
        if node[2]:
            if mc.objExists(node[0].replace(search, replace)):
                mc.delete(node[0].replace(search, replace))
            newKeyNode = mc.rename(newKeyNode, node[0].replace(search, replace))
            mirrorKeys(newKeyNode)

        # Go through all the connections.
        for curNode in connections:

            # If in driver mode, check to see if node connected to keyframe
            # is a blendWeighted node.
            origBW = ''
            if not mode:
                nodeType = mc.ls(curNode.split('.')[0], st=True)[1]
                if nodeType == 'blendWeighted':
                    origBW = curNode
                    connections2 = mc.listConnections(
                        '%s.output' % curNode.split('.')[0],
                        d=True, s=False, p=True, scn=True)
                else:
                    connections2 = [curNode]
            else:
                connections2 = [curNode]

            # Connect the duplicated keyframes
            # to their respective target connections.
            for curNode2 in connections2:
                if search or not mode:
                    # regex search pattern section.
                    curRegexer = re.search(search, curNode2)
                    errorCheck = False
                    print (replace, iterExec, curNode,
                           curNode2, mode, newKeyNode, origBW)  # delete me
                    if hasattr(curRegexer, 'group'):
                        repPattern = curRegexer.group(0)
                        if repPattern:
                            (errorCheck, newConn) = \
                                connectToConn(replace, iterExec, curNode,
                                              curNode2, repPattern, mode, newKeyNode, origBW)
                        else:
                            errorCheck = True
                    else:
                        errorCheck = True

                    if errorCheck:
                        if mode:
                            print ('\nFailure to find a driver for node %s '
                                   'based on search criteria %s for driver node %s .'
                                   % (target, search, curNode2.split('.')[0]))
                            mc.delete(newKeyNode)
                        else:
                            print ('\nFailure to find a driven for nodes %s '
                                   'based on search criteria %s for driven node %s .'
                                   % (target, search, curNode2.split('.')[0]))
                        continue

                elif mode:
                    mc.connectAttr(curNode2, '%s.input' % newKeyNode, f=True)
                    newConn = curNode2

                # Connect the new SDK's to the new driver attrs.
                if mode:
                    mc.connectAttr('%s.output' % newKeyNode,
                                   '%s.%s' % (target, node[1]), f=True)
                else:
                    mc.connectAttr('%s.%s' % (target,
                                              node[1].replace(drAttrSearch, drAttrReplace)),
                                   '%s.input' % newKeyNode, f=True)

                SDKResults.append('Connected Driver node %s.%s.output to '
                                  'Driven node %s.%s .' %
                                  (newConn, '.'.join(curNode2.split('.')[1:]), target, node[1]))


def mirrorSelectedChannels(node=None, attrs=None, mode='driver'):
    ''' Mirror any keyrames found in the specified attributes on these node.
    If no nodes and attrs are specified, the selection list is used, and
    whatever channels are specified in the channel box are used.

    mode determines whether the command will look for keyframes that are
    driving the attribute, or are driven by an attribute (driver, driven).

    This is meant as more of a convenience function to adjust SDK's after
    they've been copied.
    '''

    if not node:
        nodes = mc.ls(sl=True)
    if not attrs:
        attrs = mc.channelBox('mainChannelBox', q=True, sma=True) or []

    if not nodes:
        print ('No nodes specified to flip.')
        return

    for node in nodes:
        if mc.ls(node, st=True)[1] in ANIM_CURVE_TYPES:
            mirrorKeys(node)
        for attr in attrs:
            if not mc.attributeQuery(attr, node=node, ex=True):
                continue
            if mode == 'driver':
                source, destination = False, True
            elif mode == 'driven':
                source, destination = True, False

            keyframes = [x for x in mc.listConnections(
                '%s.%s' % (node, attr), scn=True, d=destination,
                s=source, p=False) or []
                         if mc.ls(x, st=True)[1] in ANIM_CURVE_TYPES]
            for keyframe in keyframes:
                mirrorKeys(keyframe)


def mirrorKeys(newKeyNode):
    '''Mirror keyframe node procedure, in case you need to flip your SDK's.
    Also works with ordinary keyframe nodes.
    '''

    keyType = mc.ls(newKeyNode, st=True)[1]
    try:
        mc.selectKey(clear=True)
    except:
        pass

    # Get the number of keyframes.
    numKeys = len(mc.listAttr(newKeyNode + '.ktv', multi=True)) / 3

    # Iterate through each key and multiply the values by -1,
    # then set the keyframe value.
    for x in range(0, numKeys):
        v = mc.getAttr(newKeyNode + '.keyTimeValue[' + str(x) + ']')
        v = [v[0][0], v[0][1] * -1]
        if keyType in ('animCurveTU', 'animCurveTA', 'animCurveTL'):
            mc.selectKey(newKeyNode, add=True, k=True, t=(v[0], v[0]))
        elif keyType in ('animCurveUU', 'animCurveUA', 'animCurveUL'):
            mc.selectKey(newKeyNode, add=True, k=True, f=(v[0], v[0]))

        if keyType in ('animCurveTA', 'animCurveUA'):
            mc.keyframe(animation='keys', absolute=True,
                        valueChange=math.degrees(v[1]))
        else:
            mc.keyframe(animation='keys', absolute=True, valueChange=v[1])
        try:
            mc.selectKey(clear=True)
        except:
            pass

