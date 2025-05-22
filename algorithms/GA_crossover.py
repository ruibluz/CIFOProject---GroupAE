import random
from copy import deepcopy
from Classes import Team, LeagueIndividual

# ====== CROSSOVER BY TEAM ======
def team_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    num_teams = len(parent1.league)
    team_structure = parent1.team_structure
    players_by_position = parent1.players_by_position
    budget = parent1.budget_limit
    max_attempts = 100

    def build_valid_child(p1: LeagueIndividual, p2: LeagueIndividual) -> LeagueIndividual:
        for _ in range(max_attempts):
            crossover_point = random.randint(1, num_teams - 1)
            child_teams = []
            used_names = set()

            # Copy prefix from parent 1
            for team in p1.league[:crossover_point]:
                child_teams.append(team)
                used_names.update(player.name for player in team.players)

            # Add teams from parent 2 without duplicates
            for team in p2.league:
                names = [p.name for p in team.players]
                if len(child_teams) < num_teams and all(name not in used_names for name in names):
                    child_teams.append(team)
                    used_names.update(names)

            # Fill missing teams
            while len(child_teams) < num_teams:
                team_players = []
                for pos, count in team_structure.items():
                    available = [p for p in players_by_position[pos] if p.name not in used_names]
                    if len(available) < count:
                        break  # not enough players
                    selected = random.sample(available, count)
                    team_players.extend(selected)

                new_team = Team(team_players)
                if new_team.is_valid(team_structure, budget):
                    child_teams.append(new_team)
                    used_names.update(p.name for p in team_players)
                else:
                    break  # invalid team, try another child

            if len(child_teams) == num_teams:
                return LeagueIndividual(players_by_position, team_structure, budget, num_teams, league=child_teams)

        return None

    child1 = build_valid_child(parent1, parent2)
    child2 = build_valid_child(parent2, parent1)

    if child1 is None or child2 is None:
        raise ValueError("❌ Could not generate valid children after multiple attempts (team crossover).")

    return child1, child2



# ====== CROSSOVER BY POSITION ======
def position_crossover(parent1: LeagueIndividual, parent2: LeagueIndividual) -> tuple:
    team_structure = parent1.team_structure
    players_by_position = parent1.players_by_position
    budget = parent1.budget_limit
    num_teams = len(parent1.league)
    max_attempts = 100

    def build_valid_child():
        for _ in range(max_attempts):
            combined_by_position = {pos: [] for pos in team_structure}
            used_names = set()

            for individual in [parent1, parent2]:
                for team in individual.league:
                    for player in team.players:
                        if player.name not in used_names:
                            combined_by_position[player.position].append(player)
                            used_names.add(player.name)

            child_pool = {pos: [] for pos in team_structure}
            for pos, players in combined_by_position.items():
                random.shuffle(players)
                half = len(players) // 2
                child_pool[pos] = players[:half]

            # Fill up if needed
            for pos, required_count in team_structure.items():
                total_needed = required_count * num_teams
                current = len(child_pool[pos])
                available = [p for p in players_by_position[pos] if p.name not in {x.name for x in child_pool[pos]}]
                if current < total_needed and len(available) >= (total_needed - current):
                    child_pool[pos].extend(random.sample(available, total_needed - current))

            all_players = deepcopy(child_pool)
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
                    break
                league.append(team)

            if len(league) == num_teams:
                return LeagueIndividual(players_by_position, team_structure, budget, num_teams, league=league)

        return None  # All attempts failed

    child1 = build_valid_child()
    child2 = build_valid_child()

    if child1 is None or child2 is None:
        raise ValueError("❌ Could not generate valid children after multiple attempts.")

    return child1, child2
