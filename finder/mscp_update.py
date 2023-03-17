from abc import ABC, abstractmethod
from typing import List

import attr

import mscp_propagation as prop
from mscp_exceptions import OperatorDisabledException
from mscp_rules import Operation


@attr.s
class MscpUpdate(Operation):
    @abstractmethod
    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        """
        Apply the changes to the MSCP
        """
        pass


#
# List of updates of the MSCP
#
@attr.s
class MUAddLandmark(MscpUpdate):
    """
    Add an operator to the set of landmarks
    """
    landmark_id: int = attr.ib()

    def apply(self, mscp):
        mscp.pb_attr.landmarks.add(self.landmark_id)
        mscp.pb_attr.min_op_count[self.landmark_id] = max(mscp.pb_attr.min_op_count[self.landmark_id], 1)
        return Operation.Outcome.SUCCESS, [prop.PropLandmarkConsistency(self.landmark_id)]


@attr.s
class MUUpdateMinOpCount(MscpUpdate):
    """
    Update the minimum number of time an operator has to be applied in any plan
    """
    op_id: int = attr.ib()
    min_op_count: int = attr.ib()

    def apply(self, mscp):
        if self.min_op_count <= 0:
            return Operation.Outcome.STABLE, []

        print(f'Update: n-({self.op_id}): {mscp.pb_attr.min_op_count[self.op_id]} -> {self.min_op_count}')
        mscp.pb_attr.landmarks.add(self.op_id)
        mscp.pb_attr.min_op_count[self.op_id] = max(mscp.pb_attr.min_op_count[self.op_id],
                                                    int(self.min_op_count))
        return Operation.Outcome.SUCCESS, [prop.PropLandmarkConsistency(self.op_id)]


@attr.s
class MUUpdateMaxOpCount(MscpUpdate):
    """
    Update the maximum number of time an operator has to be applied in any plan
    """
    op_id: int = attr.ib()
    max_op_count: int = attr.ib()

    def apply(self, mscp):
        if self.max_op_count >= float('inf'):
            return Operation.Outcome.STABLE, []

        rounded_max_op_count = round(self.max_op_count)

        removed = '(removed)' if self.max_op_count == 0 else ''
        print(f'Update: n+({self.op_id}): {mscp.pb_attr.max_op_count[self.op_id]} -> {rounded_max_op_count} {removed}')
        mscp.pb_attr.max_op_count[self.op_id] = min(mscp.pb_attr.max_op_count[self.op_id],
                                                    rounded_max_op_count)
        mscp_updates = []
        if self.max_op_count == 0:
            mscp_updates.append(MURemoveOperator(self.op_id))
        return Operation.Outcome.SUCCESS, mscp_updates


#
# Make a method for the modification of the model and another for additional changes?
#
@attr.s
class MURemoveOperator(MscpUpdate):
    """
    Disable an operator from the STRIPS instance
    """
    op_id: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        if self.op_id in mscp.pb_attr.landmarks:
            return Operation.Outcome.UNSAT, []

        mscp.problem.remove_operator(self.op_id)
        return Operation.Outcome.SUCCESS, [prop.PropActDel(self.op_id)]


@attr.s
class MURemoveFluent(MscpUpdate):
    """
    Disable a fluent from the STRIPS instance
    """
    fluent: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        if self.fluent in mscp.problem.goal_pos:
            return Operation.Outcome.UNSAT, []

        mscp.problem.remove_fluent(self.fluent)
        return Operation.Outcome.SUCCESS, []


@attr.s
class MUAddNegativeGoal(MscpUpdate):
    """
    Add a fluent to the set of fluents that are false in all goal states
    """
    fluent: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        if self.fluent in mscp.problem.goal_pos:
            return Operation.Outcome.UNSAT, []

        mscp.problem.goal_neg.append(self.fluent)
        return Operation.Outcome.SUCCESS, []


@attr.s
class MUAddOperatorMutex(MscpUpdate):
    """
    Add a pair of operators to the list of operator mutexes
    """
    op1_id: int = attr.ib()
    op2_id: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        mscp.pb_attr.op_mutexes.add({self.op1_id, self.op2_id})
        return Operation.Outcome.SUCCESS, []


@attr.s
class MURemoveOperatorFromAPre(MscpUpdate):
    """
    Remove an operator from the list of the operators that can be applied before another
    """
    apre_op_id: int = attr.ib()
    remove_op_id: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        try:
            mscp_updates = []
            mscp.pb_attr.apre[self.apre_op_id].remove(self.remove_op_id)

            if (not mscp.problem.is_operator_disabled(self.remove_op_id)) and \
                    self.apre_op_id in mscp.pb_attr.landmarks \
                    and self.remove_op_id not in mscp.pb_attr.apost[self.apre_op_id]:
                mscp_updates.append(MURemoveOperator(self.remove_op_id))

            return Operation.Outcome.SUCCESS, mscp_updates
        except KeyError:
            return Operation.Outcome.FAILED, []


@attr.s
class MUAddFluentToPrePos(MscpUpdate):
    """
    Add a fluent to the positive preconditions of an operator
    """
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        try:
            mscp_updates = []
            operator = mscp.problem.get_operator_by_id(self.op_id)
            operator.pre_pos.add(self.fluent)

            return Operation.Outcome.SUCCESS, mscp_updates

        except OperatorDisabledException:
            return Operation.Outcome.FAILED, []


@attr.s
class MUAddFluentToPreNeg(MscpUpdate):
    """
    Add a fluent to the negative preconditions of an operator
    """
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        try:
            mscp_updates = []
            operator = mscp.problem.get_operator_by_id(self.op_id)
            operator.pre_neg.add(self.fluent)

            return Operation.Outcome.SUCCESS, mscp_updates

        except OperatorDisabledException:
            return Operation.Outcome.FAILED, []


@attr.s
class MUAddFluentToGoalNeg(MscpUpdate):
    """
    Add an operator to the negative preconditions of an operator
    """
    fluent: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        mscp_updates = []
        mscp.problem.goal_neg.append(self.fluent)

        return Operation.Outcome.SUCCESS, mscp_updates


@attr.s
class MURemoveOperatorFromAPost(MscpUpdate):
    """
    Remove an operator from the list of the operators that can be applied after another
    """
    apost_op_id: int = attr.ib()  # Operator of which we consider the a_post
    remove_op_id: int = attr.ib()  # Operator to be removed

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        try:
            mscp_updates = []
            mscp.pb_attr.apost[self.apost_op_id].remove(self.remove_op_id)

            if (not mscp.problem.is_operator_disabled(self.remove_op_id)) \
                    and self.apost_op_id in mscp.pb_attr.landmarks \
                    and self.remove_op_id not in mscp.pb_attr.apre[self.apost_op_id]:
                mscp_updates.append(MURemoveOperator(self.remove_op_id))

            return Operation.Outcome.SUCCESS, mscp_updates
        except KeyError:
            return Operation.Outcome.FAILED, []


@attr.s
class MUAddMutex(MscpUpdate):
    """
    Mark an unordered pair of fluents as a mutex of the STRIPS instance
    """
    f1_id: int = attr.ib()
    f2_id: int = attr.ib()

    def apply(self, mscp) -> tuple[Operation.Outcome, list]:
        mscp.pb_attr.mutexes.add({self.f1_id, self.f2_id})
        return Operation.Outcome.SUCCESS, []
