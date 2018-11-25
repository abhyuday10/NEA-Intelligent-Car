import random

import neural_net as nn
import constants



# Code class to manage all data for one entity
class Code:
    def __init__(self, topology):
        self.topology = topology
        self.brain = nn.Network(topology)
        self.weights = self.brain.get_network_weights()
        self.fitness = None
        self.time = 0

        self.fittest = False

    def set_weights(self, weights):
        self.brain.set_network_weights(weights)
        self.weights = weights


# Function to generate population of random members
def generate_population(pool_size, topology):
    pool = []
    for solution in range(pool_size):
        member = Code(topology)
        pool.append(member)
    return pool


# Crossover to create one child base on probability
def produce_child_solution(first, second):
    if random.uniform(0, 1) <= constants.CROSSOVER_RATE:
        crossover = random.randrange(0, len(first.weights))
        topology = first.topology
        offspring_weights = first.weights[0: crossover] + second.weights[crossover:]

        offspring = Code(topology)
        offspring.set_weights(offspring_weights)

        return [offspring]
    else:
        return [first, second]


# Mutation of one solution to give random features
def mutate(solution):
    weights = solution.weights
    for i in range(0, len(weights) - 1):
        if random.uniform(0, 1) <= constants.MUTATION_RATE:
            weights[i] = weights[i] * random.uniform(0.5, 1.5)
    solution.set_weights(weights)
    return solution


# Roulette parent selection
def choose_parent(population):
    population_fitness = 0
    for i in population:
        population_fitness += i.fitness

    pie_size = population_fitness * random.uniform(0, 1)
    fitness = 0
    for i in population:
        fitness += i.fitness
        if fitness >= pie_size:
            return i




