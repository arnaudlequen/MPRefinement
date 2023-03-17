import contextlib
import math
from enum import Enum

# import gurobipy as gp

from abc import ABC, abstractmethod

import attr
import attrs
# from gurobipy import GRB, MVar
from ortools.linear_solver import pywraplp

from utils import silence_stdout
from mscp_rules import CriterionLP, Operation, LPOptimization
from strips_problem import StripsProblem
from time import perf_counter

# EPSILON = sys.float_info.epsilon
EPSILON = 10
filler = '=' * 30

NEGATED_PREFIX = 'Negated_'

# TODO: IMPORTANT
# TODO: Update everything so that we use the new method for enumerating operators/fluents (skipping disabled fluents)


class CriterionLPGurobi(CriterionLP):

    def apply_single(self, mscp, pb_attr, steps_duration, certificate_path, silent=False):
        # Translation to a LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model = CriterionLPGurobi.create_model(problem, silent)

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Solving...")
            print(filler)

        model.optimize()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Solving done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        iis_pruned = []

        if not silent:
            print("Result")
            print(filler)

        # Status 3: Infeasible
        if not model.getAttr('Status') == 3:
            outcome = CriterionLP.Outcome.POSITIVE
            if not silent:
                print('NO PLAN EXISTS')
        else:
            outcome = CriterionLP.Outcome.NEGATIVE
            if not silent:
                print('NO FEASIBLE REGION')

            model.computeIIS()

            iis_pruned = []
            for c in model.getConstrs():
                if c.IISConstr and c.constrName.startswith('op'):
                    iis_pruned.append(int(c.constrName[2:]))

        return outcome, iis_pruned

    @staticmethod
    def create_model(problem: StripsProblem, silent: bool):
        env = gp.Env(empty=True)
        if silent:
            env.setParam('OutputFlag', 0)
            env.setParam('LogToConsole', 0)

        # Do this when the licence is installed
        # model = gp.Model(env=env)
        model = gp.Model()
        lp_vars = model.addVars(list(range(problem.get_max_fluent_id())), vtype=GRB.CONTINUOUS, name="f")

        # Todo: check if MVar() is more appropriate?
        goal_pos_var = MVar([lp_vars[f] for f in problem.get_goal_state()[0]])
        init_pos_var = MVar([lp_vars[f] for f in problem.get_initial_state()[0]])
        model.addConstr(goal_pos_var.sum() - init_pos_var.sum() >= EPSILON, name='energydelta')

        # Action constraints
        constraints_count = 0
        for operator_id in problem.enumerate_op_id():
            operator = problem.get_operator_by_id(operator_id)
            if operator.is_empty():
                continue
            positive_op_vars = []
            negative_op_vars = []

            for f in operator.eff_pos:
                if f not in operator.pre_pos:
                    positive_op_vars.append(lp_vars[f])

            for f in operator.eff_neg:
                if f in operator.pre_pos and f not in operator.eff_pos:
                    negative_op_vars.append(lp_vars[f])

            constraints_count += 1

            model.addConstr(MVar(positive_op_vars).sum() - MVar(negative_op_vars).sum() <= 0, name=f'op{operator_id}')

        return model


