import random
import copy
from utils.Classes import Team

# MUTATION SWAP PLAYERS
def mutation_swap_players(individual, max_attempts=100):

    """

    Performs one swap per team in the League (Individual):
    For each team, attempts to swap one player (same position) with another team.
    Ensures validity (structure, budget, no duplicates).
    
    Parameters:
        individual (LeagueIndividual): The individual to mutate.
        max_attempts (int): Maximum number of attempts to find a valid mutation.

    Returns:
        LeagueIndividual: A new individual with the mutation applied.
    
    Raises:
        ValueError: If a valid mutation cannot be produced after multiple attempts.
    """
    # ensure the individual is valid
    for _ in range(max_attempts):
        new_indiv = copy.deepcopy(individual)
        if new_indiv.league is None:
            continue

        team_count = len(new_indiv.league)
        any_success = False

        for i, team1 in enumerate(new_indiv.league):
            for _ in range(10):  # max_attempts_per_team
                j = random.choice([idx for idx in range(team_count) if idx != i]) # randomly select another team
                team2 = new_indiv.league[j]

                # Check if teams have players in common positions
                common_positions = list({p.position for p in team1.players}.intersection(
                                         {p.position for p in team2.players}))
                if not common_positions:
                    continue
                
                # Randomly select a position and players to swap
                pos = random.choice(common_positions)
                p1 = random.choice([p for p in team1.players if p.position == pos])
                p2 = random.choice([p for p in team2.players if p.position == pos])

                # Swap players
                new_team1 = Team([p2 if p.name == p1.name else p for p in team1.players])
                new_team2 = Team([p1 if p.name == p2.name else p for p in team2.players])
                
                temp_league = new_indiv.league[:]
                temp_league[i] = new_team1
                temp_league[j] = new_team2

                all_names = [p.name for team in temp_league for p in team.players]
                if len(all_names) != len(set(all_names)):
                    continue
                    
                # Check if the new teams are valid
                if new_team1.is_valid(new_indiv.team_structure, new_indiv.budget_limit) and \
                   new_team2.is_valid(new_indiv.team_structure, new_indiv.budget_limit):

                    new_indiv.league[i] = new_team1
                    new_indiv.league[j] = new_team2
                    any_success = True
                    break

        if any_success:
            new_indiv.fitness = new_indiv.evaluate_fitness()
            return new_indiv

    raise ValueError("mutation_swap_players: Could not produce valid individual after retries.")



# MUTATION REGENERATE TEAM
def mutation_regenerate_team(individual, max_attempts=100):
    """
    Regenerates one team by:
    1. Removing a random team x
    2. Extracting 7 position-respecting players from the other teams
    3. Replacing the removed team with those players
    4. Redistributing the removed players back into the other 4 teams

    Parameters:
        individual (LeagueIndividual): The individual to mutate.
        max_attempts (int): Maximum number of attempts to find a valid mutation.
    
    Returns:
        LeagueIndividual: A new individual with the mutation applied.

    Raises:
        ValueError: If a valid mutation cannot be produced after multiple attempts.    
    """
    
    for _ in range(max_attempts):
        new_indiv = copy.deepcopy(individual)
        team_structure = new_indiv.team_structure
        budget = new_indiv.budget_limit
        num_teams = len(new_indiv.league)

        # Randomly select a team to regenerate
        team_x_index = random.randint(0, num_teams - 1)
        team_x = new_indiv.league[team_x_index]
        team_x_players = team_x.players

        # create a pool of players from the other teams
        donor_teams = [i for i in range(num_teams) if i != team_x_index]
        donor_pool = {pos: [] for pos in team_structure}
        for i in donor_teams:
            for p in new_indiv.league[i].players:
                donor_pool[p.position].append((p, i))

        # Check if we can fill the team structure with the donor pool
        selected_new_players = []
        selected_indices = {i: set() for i in donor_teams}
        for pos, count in team_structure.items():
            candidates = [entry for entry in donor_pool[pos] if entry[0].name not in [p.name for p in selected_new_players]]
            if len(candidates) < count:
                break
            picks = random.sample(candidates, count)
            selected_new_players.extend([p for p, _ in picks])
            for p, idx in picks:
                selected_indices[idx].add(p.name)

        if len(selected_new_players) != sum(team_structure.values()):
            continue

        # create a new team with the selected players
        new_team_x = Team(selected_new_players)
        if not new_team_x.is_valid(team_structure, budget):
            continue

        new_indiv.league[team_x_index] = new_team_x

        # redistribute the players from team x to the other teams
        to_redistribute = {pos: [] for pos in team_structure}
        for p in team_x_players:
            to_redistribute[p.position].append(p)

        # Check if we can fill the teams with the remaining players
        valid = True
        for i in donor_teams:
            team = new_indiv.league[i]
            remaining = [p for p in team.players if p.name not in selected_indices[i]]
            slots = {pos: team_structure[pos] - sum(1 for p in remaining if p.position == pos) for pos in team_structure}
            added = []

            for pos, count in slots.items():
                if len(to_redistribute[pos]) < count:
                    valid = False
                    break
                chosen = random.sample(to_redistribute[pos], count)
                added.extend(chosen)
                to_redistribute[pos] = [p for p in to_redistribute[pos] if p.name not in [x.name for x in chosen]]

            if not valid:
                break

            rebuilt = Team(remaining + added)
            if not rebuilt.is_valid(team_structure, budget):
                valid = False
                break
            new_indiv.league[i] = rebuilt

        if valid:
            new_indiv.fitness = new_indiv.evaluate_fitness()
            return new_indiv

    raise ValueError("mutation_regenerate_team: Failed after multiple retries.")



