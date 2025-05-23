# algorithm.py
import random
from copy import deepcopy
from solutions.GASolution import GASolution
from utils.Classes import LeagueIndividual

# POPULATION GENERATION
def generate_initial_population(size, players_by_position, team_structure, budget_limit, num_teams):

    """
    Generate a random initial population of LeagueIndividuals.
    Each individual is a LeagueIndividual object that represents a league of teams.

    Args:
        size (int): The number of individuals to generate.
        players_by_position (dict): A dictionary where keys are positions and values are lists of Player objects.
        team_structure (dict): A dictionary defining the structure of each team (e.g., number of players per position).
        budget_limit (float): The budget limit for the league.
        num_teams (int): The number of teams in the league.
    """

    population = []
    attempts = 0
    max_attempts = 1000 # avoid infinite loop if unable to generate valid leagues

    while len(population) < size and attempts < max_attempts:
        indiv = LeagueIndividual(players_by_position, team_structure, budget_limit, num_teams)
        if indiv.league is not None: # proceed if the league is valid
            population.append(GASolution(indiv))
        attempts += 1

    return population

# MAIN GENETIC ALGORITHM FUNCTION
def genetic_algorithm(
    players_by_position, 
    team_structure, 
    budget_limit,   
    num_teams,     
    population_size, 
    generations,   
    selection_fn,   
    crossover_fn, 
    mutation_fn, 
    mutation_rate=0.2, 
    xo_prob=0.9, 
    elitism=True, 
    k_tournament=None, 
    verbose=True 
):
    
    """
    Executes a genetic algorithm to optimize a population of possible solutions.

    Args:
        players_by_position (dict): A dictionary where keys are positions and values are lists of Player objects.
        team_structure (dict): A dictionary defining the structure of each team.
        budget_limit (float): The budget limit for the league.
        num_teams (int): The number of teams in the league.
        population_size (int): list of individuals (randomly generated solutions).
        generations (int): The number of generations to evolve.
        selection_fn (Callable): Function used for selecting individuals.
        crossover_fn (Callable): Function used for crossover between two parents.
        mutation_fn (Callable): Function used for mutating an individual.
        mutation_rate (float, optional): Probability of applying mutation. Defaults to 0.2.
        xo_prob (float, optional): Probability of applying crossover. Defaults to 0.9.
        elitism (bool, optional): If True, carries the best individual to the next generation. Defaults to True.
        k_tournament (int, optional): Number of individuals to select in the tournament selection. Defaults to None.
        verbose (bool, optional): If True, prints detailed logs for debugging. Defaults to True.

    Returns:
        LeagueIndividual: The best individual found after the specified number of generations.
    """

    # Generate the initial population
    population = generate_initial_population(
        population_size, players_by_position, team_structure, budget_limit, num_teams
    )

    for generation in range(generations):
        fitnesses = [ind.fitness() for ind in population] # get fitness of each individual

        # get the best individual of the current generation
        if elitism:
            best_individual = min(population, key=lambda x: x.fitness())

        new_population = []

        while len(new_population) < population_size:
            # check if the selection function is tournament selection
            if selection_fn.__name__ == "sel_tournament":
                parents = selection_fn(population, fitnesses, k=k_tournament, num=2)
            else: # otherwise use the default selection function
                parents = selection_fn(population, fitnesses, num=2)

            parent1, parent2 = parents

            # crossover parents to create children
            if random.random() < xo_prob:
                try:
                    child1, child2 = parent1.crossover(parent2, crossover_fn)
                except:
                    continue
            else:
                child1, child2 = deepcopy(parent1), deepcopy(parent2)

            # mutate children (offspring)
            if random.random() < mutation_rate:
                try:
                    child1 = child1.mutate(mutation_fn)
                except:
                    pass

            if random.random() < mutation_rate:
                try:
                    child2 = child2.mutate(mutation_fn)
                except:
                    pass

            new_population.extend([child1, child2])

        if elitism:
            worst_idx = max(range(len(new_population)), key=lambda i: new_population[i].fitness())
            new_population[worst_idx] = best_individual

        population = new_population[:population_size]

        if verbose:
            best_fitness = min(ind.fitness() for ind in population)
            avg_fitness = sum(ind.fitness() for ind in population) / len(population)
            print(f"Generation {generation+1:03d} | Best: {best_fitness:.4f} | Avg: {avg_fitness:.4f}")

    best = min(population, key=lambda x: x.fitness())
    return best
