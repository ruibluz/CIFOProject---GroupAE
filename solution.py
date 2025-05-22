from abc import ABC, abstractmethod

class Solution(ABC):
    def __init__(self, repr=None):
        """
        Base abstract class for solutions to optimization problems.
        If no representation is given, it initializes randomly.
        """
        if repr is None:
            repr = self.random_initial_representation()
        self.repr = repr

    def __repr__(self):
        return str(self.repr)

    @abstractmethod
    def fitness(self):
        """
        Must return the fitness of the solution.
        """
        pass

    @abstractmethod
    def random_initial_representation(self):
        """
        Must return a random, valid representation of a solution.
        """
        pass
