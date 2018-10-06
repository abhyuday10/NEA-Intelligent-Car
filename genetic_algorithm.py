import random

import neural_net as nn

CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.05


# Chromosome class to manage all data for one entity
class Chromosome:
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
    for chrom in range(pool_size):
        member = Chromosome(topology)
        pool.append(member)
    return pool


# Crossover to create one child base on probability
def breed_two_chromosomes(first, second):
    if random.uniform(0, 1) <= CROSSOVER_RATE:
        crossover = random.randrange(0, len(first.weights))
        topology = first.topology
        offspring_weights = first.weights[0: crossover] + second.weights[crossover:]

        offspring = Chromosome(topology)
        offspring.set_weights(offspring_weights)

        return [offspring]
    else:
        return [first, second]


# Mutation of one chromosome to give random features
def mutate(chromosome):
    weights = chromosome.weights
    for i in range(0, len(weights) - 1):
        if random.uniform(0, 1) <= MUTATION_RATE:
            weights[i] = weights[i] * random.uniform(0.5, 1.5)
    chromosome.set_weights(weights)
    return chromosome


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


print("___Parents___")
Chromosome1 = Chromosome(topology=[5, 3, 2])
Chromosome2 = Chromosome(topology=[5, 3, 2])

Chromosome1.brain.print_network_weights()
Chromosome2.brain.print_network_weights()


print("___Child___")
childs = breed_two_chromosomes(Chromosome1, Chromosome2)
for child in childs:
    child.brain.print_network_weights()

print("___Mutated Child___")
for child in childs:
    mutated_child = mutate(child)
    child.brain.print_network_weights()



