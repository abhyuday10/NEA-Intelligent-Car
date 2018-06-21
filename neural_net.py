import math
import random

import numpy as np


class Connection:
    def __init__(self, connectedNeuron):
        self.connectedNeuron = connectedNeuron
        self.weight = np.random.normal()
        self.dWeight = 0.0


class Neuron:
    eta = 0.09
    alpha = 0.015

    def __init__(self, prev_layer):
        self.dendrons = []
        self.error = 0.0
        self.gradient = 0.0
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

    def backPropagate(self):
        self.gradient = self.error * self.dSigmoid(self.output)
        for dendron in self.dendrons:
            dendron.dweight = Neuron.eta * (dendron.connectedNeuron.output * self.gradient)
            dendron.weight += dendron.dweight
            dendron.connectedNeuron.addError(self.gradient * dendron.weight)
        self.error = 0

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x * 1.0))

    def dSigmoid(self, x):
        return x * (1.0 - x)

    def addError(self, error):
        self.error = self.error + error

    def setError(self, error):
        self.error = error

    def setOutput(self, output):
        self.output = output

    def getOutput(self):
        return self.output


class Network:
    def __init__(self, topology):
        self.layers = []
        self.topology=topology
        layerNumber = 0
        for layerNum in range(len(topology)):
            layerNumber += 1
            # print(layerNumber)
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

    def getError(self, targets):
        totalError = 0
        for i in range(len(targets)):
            error = (targets[i] - self.layers[-1][i].getOutput())
            totalError += error ** 2
        totalErrorSqrd = totalError / len(targets)
        totalError = math.sqrt(totalErrorSqrd)
        return totalError

    def feedForward(self):
        for layer in self.layers[1:]:
            for neuron in layer:
                neuron.feedForward()

    def backPropagate(self, targets):
        for i in range(len(targets)):
            self.layers[-1][i].setError(targets[i] - self.layers[-1][i].getOutput())

        for layer in self.layers[::-1]:
            for neuron in layer:
                neuron.backPropagate()

    def getResults(self):
        output = []
        print(len(self.layers[-1]))
        for neuron in self.layers[-1]:
            output.append(neuron.getOutput())
        return output

    def getDiscreteResults(self):
        output = []
        # print(len(self.layers[-1]))
        for neuron in self.layers[-1]:
            o = neuron.getOutput()
            if o > 0.5:
                o = "right"
            else:
                o = "left"
            output.append(o)
        return output


def main():
    print("Started Network Training")
    topology = [2, 3, 2]
    net = Network(topology)
    Neuron.eta = 0.09
    Neuron.alpha = 0.015

    inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    outputs = [[0, 0], [1, 1], [1, 0], [0, 1]]
    net.printNetStruct()
    for layer in net.layers:
        print(len(layer))
    while 1:
        # time.sleep(1)
        error = 0
        for i in range(len(inputs)):
            net.setInputs(inputs[i])
            net.feedForward()
            net.backPropagate(outputs[i])
            error = error + net.getError(outputs[i])

        # net.printNet()
        print("error: ", error)
        if error < 0.01:
            break

    while True:
        a = input("Enter A: \n")
        b = input("Enter B: \n")
        net.setInputs([float(a), float(b)])
        net.feedForward()
        print(net.getThResults())


# def randomiseWeights(weights):
#     for i in range(len(weights) - 1):
#         weights[i] = (random.uniform(-1, 1))
#     print(weights)
#     return weights


# main()
# nn = Network([2, 2])
# weights = nn.getNetWeights()
# print(weights)
#
# randomiseWeights(weights)
# nn.setNetWeights(weights)
# print(nn.getNetWeights())
