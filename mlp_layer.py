import numpy
import math

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

class Layer(object):
    def __init__(self, num_neurons, weight_function=lambda: numpy.random.uniform(0.0, 0.25), activation_fn=lambda x: sigmoid(x), derivative_fn=lambda x: sigmoid(x) * (1 - sigmoid(x))):
        if num_neurons <= 0:
            raise ValueError

        self.num_neurons = num_neurons
        self.weight_function = weight_function
        self.next = None
        self.prev = None
        self.weights = None
        self.weight_changes = None
        self.difs = None
        self.has_bias = False
        self.values = []
        self.activation_fn = activation_fn
        self.derivative_fn = derivative_fn

    ## set the next layer
    def next_layer(self, layer):
        self.next = layer

    ## set the previous layer
    def prev_layer(self, layer):
        self.prev = layer

    ## initialize value vector
    def init_values(self):
        self.values = [0 for _ in range(self.num_neurons)]
        if self.has_bias:
            self.values[-1] = 1.

    ## initialize weight matrix between this layer and his follower
    def init_weights(self):
        if self.next is not None:
            self.weights = []
            self.weight_changes = []
            for i in range(self.num_neurons):
                self.weights.append([self.weight_function()
                    for _ in range(self.next.num_neurons)])
                self.weight_changes.append([0
                    for _ in range(self.next.num_neurons)])

    ## used to set the bias if desired
    def set_bias(self):
        self.num_neurons += 1
        self.has_bias = True

