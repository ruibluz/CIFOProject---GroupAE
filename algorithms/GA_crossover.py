import random
from copy import deepcopy
from Classes import Team, LeagueIndividual

# ====== CROSSOVER BY TEAM ======
def team_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    num_teams = len(parent1.league)
    team_structure = parent1.team_structure
    players_by_position = parent1.players_by_position
    budget = parent1.budget_limit
    crossover_point = random.randint(1, num_teams - 1)

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
            if len(child_teams) < num_teams and all(name not in used_names for name in names):
                child_teams.append(team)
                used_names.update(names)

        # Generate new teams to complete the league
        while len(child_teams) < num_teams:
            team_players = []
            for position, count in team_structure.items():
                available = [p for p in players_by_position[position] if p.name not in used_names]
                if len(available) < count:
                    break
                selected = random.sample(available, count)
                team_players.extend(selected)

            new_team = Team(team_players)
            if new_team.is_valid(team_structure, budget):
                child_teams.append(new_team)
                used_names.update(p.name for p in team_players)

        return LeagueIndividual(players_by_position, team_structure, budget, num_teams, league=child_teams)

    child1 = build_child(parent1, parent2)
    child2 = build_child(parent2, parent1)
    return child1, child2


# ====== CROSSOVER BY POSITION ======
def position_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    team_structure = parent1.team_structure
    players_by_position = parent1.players_by_position
    budget = parent1.budget_limit
    num_teams = len(parent1.league)

    combined_by_position = {pos: [] for pos in team_structure}
    used_names = set()

    for individual in [parent1, parent2]:
        for team in individual.league:
            for player in team.players:
                if player.name not in used_names:
                    combined_by_position[player.position].append(player)
                    used_names.add(player.name)

    child1_pool = {pos: [] for pos in team_structure}
    child2_pool = {pos: [] for pos in team_structure}

    for pos, players in combined_by_position.items():
        random.shuffle(players)
        midpoint = len(players) // 2
        child1_pool[pos] = players[:midpoint]
        child2_pool[pos] = players[midpoint:]

    def fill_position_pool(pool):
        for pos, required_count in team_structure.items():
            total_needed = required_count * num_teams
            current_count = len(pool[pos])
            available = [p for p in players_by_position[pos] if p.name not in {x.name for x in pool[pos]}]
            if current_count < total_needed:
                extra = random.sample(available, total_needed - current_count)
                pool[pos].extend(extra)
        return pool

    child1_pool = fill_position_pool(child1_pool)
    child2_pool = fill_position_pool(child2_pool)

    def build_league_from_pool(pool) -> LeagueIndividual:
        all_players = deepcopy(pool)
        league = []
        used_names = set()

        for _ in range(num_teams):
            team_players = []
            for pos, count in team_structure.items():
                candidates = [p for p in all_players[pos] if p.name not in used_names]
                if len(candidates) < count:
                    break
                selected = random.sample(candidates, count)
                team_players.extend(selected)
                used_names.update(p.name for p in selected)
                all_players[pos] = [p for p in all_players[pos] if p.name not in used_names]

            team = Team(team_players)
            if not team.is_valid(team_structure, budget):
                return LeagueIndividual(players_by_position, team_structure, budget, num_teams, league=None)

            league.append(team)

        return LeagueIndividual(players_by_position, team_structure, budget, num_teams, league=league)

    child1 = build_league_from_pool(child1_pool)
    child2 = build_league_from_pool(child2_pool)

    return child1, child2