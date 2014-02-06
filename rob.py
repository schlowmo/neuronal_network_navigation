import vrep
import time
import numpy

class robController(object):
	
	def __init__(self, clientID):
		self.clientID = clientID
		
		err,leftMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobLeftMotor",vrep.simx_opmode_oneshot_wait)
		if err==vrep.simx_error_noerror:
			self.leftMotorHandle = leftMotorHandle
			print('Get handle for left motor: {}'.format(leftMotorHandle))
		else:
			print('Error by getting handle for left motor: {}'.format(err))
			
		err,rightMotorHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRobRightMotor",vrep.simx_opmode_oneshot_wait)
		if err==vrep.simx_error_noerror:
			self.rightMotorHandle = rightMotorHandle
			print('Get handle for right motor: {}'.format(rightMotorHandle))
		else:
			print('Error by getting handle for right motor: {}'.format(err))

		err,visionSensorHandle=vrep.simxGetObjectHandle(clientID,"Vision_sensor",vrep.simx_opmode_oneshot_wait)
		if err==vrep.simx_error_noerror:
			self.visionSensorHandle = visionSensorHandle
			print('Get handle for vision sensor: {}'.format(visionSensorHandle))
		else:
			print('Error by getting handle for vision sensor: {}'.format(err))

		err,bubbleRobHandle=vrep.simxGetObjectHandle(clientID,"remoteApiControlledBubbleRob",vrep.simx_opmode_oneshot_wait) #getHandle
		if err==vrep.simx_error_noerror:
			self.bubbleRobHandle = bubbleRobHandle
			print('Get handle for bubbleRob: {}'.format(bubbleRobHandle))
		else:
			print('Error by getting handle for bubbleRob: {}'.format(err))

		err,self.bubbleRobStartPosition = vrep.simxGetObjectPosition(clientID, bubbleRobHandle, -1, vrep.simx_opmode_oneshot_wait) #getStartPosition
			
	def move(self, direction):
		"""
			sets velocity of wheels to move the bubbleRob
		"""

		velocity = []

		if direction == 0: #forward
			velocity = [8,8]
		elif direction == 1: #left
			velocity = [3,8]
		elif direction == 2: #right
			velocity = [8,3]
		elif direction == 3: #backward
			velocity = [-8,-8]

		vrep.simxSetJointTargetVelocity(self.clientID,self.leftMotorHandle,velocity[0],vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetVelocity(self.clientID,self.rightMotorHandle,velocity[1],vrep.simx_opmode_oneshot)

		time.sleep(0.1)

	def get_and_process_image(self):
		"""
			returns the aggregated data of bubbleRobs Vision Sensor
		"""
		err,res,img = vrep.simxGetVisionSensorImage(self.clientID,self.visionSensorHandle,0,vrep.simx_opmode_oneshot_wait)

		colval = numpy.zeros((res[0]*res[1],3))
		i = 0
		for pix in range(res[0]*res[1]):
			for col in range(3):
				if img[i] >= 0:
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

	def reset_rob(self):
		"""
			Sets the bubbleRob to his starting position; mind the hack, simulation has to be stopped 
		"""

		##### Set absolute position

		#stop simulation
		vrep.simxStopSimulation(self.clientID,vrep.simx_opmode_oneshot_wait) 

		#100ms delay, this is a hack because server isn't ready either
		time.sleep(0.3)

		#set on absolute position
		err = vrep.simxSetObjectPosition(self.clientID, self.bubbleRobHandle, -1, self.bubbleRobStartPosition, vrep.simx_opmode_oneshot_wait)

		#start simulation again
		vrep.simxStartSimulation(self.clientID,vrep.simx_opmode_oneshot_wait)

		time.sleep(0.3)
