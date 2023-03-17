import attr

from mscp_exceptions import OperatorDisabledException
from parser.ast_types import *
from data_structures import OperatorProfile
import math
from typing import List, Dict


@attr.s
class StripsProblem:
    predicate_to_varId: dict = attr.ib()
    varId_to_predicate: dict = attr.ib()

    # All mentions to PDDL refer to grounded PDDL predicates and actions
    # Convention: action in PDDL, operator in STRIPS
    action_to_opId: dict = attr.ib()
    opId_to_action: dict = attr.ib()
    opId_to_operator: Dict[int, Operator] = attr.ib()

    init_pos: list = attr.ib()
    init_neg: list = attr.ib()
    goal_pos: list = attr.ib()
    goal_neg: list = attr.ib()

    # Modified elements
    disabled_fluents: list = attr.ib(init=False)
    disabled_operators: list = attr.ib(init=False)

    # True properties
    fluent_count: int = attr.ib(init=False)
    operator_count: int = attr.ib(init=False)

    # Statistics
    max_pre_arity: int = attr.ib(init=False, default=0)
    max_eff_arity: int = attr.ib(init=False, default=0)

    # Constraint iteration
    operators_profiles: List[OperatorProfile] = attr.ib(init=False)

    def __attrs_post_init__(self):
        n = len(self.varId_to_predicate)
        m = len(self.opId_to_action)

        # Allows us not to recompute the number of active elements everytime it's needed
        self.true_fluent_count = n  # Constant
        self.true_operator_count = m  # Constant
        self.fluent_count = n
        self.operator_count = m

        # There must be a way to initialize this otherwise
        self.operators_profiles = [OperatorProfile()] * m

        # Elements that might be removed later
        self.disabled_fluents = [False] * n
        self.disabled_operators = [False] * m

        for i in range(m):
            op = self.opId_to_operator[i]

            prep_to_effn = len(set(op.pre_pos).intersection(set(op.eff_neg)))
            pren_to_effp = len(set(op.pre_neg).intersection(set(op.eff_pos)))

            op_profile = OperatorProfile(len(op.pre_pos), len(op.pre_neg),
                                         len(op.eff_pos), len(op.eff_neg),
                                         prep_to_effn, pren_to_effp)

            self.operators_profiles[i] = op_profile

    def pretty_print_action_by_op_id(self, op_id):
        """
        Pretty print a grounded STRIPS action
        """
        # TODO: rework it all, redundancy with something that is already in Grounder.py
        operator = self.opId_to_operator[op_id]

        action_name = operator.name
        pre_pos, pre_neg = operator.pre_pos, operator.pre_neg
        eff_pos, eff_neg = operator.eff_pos, operator.eff_neg

        flat_fluents = [' '.join(map(lambda x: self.varId_to_predicate[x], l)) for l in [pre_pos, pre_neg, eff_pos, eff_neg]]
        pre_eff = ' '.join([f"({fluents})" for fluents in flat_fluents])
        return f"<{action_name}: {pre_eff}>"

    def __str__(self):
        f_digit = math.ceil(math.log10(len(self.varId_to_predicate) + 1))
        o_digit = math.ceil(math.log10(len(self.opId_to_action) + 1))
        s  = f'Fluents: {self.get_fluent_count()} fluents \n'
        s += '\n'.join([f" {f_id: >{f_digit}}: {f_name}"
                        for f_id, f_name in self.varId_to_predicate.items() if not self.disabled_fluents[f_id]])
        s += '\n'
        s += f'Operators: {self.get_operator_count()} operators\n'
        # s += '\n'.join([f" {o_id: >{o_digit}}: {o_name}" for o_id, o_name in self.opId_to_action.items()])
        s += '\n'.join([f" {o_id: >{o_digit}}: {op}"
                        for o_id, op in self.opId_to_operator.items() if not self.disabled_operators[o_id]])
        s += '\n'
        s += 'Initial state:\n'
        s += '+ '
        s += ' '.join(list(map(str, self.init_pos)))
        s += '\n'
        s += '- '
        s += ' '.join(list(map(str, self.init_neg)))
        s += '\n'
        s += 'Goal:\n'
        s += '+ '
        s += ' '.join(list(map(str, self.goal_pos)))
        s += '\n'
        s += '- '
        s += ' '.join(list(map(str, self.goal_neg)))

        return s

    def remove_fluent(self, fluent_id):
        # Remove from init and goal
        lsts = [self.init_pos, self.init_neg,
                self.goal_pos, self.goal_neg]

        for lst in lsts:
            if fluent_id in lst:
                lst.remove(fluent_id)

        # Remove from each operator
        for operator in self.opId_to_operator.values():
            operator.remove_fluent(fluent_id)

        # Update global information
        self.disabled_fluents[fluent_id] = True
        self.fluent_count -= 1

    def remove_operator(self, op_id):
        # Update global information
        if self.disabled_operators[op_id]:
            raise OperatorDisabledException
        self.disabled_operators[op_id] = True
        self.operator_count -= 1

    def copy(self):
        # TODO: Check that the copy is in depth
        # TODO: Allow for partial in-depth copy (shallow copy of operators but not of fluents, for instance)
        predicate_to_var_id = self.predicate_to_varId.copy()
        var_id_to_predicate = self.varId_to_predicate.copy()
        action_to_op_id = self.action_to_opId.copy()
        op_id_to_action = self.opId_to_action.copy()
        init_pos = self.init_pos.copy()
        init_neg = self.init_neg.copy()
        goal_pos = self.goal_pos.copy()
        goal_neg = self.goal_neg.copy()

        op_id_to_operator = {}
        for op_id, operator in self.opId_to_operator.items():
            op_id_to_operator[op_id] = operator.copy()

        problem = StripsProblem(predicate_to_var_id, var_id_to_predicate,
                                action_to_op_id, op_id_to_action,
                                op_id_to_operator,
                                init_pos, init_neg,
                                goal_pos, goal_neg)

        # Update the problem to include disabled elements
        problem.disabled_fluents = self.disabled_fluents.copy()
        problem.disabled_operators = self.disabled_operators.copy()
        problem.fluent_count = self.fluent_count
        problem.operator_count = self.operator_count

        return problem

    # Helper methods
    @staticmethod
    def apply_operator_on_state(operator: Operator, state: set):
        if not set(operator.pre_pos).issubset(state):
            return None
        return state.difference(operator.eff_neg).union(operator.eff_pos)

    # Operators and fluents accessors
    @property
    def operators(self):
        for op_id in range(self.true_operator_count):
            if not self.disabled_operators[op_id]:
                yield self.opId_to_operator[op_id]

    @property
    def operators_id(self):
        for op_id in range(self.true_operator_count):
            if not self.disabled_operators[op_id]:
                yield op_id

    @property
    def fluents_id(self):
        for fluent_id in range(self.true_fluent_count):
            if not self.disabled_fluents[fluent_id]:
                yield fluent_id

    # Enumerators
    def enumerate_op_id(self):
        for op_id in range(self.true_operator_count):
            if not self.disabled_operators[op_id]:
                yield op_id

    def enumerate_op(self):
        for op_id in range(self.true_operator_count):
            if not self.disabled_operators[op_id]:
                yield self.opId_to_operator[op_id]

    def enumerate_fluent_id(self):
        for fluent_id in range(self.true_fluent_count):
            if not self.disabled_fluents[fluent_id]:
                yield fluent_id

    # Getters for primordial elements of the problem
    def get_initial_state(self):
        return self.init_pos, self.init_neg

    def get_goal_state(self):
        return self.goal_pos, self.goal_neg

    # Getters for statistics about the problem
    def get_fluent_count(self):
        return self.fluent_count

    def get_operator_count(self):
        return self.operator_count

    # Getters for technical elements of the problem
    def get_max_fluent_id(self):
        return self.true_fluent_count

    def get_max_operator_id(self):
        return self.true_operator_count

    def is_fluent_disabled(self, var_id):
        return self.disabled_fluents[var_id]

    def is_operator_disabled(self, op_id):
        return self.disabled_operators[op_id]

    # Getters for items of the problem
    def get_operator_profile(self, op_id: int):
        if not self.disabled_operators[op_id]:
            return self.operators_profiles[op_id]
        return None

    def get_fluent_name(self, var_id):
        if not self.disabled_fluents[var_id]:
            return self.varId_to_predicate[var_id]
        return None

    def get_operator_name(self, op_id):
        return self.opId_to_action[op_id]

    def get_predicate_by_var_id(self, var_id):
        if not self.disabled_fluents[var_id]:
            return self.varId_to_predicate[var_id]
        return None

    def get_var_id_by_predicate(self, predicate):
        return self.predicate_to_varId[predicate]

    def get_action_by_op_id(self, op_id):
        if not self.disabled_operators[op_id]:
            return self.opId_to_action[op_id]
        return None

    def get_operator_by_id(self, op_id):
        if self.disabled_operators[op_id]:
            raise OperatorDisabledException
        return self.opId_to_operator[op_id]

    def get_operator_id(self, operator):
        op_name = operator.name
        op_id = self.action_to_opId[op_name]
        if self.disabled_operators[op_id]:
            raise OperatorDisabledException
        return op_id

    # Deep copy
    def copy_replace_operator_by_id(self, op_id):
        new_operator = self.get_operator_by_id(op_id).copy()
        self.opId_to_operator[op_id] = new_operator
        # Note: operator profiles not taken into account
        return new_operator
