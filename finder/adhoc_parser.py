from time import perf_counter

from strips_converter import StripsConverter

filler = '=' * 30


def adhoc_parser(args):
    """
    Extract STRIPS instances out of PDDL files and return STRIPSProblem instances
    """
    # Extract problems from file
    step_start = perf_counter()
    print("Extracting domain and instances from file...")
    print(filler)
    converter = StripsConverter()
    pddl_domain = converter.build_domain(args.domain_path)
    pddl_instance = converter.build_instance(args.instance_path)
    step_time = perf_counter() - step_start
    print(f"PDDL extraction done in {step_time:.1f}s!\n")

    # Convert them to STRIPS
    step_start = perf_counter()
    print("Converting problems to STRIPS...")
    print(filler)
    problem = converter.build_strips_problem(pddl_domain, pddl_instance)
    step_time = perf_counter() - step_start
    print(f"Conversion to STRIPS done in {step_time:.1f}s!\n")

    return problem