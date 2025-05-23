from algorithms.GA_selection import sel_tournament, sel_rank, sel_roulette

def select_parents(population, method='tournament', num_parents=2, tournament_k=3):
    """
    Selects parent individuals from the population based on the given selection method.

    Args:
        population (list[GASolution]): Current population.
        method (str): One of 'tournament', 'rank', 'roulette'.
        num_parents (int): Number of parents to return.
        tournament_k (int): Tournament size (used only for 'tournament' method).

    Returns:
        list[GASolution]: Selected parents.
    """
    fitness_values = [ind.fitness() for ind in population]

    if method == 'tournament':
        return sel_tournament(population, fitness_values, k=tournament_k, num=num_parents)
    elif method == 'rank':
        return sel_rank(population, fitness_values, num=num_parents)
    elif method == 'roulette':
        return sel_roulette(population, fitness_values, num=num_parents)
    else:
        raise ValueError(f"❌ Unknown selection method: {method}")
