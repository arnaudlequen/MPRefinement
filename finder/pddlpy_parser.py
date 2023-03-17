from time import perf_counter
from strips_problem import StripsProblem, Operator
import pddlpy
import itertools as it

filler = '=' * 30


def pddlpy_parser(args):
    """
    Extract STRIPS instances out of PDDL files and return STRIPSProblem instances
    """
    # Extract problems from file
    global_start = perf_counter()
    print("Extracting PDDLPy object from file...")
    print(filler)
    domain_problem = pddlpy.DomainProblem(args.domain_path, args.instance_path)
    step_time = perf_counter() - global_start
    print(f"PDDL extraction done in {step_time:.1f}s!\n")

    # Convert to our internal representation
    step_start = perf_counter()
    print("Converting problems to STRIPS...")
    print(filler)
    print("Grounding instance...")
    # problem = converter.build_strips_problem(pddl_domain, pddl_instance)

    predicates_lst = DynamicList()

    operators = []

    for op_name in domain_problem.operators():
        print(op_name)
        for operator in domain_problem.ground_operator(op_name):
            print(operator)
            operator_name = operator_to_str(operator)

            pre_pos = list(operator.precondition_pos)
            pre_neg = list(operator.precondition_neg)
            eff_pos = list(operator.effect_pos)
            eff_neg = list(operator.effect_neg)

            for attr_lst in [pre_pos, pre_neg, eff_pos, eff_neg]:
                attr_lst[:] = list(map(lambda x: predicates_lst.get_id(tuple_to_predicate(x)), attr_lst))

            op = Operator(operator_name, pre_pos, pre_neg, eff_pos, eff_neg)
            operators.append(op)

    action_to_op_id = {}
    op_id_to_action = {}
    op_id_to_operator = {}

    for i, operator in enumerate(operators):
        action_to_op_id[operator.name] = i
        op_id_to_action[i] = operator.name
        op_id_to_operator[i] = operator

    init_pos = list(map(lambda x: predicates_lst.get_id(atom_to_predicate(x)), domain_problem.initialstate()))
    init_neg = []
    goal_pos = list(map(lambda x: predicates_lst.get_id(atom_to_predicate(x)), domain_problem.goals()))
    goal_neg = []

    predicate_to_var_id = predicates_lst.dic
    var_id_to_predicate = predicates_lst.reverse_dic

    problem = StripsProblem(predicate_to_var_id, var_id_to_predicate,
                            action_to_op_id, op_id_to_action,
                            op_id_to_operator,
                            init_pos, init_neg,
                            goal_pos, goal_neg)

    print(f"Done. Found {problem.get_fluent_count()} fluents and {problem.get_operator_count()} operators "
          f"in {perf_counter() - step_start:.1f}s")
    step_time = perf_counter() - global_start
    print(f"Conversion to STRIPS done in {step_time:.1f}s!\n")

    return problem


def operator_to_str(operator):
    return f"{operator.operator_name}_{'_'.join(operator.variable_list.values())}"


def atom_to_predicate(atom):
    return tuple_to_predicate(atom.predicate)


def tuple_to_predicate(tuple):
    return f"({' '.join(tuple)})"  # atom.predicate ?


class DynamicList:
    def __init__(self):
        self.dic = {}
        self.reverse_dic = {}

    def get_id(self, item):
        if item in self.dic:
            return self.dic[item]

        self.dic[item] = len(self.dic)
        self.reverse_dic[self.dic[item]] = item
        return self.dic[item]
