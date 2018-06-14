import random

import neural_net as nn


class Chromosome():
    def __init__(self):
        self.brain = nn.Network(NETWORK_STRUCTURE)
        self.weights = self.brain.getNetWeights()


def generate_population(POOL_SIZE,):
    pool = []
    for chrom in range(POOL_SIZE):


    return pool


def breed_two_chromosomes(first, second):
    if random.uniform(0, 1) <= CROSSOVER_RATE:
        crossover = random.randrange(0, len(first.code))
        # print("Original: ",first.code)
        offspring1 = Chromosome(genes=None, code=(first.code[0: crossover] + second.code[crossover:]))
        # print("Final:    ",offspring1.code)
        return [offspring1]
    else:
        return [first, second]


def mutate(chromosome):
    chromoList = list(chromosome.code)
    for i in range(0, len(chromoList)):
        if random.uniform(0, 1) <= MUTATION_RATE:
            cellIndex = random.randint(0, len(chromoList) - 1)
            if chromoList[cellIndex] == "0":
                chromoList[cellIndex] = "1"
            elif chromoList[cellIndex] == "1":
                chromoList[cellIndex] = "0"
    chromosome.code = "".join(chromoList)
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
