from abc import abstractmethod, ABC
from enum import Enum
from typing import List

from mscp_exceptions import ImpossibleModelChangeException
from model_change import ModelChange
from mutex_manager import MutexManager
from strips_problem import StripsProblem

import attr


# This file contains the barebones for additional propagation rules and tests

class Criterion(ABC):
    class Outcome(Enum):
        POSITIVE = 1,
        NEGATIVE = 2,
        ERROR = 3,

    @abstractmethod
    def apply_single(self, mscp, pb_attr, steps_duration, certificate_path, silent=False):
        pass


class CriterionLP(Criterion, ABC):
    pass


class CriterionStruct(Criterion, ABC):
    pass


class LPOptimization(ABC):
    # TODO: Change this so it is not redundant with the above definition
    class Outcome(Enum):
        POSITIVE = 1,
        NEGATIVE = 2,
        ERROR = 3,
    pass


@attr.s(init=False)
class StripsProblemAttributes:
    """
    Additional information on the elements of a STRIPS instance
    """
    landmarks: set = attr.ib()
    spre: list = attr.ib()
    apre: list = attr.ib()
    apost: list = attr.ib()
    mutexes: MutexManager = attr.ib()
    op_mutexes: MutexManager = attr.ib()
    max_op_count: List[int | float] = attr.ib()
    min_op_count: List[int] = attr.ib()

    def __init__(self, problem: StripsProblem):
        self.landmarks = set()

        self.spre = [set() for _ in range(problem.get_operator_count() + 1)]
        self.apre = [set() for _ in range(problem.get_operator_count() + 1)]
        self.apost = [set() for _ in range(problem.get_operator_count() + 1)]

        self.mutexes = MutexManager()
        self.op_mutexes = MutexManager()

        self.max_op_count = [float('inf') for _ in range(problem.get_operator_count() + 1)]
        self.min_op_count = [0 for _ in range(problem.get_operator_count() + 1)]

    def __str__(self):
        s = f"Landmarks: \n"
        s += f"{' '.join(str(s) for s in self.landmarks)} \n"
        # s += f"S_pre: \n"
        # s += f"{' '.join(str(s) for s in self.spre)} \n"
        # s += f"A_pre: \n"
        # s += f"{' '.join(str(s) for s in self.apre)} \n"
        # s += f"A_post: \n"
        # s += f"{' '.join(str(s) for s in self.apost)} \n"
        # s += f"Mutexes: \n"
        # s += f"{' '.join(str(s) for s in self.mutexes)} \n"
        # s += f"Max OP Count: \n"
        # s += f"{' '.join(str(s) for s in self.max_op_count)} \n"
        # s += f"Min OP Count: \n"
        # s += f"{' '.join(str(s) for s in self.min_op_count)} \n"

        return s


# Operations for iterative refinement of the model
# IMPORTANT: DO NOT initialize anything in the __init__ methods (except potentially params), as operations are stored as
# empty shells first, and then initialized when needed
@attr.s
class Operation(ABC):
    class Outcome(Enum):
        UNSAT = 0,
        SUCCESS = 1,  # Criterion applied and some conclusion can be drawn
        STABLE = 2,  # Criterion applied but nothing changed
        FAILED = 3,  # Something went wrong

    @abstractmethod
    def apply(self, mscp) -> tuple[Outcome, list]:
        """
        Apply the operation and return the outcome, as well as a list of operations that have to be added to the queue

        Return: Outcome, List of Operation instances to add to the queue
        """
        return Operation.Outcome.STABLE, []

    def test(self, mscp) -> bool:
        """
        Checks if the propagation rule can be applied
        """
        return True


@attr.s
class Propagation(Operation, ABC):
    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        if not self.test(mscp):
            return Operation.Outcome.FAILED, []

        return self.propagate(mscp)

    @abstractmethod
    def propagate(self, mscp) -> tuple[Operation.Outcome, list]:
        """
        Change the STRIPS instance in accordance to the rule that is modelled
        """
        pass


@attr.s
class Test(Operation, ABC):
    @abstractmethod
    def build_model_changes(self, mscp) -> ModelChange:
        """
        Function that builds the sequence of operations that leads to the creation of the new model on which
        the criterion is then tested
        """
        pass

    @abstractmethod
    def initialize_criterion(self) -> Criterion:
        """
        Method that initializes the criterion to be applied
        """
        pass

    def apply(self, mscp):
        """
        Create and apply the model changes
        """
        if not self.test(mscp):
            return Operation.Outcome.FAILED, []

        try:
            model_changes = self.build_model_changes(mscp)
        except ImpossibleModelChangeException:
            return Operation.Outcome.FAILED, []

        new_problem = model_changes.apply_copy(mscp.problem)

        # Initialize the criterion
        criterion = self.initialize_criterion()

        # Apply the criterion
        crit_outcome = criterion.apply_single(new_problem, mscp.pb_attr, {}, None, silent=True)

        # If the criterion is successful, apply the changes to the MSCP
        return self.resolve(mscp, crit_outcome)

    @abstractmethod
    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        """
        Changes to apply to the initial model and/or the additional attributes, in the case where the criterion is
        successfully applied
        """
        pass


class GlobalTest(Test, ABC):
    def build_model_changes(self, mscp) -> ModelChange:
        """
        No model change for the first implementation
        """
        return ModelChange()

    def apply(self, mscp):
        # Create and apply the model changes
        # model_changes = self.build_model_changes(mscp)

        # Initialize the criterion
        criterion = self.initialize_criterion()

        # Apply the criterion
        crit_outcome = criterion.apply_single(mscp, None, {}, None, silent=True)

        # If the criterion is successful, apply the changes to the MSCP
        return self.resolve(mscp, crit_outcome)
