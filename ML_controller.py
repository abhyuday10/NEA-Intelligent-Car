import environment as env
import genetic_algorithm as ga
import matplotlib.pyplot as plt
import constants


# Set all members' fitness to 0
def reset_fittest(population):
    for solution in population:
        solution.fittest = False
    return population


# Main loop
def main():
    # Setup Graphing variables
    generation_fitnesses = []
    figure = plt.figure(figsize=(6, 3))
    fitnessGraph = figure.add_subplot(1, 1, 1)
    fitnessGraph.set_xlabel("Generation")
    fitnessGraph.set_ylabel("Fitness")

    # Generate Population and set up simulation
    population = ga.generate_population(constants.POOL_SIZE, constants.TOPOLOGY)
    print("Initial population generated")

    # Display generated population
    population[0].brain.print_network_structure()
    for i in population:
        i.brain.print_network_weights()

    generation = 0
    solution_found = False
    print("Solution not found in initial population...Continuing evaluation")
    while not solution_found:

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
        x = [i for i in range(0, len(generation_fitnesses))]
        y = generation_fitnesses

        fitnessGraph.clear()
        fitnessGraph.set_xlabel("Generation")
        fitnessGraph.set_ylabel("Average Fitness")
        fitnessGraph.plot(x, y)
        plt.pause(0.1)

        # Display current iteration info
        print("")
        print("Generation: ", generation)
        print("Average generation fitness: ", avg_fitness)
        print('Target Number: ' + str(constants.TARGET_TIME))
        print("Best Code fitness = ", solution.time)
        print("")

        # Stop simulation if minumum criteria met
        if solution.time >= constants.TARGET_TIME:
            solution_found = True
            print("Minimum search criteria met, terminating instance...")
        else:
            print("Solution criteria not met, producing new population")

        # Generate new generation
        # Choose 2 parents and create and add one child to next population
        new_population = []
        while len(new_population) < constants.POOL_SIZE:

            parent1 = ga.choose_parent(population)
            parent2 = ga.choose_parent(population)

            childs = ga.produce_child_solution(parent1, parent2)
            for child in childs:
                if child not in population:
                    child = ga.mutate(child)
                    new_population.append(child)

        # Add best solution from last iteration
        new_population.append(solution)
        population = new_population
        generation += 1


print("")
if __name__ == '__main__':
    main()
