import numpy
import random
import KTimage as KT
from mlp_network import MLP
from mlp_layer import Layer

## Class for modeling the basics of the world
class world_model:
    def __init__(self, size_x, size_y, target_x, target_y):
        #set size of world
        self.size_x = size_x
        self.size_y = size_y
        #set position of target
        self.target_x = target_x
        self.target_y = target_y
    ## initialize agent position for new trial
    def initialize(self):
        self.pos_x = random.randint(0, size_x - 1)
        self.pos_y = random.randint(0, size_y - 1)
    ##Set new position depending on action, respect world boundaries
    def act(self, action):
        #up
        if action == 0:
            self.pos_y -= 1
            if self.pos_y < 0:
                self.pos_y = 0
                #self.pos_y = size_y - 1
        #down
        elif action == 1:
            self.pos_y += 1
            if self.pos_y > self.size_y - 1:
                self.pos_y = self.size_y - 1
                #self.pos_y = 0
        #left
        elif action == 2:
            self.pos_x -= 1
            if self.pos_x < 0:
                self.pos_x = 0
                #self.pos_x = size_x - 1
        #right
        elif action == 3:
            self.pos_x += 1
            if self.pos_x > self.size_x - 1:
                self.pos_x = self.size_x -1
                #self.pos_x = 0
    def get_sensor_for_mlp(self):
        return [0.0 + self.pos_x, 0.0 + self.pos_y]
    ## Return reward of 1 if agent's position is same as target's position, otherwise return 0
    def get_reward(self):
        reward = 0
        if self.pos_x == self.target_x and self.pos_y == self.target_y:
            reward = 1
        return reward

## The neuronal network with some helper methods
class neuronal_network_model:
    def __init__(self, size_x, size_y, discount, reliability_for_action, world):
        # initialize fields
        self.world = world
        self.size_y = size_y
        self.size_x = size_x
        self.discount = discount
        self.reliability_for_action = reliability_for_action
        self.mlp = MLP(0.01)
        self.mlp.add_layer(Layer(2)) # two input neurons for x and y
        self.mlp.add_layer(Layer(6)) # hidden Layer
        self.mlp.add_layer(Layer(4, lambda: numpy.random.uniform(0.0, 0.25), lambda x: x, lambda x: 1.0)) # four output neurons, one for each action
        self.mlp.init_network(True) # initialize network with bias
    ## action selection with Boltzman-Softmax
    def select_action(self, q_vector):
        h = numpy.array(q_vector)
        h_exp = numpy.exp(h * self.reliability_for_action)
        h_exp = h_exp / numpy.sum(h_exp)
        random = numpy.random.rand(1)
        action = 0
        if random > h_exp[0] and random < h_exp[0] + h_exp[1]:
            action = 1
        elif random > h_exp[0] + h_exp[1] and random < h_exp[0] + h_exp[1] + h_exp[2]:
            action = 2
        elif random > h_exp[0] + h_exp[1] + h_exp[2]:
            action = 3
        return action
    ## return q value at current position with specified action
    def get_q(self, position):
        q = self.mlp.get_result(position)
        return q
    ## update q Value for specified action at specified index
    def update_weight(self, new_q_vector, old_q_vector, new_position, old_position, new_action, old_action, reward):
        old_q_vector = self.get_q(old_position)
        if (reward):
            prediction_error = reward
        else:
            prediction_error = discount * new_q_vector[new_action] - old_q_vector[old_action]
        
        new_q_vector = [old_q_vector[0],old_q_vector[1],old_q_vector[2],old_q_vector[3]]

        new_q_vector[old_action] += prediction_error
        self.mlp.back_propagate(new_q_vector)
        self.mlp.get_result(new_position)
    ## return transposed weight-matrix for visualisation
    def get_weights_for_visualisation(self):
        return numpy.transpose(self.w)



#enviromental variables
size_x, size_y = 5,5 #size of world
target_x, target_y = 2,2 #Where is the target?
discount = 0.9 # discount factor
reliability_for_action = 50
max_moves = 100000 # how much moves to be taken without reaching the target before aborting
trials = 10000 # how often should the agent try to reach the target

# create new world
world = world_model(size_x, size_y, target_x, target_y)

# create new neuronal network
neuronal_network = neuronal_network_model(size_x, size_y, discount, reliability_for_action, world)

## repeat until number of trials is reached
for x in range(1, trials):
    # set agent to new random position
    world.initialize()
    # initializing variables for first step
    old_position = world.get_sensor_for_mlp()
    old_q_vector = neuronal_network.get_q(old_position)
    old_action = neuronal_network.select_action(old_q_vector)

    if (world.get_reward() != 1): # if agents starting position is same as target position, don't move and update
        ## repeat until numer of max_moves is reached or target reached
        for i in range(1, max_moves):
            # move agent
            world.act(old_action)
            new_position = world.get_sensor_for_mlp()
            new_q_vector = neuronal_network.get_q(new_position)
            # check for reward
            reward = world.get_reward()

            # select new action
            new_action = neuronal_network.select_action(new_q_vector)
           
            neuronal_network.update_weight(new_q_vector, old_q_vector, new_position, old_position, new_action, old_action, reward)

            if reward == 1: # reached target, exit
                break

            # new values become old values
            old_action = new_action
            old_q_vector = new_q_vector
            old_position = new_position

       
    else:
        print "Initialized on target"
    #print neuronal_network.mlp.as_graph()
    print x, i
    #if (x % 200 == 0):
    #    reliability_for_action += 1
    #    print "Increasing reliability_for_action to %i" % (reliability_for_action)
        #KT.exporttiles (neuronal_network.get_weights_for_visualisation(), size_x, size_y, "pgm/obs_W_1_0.pgm", 1,4)
