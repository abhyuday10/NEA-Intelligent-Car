import numpy as np
import math


class Connection:
    def __init__(self, connectedNeuron):
        self.connectedNeuron = connectedNeuron
        self.weight = np.random.normal()
        self.dWeight = 0.0


class Neuron:
    eta = 0.001
    alpha = 0.01

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
        if self.dendrons:
            for connection in self.dendrons:
                sumOutput += connection.connectedNeuron.getOutput() * connection.weight
        self.output = self.sigmoid(sumOutput)

    def backpropagate(self):
        self.gradient=self.error*self.dSigmoid(self.output)
        for dendron in self.dendrons:
            dendron.dweight=Neuron.eta*(dendron.connectedNeuron.output*self.gradient)
            dendron.dweight+=dendron.dweight
            dendron.connectedNeuron.addError(self.gradient*dendron.weight)
        self.error=0

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x * 1.0))

    def dSigmoid(self, x):
        return x * (1.0 - x)

    def AddError(self, error):
        self.error = self.error + error

    def setError(self, error):
        self.error = error

    def setOutput(self, output):
        self.output = output

    def getOutput(self):
        return self.output

class Network:
    def __init__(self, topology):
        self.layers=[]
        for numNeurons in topology:
            layer=[]
            for i in range(numNeurons):
                if len(self.layers)==0:
                    layer.append(Neuron(None))
                else:
                    layer.append(Neuron(self.layers[-1]))
            self.layers.append(layer)

    def setInputs(self, inputs):
        for i in range(len(inputs)):
            print(i)
            self.layers[0][i].setOutput(inputs(i))

    def getError(self, targets):
        totalError=0
        for i in range(len(targets)):
            error=(targets[i]-self.layers[-1][i].getOutput())
            totalError+=error**2
        totalErrorSqrd=totalError/len(targets)
        totalError=math.sqrt(totalErrorSqrd)
        return totalError

    def feedForward(self):
        for layer in self.layers[1:]:
            for neuron in layer:
                neuron.feedForward()

    def backPropagate(self, targets):
        for i in range(len(targets)):
            self.layers[-1][i].setError(targets[i]-self.layers[-1][i].getOutput())

        for layer in self.layers[::-1]:
            for neuron in layer:
                neuron.backPropagate()

    def getResults(self):
        output=[]
        for neuron in self.layers[-1]:
            output.append(neuron.getOutput())
        return output

    def getThResults(self):
        output=[]
        for neuron in self.layers[-1]:
            o=neuron.getOutput()
            if o>0.5:
                o=1
            else:
                o=0
            output.append(o)
        return output

def main():
    topology=[2,3,2]
    net=Network(topology)
    Neuron.eta=0.09
    Neuron.alpha=0.015

    inputs=[[0,0],[0,1],[1,0],[1,1]]
    outputs=[[0,0],[1,1],[1,0],[0,1]]



    while 1:
        error=0
        for i in range(len(inputs)):
            net.setInputs(inputs[i])
            net.feedForward()
            net.backPropagate(outputs[i])
            error=error+net.getError(outputs[i])

        print("error: ",error)
        if error<0.01:
            break

main()