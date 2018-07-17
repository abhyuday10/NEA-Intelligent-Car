import math
import numpy as np


class Connection:
    def __init__(self, connected_neuron):
        self.connectedNeuron = connected_neuron
        self.weight = np.random.normal()


class Neuron:

    def __init__(self, prev_layer):
        self.dendrons = []
        self.output = 0.0
        if prev_layer is None:
            pass
        else:
            for neuron in prev_layer:
                connection = Connection(neuron)
                self.dendrons.append(connection)

    def feed_forward(self):
        sum_output = 0
        if len(self.dendrons) == 0:
            return
        for connection in self.dendrons:
            sum_output += (connection.connectedNeuron.get_output() * connection.weight)
        self.output = self.sigmoid(sum_output)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x * 1.0))

    def set_output(self, output):
        self.output = output

    def get_output(self):
        return self.output


class Network:
    def __init__(self, topology):
        self.layers = []
        self.topology = topology
        layer_number = 0
        for layerNum in range(len(topology)):
            layer_number += 1
            layer = []
            for i in range(topology[layerNum]):
                if len(self.layers) == 0:
                    layer.append(Neuron(None))
                else:
                    layer.append(Neuron(self.layers[-1]))

            if not layer_number >= len(topology):
                layer.append(Neuron(None))  # bias neuron
                layer[-1].set_output(1)  # setting output of bias neuron as 1

            self.layers.append(layer)

    def print_network_structure(self):
        structure = []
        for layer in self.layers:
            structure.append(len(layer))
        print(structure)

    def print_network_weights(self):
        layers = []
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    layers.append(dendron.weight)
        print(layers)

    def get_network_weights(self):
        layers = []
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    layers.append(dendron.weight)
        return layers

    def set_network_weights(self, weights):
        i = 0
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    if i > len(weights) - 1:
                        return
                    dendron.weight = weights[i]
                    i += 1

    def set_inputs(self, inputs):
        for i in range(len(inputs)):
            self.layers[0][i].set_output(inputs[i])

    def feed_forward(self):
        for layer in self.layers[1:]:
            for neuron in layer:
                neuron.feed_forward()

    def get_results(self):
        output = []
        for neuron in self.layers[-1]:
            output.append(neuron.get_output())
        return output

    def get_decision(self):
        if self.layers[-1][0].get_output() > self.layers[-1][1].get_output():
            return "left"
        elif self.layers[-1][0].get_output() < self.layers[-1][1].get_output():
            return "right"
