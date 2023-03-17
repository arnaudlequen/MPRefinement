from typing import List

import attr

import mscp
import mscp_update as moup
from mscp_exceptions import OperatorDisabledException, ImpossibleModelChangeException
from mscp_criterion_struct import ResourceShortageCriterionStruct
from mscp_rules import Criterion, LPOptimization
from linear_program import *
import model_change as moch
from mscp_rules import Test, Operation, CriterionLP, GlobalTest


@attr.s
class SolvabilityTest(Test):
    """
    Dry test to check if the instance can be immediately decided as Unsat
    """
    def build_model_changes(self, mscp) -> moch.ModelChange:
        return moch.ModelChange()

    def initialize_criterion(self):
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        # real return type: tuple[Operation.Outcome, List[moup.MscpUpdate]]
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            return Operation.Outcome.UNSAT, []

        return Operation.Outcome.STABLE, []


@attr.s
class SolvabilityTest(Test):
    """
    Dry test to check if the instance can be immediately decided as Unsat
    """
    def build_model_changes(self, mscp) -> moch.ModelChange:
        return moch.ModelChange()

    def initialize_criterion(self):
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        # real return type: tuple[Operation.Outcome, List[moup.MscpUpdate]]
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            return Operation.Outcome.UNSAT, []

        return Operation.Outcome.STABLE, []


@attr.s
class MinOpCountOperation(Operation):
    """
    Try to find a lower bound on the minimum number of times an operator has to be applied in any plan
    """
    op_id: int = attr.ib()

    def initialize_criterion(self):
        return OperatorCountingLPOptimization()

    def apply(self, mscp):
        """
        Create and apply the model changes
        """

        # Initialize the criterion
        criterion = self.initialize_criterion()

        # Apply the criterion
#        def apply_single(self, problem: StripsProblem, op_id: int, steps_duration, certificate_path, silent=False):

        crit_outcome, op_count_value = criterion.apply_single(mscp, self.op_id, {}, None, silent=True)

        # If the criterion is successful, apply the changes to the MSCP
        return self.resolve(mscp, crit_outcome, op_count_value)  # TODO: Add more generic arguments

    def resolve(self, mscp, crit_outcome, op_count_value) -> tuple[Operation.Outcome, list]:
        if crit_outcome == LPOptimization.Outcome.NEGATIVE:
            return Operation.Outcome.UNSAT, []
        elif crit_outcome == LPOptimization.Outcome.POSITIVE and op_count_value == 0:
            return Operation.Outcome.STABLE, []
        elif crit_outcome == LPOptimization.Outcome.POSITIVE:
            return Operation.Outcome.SUCCESS, [moup.MUUpdateMinOpCount(self.op_id, op_count_value)]
        return Operation.Outcome.FAILED, []


@attr.s
class MaxOpCountOperation(Operation):
    """
    Try to find an upper bound on the maximum number of times an operator has to be applied in any plan
    """
    op_id: int = attr.ib()

    def initialize_criterion(self):
        return MaxOperatorCountingLPOptimization()

    def apply(self, mscp):
        """
        Create and apply the model changes
        """

        # Initialize the criterion
        criterion = self.initialize_criterion()

        # Apply the criterion
#        def apply_single(self, problem: StripsProblem, op_id: int, steps_duration, certificate_path, silent=False):

        crit_outcome, op_count_value = criterion.apply_single(mscp, self.op_id, {}, None, silent=True)

        # If the criterion is successful, apply the changes to the MSCP
        return self.resolve(mscp, crit_outcome, op_count_value)  # TODO: Add more generic arguments

    def resolve(self, mscp, crit_outcome, op_count_value) -> tuple[Operation.Outcome, list]:
        if crit_outcome == LPOptimization.Outcome.NEGATIVE:
            return Operation.Outcome.UNSAT, []
        elif crit_outcome == LPOptimization.Outcome.POSITIVE:
            return Operation.Outcome.SUCCESS, [moup.MUUpdateMaxOpCount(self.op_id, op_count_value)]
        return Operation.Outcome.FAILED, []


