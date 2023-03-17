import subprocess
from time import perf_counter

from parser.ast_types import Operator
from strips_problem import StripsProblem

small_filler = '-' * 30


def touistplan_parser(args, steps_duration):
    blankfile = open('./tmp/blankrules.touistl', 'w+')
    blankfile.close()

    # Running the process writes in a file that is then read during a call to touist_process_problem_sets
    print("Parsing problem...")
    step_start = perf_counter()
    print(small_filler)
    print(f"Instance {args.instance_path}")
    problem = touistparse_parse_single(args.domain_path, args.instance_path)
    # problem = touistplan_parse_single_file(args.domain_path, args.instance_path)
    print(f"Done. Found {problem.get_fluent_count()} fluents and {problem.get_operator_count()} operators "
          f"in {perf_counter() - step_start:.2f}s")
    print()

    if problem.get_fluent_count() == 0 or problem.get_operator_count() == 0:
        print("ERROR: Empty problem. Maybe the parser encountered an error?")
        return None

    return problem


def trim_action_or_predicate(element):
    return element[2:]


def touistparse_parse_single(domain_path, instance_path):
    step_start = perf_counter()
    print("Calling TouISTPlan to extract STRIPS problem from file...")
    subprocess_args = ['./Solvers/touistparse', domain_path, instance_path]
    process = subprocess.run(subprocess_args, capture_output=True, text=True)
    print(f"Extraction done in {perf_counter() - step_start:.1f}s")
    step_start = perf_counter()
    print("Processing the output...")
    problem = touist_process_problem_sets_string(process.stdout)
    print(f"Processing done in {perf_counter() - step_start:.1f}s")
    print(process.stderr)

    return problem


def touistplan_parse_single_file(domain_path, instance_path):
    step_start = perf_counter()
    print("Calling TouISTPlan to extract STRIPS problem from file...")
    subprocess_args = ['./Solvers/touistplan', domain_path, instance_path, '-e', 'sat',
                       '-insat', './tmp/blankrules.touistl']
    process = subprocess.run(subprocess_args, capture_output=True)
    print(f"Extraction done in {perf_counter() - step_start:.1f}s")
    step_start = perf_counter()
    print("Processing the output file...")
    problem = touist_process_problem_sets()
    print(f"Processing done in {perf_counter() - step_start:.1f}s")

    return problem


def touist_process_problem_sets_string(output: str) -> StripsProblem:
    predicate_to_varId = {}
    varId_to_predicate = {}

    action_to_opId = {}
    opId_to_action = {}
    opId_to_operator = {}

    # Temporary variables as we need to store the predicates before they are assigned an id, if we want to perform a
    # single pass
    init_pos_predicates = []
    goal_pos_predicates = []

    init_pos = []
    init_neg = []
    goal_pos = []
    goal_neg = []

    parsing = False

    for line in output.split('\n'):
        if line.startswith('!================!'):
            if parsing:
                break
            else:
                parsing = True
                continue
        if not parsing:
            continue

        if line.startswith("$F ="):
            predicates = line.split('[')[1][:-1].split(',')
            predicates = map(trim_action_or_predicate, predicates)
            for varId, predicate in enumerate(predicates):
                predicate_to_varId[predicate] = varId
                varId_to_predicate[varId] = predicate

        elif line.startswith("$O ="):
            actions = line.split('[')[1][:-1].split(',')
            actions = map(trim_action_or_predicate, actions)
            for opId, action in enumerate(actions):
                action_to_opId[action] = opId
                opId_to_action[opId] = action

                operator = Operator(action, [], [], [], [])
                opId_to_operator[opId] = operator

        # Todo: refactor this whole block
        elif line.startswith("$Cond("):
            action, predicates = line.split(' = ')
            action = trim_action_or_predicate(action[6:-1])
            predicates = list(map(trim_action_or_predicate, predicates[1:-1].split(',')))

            opId = action_to_opId[action]
            operator = opId_to_operator[opId]
            if predicates != ['']:
                operator.pre_pos = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

        elif line.startswith("$Add("):
            action, predicates = line.split(' = ')
            action = trim_action_or_predicate(action[5:-1])
            predicates = list(map(trim_action_or_predicate, predicates[1:-1].split(',')))

            opId = action_to_opId[action]
            operator = opId_to_operator[opId]
            if predicates != ['']:
                operator.eff_pos = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

        elif line.startswith("$Del("):
            action, predicates = line.split(' = ')
            action = trim_action_or_predicate(action[5:-1])
            predicates = list(map(trim_action_or_predicate, predicates[1:-1].split(',')))

            opId = action_to_opId[action]
            operator = opId_to_operator[opId]
            if predicates != ['']:
                operator.eff_neg = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

        elif line.startswith("$I = "):
            _, predicates = line.split(' = ')
            init_pos_predicates = list(map(trim_action_or_predicate, predicates[1:-1].split(',')))
            if init_pos_predicates == ['']:
                init_pos_predicates = []

        elif line.startswith("$G = "):
            _, predicates = line.split(' = ')
            goal_pos_predicates = list(map(trim_action_or_predicate, predicates[1:-1].split(',')))
            if goal_pos_predicates == ['']:
                goal_pos_predicates = []

    if init_pos_predicates:
        init_pos = list(map(lambda p: predicate_to_varId[p], init_pos_predicates))
    else:
        init_pos = []
    if goal_pos_predicates:
        goal_pos = list(map(lambda p: predicate_to_varId[p], goal_pos_predicates))
    else:
        goal_pos = []

    problem = StripsProblem(predicate_to_varId, varId_to_predicate,
                            action_to_opId, opId_to_action, opId_to_operator,
                            init_pos, init_neg,
                            goal_pos, goal_neg)

    return problem


