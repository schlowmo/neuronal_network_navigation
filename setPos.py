#!/usr/bin/python

# Copyright 2006-2013 Dr. Marc Andreas Freese. All rights reserved. 
# marc@coppeliarobotics.com
# www.coppeliarobotics.com
# 
# -------------------------------------------------------------------
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# You are free to use/modify/distribute this file for whatever purpose!
# -------------------------------------------------------------------
#
# This file was automatically created for V-REP release V3.0.3 on April 29th 2013

# Make sure to have the server side running in V-REP!
# Start the server from a child script with following command:
# simExtRemoteApiStart(19999) -- starts a remote API server service on port 19999

import vrep
import sys
import numpy
import KTimage as KT


def printErr (err, textOK, textNotOK):
    if  err==vrep.simx_error_noerror:
        print textOK
    else:
        print "Error code =", err, textNotOK

print 'Program started'

clientID=vrep.simxStart('127.0.0.1',19997,True,True,5000,5)
if clientID!=-1:
    print('Connected to remote API server')

    err,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_oneshot_wait)
    printErr(err,'Number of objects in the scene: {}'.format(len(objs)),'Remote API function call returned error')
    
    vrep.simxAddStatusbarMessage (clientID,"Connect from Python Client",vrep.simx_opmode_oneshot_wait)

    err,allHandles,allIntData,allFloatData,allStringData = vrep.simxGetObjectGroupData(clientID,vrep.sim_appobj_object_type,0,vrep.simx_opmode_oneshot_wait)
    print "Err ", err
    print "allHandles: ", allHandles
    print "allIntData: ", allIntData
    print "allFloatData: ", allFloatData
    print "allStringData: ", allStringData

    err,bubbleRobHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRob",vrep.simx_opmode_oneshot_wait)
    err,bubbleRobBodyHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobBody",vrep.simx_opmode_oneshot_wait)
    err,bubbleRobBodyRespHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobBody_respondable",vrep.simx_opmode_oneshot_wait)
    err,bubbleRobGraphHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobGraph",vrep.simx_opmode_oneshot_wait)

    printErr(err,'Get handle for BubbleRob: {}'.format(bubbleRobHandle),'Error by getting handle for BubbleRob: {}'.format(err))

    err,leftMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobLeftMotor",vrep.simx_opmode_oneshot_wait)
    printErr(err,'Get handle for left motor: {}'.format(leftMotorHandle),'Error by getting handle for left motor')

    err,leftWheelHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobLeftWheel",vrep.simx_opmode_oneshot_wait)
    printErr(err,'Get handle for left Wheel: {}'.format(leftWheelHandle),'Error by getting handle for left Wheel')

    err,rightMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobRightMotor",vrep.simx_opmode_oneshot_wait)
    printErr(err,'Get handle for right motor: {}'.format(rightMotorHandle),'Error by getting handle for right motor')

    err,rightWheelHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobRightWheel",vrep.simx_opmode_oneshot_wait)
    printErr(err,'Get handle for right Wheel: {}'.format(rightWheelHandle),'Error by getting handle for right Wheel')

    err,robLinkHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobLink",vrep.simx_opmode_oneshot_wait)

    err,robCasterHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobCaster",vrep.simx_opmode_oneshot_wait)


    relative = vrep.sim_handle_parent
    rel_Graph = vrep.sim_handle_parent
    rel_BodyResp = vrep.sim_handle_parent
    rel_Body = vrep.sim_handle_parent

	###### Set relative position
    #Stop the Simulation
    #vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot_wait)

    #err,bubbleRobPosition = vrep.simxGetObjectPosition(clientID, bubbleRobBodyRespHandle, -1, vrep.simx_opmode_oneshot_wait)
    #printErr(err,"get bubbleRob position ","err while get bubbleRob position")
    
    #set on relative position
    #err = vrep.simxSetObjectPosition(clientID, bubbleRobHandle, bubbleRobBodyRespHandle, [1,0,0], vrep.simx_opmode_oneshot_wait)
    #printErr(err,"setting bubbleRob position ","err while setting bubbleRob position ")

    #restart the simulation
    vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)
    
    
    ###### Set absolute position
    #stop simulation
    vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot_wait)

    err,bubbleRobPosition = vrep.simxGetObjectPosition(clientID, bubbleRobBodyRespHandle, -1, vrep.simx_opmode_oneshot_wait)
    printErr(err,"get bubbleRob position ","err while get bubbleRob position")
    
    #set on absolute position
    err = vrep.simxSetObjectPosition(clientID, bubbleRobBodyRespHandle, -1, [2,2,2], vrep.simx_opmode_oneshot_wait)
    printErr(err,"setting bubbleRob position ","err while setting bubbleRob position ")

    vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)
