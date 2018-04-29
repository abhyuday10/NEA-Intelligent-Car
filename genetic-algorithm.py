import random
import time

CODE_TABLE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/']
CHROMOSOME_LENGTH = 40
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.001
POOL_SIZE = 400
TARGET = 3866


class Chromosome():
    def __init__(self, genes, code=""):
        self.code = code
        self.fitness = None
        self.formula = None
        self.result = None
        if genes is not None:
            for gene in genes:
                self.code += str(gene)

        self.set_self_formula()
        self.set_self_result()

    def set_self_formula(self):
        split_length = len(self.code) // CHROMOSOME_LENGTH
        split_binary = [self.code[i:i + split_length] for i in range(0, len(self.code), split_length)]
        equation = ""
        for item in split_binary:
            try:
                equation += parse_to_chr(item)
            except:
                continue

        operand = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        operator = ['+', '-', '*', '/']
        new_equation = ""
        nextType = operand

        for index in range(len(equation)):
            if equation[index] in nextType:
                new_equation += equation[index]
                if nextType == operand:
                    nextType = operator
                elif nextType == operator:
                    nextType = operand
        if new_equation[-1:] in operator:
            self.formula = new_equation[:-1]
        elif len(new_equation) == 0:
            self.formula = None
        else:
            self.formula = new_equation

    def set_self_result(self):
        # last_valid_character = ''
        # result = 0
        # formula = ''
        #
        # old_formula = self.formula
        # old_formula = list(old_formula)
        # new_formula = []
        # for thing in old_formula:
        #     if is_integer(thing):
        #         new_formula.append(int(thing))
        #     else:
        #         new_formula.append(thing)
        #
        # for i in new_formula:
        #     if last_valid_character == '' and is_integer(i):
        #         last_valid_character = i
        #         formula = formula + str(i)
        #         result = i
        #     elif last_valid_character == '' and not is_integer(i):
        #         continue
        #     else:
        #         if not is_integer(last_valid_character) and is_integer(i):
        #             if last_valid_character == '+':
        #                 result += i
        #             elif last_valid_character == '-':
        #                 result -= i
        #             elif last_valid_character == '*':
        #                 result *= i
        #             elif last_valid_character == '/':
        #                 if i == 0:
        #                     continue
        #                 result /= i
        #             last_valid_character = i
        #             formula = formula + str(i)
        #         elif is_integer(last_valid_character) and not is_integer(i):
        #             last_valid_character = i
        #             formula = formula + str(i)
        #
        # self.result = result

        if self.formula is not None:
            try:
                self.result = eval(self.formula)
            except Exception as e:
                # print("removing due to: ",e)
                self.result = None

    def set_self_fitness(self):
        if TARGET == self.result:
            self.fitness = 9999
        elif self.result is None:
            self.fitness = 0
        else:
            self.fitness = 1 / abs(TARGET - self.result)


def is_integer(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


def parse_to_chr(binarycharacter):
    if binarycharacter == "1110" or binarycharacter == "1111":
        return None
    return CODE_TABLE[int(binarycharacter, 2)]


def parse_to_binary(stringchr):
    return str(bin(CODE_TABLE.index(stringchr))[2:].zfill(4))


def generate_population():
    pool = []
    for chrom in range(POOL_SIZE):
        genes = []
        for gene in range(CHROMOSOME_LENGTH):
            genes.append(parse_to_binary(random.choice(CODE_TABLE)))
        pool.append(Chromosome(genes))
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


        # firstList = list(first.code)
        # secondList = list(second.code)
        #
        # # Cross DNA based on probability
        # if random.uniform(0, 1) <= crossRate:
        #     point = random.randint(0, len(firstList) - 1)
        #     for i in range(point, len(firstList)):
        #         tmp = firstList[i]
        #         firstList[i] = secondList[i]
        #         secondList[i] = tmp
        #
        # first.code = "".join(firstList)
        # second.code = "".join(secondList)


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


def main():
    # Generate Population
    population = generate_population()

    # Check for solution
    generation = 0
    solution_found = False

    while (not solution_found):
        # Test Population: formula, result, fitness
        for chromosome in population:
            chromosome.set_self_formula()
            chromosome.set_self_result()
            chromosome.set_self_fitness()
            # print(chromosome.result)

            # Kill weaklings?
        # for i in range(0,len(population)-2,-1):
        #     if population[i].result==None or population[i].formula==None:
        #         population.remove(population[i])

        # Find best Chromosome and show info
        bestChromosome = population[0]
        for chromosome in population:
            if chromosome.fitness > bestChromosome.fitness:
                bestChromosome = chromosome


        # TODO: Calculate and display normalised generation fitness
        total_population_fitness = 0
        for i in population:
            total_population_fitness += i.fitness
        avg_fitness=total_population_fitness/len(population)

        print("Generation: ", generation)
        print("Average generation fitness: ", avg_fitness)
        print('Target Number: ' + str(TARGET))
        print("Best Chromosome: ", bestChromosome.formula, " = ", bestChromosome.result)
        print("")



        if bestChromosome.result == TARGET:
            solution_found = True
            print("SUCCESS!!")

        # Breed new generation
        new_population = []
        while len(new_population)<POOL_SIZE:

            parent1 = choose_parent(population)
            parent2 = choose_parent(population)

            while parent2.result == parent1.result:
                parent2 = choose_parent(population)

            # print("parent1: ",parent1.result)
            # print("parent2: ",parent2.result)

            childs = breed_two_chromosomes(parent1, parent2)
            for child in childs:
                child=mutate(child)
                new_population.append(child)



        # print([thing.result for thing in population])

        population = new_population
        # random.shuffle(population)
        generation += 1
        # time.sleep(1.5)


main()

