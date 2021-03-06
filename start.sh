#!/usr/bin/python

import platform
import os
import sys
import select
import time
import ConfigParser
import dill

#read Configuration from config.ini using native ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

#defines function for saving a network using dill module
def saveNetwork(network, filename):
	with open('saved/' + filename + '.pk', 'wb') as output:
		dill.dump(network, output, dill.HIGHEST_PROTOCOL)

#defines function for loading a network using dill module
def loadNetwork(filename):
	with open('saved/' + filename + '.pk') as input:
		return dill.load(input)

def heardEnter():
	i,o,e = select.select([sys.stdin],[],[],0.0001)
	for s in i:
		if s == sys.stdin:
			input = sys.stdin.readline()
			return False
	return True

if Config.getboolean('environment', 'automatic'):
	vrepPath = Config.get('environment', 'vrepPath')
	#OS switch
	if platform.system() =='Windows':
		print "Setup routines for Windows not implemented yet. Aborting! Use a better OS (guess what), do a manual setup or the best solution: write your own setup routine and share it with others!"
	elif platform.system() == 'Darwin':
		print "Setup routines for Mac OS not implemented yet. Aborting! Use a better OS (guess what), do a manual setup or the best solution: write your own setup routine and share it with others!"
	else:
		print "Smart one, you're using the right OS. I will try automatic setup for you!"
		
		#Check if necessary librarys exists in this directory, if not, symlink to them
		if not os.path.exists("./remoteApi.so"):
			os.symlink(vrepPath + "remoteApi.so", "./remoteApi.so")
		else: 
			print "remoteApi.so already exists, hopefully it's a working link"
		if not os.path.exists("./vrep.py"):
			os.symlink(vrepPath + "/programming/Python/vrep.py", "./vrep.py")
		else: 
			print "vrep.py already exists, hopefully it's a working link"
		if not os.path.exists("./vrepConst.py"):
			os.symlink(vrepPath + "/programming/Python/vrepConst.py", "./vrepConst.py")
		else: 
			print "vrepConst.py already exists, hopefully it's a working link"
		remoteServiceConfig = file(vrepPath + 'remoteApiConnections.txt').read()
		if "portIndex2_port = 19999" in remoteServiceConfig:
			print "Continious Remote API Service Server seems to be configured correctly, all setup is done"
		else:
			print "Continious Remote API Service Server has to be added to remoteApiConnections.txt in your v-rep directory"
			print "Please add the following lines to this file, restart V-REP and run this start.sh script again:\n"
			print "portIndex2_port = 19999\nportIndex2_debug = false\nportIndex2_syncSimTrigger = false\n"
			exit(0)

#now neccessary librarys are symlinked, so we can import vrep and afterwards our own classes
import vrep
from rob import robController
from brain import brainModel

#connect to contonious remote API server service
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5)