# MUTATION BALANCE TEAMS
def mutation_balance_teams(individual, max_attempts=100):
    """
    Attempts to swap one player between the strongest and weakest teams 
    (teams with highest and lowest average skill)
    to reduce the standard deviation of average skill.
    Applies the change only if fitness improves.

    Parameters:
        individual (LeagueIndividual): The individual to mutate.
        max_attempts (int): Maximum number of attempts to find a valid mutation.

    Returns:
        LeagueIndividual: A new individual with the mutation applied.

    Raises:
        ValueError: If a valid mutation cannot be produced after multiple attempts.
    """
    for _ in range(max_attempts):
        new_indiv = copy.deepcopy(individual)
        teams = new_indiv.league
        team_structure = new_indiv.team_structure
        budget = new_indiv.budget_limit

        # Sort teams by average skill
        team_skills = sorted([(i, team.avg_skill()) for i, team in enumerate(teams)], key=lambda x: x[1])
        # Select the weakest and strongest teams
        low_index = team_skills[0][0]
        high_index = team_skills[-1][0]
        team_low = teams[low_index]
        team_high = teams[high_index]

        # Check if teams have players in common positions
        common_positions = list(set(p.position for p in team_low.players).intersection(
                                 set(p.position for p in team_high.players)))
        if not common_positions:
            continue
        
        # Randomly select a position and players to swap
        pos = random.choice(common_positions)
        candidates_low = sorted([p for p in team_low.players if p.position == pos], key=lambda p: p.skill)
        candidates_high = sorted([p for p in team_high.players if p.position == pos], key=lambda p: -p.skill)

        # Check if we can swap players
        for pl in candidates_low:
            for ph in candidates_high:
                new_low = Team([ph if p.name == pl.name else p for p in team_low.players])
                new_high = Team([pl if p.name == ph.name else p for p in team_high.players])

                if not new_low.is_valid(team_structure, budget):
                    continue
                if not new_high.is_valid(team_structure, budget):
                    continue
                
                # swap players
                temp_league = new_indiv.league[:]
                temp_league[low_index] = new_low
                temp_league[high_index] = new_high
                all_names = [p.name for t in temp_league for p in t.players]
                if len(all_names) != len(set(all_names)):
                    continue

                temp_indiv = copy.deepcopy(new_indiv)
                temp_indiv.league[low_index] = new_low
                temp_indiv.league[high_index] = new_high
                new_fitness = temp_indiv.evaluate_fitness()

                if new_fitness < new_indiv.fitness:
                    temp_indiv.fitness = new_fitness
                    return temp_indiv

    raise ValueError("mutation_balance_teams: Failed to improve fitness after retries.")
