from solutions.solution import Solution
from utils.Classes import LeagueIndividual

class GASolution(Solution):
    def __init__(self, individual: LeagueIndividual):
        """
        Wraps a LeagueIndividual instance as a GA solution. 
        to integrate it into a GA framework. Provides methods for fitness 
        evaluation, mutation, and crossover.

        Args:
            individual (LeagueIndividual): The LeagueIndividual instance to wrap.

        Raises:
            NotImplementedError: If random_initial_representation is called.
        """
        self.individual = individual
        super().__init__(repr=individual)  # Required by the abstract Solution base class

    def fitness(self):
        """
        Returns the fitness of the solution, delegated to the LeagueIndividual.
        """
        return self.individual.fitness

    def random_initial_representation(self):
        """
        Not used here because LeagueIndividual generation happens outside.
        Raises error to avoid misuse.
        """
        raise NotImplementedError("Use LeagueIndividual directly to generate individuals.")

    def mutate(self, mutation_fn):
        """
        Applies a mutation function to the wrapped LeagueIndividual.
        Returns a new GASolution.
        """
        mutated = mutation_fn(self.individual)
        return GASolution(mutated)

    def crossover(self, other, crossover_fn):
        """
        Applies a crossover function to two GASolutions (2 LeagueIndividual).
        Returns two new GASolutions (offspring).
        """
        child1, child2 = crossover_fn(self.individual, other.individual)
        return GASolution(child1), GASolution(child2)

    def __repr__(self):
        return f"<GASolution fitness={self.fitness():.4f}>"
