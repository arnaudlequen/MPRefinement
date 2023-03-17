import argparse
import heapq as hq
import itertools as it
from ortools.linear_solver import pywraplp
import random
import sys
from time import perf_counter

from adhoc_parser import adhoc_parser
from fd_parser import fd_parser
from mscp import Mscp
from linear_program import CriterionLPORTools, CriterionLPGurobi
from pddlpy_parser import pddlpy_parser
from touistparse import touistplan_parser
from utils import print_trace

from ortools.init import pywrapinit

filler = '=' * 30
small_filler = '-' * 30


def main(argv):
    parser = argparse.ArgumentParser(description="Sub-isomorphism finder for STRIPS planning problems")
    parser.add_argument('domain_path', metavar='domain.pddl', type=str, default=None,
                        help="The domain file in PDDL format")
    parser.add_argument('instance_path', metavar='instance.pddl', type=str, default=None, nargs='?',
                        help="The file of the problem from which to extract a subproblem, in PDDL format")
    parser.add_argument('--parser', type=str, default='fd',
                        help="Which parser among adhoc, pddlpy, touist to use")
    parser.add_argument('-t', '--trace', type=str, default=None,
                        help="Output a datafile that summarizes the main data points of the execution")
    parser.add_argument('--certificate', type=str, default=None,
                        help="Output a solution to the LP, that serves as a certificate in the case where no "
                             "plan exists")
    parser.add_argument('-l', '--testslist', type=str, default=None,
                        help="Input a list of tests to be performed") ## TODO: Say more about the format of the file
    parser.add_argument('-s', '--nostop', action=argparse.BooleanOptionalAction,
                        help="If specified, the algorithm will perform all operations before exiting, even if UNSAT is "
                             "met before")
    parser.add_argument('-d', '--stripsdump', type=str, default=None,
                        help="Dump the STRIPS model in the specified file")
    args = parser.parse_args()

    pywrapinit.CppBridge.InitLogging('main.py')
    cpp_flags = pywrapinit.CppFlags()
    cpp_flags.logtostderr = False
    cpp_flags.log_prefix = False
    pywrapinit.CppBridge.SetFlags(cpp_flags)

    steps_duration = {}
    global_start_time = perf_counter()

    print(filler)
    print("Model-Space Constraint Propagation")
    print(filler)
    print()

    # Parsing
    step_start = perf_counter()
    if args.instance_path is None:
        print("No domain supplied. Assuming domain.pddl\n")
        domain_path = '/'.join(args.domain_path.split('/')[:-1] + ['domain.pddl'])
        args.instance_path = args.domain_path
        args.domain_path = domain_path

    match args.parser:
        case 'touist':
            problem = touistplan_parser(args, steps_duration)
        case 'pddlpy':
            problem = pddlpy_parser(args)
        case 'fd':
            problem = fd_parser(args)
        case 'adhoc':
            problem = adhoc_parser(args)
        case _:
            problem = fd_parser(args)

    if args.stripsdump:
        with open(args.stripsdump, 'w+') as dump_file:
            print(problem, file=dump_file)

    step_time = perf_counter() - step_start
    steps_duration["pddl_parsing"] = step_time

    if problem is None:
        print("Aborting...")
        return

    # Part of a previous code that used IIS
    #     # outcome = CriterionORTools.lp_criterion_single(problem_c, steps_duration, args.certificate, silent=True)
    #     outcome, iis_pruned = CriterionGurobi.lp_criterion_single(problem_c, steps_duration,
    #                                                               args.certificate, silent=True)
    #
    #     print(f'Size of the pruned IIS: {len(iis_pruned)}')
    #     for new_operator in iis_pruned:
    #         if new_operator in remove_operators:
    #             continue
    #         new_remove_operators = remove_operators[:]

    # outcome, _ = CriterionORTools.apply_single(problem, steps_duration, args.certificate, silent=True)

    print("Starting search...")
    print(filler)
    sys.stdout.flush()
    step_time = perf_counter()
    mscp = Mscp(problem, steps_duration)

    mscp.initialize_attributes()

    outcome, statistics = mscp.explore(args.testslist, args.nostop)

    step_time = perf_counter() - step_start
    steps_duration["search"] = step_time

    print(small_filler)
    print("Search phase ended")
    print()

    print("Result")
    print(filler)
    if outcome:
        print('NO PLAN EXISTS')
    else:
        print('SOLVABILITY UNKNOWN')
    print()

    print(filler)
    step_time = perf_counter() - global_start_time
    print(f"Total time: {step_time:.1f}s")
    steps_duration["total_time"] = step_time

    steps_duration = {f'stime_{name}': time for (name, time) in steps_duration.items()}
    statistics = {f'search_{name}': time for (name, time) in statistics.items()}
    statistics = statistics | steps_duration

    if args.trace is not None:
        # TODO: Rewrite print_trace
        print_trace(args, outcome, problem, statistics)
    print()


def hash_op_list(lst):
    return '_'.join(list(map(str, lst)))


if __name__ == '__main__':
    main(sys.argv)
