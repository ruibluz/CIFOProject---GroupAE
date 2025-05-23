# algorithm.py
import random
from copy import deepcopy
from solutions.GASolution import GASolution
from utils.Classes import LeagueIndividual

# === POPULATION GENERATION ===
def generate_initial_population(size, players_by_position, team_structure, budget_limit, num_teams):
    population = []
    attempts = 0
    max_attempts = 1000

    while len(population) < size and attempts < max_attempts:
        indiv = LeagueIndividual(players_by_position, team_structure, budget_limit, num_teams)
        if indiv.league is not None:
            population.append(GASolution(indiv))
        attempts += 1

    return population

# === MAIN GA FUNCTION ===
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
    population = generate_initial_population(
        population_size, players_by_position, team_structure, budget_limit, num_teams
    )

    for generation in range(generations):
        fitnesses = [ind.fitness() for ind in population]

        if elitism:
            best_individual = min(population, key=lambda x: x.fitness())

        new_population = []

        while len(new_population) < population_size:
            # === SELECTION ===
            if selection_fn.__name__ == "sel_tournament":
                parents = selection_fn(population, fitnesses, k=k_tournament, num=2)
            else:
                parents = selection_fn(population, fitnesses, num=2)

            parent1, parent2 = parents

            # === CROSSOVER OR COPY ===
            if random.random() < xo_prob:
                try:
                    child1, child2 = parent1.crossover(parent2, crossover_fn)
                except:
                    continue
            else:
                child1, child2 = deepcopy(parent1), deepcopy(parent2)

            # === MUTATION ===
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
