import numpy
from mlp_network import MLP
from mlp_layer import Layer

class brainModel:
        def __init__(self, reliability_for_action, discount, learning_rate, bias):
            self.reliability_for_action = reliability_for_action
            self.discount = discount
            self.learning_rate = learning_rate
            self.bias = bias

            self.mlp = MLP(self.learning_rate)
            self.mlp.add_layer(Layer(6))
            self.mlp.add_layer(Layer(6))
            self.mlp.add_layer(Layer(3))
            self.mlp.init_network(self.bias)
    
        def get_reward(self, input_vals):
            right_color_no = 0 # 0 for red, 1 for green and 2 for yellow
            right_color_position_no = right_color_no + 1

            right_color_position_difference = abs(input_vals[right_color_position_no])

            right_color = 0.0 + input_vals[right_color_no]
            reward = 0.0

            #right_color = 0.0 + right_color / 10

            reward = right_color * (1 - right_color_position_difference)

            return reward

        def update_weights(self, old_q, new_q, old_action, new_action, old_input_vals, new_input_vals, reward):
            old_q_vector = self.mlp.get_result(old_input_vals)
            if (reward == 1):
                prediction_error = reward
            else:
                prediction_error = reward + self.discount * new_q[new_action] - old_q_vector[old_action]
            
            new_q = [old_q_vector[0],old_q_vector[1],old_q_vector[2]]

            new_q[old_action] += prediction_error
            self.mlp.back_propagate(new_q)
            self.mlp.get_result(new_input_vals)

        def select_action(self,q_vector):
            h = numpy.array(q_vector)
            h_exp = numpy.exp(h * self.reliability_for_action)
            h_exp = h_exp / numpy.sum(h_exp)
            random = numpy.random.rand(1)
            action = 0
            if random > h_exp[0] and random < h_exp[0] + h_exp[1]:
                action = 1
            elif random > h_exp[0] + h_exp[1] and random < h_exp[0] + h_exp[1] + h_exp[2]:
                action = 2
            '''elif random > h_exp[0] + h_exp[1] + h_exp[2]:
                action = 3'''
            return action