if clientID!=-1: #check if the connection to remote API server service was successfull
	print('Connected to remote API server')
	vrep.simxAddStatusbarMessage (clientID,"Connect from Python Client",vrep.simx_opmode_oneshot_wait)

	#create instance of robController
	rob = robController(clientID)
	reliability_for_action = Config.getfloat('network', 'reliability_for_action')
	
	#create new brainModel instance or load saved one from file
	discount = Config.getfloat('network', 'discount')
	learning_rate = Config.getfloat('network', 'learning_rate')
	momentum = Config.getfloat('network', 'momentum')
	bias = Config.getboolean('network', 'bias')
	hidden_layers = Config.getint('network', 'hidden_layers')
	number_of_neurons = Config.get('network', 'number_of_neurons').split(',')

	load = raw_input("Would you like to import a saved network?[Y/N]  ")
	if (load.upper() == 'Y'):
		filename = raw_input("Enter filename (under saved directory, without extension), leave empty if you changed your mind: ")
		if (filename != ''):
			brain = loadNetwork(filename)
			print "Network loaded."
			saved_reliability_for_action, saved_discount, saved_learning_rate, saved_momentum, saved_bias, saved_hidden_layers, saved_number_of_neurons = brain.get_params()
			print "SAVED PARAMS [S]:reliability_for_action = ", saved_reliability_for_action, " discount = ", saved_discount, " learning_rate = ", saved_learning_rate, " momentum = ", saved_momentum, " bias = ", saved_bias, " hidden_layers = ", saved_hidden_layers, " number_of_neurons = ", saved_number_of_neurons
			print "CURRENT PARAMS [C]: reliability_for_action = ", reliability_for_action, " discount = ", discount, " learning_rate = ", learning_rate, " momentum = ", momentum, " bias = ", bias, " hidden_layers = ", hidden_layers, " number_of_neurons = ", number_of_neurons
			print "Note that bias and the number/neurons of hidden layers cannot be changed (yet)"
			whichConfig = raw_input("Which params would you like to use? [S/C] ")
			if (whichConfig.upper() == 'C'):
				brain.set_params(reliability_for_action, discount, learning_rate, momentum)
		else:
			brain = brainModel(reliability_for_action, discount, learning_rate, momentum, bias, hidden_layers, number_of_neurons)
	else:
		brain = brainModel(reliability_for_action, discount, learning_rate, momentum, bias, hidden_layers, number_of_neurons)

	#check if error occurs, we need this for our error checking while loop, suggested by v-rep devs
	err,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_oneshot_wait)

	#get max runs and max steps from config file, if config file returns 0, set to true to get infinite rules (remember, the will respect break conditions anyway)
	max_runs = Config.getint('simulation', 'runs') if Config.getint('simulation', 'runs') != 0 else True
	max_steps = Config.getint('simulation', 'steps') if Config.getint('simulation', 'steps') != 0 else True
	max_useless_steps = Config.getint('simulation', 'useless_steps') if Config.getint('simulation', 'useless_steps') != 0 else True
	
	number_of_runs = 0

	print "\n=============================================================================================="
	print "========== Press ENTER to end simulation, you will get some options what to do next. =========="
	print "===============================================================================================\n"

	#start simulation
	vrep.simxStartSimulation(clientID,vrep.simx_opmode_oneshot_wait)
	
	#loop until max_runs is reached or forever if max_runs is set to unlimited
	while ((max_runs == True or number_of_runs <= max_runs) and heardEnter()):
		#loop checking for errors
		while(err == vrep.simx_error_noerror or err == vrep.simx_error_novalue_flag): #this is our error checking loop, should run forever if no error in v-rep occurs

			#initialize first state
			old_input_vals = rob.get_and_process_image()
			old_q = brain.mlp.get_result(old_input_vals)
			old_action = brain.select_action(old_q)

			#set step counters to zero
			number_of_useless_steps = 0
			number_of_steps = 0

			#loop until max_steps is reached or forever if max_steps is set to unlimited
			while (max_steps == True or number_of_steps <= max_steps):
				rob.move(old_action)
				
				#get current state
				new_input_vals = rob.get_and_process_image()
				new_q = brain.mlp.get_result(new_input_vals)
				new_action = brain.select_action(new_q)
				
				#check for reward
				reward = brain.get_reward(new_input_vals)
				
				#update network (MLP) based on last and current step
				brain.update_weights(old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward)

				#old becomes new
				old_q = new_q
				old_action = new_action
				old_input_vals = new_input_vals

				#check if target is reached
				if reward == 0.96875:
					print "Target reached, resetting!"
					rob.reset_rob()
					break
				#check if number of useless steps is reached
				elif (max_useless_steps != True and reward == 0):
					number_of_useless_steps += 1
					if number_of_useless_steps > max_useless_steps:
						number_of_useless_steps = 0
						print "To many useless steps, resetting!"
						rob.reset_rob()
						break
				#set useless step counter to zero
				else:
					number_of_useless_steps = 0

				number_of_steps += 1

			number_of_runs +=1

			#check if error occurs, if yes, while loop won't repeat
			err,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_oneshot_wait)

			break

	#stop simulation and close connection to remote API server serice
	vrep.simxStopSimulation(clientID, vrep.simx_opmode_oneshot_wait)
	vrep.simxFinish(clientID)

#if connection to remote API server service failed, abort
else:
	print('Failed connecting to remote API server, aborting')
	vrep.simxFinish(clientID)
	exit(1)


#ask user if the network shoukd be saved
print "Simulation ended, would you like to save current status of neuronal_network?"
save = raw_input('Press Y or N:  ')
save = save.upper() == 'Y'
if(save):
	filename = raw_input('Please enter a filename without extension. [Default: network, if no filename given]: ')
	if (filename == ''):
		filename = 'network'
	saveNetwork(brain, filename)
	print 'Saved network as: saved/' + filename + '.pk'
	print 'Finished!'
else:
	print 'Finished without saving!'

#exit without errors
exit(0)