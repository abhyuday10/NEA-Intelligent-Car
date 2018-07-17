import math
import numpy as np


class Connection:
    def __init__(self, connectedNeuron):
        self.connectedNeuron = connectedNeuron
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

    def feedForward(self):
        sumOutput = 0
        if len(self.dendrons) == 0:
            return
        for connection in self.dendrons:
            sumOutput += (connection.connectedNeuron.getOutput() * connection.weight)
        self.output = self.sigmoid(sumOutput)

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x * 1.0))

    def setOutput(self, output):
        self.output = output

    def getOutput(self):
        return self.output


class Network:
    def __init__(self, topology):
        self.layers = []
        self.topology = topology
        layerNumber = 0
        for layerNum in range(len(topology)):
            layerNumber += 1
            layer = []
            for i in range(topology[layerNum]):
                if len(self.layers) == 0:
                    layer.append(Neuron(None))
                else:
                    layer.append(Neuron(self.layers[-1]))

            if not (layerNumber) >= len(topology):
                layer.append(Neuron(None))  # bias neuron
                layer[-1].setOutput(1)  # setting output of bias neuron as 1

            self.layers.append(layer)

    def printNetStruct(self):
        struct = []
        for layer in self.layers:
            sum = 0
            for neuron in layer:
                sum += 1
            struct.append(sum)
        print(struct)

    def printNet(self):
        layers = []
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    layers.append(dendron.weight)
        print(layers)

    def getNetWeights(self):
        layers = []
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    layers.append(dendron.weight)
        return layers

    def setNetWeights(self, weights):
        i = 0
        for layer in self.layers:
            for neuron in layer:
                for dendron in neuron.dendrons:
                    if i > len(weights) - 1:
                        return
                    dendron.weight = weights[i]
                    i += 1

    def setInputs(self, inputs):
        for i in range(len(inputs)):
            self.layers[0][i].setOutput(inputs[i])

    def feedForward(self):
        for layer in self.layers[1:]:
            for neuron in layer:
                neuron.feedForward()

    def getResults(self):
        output = []
        for neuron in self.layers[-1]:
            output.append(neuron.getOutput())
        return output

    def getDiscreteResults(self):
        if self.layers[-1][0].getOutput() > self.layers[-1][1].getOutput():
            return "left"
        elif self.layers[-1][0].getOutput() < self.layers[-1][1].getOutput():
            return "right"
