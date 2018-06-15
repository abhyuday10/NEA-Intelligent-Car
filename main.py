'''GENETIC CONTROLLER'''
import genetic_algorithm as ga
import game_model as game
import neural_net as nn



POOL_SIZE = 400
TARGET_TIME = 60
TOPOLOGY=[5,2,1]


def main():
    # Generate Population
    population = ga.generate_population(TOPOLOGY)

    # Check for solution
    generation = 0
    solution_found = False

    while (not solution_found):
        # Evaluate population fitness
        for chromosome in population:


        # Find best Chromosome and show info
        bestChromosome = population[0]
        for chromosome in population:
            if chromosome.fitness > bestChromosome.fitness:
                bestChromosome = chromosome

        # TODO: Calculate and display normalised generation fitness
        total_population_fitness = 0
        for i in population:
            total_population_fitness += i.fitness
        avg_fitness = total_population_fitness / len(population)

        print("Generation: ", generation)
        print("Average generation fitness: ", avg_fitness)
        print('Target Number: ' + str(TARGET_TIME))
        print("Best Chromosome: ", bestChromosome.formula, " = ", bestChromosome.time)
        print("")

        if bestChromosome.time >= TARGET_TIME:
            solution_found = True
            print("SUCCESS!!")

        # Breed new generation
        new_population = []
        while len(new_population) < POOL_SIZE:

            parent1 = ga.choose_parent(population)
            parent2 = ga.choose_parent(population)

            while parent2.time == parent1.time:
                parent2 = ga.choose_parent(population)

            childs = ga.breed_two_chromosomes(parent1, parent2)
            for child in childs:
                child = ga.mutate(child)
                new_population.append(child)

        population = new_population
        generation += 1


if __name__ == '__main__':
    main()
