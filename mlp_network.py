import math
from mlp_layer import Layer
import KTimage as KT

class MLP(object):
    def __init__(self, step = 0.3, momentum = 0.0):
        self.layers = []
        self.step = step
        self.momentum = momentum # set to zero if you don't want to use a momentum in backpropagation
        self.verbose = False

    ## Add layer while first layer is input layer, last layer is output layer and the rest are hidden layers
    def add_layer(self, layer):
        self.layers.append(layer)

    ## Initialize weights between layers and set bias to input layer if desired
    def init_network(self, bias=False):
        if bias:
            self.layers[0].set_bias()
        
        for i in range(len(self.layers)):
            if i < len(self.layers)-1:
                self.layers[i].next_layer(self.layers[i+1])
                self.layers[i].init_weights()

            if i > 0:
                self.layers[i].prev_layer(self.layers[i-1])

            self.layers[i].init_values()

    ## Train the network until max_interations or the desired accurency (error) is reached (optional)
    def train(self, input, target):
            self.get_result(input)
            self.back_propagate(target)
            

    ## get result for an inpunt
    def get_result(self, input):
        zero_layer = self.layers[0]
        required = zero_layer.num_neurons
        if zero_layer.has_bias:
            required -= 1
        if required != len(input):
            raise ValueError

        if zero_layer.has_bias:
            for i in range(zero_layer.num_neurons-1):
                zero_layer.values[i] = input[i]
        else:
            zero_layer.values = input
        self.activate()
        return self.layers[-1].values

    ## activate each layer
    def activate(self):
        for layer in self.layers[1:]:
            lim = layer.num_neurons
            if layer.has_bias:
                lim -= 1
            for idx in range(lim):
                val = 0.0
                for h_idx, h_neuron_value in enumerate(layer.prev.values):
                    val = val + h_neuron_value * layer.prev.weights[h_idx][idx]
                layer.values[idx] = layer.activation_fn(val)

    ## back propagate error for each layer
    def back_propagate(self, desired):
        difs = []
        total_error = 0.0

        for layer in reversed(self.layers):
            layer.difs = []
            if layer.next is None:
                #print "old_val:",layer.values
                #print "tar_val:",desired
                for idx, value in enumerate(layer.values):
                    err = desired[idx] - value
                    total_error = (err**2)/2
                    layer.difs.append(err)
            else:
                for idx, value in enumerate(layer.values):
                    dif = 0.0
                    err = 0.0
                    for l_idx, l_dif in enumerate(layer.next.difs):
                        err += l_dif * layer.weights[idx][l_idx]

                    dif = layer.derivative_fn(value) * err
                    layer.difs.append(dif)

        for layer in self.layers:
            if layer.next is None:
                continue
            for i in range(layer.num_neurons):
                for j in range(layer.next.num_neurons):
                    weight_change = layer.values[i] * layer.next.difs[j]
                    layer.weights[i][j] += self.step * weight_change
                    layer.weight_changes[i][j] = weight_change
        return total_error

    def visualise_weights(self):
        pass
        #for layer in self.layers:
        #    if layer.next is not None:
        #        KT.exporttiles (layer, res[1], res[0], "/home/morten/Uni/neuronale_netzwerke/V-REP/scenes/mybubbleRob/pgm/", 3, 1)
    