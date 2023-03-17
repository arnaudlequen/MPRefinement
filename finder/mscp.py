import collections
import sys

from enum import Enum

import mscp_update as moup
from mscp_criterion_test import *
from mscp_rules import StripsProblemAttributes, Operation, Propagation
from strips_problem import StripsProblem


class Mscp:

    # Progress of the algorithm
    class Status(Enum):
        INIT = 0,
        INCON = 1,  # Inconclusive
        UNSAT = 2,

    # Beginning of the actual class
    status: Status
    problem: StripsProblem
    pb_attr: StripsProblemAttributes

    operation_types = [ActionOrderingTest,
                       ActionPreImpossibleTest,
                       ActionDeadlockTest,
                       AddPreNegTest,
                       FluentGoalNegTest,
                       OperatorMutexTest,
                       LandmarkTest,
                       DoubleOpCountTest,
                       MinOpCountOperation,
                       MaxOpCountOperation,
                       FluentReachableTest,
                       moup.MURemoveOperator]

    def __init__(self, problem: StripsProblem, steps_duration: dict[str, float]):
        self.status = Mscp.Status.INIT
        self.problem = problem
        self.pb_attr = StripsProblemAttributes(problem)
        self.steps_duration = steps_duration

    def initialize_attributes(self):
        """
        Initialize the additional sets
        """
        a_set = set(range(self.problem.get_operator_count()))

        for op_id in range(self.problem.get_operator_count()):
            self.pb_attr.apre[op_id] = a_set.copy()
            self.pb_attr.apost[op_id] = a_set.copy()

            op_pre = self.problem.get_operator_by_id(op_id).pre_pos
            self.pb_attr.spre[op_id] = op_pre

        self.status = Mscp.Status.INCON

    def explore(self, explore_list, nostop):
        """
        Main loop of the algorithm. Tries to apply various operations and return True iff the algorithm can conclude
        that the instance can not be solved
        """
        statistics = {}

        # Find a way to initialize the queue smartly
        items = []

        # Set up the list of tasks to perform
        explore_queue = collections.deque([])
        try:
            with open(explore_list, 'r') as exp_file:
                for line in exp_file.readlines():
                    explore_queue.append(line.strip())
        except FileNotFoundError:
            print(f"Explore list not found: {explore_list}")

        update_queue = collections.deque(items)

        while explore_queue:
            element = explore_queue.popleft()
            self.add_update_queue(update_queue, element)


        # for fluent_id in self.problem.fluents_id:
        #     update_queue.append(GoalResourceShortageTest(fluent_id))
        ## TEMP END

        for operation_type in self.operation_types:
            statistics[operation_type.__qualname__] = 0

        final_outcome = False

        while update_queue:
            current_operation = update_queue.popleft()

            outcome, new_operations = current_operation.apply(self)
            if outcome == Operation.Outcome.UNSAT:
                # The instance is not solvable
                final_outcome = True
                if not nostop:
                    break

            # Put this in a function that updates the statistics more generally
            self.update_statistics(statistics, current_operation, outcome)

            # Depending on the nature of the operation that we applied, add MscpUpdates' operations at the end of the
            # queue, or Operations' MscpUpdates at the beginning
            # if isinstance(current_operation, moup.MscpUpdate):
            #     for mscp_update in new_operations:
            #         update_queue.appendleft(mscp_update)
            # else:
            #     for operation in new_operations:
            #         update_queue.appendleft(operation)

            # Actually, always add on top of the stack the new operations
            for operation in new_operations:
                update_queue.appendleft(operation)

        # print(self.problem)
        # print(self.pb_attr)

        print()
        print("Statistics:")
        print('-'*24)

        print(f"Percentage of removed operators: "
              f"{statistics[moup.MURemoveOperator.__qualname__] / self.problem.get_max_operator_id() * 100:.2f}%")

        print(f"- through PreImpossibleTest: "
              f"{statistics[ActionPreImpossibleTest.__qualname__] / self.problem.get_max_operator_id() * 100:.2f}%")

        print(f"Added negative preconditions: "
              f"{statistics[AddPreNegTest.__qualname__]}")

        print(f"Added negative goals: "
              f"{statistics[FluentGoalNegTest.__qualname__]}")

        print(f"Operator mutex found: "
              f"{statistics[OperatorMutexTest.__qualname__]}")

        print(f"Landmarks found: "
              f"{len(self.pb_attr.landmarks)} / {self.problem.get_operator_count()} "
              f"({len(self.pb_attr.landmarks) / self.problem.get_operator_count() * 100:.2f}%)")

        total_orderings = self.problem.get_operator_count() * (self.problem.get_operator_count() - 1) // 2
        print(f"Orderings found: "
              f"{statistics[ActionOrderingTest.__qualname__]} / {total_orderings} "
              f"({statistics[ActionOrderingTest.__qualname__] / total_orderings * 100:.2f}%)")

        return final_outcome, statistics

    def update_statistics(self, statistics, current_operation, outcome):
        for operation_type in Mscp.operation_types:
            if not isinstance(current_operation, operation_type):
                continue
            if outcome == Operation.Outcome.SUCCESS:
                statistics[operation_type.__qualname__] += 1
            break

    def add_update_queue(self, update_queue, element):
        match element:
            case 'SolvabilityTest':
                update_queue.append(SolvabilityTest())
                return

            case 'EnergyFluentOperatorTest':
                update_queue.append(EnergyFluentOperatorTest())
                return

            case 'DoubleOpCountTest':
                update_queue.append(DoubleOpCountTest())
                return

            case 'LandmarkTest':
                for op_id in self.problem.operators_id:
                    update_queue.append(LandmarkTest(op_id))
                return

            case 'ActionPreImpossibleTest':
                for op_id in self.problem.operators_id:
                    update_queue.append(ActionPreImpossibleTest(op_id))
                return

            case 'ActionDeadlockTest':
                for op_id in self.problem.operators_id:
                    update_queue.append(ActionDeadlockTest(op_id))
                return

            case 'OperationCountOperation':
                for op_id in self.problem.operators_id:
                    update_queue.append(MinOpCountOperation(op_id))
                return

            case 'MaxOpCountOperation':
                for op_id in self.problem.operators_id:
                    update_queue.append(MaxOpCountOperation(op_id))
                return

            case 'FluentReachableTest':
                for fluent in self.problem.fluents_id:
                    if fluent not in self.problem.init_pos:
                        update_queue.append(FluentReachableTest(fluent))
                return

            case 'FluentGoalNegTest':
                for fluent in self.problem.fluents_id:
                    update_queue.append(FluentGoalNegTest(fluent))
                return

            case 'OperatorMutexTest':
                for op1_id in self.problem.operators_id:
                    for op2_id in self.problem.operators_id:
                        if op1_id >= op2_id:
                            update_queue.append(OperatorMutexTest(op1_id, op2_id))
                    update_queue.append(DoubleOpCountTest())
                return

            case 'AddPreNegTest':
                for fluent in self.problem.fluents_id:
                    for op_id in self.problem.operators_id:
                        update_queue.append(AddPreNegTest(op_id, fluent))
                    update_queue.append(DoubleOpCountTest())
                return

            case 'MutexTest':
                for f1_id in self.problem.fluents_id:
                    for f2_id in self.problem.fluents_id:
                        if f1_id > f2_id:
                            update_queue.append(MutexTest(f1_id, f2_id))
                return

            case 'ActionOrderingTest':
                for op1_id in self.problem.operators_id:
                    for op2_id in self.problem.operators_id:
                        if op1_id != op2_id:
                            update_queue.append(ActionOrderingTest(op1_id, op2_id))
                return

            case 'ResourceShortageTest':
                for fluent_id in self.problem.fluents_id:
                    update_queue.append(GoalResourceShortageTest(fluent_id))
                return

            case _:
                print(f"Unknown operation: {element}")
