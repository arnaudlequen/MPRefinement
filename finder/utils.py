import os
import sys
from contextlib import contextmanager


def print_trace(args, outcome, problem, statistics):
    if args.trace is None:
        return

    print(f"Saving trace in {args.trace}")
    with open(args.trace, "w") as file:
        ordered_times = [(k, v) for k, v in statistics.items()]

        var_names = ['pb_fluents', 'pb_operators']
        var_values = [problem.get_max_fluent_id() + 1, problem.get_max_operator_id() + 1]
        var_values = list(map(str, var_values))

        file.write(','.join(var_names))
        file.write(',outcome,')
        file.write(','.join(list(map(lambda x: x[0], ordered_times))))
        file.write('\n')
        file.write(','.join(var_values))
        file.write(f',{str(outcome_to_int(outcome))},')
        file.write(','.join(list(map(lambda x: f'{x[1]:.1f}', ordered_times))))


def outcome_to_int(outcome: str):
    match outcome:
        case True:
            return 1
        case False:
            return 0
        case _:
            return -1


@contextmanager
def silence_stdout():
    old_target = sys.stdout
    old_target_err = sys.stderr
    try:
        with open(os.devnull, "w") as new_target:
            sys.stdout = new_target
            sys.stderr = new_target
            yield new_target
    finally:
        sys.stdout = old_target
        sys.stderr = old_target_err
