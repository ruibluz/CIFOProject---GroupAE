import random
import copy
from Classes import Team

# ====== MUTATION SWAP PLAYERS ======
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


# ===== MUTATION REGENERATE TEAM ======
def mutation_regenerate_team(individual):
    """
    Regenerates one team by:
    1. Removing a random team x
    2. Extracting 7 position-respecting players from the other teams
    3. Replacing the removed team with those players
    4. Redistributing the removed players back into the other 4 teams

    """
    new_indiv = copy.deepcopy(individual)
    team_structure = new_indiv.team_structure
    budget = new_indiv.budget_limit
    num_teams = len(new_indiv.league)

    # select random team x
    team_x_index = random.randint(0, num_teams - 1)
    team_x = new_indiv.league[team_x_index]
    team_x_players = team_x.players  # 7 players to redistribute later

    # build a pool of players from the other 4 teams
    donor_teams = [i for i in range(num_teams) if i != team_x_index]
    donor_pool = {pos: [] for pos in team_structure}
    for i in donor_teams:
        for p in new_indiv.league[i].players:
            donor_pool[p.position].append((p, i))  # keep track of which team the player comes from

    # select 7 new players for team x (by position)
    selected_new_players = []
    selected_indices = {i: set() for i in donor_teams}
    for pos, count in team_structure.items():
        candidates = [entry for entry in donor_pool[pos] if entry[0].name not in [p.name for p in selected_new_players]]
        if len(candidates) < count:
            return individual, False  # not enough available players
        picks = random.sample(candidates, count)
        selected_new_players.extend([p for p, _ in picks])
        for p, idx in picks:
            selected_indices[idx].add(p.name)  # mark as used

    # replace team x with selected players
    new_team_x = Team(selected_new_players)
    if not new_team_x.is_valid(team_structure, budget):
        return individual, False  # Invalid team

    new_indiv.league[team_x_index] = new_team_x

    # redistribute original team_x players into donor teams
    to_redistribute = {pos: [] for pos in team_structure}
    for p in team_x_players:
        to_redistribute[p.position].append(p)

    # rebuild each donor team with updated players
    for i in donor_teams:
        team = new_indiv.league[i]
        remaining = [p for p in team.players if p.name not in selected_indices[i]]
        slots = {pos: team_structure[pos] - sum(1 for p in remaining if p.position == pos) for pos in team_structure}

        added = []
        for pos, count in slots.items():
            available = to_redistribute[pos]
            if len(available) < count:
                return individual, False  # Not enough players to refill team
            chosen = random.sample(available, count)
            added.extend(chosen)
            to_redistribute[pos] = [p for p in available if p.name not in [x.name for x in chosen]]

        rebuilt = Team(remaining + added)
        if not rebuilt.is_valid(team_structure, budget):
            return individual, False  # Reconstructed team invalid
        new_indiv.league[i] = rebuilt

    # Success — mutation completed
    new_indiv.fitness = new_indiv.evaluate_fitness()
    return new_indiv, True


# ====== MUTATION BALANCE TEAMS ======
def mutation_balance_teams(individual):
    """
    Attempts to swap one player between the strongest and weakest teams 
    (teams with highest and lowest average skill)
    to reduce the standard deviation of average skill.
    Applies the change only if fitness improves.

    """
    new_indiv = copy.deepcopy(individual)
    teams = new_indiv.league
    team_structure = new_indiv.team_structure
    budget = new_indiv.budget_limit

    # identify team with highest and lowest average skill
    team_skills = [(i, team.avg_skill()) for i, team in enumerate(teams)]
    team_skills.sort(key=lambda x: x[1])  # ascending order

    low_index = team_skills[0][0]
    high_index = team_skills[-1][0]

    team_low = teams[low_index]
    team_high = teams[high_index]

    max_attempts = 20
    for _ in range(max_attempts):
        # Find common positions
        positions_low = {p.position for p in team_low.players}
        positions_high = {p.position for p in team_high.players}
        common_positions = list(positions_low.intersection(positions_high))
        if not common_positions:
            return individual  # no compatible swap possible

        pos = random.choice(common_positions)

        # sort to encourage meaningful skill transfer
        candidates_low = sorted([p for p in team_low.players if p.position == pos], key=lambda p: p.skill)
        candidates_high = sorted([p for p in team_high.players if p.position == pos], key=lambda p: -p.skill)

        for pl in candidates_low:
            for ph in candidates_high:
                # Try swapping player low and player high
                new_team_low_players = [ph if p.name == pl.name else p for p in team_low.players]
                new_team_high_players = [pl if p.name == ph.name else p for p in team_high.players]

                new_team_low = Team(new_team_low_players)
                new_team_high = Team(new_team_high_players)

                # Check validity
                if not new_team_low.is_valid(team_structure, budget):
                    continue
                if not new_team_high.is_valid(team_structure, budget):
                    continue

                # Check for duplicates in the league
                temp_league = new_indiv.league[:]
                temp_league[low_index] = new_team_low
                temp_league[high_index] = new_team_high

                all_names = [p.name for t in temp_league for p in t.players]
                if len(all_names) != len(set(all_names)):
                    continue  # duplicate detected

                # Check if fitness improves
                temp_indiv = copy.deepcopy(new_indiv)
                temp_indiv.league[low_index] = new_team_low
                temp_indiv.league[high_index] = new_team_high
                new_fitness = temp_indiv.evaluate_fitness()

                if new_fitness < new_indiv.fitness:
                    # Accept the mutation
                    temp_indiv.fitness = new_fitness
                    return temp_indiv

    return individual  # no improving swap found
