from time import perf_counter
import parser.fdtranslate.pddl_parser as pddl_parser
from parser.fdtranslate.instantiate import explore
from parser.fdtranslate.normalize import normalize

from strips_problem import StripsProblem, Operator

filler = '=' * 30
NEG_PREFIX = 'Negated_'


def fd_parser(args):
    """
    Extract STRIPS instances out of PDDL files and return STRIPSProblem instances
    """
    # Extract problems from file
    global_start = perf_counter()
    print("Calling FastDownward's parser...")
    print(filler)

    task = pddl_parser.open(args.domain_path, args.instance_path)
    relaxed_reachable, atoms, actions, _, _ = explore(task)

    tasks_requirements = str(task.requirements).split(', ')
    has_negative_preconditions = ':negative-preconditions' in tasks_requirements \
                                 or ':adl' in str(task.requirements).split(', ')

    print("FD parsing done. Conversion to legacy internal representation...")

    predicates = DynamicList()

    for atom in atoms:
        predicate = normalize_atom(atom)
        predicates.add(predicate)

    # if ':negative-preconditions' in str(task.requirements).split(', '):
    #     positive_predicates = list(predicates.elements())[:]
    #     for predicate in positive_predicates:
    #         predicates.add(NEG_PREFIX + predicate)

    action_to_op_id = {}
    op_id_to_action = {}
    op_id_to_operator = {}

    for action in actions:
        pre_pos = set(map(predicates.get_id, normalize_atom_list_by_sign(action.precondition, '+')))
        pre_pos.update(set(map(predicates.get_id, normalize_atom_list_by_sign(action.precondition, '-'))))
        pre_neg = set()
        # pre_pos = list(map(predicates.get_id, map(normalize_atom, action.precondition)))
        # pre_neg = []
        eff_pos = set(map(predicates.get_id, map(lambda x: normalize_atom(x[1]), action.add_effects)))
        eff_neg = set(map(predicates.get_id, map(lambda x: normalize_atom(x[1]), action.del_effects)))

        if has_negative_preconditions:
            for predicate_id in eff_pos:
                predicate = predicates.get_element_by_id(predicate_id)
                if predicate.startswith(NEG_PREFIX):
                    continue
                negated_predicate = NEG_PREFIX + predicate
                eff_neg.add(predicates.get_id(negated_predicate))

            for predicate_id in eff_neg:
                predicate = predicates.get_element_by_id(predicate_id)
                if predicate.startswith(NEG_PREFIX):
                    continue
                negated_predicate = NEG_PREFIX + predicate
                eff_pos.add(predicates.get_id(negated_predicate))


        operator = Operator(action.name, pre_pos, pre_neg, eff_pos, eff_neg)
        op_id = len(action_to_op_id)

        action_to_op_id[action.name] = op_id
        op_id_to_action[op_id] = action.name
        op_id_to_operator[op_id] = operator

    # print('\n'.join(predicate_to_var_id))

    init_pos = list(map(lambda x: predicates.get_id(normalize_atom(x)), task.init))
    init_neg = []
    goal_pos = list(map(lambda x: predicates.get_id(normalize_atom(x)), task.goal.to_untyped_strips()))
    goal_neg = []

    if has_negative_preconditions:
        for predicate in predicates.elements():
            negated_predicate = NEG_PREFIX + predicate
            if predicates.get_id(predicate) not in init_pos and not predicate.startswith('=') \
                    and predicates.contains(negated_predicate):
                init_pos.append(predicates.get_id(negated_predicate))

    problem = StripsProblem(predicates.dic, predicates.reverse_dic,
                            action_to_op_id, op_id_to_action,
                            op_id_to_operator,
                            init_pos, init_neg,
                            goal_pos, goal_neg)

    # print(problem)

    print(filler)
    print(f"Done. Found {problem.get_fluent_count()} fluents and {problem.get_operator_count()} operators "
          f"in {perf_counter() - global_start:.1f}s")
    step_time = perf_counter() - global_start  # Remove
    print(f"Conversion to STRIPS done in {step_time:.1f}s!\n")

    return problem


def normalize_atom_list_by_sign(atom_list, sign):
    """
    Take a list of raw atoms out of FDTranslate, keep the ones that have the sign we require, and normalize them
    """
    assert sign in ['+', '-'], f"Sign unknown: {sign}"
    keep_list = []

    for atom in atom_list:
        str_atom = str(atom)
        if sign == '+' and str_atom.startswith('Atom'):
            keep_list.append(normalize_atom(str_atom))
        elif sign == '-' and str_atom.startswith('NegatedAtom'):
            keep_list.append(normalize_atom(str_atom))

    return keep_list


def normalize_atom(atom):
    str_atom = str(atom)
    if str_atom.startswith('NegatedAtom'):
        return NEG_PREFIX + str(atom)[12:]
    return str(atom)[5:]


class DynamicList:
    def __init__(self):
        self.dic = {}
        self.reverse_dic = {}

    def add(self, item):
        self.get_id(item)

    def get_id(self, item):
        if item in self.dic:
            return self.dic[item]

        self.dic[item] = len(self.dic)
        self.reverse_dic[self.dic[item]] = item
        return self.dic[item]

    def get_element_by_id(self, id):
        if id in self.reverse_dic:
            return self.reverse_dic[id]
        return None

    def elements(self):
        return self.dic.keys()

    def contains(self, element):
        return element in self.dic
