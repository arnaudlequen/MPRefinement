import attr

from mscp_rules import CriterionStruct, Criterion


@attr.s
class ResourceShortageCriterionStruct(CriterionStruct):
    fluent_id: int = attr.ib()

    def apply_single(self, mscp, pb_attr, steps_duration, certificate_path, silent=False):
        # TODO: optimization to keep in memory the operators to test
        possible_add_count = 1 if self.fluent_id in mscp.problem.init_pos else 0
        strict_del_count = 0

        for op_id in mscp.problem.operators_id:
            operator = mscp.problem.get_operator_by_id(op_id)

            if self.fluent_id in operator.eff_pos:
                if mscp.pb_attr.max_op_count[op_id] == -1:  # Infinity
                    possible_add_count = float('inf')
                    break
                possible_add_count += mscp.pb_attr.max_op_count[op_id]

            strict_del = set(operator.pre_pos).intersection(set(operator.eff_neg))
            if self.fluent_id in strict_del:
                strict_del_count += mscp.pb_attr.min_op_count[op_id]

        if strict_del_count > possible_add_count:
            return Criterion.Outcome.POSITIVE
        return Criterion.Outcome.NEGATIVE
