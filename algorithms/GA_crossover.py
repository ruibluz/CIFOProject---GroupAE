import random
from copy import deepcopy
from Classes import Player, Team, LeagueIndividual

# # ====== CROSSOVER BY TEAM ======

def team_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    crossover_point = random.randint(1, NUM_TEAMS - 1)

    def build_child(p1: LeagueIndividual, p2: LeagueIndividual) -> LeagueIndividual:
        child_teams = []
        used_names = set()

        # Copy prefix teams from parent 1
        for team in p1.league[:crossover_point]:
            child_teams.append(team)
            used_names.update(player.name for player in team.players)

        # Add valid teams from parent 2 without duplicate players
        for team in p2.league:
            names = [player.name for player in team.players]
            if len(child_teams) < NUM_TEAMS and all(name not in used_names for name in names):
                child_teams.append(team)
                used_names.update(names)

        # If needed, generate new teams to complete the league
        while len(child_teams) < NUM_TEAMS:
            team_players = []
            for position, count in TEAM_STRUCTURE.items():
                available = [
                    p for p in players_by_position[position]
                    if p.name not in used_names
                ]
                if len(available) < count:
                    break  # not enough players to form a valid team
                selected = random.sample(available, count)
                team_players.extend(selected)

            new_team = Team(team_players)
            if new_team.is_valid(TEAM_STRUCTURE, BUDGET_LIMIT):
                child_teams.append(new_team)
                used_names.update(p.name for p in team_players)

        return LeagueIndividual(players_by_position, TEAM_STRUCTURE, BUDGET_LIMIT, league=child_teams)

    child1 = build_child(parent1, parent2)
    child2 = build_child(parent2, parent1)
    return child1, child2



# # ====== CROSSOVER BY POSITION ======
def position_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    # Step 1: Collect all players by position from both parents
    combined_by_position = {pos: [] for pos in TEAM_STRUCTURE}
    used_names = set()

    for individual in [parent1, parent2]:
        for team in individual.league:
            for player in team.players:
                if player.name not in used_names:
                    combined_by_position[player.position].append(player)
                    used_names.add(player.name)

    # Step 2: Shuffle each position group and split into two sets
    child1_pool = {pos: [] for pos in TEAM_STRUCTURE}
    child2_pool = {pos: [] for pos in TEAM_STRUCTURE}

    for pos, players in combined_by_position.items():
        random.shuffle(players)
        midpoint = len(players) // 2
        child1_pool[pos] = players[:midpoint]
        child2_pool[pos] = players[midpoint:]

    # Step 3: Fill up missing players in each pool if needed
    def fill_position_pool(pool):
        for pos, required_count in TEAM_STRUCTURE.items():
            total_needed = required_count * NUM_TEAMS
            current_count = len(pool[pos])
            available = [
                p for p in players_by_position[pos]
                if p.name not in {x.name for x in pool[pos]}
            ]
            if current_count < total_needed:
                extra = random.sample(available, total_needed - current_count)
                pool[pos].extend(extra)
        return pool

    child1_pool = fill_position_pool(child1_pool)
    child2_pool = fill_position_pool(child2_pool)

    # Step 4: Build teams from the position pools
    def build_league_from_pool(pool) -> LeagueIndividual:
        all_players = deepcopy(pool)
        league = []
        used_names = set()

        for _ in range(NUM_TEAMS):
            team_players = []

            for pos, count in TEAM_STRUCTURE.items():
                candidates = [p for p in all_players[pos] if p.name not in used_names]
                if len(candidates) < count:
                    break  # cannot build a valid team
                selected = random.sample(candidates, count)
                team_players.extend(selected)
                used_names.update(p.name for p in selected)
                all_players[pos] = [p for p in all_players[pos] if p.name not in used_names]

            team = Team(team_players)
            if not team.is_valid(TEAM_STRUCTURE, BUDGET_LIMIT):
                return LeagueIndividual(players_by_position, TEAM_STRUCTURE, BUDGET_LIMIT, league=None)

            league.append(team)

        return LeagueIndividual(players_by_position, TEAM_STRUCTURE, BUDGET_LIMIT, league=league)

    child1 = build_league_from_pool(child1_pool)
    child2 = build_league_from_pool(child2_pool)

    return child1, child2