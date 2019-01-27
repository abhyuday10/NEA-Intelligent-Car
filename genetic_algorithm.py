"""This module contains all the genetic operator functions used for training and production of new generations."""

import random

import neural_net as nn
import constants


class Code:
    """Code class to manage all data for one entity.
    This unique code is what represents a solution."""

    def __init__(self, topology):
        self.topology = topology

        # A brain is the neural network specifically created from this code.
        self.brain = nn.Network(topology)

        # Weights of neural network stored here so it can be easily modified for training
        self.weights = self.brain.get_network_weights()

        # Fitness: calculated value representing how well this solution performs
        self.fitness = None
        # Time: Time spent in environment without crashing; used to calculate fitness.
        self.time = 0

        # Bool to store whether this solution is the best of their generation
        self.fittest = False

    def set_weights(self, weights):
        """Setter function to set weights of the neural network"""
        self.brain.set_network_weights(weights)
        self.weights = weights


def generate_population(pool_size, topology):
    """Function to generate population of random members"""
    pool = []
    for solution in range(pool_size):
        member = Code(topology)
        pool.append(member)
    return pool


def produce_child_solution(first, second):
    """Crossover to create one child base on probability."""
    if random.uniform(0, 1) <= constants.CROSSOVER_RATE:
        # Only creates child if required probability met.

        # Determines random point in the list of weights to cross the data between parents (refer to design section).
        crossover = random.randrange(0, len(first.weights))

        # Child created has same network structure
        topology = first.topology

        # Function create to child code by crossing weights of parents from the point previously determined
        offspring_weights = first.weights[0: crossover] + second.weights[crossover:]

        # Code object created from newly created weights
        child = Code(topology)
        child.set_weights(offspring_weights)

        return [child]
    else:
        return [first, second]


def mutate(solution):
    """Mutation of one solution to give random features"""
    weights = solution.weights

    for i in range(0, len(weights) - 1):
        # Scales some of the weights based on probability specified
        if random.uniform(0, 1) <= constants.MUTATION_RATE:
            weights[i] = weights[i] * random.uniform(0.5, 1.5)
    solution.set_weights(weights)  # Updates the weights of the solution

    return solution


def choose_parent(population):
    """Roulette parent selection
    algorithm to choose an individual from population with members with higher fitness
    having a greater probability of being selected."""
    population_fitness = 0
    for i in population:
        population_fitness += i.fitness

    pie_size = population_fitness * random.uniform(0, 1)
    # Assigns a slice of radius proportional to members' fitness
    # Random value determined in pie
    # Member with landing slice is selected
    fitness = 0
    for i in population:
        fitness += i.fitness
        if fitness >= pie_size:
            return i
