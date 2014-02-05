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

Installation
------------
* install python module dependencies, those are: numpy, dill and matplotlib
* edit the value of vrepPath in config.ini to met your local installation of V-REP
* add the following lines to remoteApiConnections.txt in your V-REP base directory: 
        portIndex2_port = 19999
        portIndex2_debug = false
        portIndex2_syncSimTrigger = true
* run start.sh, symlinks should be created automatically; if you skipped the last step, the script will tell you what to do
* if creation of symlinks fails, try it manually (vrep.py, vrepConst.py, remoteApi.so)