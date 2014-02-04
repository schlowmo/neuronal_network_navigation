#!/usr/bin/python

import platform
import os
import sys
import select
import time
import ConfigParser

Config = ConfigParser.ConfigParser()

Config.read("config.ini")

print Config.items("environment")

def heardEnter():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return False
    return True

vrepPath = "/home/morten/Uni/neuronale_netzwerke/V-REP/"
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
print "\n================================================================================================================="
print "========== Press ENTER if you want the simulation to pause, you will get some options what to do next. =========="
print "=================================================================================================================\n"

while (heardEnter()): 
	print "Still Running!"
	time.sleep(2)


print "Enter pressed, aborting!"