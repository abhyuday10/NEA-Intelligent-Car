"""This is the Machine Learning controller module which is responsible for managing the entire training process.
Uses the functions from the genetic algorithm module for training new generations and uses the environment module for evaluating their performance.
This is essentially an extended application of the genetic algorithm"""

import environment as env
import genetic_algorithm as ga
import matplotlib.pyplot as plt  # For graphing the data
import constants


# Set all members' fitness to 0
def reset_fittest(population):
    for solution in population:
        solution.fittest = False
    return population


def main():
    # Setup Graphing variables
    generation_fitnesses = []  # To store average fitness for each generation (y coordinate)
    figure = plt.figure(figsize=(6, 3))
    fitness_graph = figure.add_subplot(1, 1, 1)
    fitness_graph.set_xlabel("Generation")  # X axis label
    fitness_graph.set_ylabel("Fitness")  # Y axis label

    # Generate Population and set up simulation
    population = ga.generate_population(constants.POOL_SIZE, constants.TOPOLOGY)
    print("Initial population generated")

    # Display generated population
    population[0].brain.print_network_structure()
    for i in population:
        i.brain.print_network_weights()

    generation = 0  # Stores the current generation of the training process
    solution_found = False  # Whether the minimum criteria for the solution met
    print("Solution not found in initial population...Continuing evaluation")

    while not solution_found:
        # Repeat evaluation and training process until suitable solution found

        # Evaluate population fitness
        print("Evaluating current population...")
        env.Environment(population, generation)

        # Find best Code and show info
        solution = population[0]
        for solution in population:
            if solution.fitness > solution.fitness:
                solution = solution

        # Mark solution as fittest in population
        solution.fittest = True
        print("Best solution located and marked at: ", hex(id(solution)))

        # Calculate average population fitness
        total_population_fitness = 0
        for i in population:
            total_population_fitness += i.fitness
        avg_fitness = total_population_fitness / len(population)

        # Visualization
        generation_fitnesses.append(avg_fitness)
        x = [i for i in range(0, len(generation_fitnesses))]  # Generation number
        y = generation_fitnesses  # Average fitness achieved on this generation

        fitness_graph.clear()
        fitness_graph.set_xlabel("Generation")
        fitness_graph.set_ylabel("Average Fitness")
        fitness_graph.plot(x, y)
        plt.pause(0.1)  # Required for rendering

        # Display current generation info
        print("")
        print("Generation: ", generation)
        print("Average generation fitness: ", avg_fitness)
        print('Target Number: ' + str(constants.TARGET_TIME))
        print("Best Code fitness = ", solution.time)
        print("")

        # Stop simulation if minimum criteria met
        if solution.time >= constants.TARGET_TIME:
            solution_found = True
            print("Minimum search criteria met, terminating simulation...")
        else:
            print("Solution criteria not met, producing new population...")

        # Generate new generation
        new_population = []  # Stores members of the next generation
        while len(new_population) < constants.POOL_SIZE:  # Keeps producing children until required population size met

            # Choose two parents
            parent1 = ga.choose_parent(population)
            parent2 = ga.choose_parent(population)

            #  Create and add one child to next population
            childs = ga.produce_child_solution(parent1, parent2)
            for child in childs:
                if child not in population:  # Prevent identical children if crossover doesn't occur
                    child = ga.mutate(child)  # Apply mutation
                    new_population.append(child)

        # Add best solution from last iteration
        new_population.append(solution)
        population = new_population
        generation += 1


print("")
if __name__ == '__main__':
    main()
