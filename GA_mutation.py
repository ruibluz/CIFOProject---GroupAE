import random
import copy
from Classes import Team

def mutation_swap_players(individual):
    """
    Performs one swap per team in the League (Individual):
    For each team, attempts to swap one player (same position) with another team.
    Ensures validity (structure, salary, no duplicates).
    Returns a mutated individual or the original if no valid swaps occurred.
    """
    new_indiv = copy.deepcopy(individual)
    team_count = len(new_indiv.league)
    max_attempts_per_team = 10
    any_success = False

    for i, team1 in enumerate(new_indiv.league):
        for attempt in range(max_attempts_per_team):
            # Pick a different team to swap with
            j = random.choice([idx for idx in range(team_count) if idx != i])
            team2 = new_indiv.league[j]

            # Find common positions
            pos1 = {p.position for p in team1.players}
            pos2 = {p.position for p in team2.players}
            common_positions = list(pos1.intersection(pos2))
            if not common_positions:
                continue

            # Choose a random position to swap
            pos = random.choice(common_positions)
            p1 = random.choice([p for p in team1.players if p.position == pos])
            p2 = random.choice([p for p in team2.players if p.position == pos])

            # Perform the swap
            new_team1_players = [p2 if p.name == p1.name else p for p in team1.players]
            new_team2_players = [p1 if p.name == p2.name else p for p in team2.players]

            new_team1 = Team(new_team1_players)
            new_team2 = Team(new_team2_players)

            # Ensure no duplicates across the league
            temp_league = new_indiv.league[:]
            temp_league[i] = new_team1
            temp_league[j] = new_team2

            all_names = [p.name for team in temp_league for p in team.players]
            if len(all_names) != len(set(all_names)):
                continue  # duplicate found

            # Validate both swapped teams
            if new_team1.is_valid(new_indiv.team_structure, new_indiv.budget_limit) and \
               new_team2.is_valid(new_indiv.team_structure, new_indiv.budget_limit):

                # Apply the swap
                new_indiv.league[i] = new_team1
                new_indiv.league[j] = new_team2
                any_success = True
                break  # stop retrying for this team

    if any_success:
        new_indiv.fitness = new_indiv.evaluate_fitness()
        return new_indiv
    else:
        return individual
