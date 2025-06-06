# imports
import random
from copy import deepcopy
import numpy as np

# ====== PLAYER CLASS ======
class Player:
    def __init__(self, name, position, skill, salary):

        """
        Represents a player in each team.
        Args:
            name (str): Name of the player.
            position (str): Position of the player ('GK', 'DEF', 'MID', 'FWD').
            skill (float): Skill level of the player.
            salary (float): Salary of the player in millions of euros.

        Returns:
            Player: An instance of the Player class.
        
        Raises:
            ValueError: If the position is not one of 'GK', 'DEF', 'MID', 'FWD'.
            ValueError: If the salary is not a positive number.
        """

        self.name = name
        self.position = position
        self.skill = skill
        self.salary = salary

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['Name'],
            position=data['Position'],
            skill=data['Skill'],
            salary=data['Salary (€M)']
        )

    def to_dict(self):
        return {
            'Name': self.name,
            'Position': self.position,
            'Skill': self.skill,
            'Salary (€M)': self.salary
        }

    def __repr__(self):
        return f"{self.position}: {self.name} | Skill: {self.skill} | Salary: €{self.salary}M"


# ====== TEAM CLASS ======
class Team:
    def __init__(self, players):

        """

        Represents a team composed of players.
        Args:
            players (list[Player]): List of Player objects in the team.

        Returns:
            Team: An instance of the Team class.
        
        Raises:
            ValueError: If the number of players is not equal to the sum of players in the team structure.
            ValueError: If the budget limit is not a positive number.

        """
        self.players = players  # List of Player objects

    # method to check if the team is valid
    def is_valid(self, structure, budget):
        if len(self.players) != sum(structure.values()):
            return False

        # Check if the team has the correct number of players in each position
        # and if the total salary is within the budget
        pos_counts = {pos: 0 for pos in structure}
        total_salary = 0
        names_seen = set()

        # add players to the team
        for player in self.players:
            if player.name in names_seen:
                return False
            names_seen.add(player.name)
            pos_counts[player.position] += 1
            total_salary += player.salary

        return pos_counts == structure and total_salary <= budget

    # get the average skill of the team
    def avg_skill(self):
        return sum(p.skill for p in self.players) / len(self.players)

    # get the total salary of the team
    def total_salary(self):
        return sum(p.salary for p in self.players)

    # get the players of the team
    def player_names(self):
        return [p.name for p in self.players]

    def __repr__(self):
        return "\n".join([f"  - {p}" for p in self.players])
    

# ====== LEAGUE INDIVIDUAL CLASS ======
class LeagueIndividual:
    def __init__(self, players_by_position, team_structure, budget_limit, num_teams, league=None):

        """
        Represents an individual (= possible solution of the search space = a league of teams)
        composed by 5 teams, each with a set of 7 players.
        Each team is composed of players from different positions, and the total salary
        of the team must not exceed the budget limit.

        Args:
            players_by_position (dict): Dictionary where keys are positions and values are lists of Player objects.
            team_structure (dict): Dictionary defining the number of players required for each position in a team.
            budget_limit (float): Maximum budget allowed for a team.
            num_teams (int): Number of teams to create.
            league (list[Team], optional): Predefined league of teams. If None, a new league will be generated.

        Returns:
            LeagueIndividual: An instance of the LeagueIndividual class.
        
        Raises:
            ValueError: If the number of teams is not equal to the sum of players in the team structure.
            ValueError: If the budget limit is not a positive number.
            ValueError: If the team structure is not a valid dictionary.
        """

        
        self.players_by_position = players_by_position
        self.team_structure = team_structure
        self.budget_limit = budget_limit
        self.num_teams = num_teams

        self.league = league if league is not None else self._generate_league()
        self.fitness = self.evaluate_fitness()

    def _generate_league(self):
        league = []
        all_players = deepcopy(self.players_by_position)
        used_names = set()

        for _ in range(self.num_teams):
            team_players = []

            for pos, count in self.team_structure.items():
                candidates = [p for p in all_players[pos] if p.name not in used_names]
                if len(candidates) < count:
                    return None  # Not enough players available

                # Randomly select players for the position
                selected = random.sample(candidates, count)
                team_players.extend(selected)
                used_names.update(p.name for p in selected)

            # Create team and check validity
            team = Team(team_players)
            if not team.is_valid(self.team_structure, self.budget_limit):
                return None

            league.append(team)

            # Remove used players from pool
            for pos in self.players_by_position:
                all_players[pos] = [p for p in all_players[pos] if p.name not in used_names]

        return league


    # function to evaluate the fitness of the league (standard deviation of the average skills of the teams)
    def evaluate_fitness(self):
        if self.league is None:
            return float('inf')

        avg_skills = []
        used_names = set()

        for team in self.league:
            if not team.is_valid(self.team_structure, self.budget_limit):
                return float('inf')

            for p in team.players:
                if p.name in used_names:
                    return float('inf')  # Duplicated player across teams
                used_names.add(p.name)

            avg_skills.append(team.avg_skill())

        return np.std(avg_skills)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __repr__(self):
        return f"<LeagueIndividual fitness={self.fitness:.4f}>"