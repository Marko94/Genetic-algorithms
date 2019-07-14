import random
import time
import sys

from operator import itemgetter


NUMBER_COUNT = 7
NOTE_LENGTH = 40
MUTATION_PROBABILITY = 0.9
POPULATION = 50
MAX_STAGNATION = 20
BEST = []
CLOSEST = 0
MIN_DELTA = 4124125


def read_from_file():
    file = open('ulaz.txt', 'r')
    a = file.readlines()
    inputs = []
    for _ in range(NUMBER_COUNT):
        inputs.append(int(a[_]))
    print(inputs)
    return inputs


def generate_chromosome():
    num_copy = numbers.copy()
    chrom = ''

    n = random.randint(0, len(num_copy) - 1)
    chrom += str(num_copy[n])
    num_copy.pop(n)
    chrom += ' '
    n = random.randint(0, len(num_copy) - 1)
    chrom += str(num_copy[n])
    num_copy.pop(n)
    chrom += ' '
    operators = 0
    operands = 2

    iterations = random.randint(0, 4)

    while iterations > 0:
        if operators < operands - 1:
            n = random.randint(0, 99)
            if n < 50:
                n = random.randint(0, len(num_copy) - 1)
                chrom += str(num_copy[n])
                num_copy.pop(n)
                operands += 1
                iterations -= 1
                chrom += ' '
            else:
                n = random.randint(0, 3)
                if n == 0:
                    chrom += '+'
                if n == 1:
                    chrom += '-'
                if n == 2:
                    chrom += '*'
                if n == 3:
                    chrom += '/'
                operators += 1
                chrom += ' '
        else :
            n = random.randint(0, len(num_copy) - 1)
            chrom += str(num_copy[n])
            num_copy.pop(n)
            operands += 1
            iterations -= 1
            chrom += ' '

    for _ in range(0, operands-1 - operators):
        n = random.randint(0, 3)
        if n == 0:
            chrom += '+'
        if n == 1:
            chrom += '-'
        if n == 2:
            chrom += '*'
        if n == 3:
            chrom += '/'
        chrom += ' '

    return chrom


def generate_population():
    gen_pop = []
    for _ in range(POPULATION):
        gen_pop.append(generate_chromosome())
    return gen_pop


def postfix_evaluation(s):
    s = s.split()
    n = len(s)
    stack = []
    for i in range(n):
        if s[i].isdigit():
            stack.append(int(s[i]))
        elif s[i] == "+":
            a = stack.pop()
            b = stack.pop()
            stack.append(float(a)+float(b))
        elif s[i] == "*":
            a = stack.pop()
            b = stack.pop()
            stack.append(float(a)*float(b))
        elif s[i] == "/":
            a = stack.pop()
            b = stack.pop()
            if float(a) == 0:
                stack.append(sys.maxsize)
            else:
                stack.append(float(b)/float(a))
        elif s[i] == "-":
            a = stack.pop()
            b = stack.pop()
            stack.append(float(b)-float(a))
    return stack.pop()


def genetic_algorithm(pop_expressions):
    closest = 23124124
    start_time = time.time()

    def cost_function(chromosome):
        result = float(postfix_evaluation(chromosome))
        global CLOSEST
        global MIN_DELTA
        global BEST
        delta = abs(result - target)
        if MIN_DELTA > delta:
            MIN_DELTA = delta
            CLOSEST = result
            BEST = chromosome
        return delta

    def tournament_selection(temp_pop):
        while True:
            a = random.choice(temp_pop)
            b = random.choice(temp_pop)
            c = random.choice(temp_pop)
            yield sorted([a, b, c], key=itemgetter(1))[0]

    def mate(chromosome1, chromosome2):
        s = chromosome1.split()
        d = chromosome2.split()
        mated = False
        while not mated:
            g = random.randint(0, len(s)-1)
            h = random.randint(0, len(d)-1)
            if s[g].isdigit() and d[h].isdigit():
                if d[h] not in s and s[g] not in d:
                    temp = s[g]
                    s[g] = d[h]
                    d[h] = temp
                    mated = True
            else:
                if not s[g].isdigit() and not d[h].isdigit():
                    temp = s[g]
                    s[g] = d[h]
                    d[h] = temp
                    mated = True

        temp_child = ' '.join(s)

        return temp_child

    def mutate(chromosome):
        temp_chromosome = chromosome.split()
        mutated = False
        while not mutated:
            w = random.randint(0, len(temp_chromosome)-1)
            if temp_chromosome[w].isdigit():
                q = random.randint(0, len(numbers)-1)
                if numbers[q] not in temp_chromosome:
                    temp_chromosome[w] = numbers[q]
                    mutated = True
            else:
                r = random.randint(0, 3)
                if r == 0:
                    temp_chromosome[w] = '+'
                if r == 1:
                    temp_chromosome[w] = '-'
                if r == 2:
                    temp_chromosome[w] = '*'
                if r == 3:
                    temp_chromosome[w] = '/'
                mutated = True

    best_match = []

    pop = [(h, cost_function(h)) for h in pop_expressions]
    pop.sort(key=lambda v: v[1], reverse=False)
    best_match = pop[0][1]

    stagnating = 0
    generations = 0

    while best_match != 0.0:
        generations += 1
        pop = pop[:(POPULATION // 2)]
        if stagnating == MAX_STAGNATION and best_match != 0.0:
            stagnating = 0
            temporary = pop[0]
            new_pop_expressions = generate_population()
            pop = [(h, cost_function(h)) for h in new_pop_expressions]
            pop[0] = temporary
            pop.sort(key=lambda v: v[1], reverse=False)
            best_match = pop[0][1]

        while len(pop) < POPULATION:
            selection = tournament_selection(pop[:POPULATION // 2])
            parent1 = next(selection)
            parent2 = next(selection)
            while parent1 == parent2:
                parent2 = next(selection)
            child = mate(parent1[0], parent2[0])
            cost = cost_function(child)
            pair = (child, cost)
            if pair not in pop:
                pop.append(pair)

        for i in range(POPULATION):
            if random.random() < MUTATION_PROBABILITY:
                mutate(pop[i][0])
                pop[i] = (pop[i][0], cost_function(pop[i][0]))

        pop.sort(key=lambda v: v[1], reverse=False)
        end_time = time.time()
        print("[ " + str(format(end_time - start_time, '.2f')) + " seconds] : " + str(pop))

        if pop[0][1] == best_match:
            stagnating += 1
        else:
            stagnating = 0
            best_match = pop[0][1]

        if end_time - start_time > 60:
            break
    return best_match


if __name__ == '__main__':
    numbers = read_from_file()
    target = numbers[6]
    numbers.pop()
    print(target)
    population = generate_population()
    print(population)
    start_time = time.time()
    best = genetic_algorithm(population.copy())
    print("Trosak : " + str(best))
    end_time = time.time()
    print("[ " + str(format(end_time - start_time, '.2f')) + " seconds] : " + str(BEST) + ' = ' + str(CLOSEST))
    # print(postfix_evaluation("15 1 / 5 / 75 4 7 - - *"))
