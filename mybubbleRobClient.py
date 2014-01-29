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
import math
import numpy
import KTimage as KT
import time
from mlp_network import MLP
from mlp_layer import Layer

print 'Program started'

clientID=vrep.simxStart('127.0.0.1',19998,True,True,5000,5)
if clientID!=-1:
    print('Connected to remote API server')

    ################################# CODE FOR RESETTING ROB POSITION ###################################################
    
    err,bubbleRobHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRob",vrep.simx_opmode_oneshot_wait) #getHandle
    err,bubbleRobStartPosition = vrep.simxGetObjectPosition(clientID, bubbleRobHandle, -1, vrep.simx_opmode_oneshot_wait) #getStartPosition
    
    def reset_rob():
        ##### Set absolute position
        
        #stop simulation
        vrep.simxStopSimulation(clientID,vrep.simx_opmode_oneshot_wait) 

        #100ms delay, this is a hack because server isn't ready either
        time.sleep(0.1)

        #set on absolute position
        err = vrep.simxSetObjectPosition(clientID, bubbleRobHandle, -1, bubbleRobStartPosition, vrep.simx_opmode_oneshot_wait)

        #start simulation again
        vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)

    ################################## END RESETTING ROB  POSITION ########################################################

    reliability_for_action = 50
    default_velocity = 3
    discount = 0.9

    vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)

    def get_number_of_pix(img):
        colval = numpy.zeros((res[0]*res[1],3))
        i = 0
        for pix in range(res[0]*res[1]):
            for col in range(3):
                if  img[i] >= 0:
                    colval[pix][col] = img[i]
                else:
                    colval[pix][col] = img[i] + 256
                i += 1

        red = 0.0
        red_position = 0.0
        green = 0.0
        green_position = 0.0
        blue = 0.0
        blue_position = 0.0

        i = 0
        for pix in colval:
            i += 1
            position = (i % 32)
            if (pix[0] > 200 and pix[1] < 100 and pix[2] < 100):
                red += 1
                red_position += -1 + position * 0.0625 
            elif (pix[0] < 100 and pix[1] > 200 and pix[2] < 100):
                green += 1
                green_position += -1 + position * 0.0625
            elif (pix[0] < 100 and pix[1] < 100 and pix[2] > 200):
                blue += 1
                blue_position += -1 + position * 0.0625
        if (red > 0):
            red_position = red_position / red
        if (green > 0):
            green_position = green_position / green
        if (blue > 0):
            blue_position = blue_position / blue

        input_vars = [red / 256, red_position, green / 256, green_position, blue / 256, blue_position]
        return input_vars

    class NEURONAL_NETWORK:
        def __init__(self, reliability_for_action, discount):
            self.reliability_for_action = reliability_for_action
            self.discount = discount

            self.mlp = MLP(0.05)
            self.mlp.add_layer(Layer(6))
            self.mlp.add_layer(Layer(6))
            self.mlp.add_layer(Layer(3))
            self.mlp.init_network(True)
    
        def get_reward(self, input_vals):
            right_color_no = 0 # 0 for red, 1 for green and 2 for yellow
            right_color_position_no = right_color_no + 1

            right_color_position_difference = math.fabs(input_vals[right_color_position_no])
            
            right_color = 0.0 + input_vals[right_color_no]
            reward = 0.0

            #right_color = 0.0 + right_color / 10

            reward = right_color * (1 - right_color_position_difference)

            return reward

        def update_weights(self, old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward):
            old_q_vector = self.mlp.get_result(old_input_vals)
            if (reward == 1):
                prediction_error = reward
            else:
                prediction_error = reward + discount * new_q[new_action] - old_q_vector[old_action]
            
            new_q = [old_q_vector[0],old_q_vector[1],old_q_vector[2]]

            new_q[old_action] += prediction_error
            self.mlp.back_propagate(new_q)
            self.mlp.get_result(new_input_vals)

        def select_action(self,q_vector):
            h = numpy.array(q_vector)
            h_exp = numpy.exp(h * reliability_for_action)
            h_exp = h_exp / numpy.sum(h_exp)
            random = numpy.random.rand(1)
            action = 0
            if random > h_exp[0] and random < h_exp[0] + h_exp[1]:
                action = 1
            elif random > h_exp[0] + h_exp[1] and random < h_exp[0] + h_exp[1] + h_exp[2]:
                action = 2
            '''elif random > h_exp[0] + h_exp[1] + h_exp[2]:
                action = 3'''
            return action

    def turn_right():
        vrep.simxSetJointTargetVelocity(clientID,leftMotorHandle,default_velocity,vrep.simx_opmode_oneshot)
        vrep.simxSetJointTargetVelocity(clientID,rightMotorHandle,0,vrep.simx_opmode_oneshot)

    def turn_left():
        vrep.simxSetJointTargetVelocity(clientID,leftMotorHandle,0,vrep.simx_opmode_oneshot)
        vrep.simxSetJointTargetVelocity(clientID,rightMotorHandle,default_velocity,vrep.simx_opmode_oneshot)

    def move_forward():
        vrep.simxSetJointTargetVelocity(clientID,leftMotorHandle,8,vrep.simx_opmode_oneshot)
        vrep.simxSetJointTargetVelocity(clientID,rightMotorHandle,8,vrep.simx_opmode_oneshot)

    def move_backward():
        vrep.simxSetJointTargetVelocity(clientID,leftMotorHandle,-default_velocity,vrep.simx_opmode_oneshot)
        vrep.simxSetJointTargetVelocity(clientID,rightMotorHandle,-default_velocity,vrep.simx_opmode_oneshot)

    
    def act(action):
        #forward
        if action == 0:
            move_forward()
        #backward
        elif action == -1:
            move_backward()
        #left
        elif action == 1:
           turn_left()
        #right
        elif action == 2:
            turn_right()

    err,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_oneshot_wait)
    if err==vrep.simx_error_noerror:
        print('Number of objects in the scene: {}'.format(len(objs)))
    else:
        print('Remote API function call returned with error code: {}'.format(err))
    
    vrep.simxAddStatusbarMessage (clientID,"Connect from Python Client",vrep.simx_opmode_oneshot_wait)

    err,leftMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobLeftMotor",vrep.simx_opmode_oneshot_wait)
    if err==vrep.simx_error_noerror:
        print('Get handle for left motor: {}'.format(leftMotorHandle))
    else:
        print('Error by getting handle for left motor: {}'.format(err))
	
    err,rightMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobRightMotor",vrep.simx_opmode_oneshot_wait)
    if err==vrep.simx_error_noerror:
        print('Get handle for right motor: {}'.format(rightMotorHandle))
    else:
        print('Error by getting handle for right motor: {}'.format(err))

    err,visionSensorHandle=vrep.simxGetObjectHandle(clientID,"Vision_sensor",vrep.simx_opmode_oneshot_wait)
    if err==vrep.simx_error_noerror:
        print('Get handle for vision sensor: {}'.format(visionSensorHandle))
    else:
        print('Error by getting handle for vision sensor: {}'.format(err))

    while(err == vrep.simx_error_noerror or err == vrep.simx_error_novalue_flag):

        # move the robot somehow
        #vrep.simxSetJointTargetVelocity(clientID,leftMotorHandle,3.1415*0.25,vrep.simx_opmode_oneshot)
        #vrep.simxSetJointTargetVelocity(clientID,rightMotorHandle,3.1415*0.25,vrep.simx_opmode_oneshot)

        neuronal_network = NEURONAL_NETWORK(reliability_for_action, discount)

        # get vision sensor image
        err,res,img = vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_oneshot_wait)

        old_input_vals = get_number_of_pix(img)
        
        old_q = neuronal_network.mlp.get_result(old_input_vals)
        old_action = neuronal_network.select_action(old_q)

        i = 0
        number_of_useless_steps = 0

        while (True):
            act(old_action)
            time.sleep(0.05)
            err,res,img = vrep.simxGetVisionSensorImage(clientID,visionSensorHandle,0,vrep.simx_opmode_oneshot_wait)
            
            new_input_vals = get_number_of_pix(img)
            
            new_q = neuronal_network.mlp.get_result(new_input_vals)
            new_action = neuronal_network.select_action(new_q)
            reward = neuronal_network.get_reward(new_input_vals)

            neuronal_network.update_weights(old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward)

            old_q = new_q
            old_action = new_action
            old_input_vals = new_input_vals

            i += 1

            if reward == 0.96875:
                print "Target reached, resetting!"
                reset_rob()
            elif reward == 0:
                number_of_useless_steps += 1
                if number_of_useless_steps > 25:
                    number_of_useless_steps = 0
                    print "To many useless steps, resetting!"
                    reset_rob()
            else:
                number_of_useless_steps = 0

        # this is only for the err return value to end the while loop correctly - some other functions don't return a reliable err code!
        err,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_oneshot_wait)

    print('Program exiting loop due to err = {}'.format(err))
    vrep.simxFinish(clientID)
else:
    print('Failed connecting to remote API server')
    vrep.simxFinish(clientID)
print('Program ended')
vrep.simxFinish(clientID)
exit(0)

