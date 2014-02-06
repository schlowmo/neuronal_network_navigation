V-REP Navigation - find colored cube with bubbleRob
===================================================

Target
------
The bubbleRob should find a colored cube in a very simple world. The default is the red one, but this can be changed in config file.

Used Networks/Algorithms
------------------------
* SARSA Algorithm
* Multi Layer Perceptron (MLP)

Additional Features
-------------------
* autosetup routines for linux
* global config file (config.ini)
* state of network can be saved and loaded
* configurable number of hidden layers in MLP

Installation
------------
* install python module dependencies, those are: numpy, dill and matplotlib
* save this directory anywhere in your filesystem
* edit the value of vrepPath in config.ini to met your local installation of V-REP
* add the following lines to remoteApiConnections.txt in your V-REP base directory: 
```
portIndex2_port = 19999
portIndex2_debug = false
portIndex2_syncSimTrigger = true
```
* (re)start v-rep after adding this lines
* run start.sh, symlinks should be created automatically; if you skipped the last step, the script will tell you what to do
* if creation of symlinks fails, try it manually (vrep.py, vrepConst.py, remoteApi.so) and rerun start.sh

Usage
-----
* before running start.sh, start V-REP and load the .ttt scene file
* the start.sh script is kind of interactive
* it will ask if you want to load a previous network state before starting the simulation
* you can stop the script by pressing ENTER, current run will be finished before the simulation is stopped
* after the simulation ends, the script will ask if you want to save the current network state
* network states will be saved in the "saved" subfolder, when you're promted for filenames, enter them without extension
* don't quit the script by pressing strg/cmd + c, because this will mess up the simulation and you won't be able to save the current state 
* the script can be configured in config.ini; you will find further explanations in the comments of this ini file

File Overview
-------------
* brain.py: neuronal network class, SARSA and MLP are combined here; used by start.sh
* config.ini: config file; parsed in start.sh
* find_the_cube.ttt: (binary) scene file for V-REP
* mlp_layer.py: class that implements Layers for MLP, used by mlp_network.py and brain.py
* mlp_network.py: class that implements a customizable MLP with a variable number of layers; used by brain.py
* readme.md: you're currently reading this
* rob.py: controller class for bubbleRob, implements functions to move the rob and to get (and process) the vision sensor; used by start.sh
* start.sh: python shell script where all the magic starts

Additional Notes
----------------
* dill is used in save_network function instead of the native module pickle because of problems with lambda functions; see [this](http://stackoverflow.com/q/16626429/2236166) stackoverflow thread for more information
