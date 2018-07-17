"""GENETIC CONTROLLER"""

import environment as game
import genetic_algorithm as ga

POOL_SIZE = 20
TARGET_TIME = 5999
TOPOLOGY = [5, 3, 2]


def reset_fittest(population):
    for chrom in population:
        chrom.fittest = False
    return population


def main():
    # Generate Population
    population = ga.generate_population(POOL_SIZE, TOPOLOGY)

    # Check for solution
    generation = 0
    solution_found = False

    while not solution_found:
        # Evaluate population fitness
        gameState = game.Game(population, generation)

        # Find best Chromosome and show info
        best_chromosome = population[0]

        # for chromosome in population:
        #     print(chromosome.fitness)

        for chromosome in population:
            if chromosome.fitness > best_chromosome.fitness:
                best_chromosome = chromosome

        best_chromosome.fittest = True

        # TODO: Calculate and display normalised generation fitness using softmax
        total_population_fitness = 0
        for i in population:
            total_population_fitness += i.fitness
        avg_fitness = total_population_fitness / len(population)

        print("Generation: ", generation)
        print("Average generation fitness: ", avg_fitness)
        print('Target Number: ' + str(TARGET_TIME))
        print("Best Chromosome: ", best_chromosome, " = ", best_chromosome.time)
        print("")

        if best_chromosome.time >= TARGET_TIME:
            solution_found = True
            print("SUCCESS!!")
        else:
            print("Solution criteria not met, producing new population")

        # Breed new generation
        new_population = []
        while len(new_population) < POOL_SIZE:

            parent1 = ga.choose_parent(population)
            parent2 = ga.choose_parent(population)

            # while parent2.time == parent1.time:
            #     parent2 = ga.choose_parent(population)

            childs = ga.breed_two_chromosomes(parent1, parent2)
            for child in childs:
                if child not in population:
                    child = ga.mutate(child)
                    new_population.append(child)

        new_population.append(best_chromosome)
        population = new_population
        generation += 1


if __name__ == '__main__':
    main()
