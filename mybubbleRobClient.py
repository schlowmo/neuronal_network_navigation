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
import KTimage as KT
import time
from mlp_network import MLP
from mlp_layer import Layer
from rob import robController
from brain import brainModel


err = vrep.simx_error_noerror

print 'Program started'

clientID=vrep.simxStart('127.0.0.1',19998,True,True,5000,5)
if clientID!=-1:
    print('Connected to remote API server')

    rob = robController(clientID) 
   
    reliability_for_action = 50
    default_velocity = 3
    discount = 0.9

    vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)

    vrep.simxAddStatusbarMessage (clientID,"Connect from Python Client",vrep.simx_opmode_oneshot_wait)

    while(err == vrep.simx_error_noerror or err == vrep.simx_error_novalue_flag):

        brain = brainModel(reliability_for_action, discount)

        old_input_vals = rob.get_and_process_image()
        
        old_q = brain.mlp.get_result(old_input_vals)
        old_action = brain.select_action(old_q)

        i = 0
        number_of_useless_steps = 0

        while (True):
            rob.move(old_action)
            time.sleep(0.05)
            
            new_input_vals = rob.get_and_process_image()
            
            new_q = brain.mlp.get_result(new_input_vals)
            new_action = brain.select_action(new_q)
            reward = brain.get_reward(new_input_vals)

            brain.update_weights(old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward)

            old_q = new_q
            old_action = new_action
            old_input_vals = new_input_vals

            i += 1

            if reward == 0.96875:
                print "Target reached, resetting!"
                rob.reset_rob()
            elif reward == 0:
                number_of_useless_steps += 1
                if number_of_useless_steps > 25:
                    number_of_useless_steps = 0
                    print "To many useless steps, resetting!"
                    rob.reset_rob()
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

