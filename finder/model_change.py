from abc import ABC, abstractmethod
from typing import List, Set

import attr

from mscp_exceptions import OperatorDisabledException
from strips_problem import StripsProblem


@attr.s
class Change(ABC):
    """
    A generic operation on a STRIPS planning instance.
    """
    @abstractmethod
    def apply(self, problem: StripsProblem):
        pass


@attr.s
class ModelChange:
    """
    A list of changes to the STRIPS planning instance to be brought to the model, before a test is applied
    """
    model_changes: List[Change] = attr.ib(default=attr.Factory(list))

    def apply_inplace(self, problem: StripsProblem):
        for change in self.model_changes:
            change.apply(problem)

        return problem

    def apply_copy(self, problem: StripsProblem):
        # TODO: do this in a smarter way by keeping track of what is deep copied or not
        new_problem = problem.copy()
        for change in self.model_changes:
            change.apply(new_problem)

        return new_problem

    def add(self, change: Change):
        self.model_changes.append(change)


#
# List of various changes that can be brought to the model
#
@attr.s
class RemoveOperator(Change):
    """
    Remove an operator from a model
    """
    op_id: int = attr.ib()

    def apply(self, problem: StripsProblem):
        problem.remove_operator(self.op_id)


@attr.s
class ChangeOperatorSet(Change):
    """
    Replace the set of operators
    """
    op_id_set: Set = attr.ib()

    def apply(self, problem: StripsProblem):
        for op_id in problem.operators_id:
            if op_id not in self.op_id_set:
                problem.remove_operator(op_id)


@attr.s
class ChangeInitialState(Change):
    """
    Replace the initial state of the instance
    """
    initial_state: list = attr.ib()

    def apply(self, problem: StripsProblem):
        problem.init_pos = self.initial_state


@attr.s
class ChangeGoalState(Change):
    """
    Replace the goal of the instance
    """
    goal_state: list = attr.ib()

    def apply(self, problem: StripsProblem):
        problem.goal_pos = self.goal_state


@attr.s
class ProjectOnFluentSet(Change):
    """
    Remove the fluents of the instance that are not in the set of fluents given in parameters
    """
    fluent_set: Set = attr.ib()

    def apply(self, problem: StripsProblem):
        for fluent_id in self.fluent_set:
            problem.remove_fluent(fluent_id)


@attr.s
class AddFluentToPrePos(Change):
    """
    Add a fluent to the positive preconditions of an operator
    """
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def apply(self, problem):
        try:
            operator = problem.copy_replace_operator_by_id(self.op_id)
            operator.pre_pos.add(self.fluent)

        except OperatorDisabledException:
            pass


@attr.s
class AddFluentToPreNeg(Change):
    """
    Add a fluent to the negative preconditions of an operator
    """
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def apply(self, problem):
        try:
            operator = problem.copy_replace_operator_by_id(self.op_id)
            operator.pre_neg.add(self.fluent)

        except OperatorDisabledException:
            pass