@attr.s
class LandmarkTest(Test):
    op_id: int = attr.ib()

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()
        model_change.add(moch.RemoveOperator(self.op_id))

        return model_change

    def initialize_criterion(self):
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Operator {self.op_id} is a landmark")
            mscp_updates = [moup.MUAddLandmark(self.op_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class ActionPreImpossibleTest(Test):
    op_id: int = attr.ib()

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()

        strict_predecessors = mscp.pb_attr.apre[self.op_id].difference({self.op_id})
        model_change.add(moch.ChangeOperatorSet(strict_predecessors))

        model_change.add(moch.ChangeGoalState(mscp.pb_attr.spre[self.op_id]))

        return model_change

    def initialize_criterion(self) -> CriterionLP:
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"ActPrImp: Operator {self.op_id} can be removed")
            mscp_updates = [moup.MURemoveOperator(self.op_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class OperatorMutexTest(Test):
    op1_id: int = attr.ib()
    op2_id: int = attr.ib()

    def test(self, mscp) -> bool:
        return not (mscp.problem.is_operator_disabled(self.op1_id) or mscp.problem.is_operator_disabled(self.op2_id))

    def build_model_changes(self, mscp) -> moch.ModelChange:
        return moch.ModelChange()

    def initialize_criterion(self) -> CriterionLP:
        return OpMutexLPCriterion(self.op1_id, self.op2_id)

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Operators {self.op1_id} and {self.op2_id} are mutex")
            mscp_updates = [moup.MUAddOperatorMutex(self.op1_id, self.op2_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class ActionDeadlockTest(Test):
    op_id: int = attr.ib()

    def build_model_changes(self, mscp) -> moch.ModelChange:
        try:
            operator = mscp.problem.get_operator_by_id(self.op_id)
        except OperatorDisabledException:
            raise ImpossibleModelChangeException

        relevant_fluents = mscp.problem.apply_operator_on_state(operator, set(mscp.pb_attr.spre[self.op_id]))

        strict_successors = mscp.pb_attr.apost[self.op_id].difference({self.op_id})

        projected_goal = mscp.pb_attr.spre[self.op_id].intersection(relevant_fluents)

        model_change = moch.ModelChange()
        model_change.add(moch.ProjectOnFluentSet(relevant_fluents))
        model_change.add(moch.ChangeOperatorSet(strict_successors))
        model_change.add(moch.ChangeInitialState(list(relevant_fluents)))
        model_change.add(moch.ChangeGoalState(projected_goal))

        return model_change

    def initialize_criterion(self) -> CriterionLP:
        # return CriterionLPORTools()
        return DoubleOpCountCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"ActDLock: Operator {self.op_id} can be removed")
            mscp_updates = [moup.MURemoveOperator(self.op_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


class EnergyFluentOperatorTest(GlobalTest):

    def initialize_criterion(self) -> CriterionLP:
        return EnergyFluentOperatorCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            return Operation.Outcome.UNSAT, []

        return Operation.Outcome.STABLE, []


class DoubleOpCountTest(GlobalTest):

    def initialize_criterion(self) -> CriterionLP:
        return EnergyFluentOperatorCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            return Operation.Outcome.UNSAT, []

        return Operation.Outcome.STABLE, []

@attr.s
class GoalResourceShortageTest(GlobalTest):
    fluent_id: int = attr.ib()

    def initialize_criterion(self) -> Criterion:
        return ResourceShortageCriterionStruct(self.fluent_id)

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        # if self.fluent_id not in mscp.problem.goal_pos:
        #     # For now, we do not support fluent landmarks, so the only case where we can deduce something from the
        #     # criteria is when we have a goal that can not be established enough times
        #     return Operation.Outcome.FAILED, []

        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            return Operation.Outcome.UNSAT, []

        return Operation.Outcome.STABLE, []


@attr.s
class MutexTest(Test):
    f1_id: int = attr.ib()
    f2_id: int = attr.ib()

    def test(self, mscp) -> bool:
        return not (mscp.problem.is_fluent_disabled(self.f1_id) or mscp.problem.is_fluent_disabled(self.f2_id))

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()

        model_change.add(moch.ChangeGoalState([self.f1_id, self.f2_id]))

        return model_change

    def initialize_criterion(self) -> CriterionLP:
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Fluents {self.f1_id} and {self.f2_id} are mutex")
            mscp_updates = [moup.MUAddMutex(self.f1_id, self.f2_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class AddPreNegGlobalTest(Test):
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()
        model_change.add(moch.AddFluentToPrePos(self.op_id, self.fluent))

        return model_change

    def initialize_criterion(self):
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Add {self.fluent} to {self.op_id}'s negative preconditions (T1)")
            mscp_updates = [moup.MUAddFluentToPreNeg(self.op_id, self.fluent)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class AddPreNegTest(Test):
    op_id: int = attr.ib()
    fluent: int = attr.ib()

    def test(self, mscp) -> bool:
        if mscp.problem.is_operator_disabled(self.op_id) or mscp.problem.is_fluent_disabled(self.fluent):
            return False
        operator = mscp.problem.get_operator_by_id(self.op_id)
        return self.fluent not in operator.pre_neg

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()
        operator = mscp.problem.get_operator_by_id(self.op_id)
        new_goal = list(operator.pre_pos).copy()
        new_goal.append(self.fluent)
        model_change.add(moch.ChangeGoalState(new_goal))

        return model_change

    def initialize_criterion(self):
        return DoubleOpCountCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Add {self.fluent} to {self.op_id}'s negative preconditions (T2)")
            mscp_updates = [moup.MUAddFluentToPreNeg(self.op_id, self.fluent)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class FluentReachableTest(Test):
    fluent: int = attr.ib()

    def test(self, mscp) -> bool:
        return not mscp.problem.is_fluent_disabled(self.fluent)

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()
        model_change.add(moch.ChangeGoalState([self.fluent]))

        return model_change

    def initialize_criterion(self):
        return DoubleOpCountCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Fluent {self.fluent} is always false")
            mscp_updates = [moup.MURemoveFluent(self.fluent)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class FluentGoalNegTest(Test):
    fluent: int = attr.ib()

    def test(self, mscp) -> bool:
        return not mscp.problem.is_fluent_disabled(self.fluent) and self.fluent not in mscp.problem.goal_pos

    def build_model_changes(self, mscp) -> moch.ModelChange:
        model_change = moch.ModelChange()
        model_change.add(moch.ChangeGoalState(mscp.problem.goal_pos + [self.fluent]))

        return model_change

    def initialize_criterion(self):
        return DoubleOpCountCriterionLP()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Fluent {self.fluent} is false in all goal states")
            mscp_updates = [moup.MUAddNegativeGoal(self.fluent)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []


@attr.s
class ActionOrderingTest(Test):
    op1_id: int = attr.ib()
    op2_id: int = attr.ib()

    def build_model_changes(self, mscp) -> moch.ModelChange:
        try:
            operator2 = mscp.problem.get_operator_by_id(self.op2_id)
        except OperatorDisabledException:
            raise ImpossibleModelChangeException

        relevant_fluents = mscp.problem.apply_operator_on_state(operator2, set(mscp.pb_attr.spre[self.op2_id]))

        relevant_operators = mscp.pb_attr.apost[self.op2_id] \
            .intersection(mscp.pb_attr.apre[self.op1_id]) \
            .difference({self.op1_id, self.op2_id})

        projected_goal = [x for x in mscp.pb_attr.spre[self.op1_id] if x in relevant_fluents]

        model_change = moch.ModelChange()
        model_change.add(moch.ProjectOnFluentSet(relevant_fluents))
        model_change.add(moch.ChangeOperatorSet(relevant_operators))
        model_change.add(moch.ChangeInitialState(list(relevant_fluents)))
        model_change.add(moch.ChangeGoalState(projected_goal))
        # model_change.add(moch.ChangeGoalState(list(mscp.pb_attr.spre[self.op1_id])))

        return model_change

    def initialize_criterion(self) -> CriterionLP:
        return CriterionLPORTools()

    def resolve(self, mscp, crit_outcome) -> tuple[Operation.Outcome, list]:
        if crit_outcome == CriterionLP.Outcome.POSITIVE:
            print(f"Operator {self.op1_id} occurs before operator {self.op2_id}")
            mscp_updates = [moup.MURemoveOperatorFromAPre(apre_op_id=self.op1_id, remove_op_id=self.op2_id)]
            mscp_updates += [moup.MURemoveOperatorFromAPost(apost_op_id=self.op2_id, remove_op_id=self.op1_id)]
            return Operation.Outcome.SUCCESS, mscp_updates
        else:
            return Operation.Outcome.STABLE, []
