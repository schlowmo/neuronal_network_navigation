import numpy
from mlp_network import MLP
from mlp_layer import Layer

class brainModel:
        def __init__(self, reliability_for_action, discount, learning_rate, momentum, bias, hidden_layers, number_of_neurons):
            #set instance variables
            self.reliability_for_action = reliability_for_action
            self.discount = discount
            self.learning_rate = learning_rate
            self.bias = bias
            self.momentum = momentum
            self.hidden_layers = hidden_layers
            self.number_of_neurons = number_of_neurons

            #create mlp
            self.mlp = MLP(self.learning_rate, self.momentum)
            self.mlp.add_layer(Layer(6))
            
            #create defined number of hidden layers
            for layer in range(self.hidden_layers):
                self.mlp.add_layer(Layer(int(self.number_of_neurons[layer])))
            
            self.mlp.add_layer(Layer(3))
            self.mlp.init_network(self.bias)

        def get_params(self):
            """
                returns the instance variables
            """
            return self.reliability_for_action, self.discount, self.learning_rate, self.momentum, self.bias, self.hidden_layers, self.number_of_neurons

        def set_params(self, reliability_for_action, discount, learning_rate, momentum):
            """
                sets changable instace variables, especially the mlp config
            """
            self.reliability_for_action = reliability_for_action
            self.discount = discount
            self.learning_rate = learning_rate

            self.mlp.learning_rate = self.learning_rate
            self.mlp.discount = self.discount
            self.mlp.momentum = momentum
    
        def get_reward(self, input_vals):
            """
                checks for reward
            """
            right_color_no = 0 # 0 for red, 1 for green and 2 for yellow
            right_color_position_no = right_color_no + 1

            right_color_position_difference = abs(input_vals[right_color_position_no])

            right_color = 0.0 + input_vals[right_color_no]
            reward = 0.0

            #right_color = 0.0 + right_color / 10

            reward = right_color * (1 - right_color_position_difference)

            return reward

        def update_weights(self, old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward):
            """
                calculates target values for MLP and back propagates them
            """
            old_q_vector = self.mlp.get_result(old_input_vals)
            if (reward == 1):
                prediction_error = reward
            else:
                prediction_error = reward + self.discount * new_q[new_action] - old_q_vector[old_action]
            
            new_q = [old_q_vector[0],old_q_vector[1],old_q_vector[2]]

            new_q[old_action] += prediction_error
            error = self.mlp.back_propagate(new_q)
            self.mlp.get_result(new_input_vals)

        def select_action(self,q_vector):
            """
                selects action based on output of the MLP init_network
            """

            h = numpy.array(q_vector)
            h_exp = numpy.exp(h * self.reliability_for_action)
            h_exp = h_exp / numpy.sum(h_exp)
            random = numpy.random.rand(1)
            action = 0
            if random > h_exp[0] and random < h_exp[0] + h_exp[1]:
                action = 1
            elif random > h_exp[0] + h_exp[1] and random < h_exp[0] + h_exp[1] + h_exp[2]:
                action = 2
            #comment this in for 4 actions
            #elif random > h_exp[0] + h_exp[1] + h_exp[2]:
            #    action = 3'''
            return action