class CriterionLPORTools(CriterionLP):

    def apply_single(self, problem, pb_attr, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model, lpvars = CriterionLPORTools.create_lp_model(problem)

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Solving...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Solving done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            outcome = CriterionLP.Outcome.POSITIVE
            if not silent:
                print('NO PLAN EXISTS')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    string_values = [f' {problem.get_fluent_name(i)} = {lpvars[i].solution_value()}'
                                     for i in range(len(lpvars)) if lpvars[i].solution_value() != 0]
                    f.write('\n'.join(string_values))
        else:
            outcome = CriterionLP.Outcome.NEGATIVE
            if not silent:
                print('NO FEASIBLE REGION')

        # return outcome, []    where [] is the IIS
        return outcome

    @staticmethod
    def create_lp_model(problem):
        # Creates the model.
        model = pywraplp.Solver.CreateSolver('GLOP')
        # model = pywraplp.Solver_CreateSolver('GUROBI_LP')

        # Creates the variables.
        num_vars = problem.get_max_fluent_id() + 1
        digits = math.ceil(math.log10(num_vars))
        lp_vars = [model.NumVar(0, model.infinity(), f'f{i:0>{digits}}') for i in range(num_vars - 1)]
        # The following line is for debugging purpose
        # lpv_to_name = {lp_vars[i]: problem.get_fluent_name(i) for i in range(num_vars - 1)}

        # Creates the constraints.
        # TODO: check that fluents of the form "=(.., ..)" can be added safely
        goal_pos_var = [lp_vars[f] for f in problem.get_goal_state()[0]]
        init_pos_var = [lp_vars[f] for f in problem.get_initial_state()[0]]

        model.Add(model.Sum(goal_pos_var) - model.Sum(init_pos_var) >= EPSILON)

        #
        # Action constraints
        constraints_count = 0
        for operator in problem.enumerate_op():
            if operator is None or operator.is_empty():
                continue
            positive_op_vars = []
            negative_op_vars = []

            for f in operator.eff_pos:
                if f not in operator.pre_pos:
                    positive_op_vars.append(lp_vars[f])

            for f in operator.eff_neg:
                if f in operator.pre_pos and f not in operator.eff_pos:
                    negative_op_vars.append(lp_vars[f])

            constraints_count += 1

            model.Add(model.Sum(positive_op_vars) - model.Sum(negative_op_vars) <= 0)

        # print(f'Test with {constraints_count} op constraints')
        return model, lp_vars  # , b


class OperatorCountingLPOptimization(LPOptimization):
    """
    Find the minimum number of times an operation has to be done in any plan
    """

    def apply_single(self, mscp, op_id: int, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model, y = DoubleOpCountCriterionLP.create_lp_model(mscp.problem, mscp.pb_attr, int_vars=True)
        model.Minimize(y[op_id])

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Optimizing...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Optimization done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        optimal_value = float('inf')

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            outcome = LPOptimization.Outcome.POSITIVE
            optimal_value = math.floor(model.Objective().Value())
            if not silent:
                print(f'Optimal value: {model.Objective().Value()}')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    pass
        elif status == pywraplp.Solver.INFEASIBLE:
            outcome = LPOptimization.Outcome.NEGATIVE
            if not silent:
                print('NO SOLUTION FOUND')
        else:
            outcome = LPOptimization.Outcome.ERROR

        return outcome, optimal_value

    @staticmethod
    def create_lp_model(mscp, op_id):
        problem = mscp.problem

        # Creates the model.
        model = pywraplp.Solver.CreateSolver('SCIP')

        # Creates the variables.
        num_vars = problem.get_max_operator_id()
        digits = math.ceil(math.log10(num_vars))
        y = [model.IntVar(0, model.infinity(), f'o{i:0>{digits}}') for i in range(num_vars)]
        # The following line is for debugging purpose
        # lpv_to_name = {lp_vars[i]: problem.get_fluent_name(i) for i in range(num_vars - 1)}

        # Compute the minimum net changes
        net_change_sup = [0] * problem.get_max_fluent_id()
        net_change_inf = [0] * problem.get_max_fluent_id()
        for f in problem.fluents_id:
            in_goal_pos = int(f in problem.get_goal_state()[0])
            in_goal_neg = int(f in problem.get_goal_state()[1])
            in_initial_pos = int(f in problem.get_initial_state()[0])
            # in_initial_neg = int(f in problem.get_initial_state()[1])
            net_change_sup[f] = 1 - in_initial_pos - in_goal_neg
            net_change_inf[f] = in_goal_pos - in_initial_pos

        # Creates the constraints
        constraints_count = 0

        # Fluent counting
        strict_effects = [[] for _ in range(problem.get_max_fluent_id())]
        strict_deletes = [[] for _ in range(problem.get_max_fluent_id())]
        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            for f in c_operator.eff_pos:
                if f not in c_operator.pre_pos and not problem.is_fluent_disabled(f):
                    strict_effects[f].append(y[c_op_id])

            for f in c_operator.eff_neg:
                if f in c_operator.pre_pos and f not in c_operator.eff_pos and not problem.is_fluent_disabled(f):
                    strict_deletes[f].append(y[c_op_id])

        for f in problem.fluents_id:
            if not (strict_effects[f] or strict_deletes[f]):
                continue
            constraints_count += 1
            constraint = model.Sum(strict_effects[f]) - model.Sum(strict_deletes[f]) >= net_change_inf[f]
            model.Add(constraint)

        # Minimum count of known operators
        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            c_min_op = mscp.pb_attr.min_op_count[c_op_id]
            if c_min_op > 0:
                model.Add(y[c_op_id] >= c_min_op)

        # Function to optimize
        model.Minimize(y[op_id])

        # print(f'Optimization with {constraints_count} op constraints')
        return model, y  # , b


class MaxOperatorCountingLPOptimization(LPOptimization):
    """
    Find the minimum number of times an operation has to be done in any plan
    """

    def apply_single(self, mscp, op_id: int, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model, y = DoubleOpCountCriterionLP.create_lp_model(mscp.problem, mscp.pb_attr, int_vars=True)
        model.Maximize(y[op_id])

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Optimizing...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Optimization done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        optimal_value = float('inf')

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            outcome = LPOptimization.Outcome.POSITIVE
            optimal_value = math.ceil(model.Objective().Value())
            if not silent:
                print(f'Optimal value: {model.Objective().Value()}')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    pass
        # elif status == pywraplp.Solver.UNBOUNDED:
        #     outcome = LPOptimization.Outcome.POSITIVE
        #     optimal_value = float('inf')
        #     print("INF")
        # elif pywraplp.Solver.INFEASIBLE:
        #     outcome = LPOptimization.Outcome.NEGATIVE
        #     optimal_value = float('inf')
        #     print('NO SOLUTION FOUND')
        else:
            outcome = LPOptimization.Outcome.ERROR

        return outcome, optimal_value

    @staticmethod
    def create_lp_model(mscp, op_id):
        problem = mscp.problem

        # Creates the model.
        model = pywraplp.Solver.CreateSolver('SCIP')

        # Creates the variables.
        num_vars = problem.get_max_operator_id()
        digits = math.ceil(math.log10(num_vars))
        y = [model.IntVar(0, model.infinity(), f'o{i:0>{digits}}') for i in range(num_vars)]
        # The following line is for debugging purpose
        # lpv_to_name = {lp_vars[i]: problem.get_fluent_name(i) for i in range(num_vars - 1)}

        # Compute the minimum net changes
        net_change = [0] * problem.get_max_fluent_id()
        for f in problem.fluents_id:
            in_goal = int(f in problem.get_goal_state()[0])
            in_initial = int(f in problem.get_initial_state()[0])
            net_change[f] = in_goal - in_initial

        # Creates the constraints
        constraints_count = 0

        # Fluent counting
        strict_effects = [[] for _ in range(problem.get_max_fluent_id())]
        strict_deletes = [[] for _ in range(problem.get_max_fluent_id())]
        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            for f in c_operator.eff_pos:
                if f not in c_operator.pre_pos and not problem.is_fluent_disabled(f):
                    strict_effects[f].append(y[c_op_id])

            for f in c_operator.eff_neg:
                if f in c_operator.pre_pos and f not in c_operator.eff_pos and not problem.is_fluent_disabled(f):
                    strict_deletes[f].append(y[c_op_id])

        for f in problem.fluents_id:
            if not (strict_effects[f] or strict_deletes[f]):
                continue
            constraints_count += 1
            constraint = model.Sum(strict_effects[f]) - model.Sum(strict_deletes[f]) >= net_change[f]
            model.Add(constraint)

        # Minimum count of known operators
        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            c_min_op = mscp.pb_attr.min_op_count[c_op_id]
            if c_min_op > 0:
                model.Add(y[c_op_id] >= c_min_op)

        # Function to optimize
        model.Maximize(y[op_id])

        # print(f'Optimization with {constraints_count} op constraints')
        return model, y  # , b


class EnergyFluentOperatorCriterionLP(CriterionLP):
    """
    Enhanced energy-based program which also takes into consideration the energy of actions
    """

    def apply_single(self, mscp, pb_attr, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        problem = mscp.problem

        if not silent:
            print("Creating model...")
            print(filler)

        model, lpvars = EnergyFluentOperatorCriterionLP.create_lp_model(mscp)

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Solving...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Solving done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            outcome = CriterionLP.Outcome.POSITIVE
            if not silent:
                print('NO PLAN EXISTS')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    string_values = [f' {problem.get_fluent_name(i)} = {lpvars[i].solution_value()}'
                                     for i in range(len(lpvars)) if lpvars[i].solution_value() != 0]
                    f.write('\n'.join(string_values))
        else:
            outcome = CriterionLP.Outcome.NEGATIVE
            if not silent:
                print('NO FEASIBLE REGION')

        # return outcome, []    where [] is the IIS
        return outcome

    @staticmethod
    def create_lp_model(mscp):
        # Creates the model.
        model = pywraplp.Solver.CreateSolver('GLOP')

        problem = mscp.problem

        # Creates the variables.
        # TODO: Check why I choose not to make the variables start at 0
        num_vars = (problem.get_max_fluent_id() + 1) + (problem.get_max_operator_id())
        digits = math.ceil(math.log10(num_vars))
        lp_vars_f = [model.NumVar(0, model.infinity(), f'f{i:0>{digits}}')
                     for i in range(problem.get_max_fluent_id() + 1)]
        lp_vars_o = [model.NumVar(0, model.infinity(), f'o{i:0>{digits}}')
                     for i in range(problem.get_max_operator_id() + 1)]

        lp_vars = lp_vars_f + lp_vars_o
        # The following line is for debugging purpose
        # lpv_to_name = {lp_vars[i]: problem.get_fluent_name(i) for i in range(num_vars - 1)}

        # Creates the constraints.
        goal_pos_var = [lp_vars_f[f] for f in problem.get_goal_state()[0]]
        init_pos_var = [lp_vars_f[f] for f in problem.get_initial_state()[0]]

        operators_energy = [mscp.pb_attr.min_op_count[o] * lp_vars_o[o] for o in problem.operators_id]

        model.Add(model.Sum(goal_pos_var) - model.Sum(init_pos_var) + model.Sum(operators_energy) >= EPSILON)

        #
        # Action constraints
        constraints_count = 0
        for op_id in problem.operators_id:
            operator = mscp.problem.get_operator_by_id(op_id)
            if operator is None or operator.is_empty():
                continue
            positive_op_vars = []
            negative_op_vars = []

            for f in operator.eff_pos:
                if f not in operator.pre_pos:
                    positive_op_vars.append(lp_vars_f[f])

            for f in operator.eff_neg:
                if f in operator.pre_pos and f not in operator.eff_pos:
                    negative_op_vars.append(lp_vars_f[f])

            constraints_count += 1

            model.Add(model.Sum(positive_op_vars) - model.Sum(negative_op_vars) + lp_vars_o[op_id] <= 0)

        # print(model.ExportModelAsLpFormat(False))

        # print(f"Added {constraints_count+1} constraints")

        return model, lp_vars  # , b


class DoubleOpCountCriterionLP(CriterionLP):
    """
    LP criterion that uses negative preconditions extracted out of an operator
    """

    def apply_single(self, problem, pb_attr, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model, y = self.create_lp_model(problem, pb_attr)

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Optimizing...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Optimization done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        if status == pywraplp.Solver.INFEASIBLE:
            outcome = CriterionLP.Outcome.POSITIVE
            if not silent:
                print('NO PLAN EXISTS')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    string_values = [f' {problem.get_fluent_name(i)} = {y[i].solution_value()}'
                                     for i in range(len(y)) if y[i].solution_value() != 0]
                    f.write('\n'.join(string_values))
        else:
            outcome = CriterionLP.Outcome.NEGATIVE
            if not silent:
                print('NO FEASIBLE REGION')

        return outcome

    @staticmethod
    def create_lp_model(problem: StripsProblem, pb_attr, int_vars=True):

        # Creates the model.
        if int_vars:
            # model = pywraplp.Solver.CreateSolver('CP_SAT')
            model = pywraplp.Solver.CreateSolver('SCIP')
            # model = pywraplp.Solver('SolveIntegerProblem',
            #                pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
            # model = pywraplp.Solver.CreateSolver('SCIP')
        else:
            model = pywraplp.Solver.CreateSolver('GLOP')

        # Creates the variables.
        # Operator variables
        num_vars = problem.get_max_operator_id()
        digits = math.ceil(math.log10(num_vars))
        if int_vars:
            y = [model.IntVar(0, model.infinity(), f'o{i:0>{digits}}') for i in range(num_vars)]
        else:
            y = [model.NumVar(0, model.infinity(), f'o{i:0>{digits}}') for i in range(num_vars)]

        # En passant variables
        # num_passant_vars = problem.get_max_fluent_id()
        # passant_digits = math.ceil(math.log10(num_passant_vars))
        # pp = [model.BoolVar(f'pp{i:0>{passant_digits}}') for i in range(num_passant_vars)]
        # pn = [model.BoolVar(f'pm{i:0>{passant_digits}}') for i in range(num_passant_vars)]

        # Operator usage variables
        u = [model.BoolVar(f'u{i:0>{digits}}') for i in range(num_vars)]

        # Compute the minimum net changes
        net_change_sup = [0] * problem.get_max_fluent_id()
        net_change_inf = [0] * problem.get_max_fluent_id()
        for f in problem.fluents_id:
            in_goal_pos = int(f in problem.get_goal_state()[0])
            in_goal_neg = int(f in problem.get_goal_state()[1])
            in_initial_pos = int(f in problem.get_initial_state()[0])
            # in_initial_neg = int(f in problem.get_initial_state()[1])
            net_change_sup[f] = 1 - in_initial_pos - in_goal_neg
            net_change_inf[f] = in_goal_pos - in_initial_pos

        # Creates the constraints
        constraints_count = 0

        # Preprocessing to form relevant sets
        strict_adds = [[] for _ in range(problem.get_max_fluent_id())]
        strict_deletes = [[] for _ in range(problem.get_max_fluent_id())]
        possible_adds = [[] for _ in range(problem.get_max_fluent_id())]
        possible_deletes = [[] for _ in range(problem.get_max_fluent_id())]

        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            for f in c_operator.eff_pos:
                if problem.is_fluent_disabled(f):
                    continue
                if f in c_operator.pre_neg:
                    strict_adds[f].append(y[c_op_id])
                if f not in c_operator.pre_pos:
                    possible_adds[f].append(y[c_op_id])

            for f in c_operator.eff_neg:
                if problem.is_fluent_disabled(f):
                    continue
                if f in c_operator.pre_pos and f not in c_operator.eff_pos:
                    strict_deletes[f].append(y[c_op_id])
                if f not in c_operator.pre_neg:
                    possible_deletes[f].append(y[c_op_id])

        # Fluent-based constraints
        for f in problem.fluents_id:
            if strict_adds[f] or possible_adds[f] or strict_deletes[f]:
                constraints_count += 1
                constraint = model.Sum(strict_adds[f]) + model.Sum(possible_adds[f]) - \
                             model.Sum(strict_deletes[f]) >= net_change_inf[f]
                model.Add(constraint)

            if strict_adds[f] or possible_deletes[f] or strict_deletes[f]:
                constraints_count += 1
                constraint = model.Sum(strict_adds[f]) - model.Sum(possible_deletes[f]) - \
                             model.Sum(strict_deletes[f]) <= net_change_sup[f]
                model.Add(constraint)

        # En passant constraints
        # unchanged_fluents_pos = set(problem.init_pos + problem.goal_pos)
        # init_neg = set(problem.fluents_id).difference(problem.init_pos)
        # unchanged_fluents_neg = init_neg | set(problem.goal_neg)
        # for op_id in problem.operators_id:
        #     if pb_attr.max_op_count[op_id] in [0, float('inf')]:
        #         continue
        #     operator = problem.get_operator_by_id(op_id)
        #
        #     for f in operator.pre_pos:
        #         if f not in operator.eff_neg and f not in unchanged_fluents_pos:
        #             constraints_count += 1
        #             constraint = y[op_id] - pb_attr.max_op_count[op_id] * pp[f] <= 0
        #             model.Add(constraint)
        #
        #     for f in operator.pre_neg:
        #         if f not in operator.eff_pos and f not in unchanged_fluents_neg:
        #             constraints_count += 1
        #             constraint = y[op_id] - pb_attr.max_op_count[op_id] * pn[f] <= 0
        #             model.Add(constraint)

        # Operator mutex constraints
        for op_id in problem.operators_id:
            if pb_attr.max_op_count[op_id] == float('inf'):
                continue
            constraint = y[op_id] - pb_attr.max_op_count[op_id] * u[op_id] <= 0
            constraints_count += 1
            model.Add(constraint)

        for op1_id, op2_id in pb_attr.op_mutexes:
            constraints_count += 1
            constraint = u[op1_id] + u[op2_id] <= 1
            model.Add(constraint)

        # Minimum count of known operators
        for c_operator in problem.operators:
            c_op_id = problem.get_operator_id(c_operator)
            c_min_op = pb_attr.min_op_count[c_op_id]
            c_max_op = pb_attr.max_op_count[c_op_id]
            if c_min_op > 0:
                constraints_count += 1
                model.Add(y[c_op_id] >= c_min_op)
            if c_max_op > 0 and c_max_op != float('inf'):
                constraints_count += 1
                model.Add(y[c_op_id] <= c_max_op)

        # print(f'Optimization with {constraints_count} op constraints')
        return model, y  # , b


@attr.s
class OpMutexLPCriterion(CriterionLP):
    """
    A variation of the previous criterion that adds constraints in order to check whether or not some pair of
    operators can occur simultaneously in some plan
    """
    op1_id: int = attr.ib()
    op2_id: int = attr.ib()

    def apply_single(self, problem, pb_attr, steps_duration, certificate_path, silent=False):
        # Translation to an LP
        step_start = perf_counter()

        if not silent:
            print("Creating model...")
            print(filler)

        model, y = self.create_lp_model(problem, pb_attr, self.op1_id, self.op2_id)

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Model created in {step_time:.1f}s!\n")
        steps_duration["lp_creation"] = step_time

        # Solve
        step_start = perf_counter()
        if not silent:
            print("Optimizing...")
            print(filler)

        status = model.Solve()

        step_time = perf_counter() - step_start
        if not silent:
            print(f"Optimization done in {step_time:.1f}s!\n")
        steps_duration["lp_solving"] = step_time

        if not silent:
            print("Result")
            print(filler)

        if status == pywraplp.Solver.INFEASIBLE:
            outcome = CriterionLP.Outcome.POSITIVE
            if not silent:
                print('NO PLAN EXISTS')
            if certificate_path is not None:
                with open(certificate_path, 'w') as f:
                    string_values = [f' {problem.get_fluent_name(i)} = {y[i].solution_value()}'
                                     for i in range(len(y)) if y[i].solution_value() != 0]
                    f.write('\n'.join(string_values))
        else:
            outcome = CriterionLP.Outcome.NEGATIVE
            if not silent:
                print('NO FEASIBLE REGION')

        return outcome

    @staticmethod
    def create_lp_model(problem: StripsProblem, pb_attr, op1_id: int, op2_id: int):
        model, y = DoubleOpCountCriterionLP.create_lp_model(problem, pb_attr)

        for op_id in [op1_id, op2_id]:
            constraint = y[op_id] >= 1
            model.Add(constraint)

        return model, y
