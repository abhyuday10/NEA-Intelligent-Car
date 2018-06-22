import random

import neural_net as nn

CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.01


class Chromosome():
    def __init__(self, topology):
        self.topology = topology
        self.brain = nn.Network(topology)
        self.weights = self.brain.getNetWeights()
        self.fitness = None
        self.time = 0

    def setWeights(self, weights):
        self.brain.setNetWeights(weights)
        self.weights = weights


def generate_population(POOL_SIZE, topology):
    pool = []
    for chrom in range(POOL_SIZE):
        member = Chromosome(topology)
        pool.append(member)
    return pool


def breed_two_chromosomes(first, second):
    if random.uniform(0, 1) <= CROSSOVER_RATE:
        crossover = random.randrange(0, len(first.weights))
        topology = first.topology
        offspringWeights = first.weights[0: crossover] + second.weights[crossover:]

        offspring = Chromosome(topology)
        offspring.setWeights(offspringWeights)

        return [offspring]
    else:
        return [first, second]


def mutate(chromosome):
    weights = chromosome.weights
    for i in range(0, len(weights) - 1):
        if random.uniform(0, 1) <= MUTATION_RATE:
            weights[i] = weights[i] * random.uniform(0.5, 1.5)
    chromosome.setWeights(weights)
    return chromosome


def choose_parent(population):
    population_fitness = 0
    for i in population:
        population_fitness += i.fitness

    pie_size = population_fitness * random.uniform(0, 1)
    fitness = 0
    for i in population:
        fitness += i.fitness
        if fitness >= pie_size:
            # print("Selected: ",i.result)
            return i