def touist_process_problem_sets() -> StripsProblem:
    predicate_to_varId = {}
    varId_to_predicate = {}

    action_to_opId = {}
    opId_to_action = {}
    opId_to_operator = {}

    # Temporary variables as we need to store the predicates before they are assigned an id, if we want to perform a
    # single pass
    init_pos_predicates = []
    goal_pos_predicates = []

    init_pos = []
    init_neg = []
    goal_pos = []
    goal_neg = []

    with open('./solvedata/in.sets.txt', 'r') as sets_file:
        line = sets_file.readline()
        while line:
            if line.startswith("$t_"):
                line = sets_file.readline()
                continue

            if line.startswith("$F ="):
                predicates = line.split('[')[1][:-2].split(',')
                predicates = map(trim_action_or_predicate, predicates)
                for varId, predicate in enumerate(predicates):
                    predicate_to_varId[predicate] = varId
                    varId_to_predicate[varId] = predicate

            elif line.startswith("$O ="):
                actions = line.split('[')[1][:-2].split(',')
                actions = map(trim_action_or_predicate, actions)
                for opId, action in enumerate(actions):
                    action_to_opId[action] = opId
                    opId_to_action[opId] = action

                    operator = Operator(action, [], [], [], [])
                    opId_to_operator[opId] = operator

            # Todo: refactor this whole block
            elif line.startswith("$Cond("):
                action, predicates = line.split(' = ')
                action = trim_action_or_predicate(action[6:-1])
                predicates = list(map(trim_action_or_predicate, predicates[1:-2].split(',')))

                opId = action_to_opId[action]
                operator = opId_to_operator[opId]
                if predicates != ['']:
                    operator.pre_pos = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

            elif line.startswith("$Add("):
                action, predicates = line.split(' = ')
                action = trim_action_or_predicate(action[5:-1])
                predicates = list(map(trim_action_or_predicate, predicates[1:-2].split(',')))

                opId = action_to_opId[action]
                operator = opId_to_operator[opId]
                if predicates != ['']:
                    operator.eff_pos = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

            elif line.startswith("$Del("):
                action, predicates = line.split(' = ')
                action = trim_action_or_predicate(action[5:-1])
                predicates = list(map(trim_action_or_predicate, predicates[1:-2].split(',')))

                opId = action_to_opId[action]
                operator = opId_to_operator[opId]
                if predicates != ['']:
                    operator.eff_neg = list(map(lambda predicate: predicate_to_varId[predicate], predicates))

            elif line.startswith("$I = "):
                _, predicates = line.split(' = ')
                init_pos_predicates = list(map(trim_action_or_predicate, predicates[1:-2].split(',')))

            elif line.startswith("$G = "):
                _, predicates = line.split(' = ')
                goal_pos_predicates = list(map(trim_action_or_predicate, predicates[1:-2].split(',')))

            line = sets_file.readline()

        init_pos = list(map(lambda p: predicate_to_varId[p], init_pos_predicates))
        goal_pos = list(map(lambda p: predicate_to_varId[p], goal_pos_predicates))

        problem = StripsProblem(predicate_to_varId, varId_to_predicate,
                                action_to_opId, opId_to_action, opId_to_operator,
                                init_pos, init_neg,
                                goal_pos, goal_neg)

        return problem