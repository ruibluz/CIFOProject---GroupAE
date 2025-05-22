import random

# Fitness proportional selection (roulette wheel)
def sel_roulette(population, fitness, num=1):
    """
    Selects individuals from the population based on their fitness using roulette wheel selection.
    Args:
        population (list): The population of individuals.
        fitness (list): The fitness values of the individuals in the population.
        num (int): The number of individuals to select.
    """

    # P("Selecting individual i") = fitness(i) / sum(fitness(j) for j in population) -> Maximization
    # 1/P("Selecting individual i") -> Minimization

    sum_fit = sum(fitness)
    prob = []
    for i in range(len(population)):
        prob.append(1/(fitness[i] / sum_fit))
    selected = random.choices(population, weights=prob, k=num)
    
    return selected

# Ranking selection
def sel_rank(population, fitness, num=1):
    """
    Selects individuals from the population based on their rank in fitness.
    Args:
        population (list): The population of individuals.
        fitness (list): The fitness values of the individuals in the population.
        num (int): The number of individuals to select.
    """
    # Sort the population by fitness
    sorted_pop = sorted(zip(population, fitness), key=lambda x: x[1], reverse=True) # Starts on Rank 1 for the worst fitness, and goes up to Rank n for the best fitness
    sum_rank = sum(range(1, len(sorted_pop) + 1)) # Sum of ranking indexes
    prob = []
    for i in range(len(sorted_pop)):
        prob.append((i + 1) / sum_rank)
    selected = random.choices([x[0] for x in sorted_pop], weights=prob, k=num)

    return selected

# Tournament selection
def sel_tournament(population, fitness, k, num=1):
    """
    Selects individuals from the population using tournament selection.
    Args:
        population (list): The population of individuals.
        fitness (list): The fitness values of the individuals in the population.
        k (int): The number of individuals in each tournament, this is, tournament size.
        num (int): The number of individuals to select.
    """
    selected = []
    
    for n in range(num):
        # Randomly select k individuals from the population
        tournament = random.sample(list(zip(population, fitness)), k)
        tournament.sort(key=lambda x: x[1])
        # Select the best individual from the tournament
        best_individual = tournament[0]
        selected.append(best_individual[0])

    return selected