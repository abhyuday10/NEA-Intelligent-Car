"""Neural network module which can function individually from the other modules. The unique structure of a neural
network represents one solution in the search space containing the ideal solution. This class is used by the environment
 to  create a 'brain'  for each car"""

import math
import random


class Connection:
    """Connection class to store connections between nodes in the network"""

    def __init__(self, connected_node):
        self.connected_node = connected_node  # Node on the previous layer
        self.weight = random.normalvariate(0, 1)  # Generating random weight from gaussian distribution (mu=0, sigma=1)


class Node:
    """Node class for network. These are connected to each other through the connection class."""

    def __init__(self, prev_layer):
        self.connections = []  # Store all connection objects to previous layer
        self.output = 0.0  # Default output value

        # No connections if this is the first layer
        if prev_layer is None:
            pass
        else:
            for node in prev_layer:
                # Otherwise connect to each node of previous layer
                connection = Connection(node)
                self.connections.append(connection)

    def feed_forward(self):
        """Propagate network through network to produce output"""
        sum_output = 0
        if len(self.connections) == 0:
            return
        for connection in self.connections:
            sum_output += (connection.connected_node.get_output() * connection.weight)  # Values scaled by weight.
        self.output = self.sigmoid(sum_output)  # Flattens output between -1 and 1.

    @staticmethod
    def sigmoid(x):
        """Simple static function to flatten input between -1 and 1"""
        return 1 / (1 + math.exp(-x * 1.0))

    def set_output(self, output):
        """Sets the output of this node; required to set the values of the input layer"""
        self.output = output

    def get_output(self):
        """Returns the output value stored in this node"""
        return self.output


class Network:
    """ Network to act as 'brain' for each car. Created from the nodes and connections previously defined.
     Requires a parameter, topology; a list which specifies the number of nodes on each layer.
     eg. [2,3,1] creates a network with input layer of 2, hidden (middle) layer of 3 and 1 on the output layer."""

    def __init__(self, topology):
        """Creates the entire network of the defined structure with random weights and biases."""
        self.layers = []
        self.topology = topology
        layer_number = 0

        for layerNum in range(len(topology)):
            # Iterate through each layer in network, creating nodes and connections as required
            layer_number += 1
            layer = []
            for i in range(topology[layerNum]):
                # Iterate through each node on this layer
                if len(self.layers) == 0:
                    # Create a null node (node with no connections to previous layer) if this is the first layer
                    layer.append(Node(None))
                else:
                    # Otherwise connect this node to each node on previous layer
                    layer.append(Node(self.layers[-1]))

            if not layer_number >= len(topology):
                # Create a bias node on every layer except the last
                layer.append(Node(None))  # bias node
                layer[-1].set_output(1)  # setting output of bias node as 1

            self.layers.append(layer)
            # Add layer to list of all the layers of the network

    def print_network_structure(self):
        """Function to output the topology eg. [2,3,1] including the bias nodes for debugging purposes."""
        structure = []
        for layer in self.layers:
            structure.append(len(layer))
        print("Initiated Neural network with structure: ", structure)

    def print_network_weights(self):
        """Function to output the values of each connection in network for debugging purposes."""
        for layerI in range(len(self.layers)):
            layer = []
            for node in self.layers[layerI]:
                for connection in node.connections:
                    layer.append(connection.weight)
            print("Layer ", layerI, ":  ", layer)
        print("")

    def get_network_weights(self):
        """Returns the weights of the network in a specific order.
        Required when creating child networks from current one."""
        layers = []
        for layer in self.layers:
            for node in layer:
                for connection in node.connections:
                    layers.append(connection.weight)
        return layers

    def set_network_weights(self, weights):
        """Sets the weights of this network to the ones provided in the list.
        Required for setting weights of child network.
        Order of weights same as outputted by the function get_network_weights()"""

        i = 0
        for layer in self.layers:
            for node in layer:
                for connection in node.connections:
                    if i > len(weights) - 1:
                        return
                    connection.weight = weights[i]
                    i += 1

    def set_inputs(self, inputs):
        """Sets the values of the nodes on the input layer to the ones in the list provided"""
        for i in range(len(inputs)):
            self.layers[0][i].set_output(inputs[i])

    def feed_forward(self):
        """Propagates values through node"""
        for layer in self.layers[1:]:
            for node in layer:
                node.feed_forward()

    def get_results(self):
        """Returns output value from the output layer"""
        output = []
        for node in self.layers[-1]:
            output.append(node.get_output())
        return output

    def get_decision(self):
        """Generates decision from value returned from the function get_results()"""
        if self.layers[-1][0].get_output() > self.layers[-1][1].get_output():
            return "left"
        elif self.layers[-1][0].get_output() < self.layers[-1][1].get_output():
            return "right"
