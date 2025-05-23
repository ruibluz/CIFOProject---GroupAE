import time
import itertools
import numpy as np

from algorithms.GA_selection import sel_roulette, sel_rank, sel_tournament
from algorithms.GA_crossover import team_crossover, position_crossover
from algorithms.GA_mutation import mutation_swap_players, mutation_regenerate_team, mutation_balance_teams
from algorithms.algorithm import genetic_algorithm

selection_methods = [sel_roulette, sel_rank, sel_tournament]
crossover_methods = [team_crossover, position_crossover]
mutation_methods = [mutation_swap_players, mutation_regenerate_team, mutation_balance_teams]

def evaluate_all_combinations(players_by_position, team_structure, budget_limit, num_teams,
                               population_size=30, generations=50, runs_per_combo=3,
                               mutation_rate=0.2, xo_prob=0.9, elitism=True, k_tournament=3, verbose=False):

    results = []

    for sel, xo, mut in itertools.product(selection_methods, crossover_methods, mutation_methods):
        fitnesses = []
        start = time.time()
        for _ in range(runs_per_combo):
            best = genetic_algorithm(
                players_by_position=players_by_position,
                team_structure=team_structure,
                budget_limit=budget_limit,
                num_teams=num_teams,
                population_size=population_size,
                generations=generations,
                selection_fn=sel,
                crossover_fn=xo,
                mutation_fn=mut,
                mutation_rate=mutation_rate,
                xo_prob=xo_prob,
                elitism=elitism,
                k_tournament=k_tournament,
                verbose=verbose
            )
            fitnesses.append(best.fitness())

        end = time.time()
        results.append({
            'selection': sel.__name__,
            'crossover': xo.__name__,
            'mutation': mut.__name__,
            'mean_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'best_fitness': np.min(fitnesses),
            'time_sec': round(end - start, 2)
        })

    return results
