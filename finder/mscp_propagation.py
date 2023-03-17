import attr

from mscp_rules import Operation
import mscp_update as mupdate
from mscp_rules import Propagation
from mscp_criterion_test import ActionOrderingTest


@attr.s
class PropActDel(Propagation):
    op_id: int = attr.ib()

    def test(self, mscp) -> bool:
        return mscp.problem.is_operator_disabled(self.op_id)

    def propagate(self, mscp) -> tuple[Operation.Outcome, list]:
        mupdates = []

        # If we try to delete a landmark, then the problem is unsolvable. But this case is taken into account
        # in the MURemoveOperator operation
        # if self.op_id in mscp.pb_attr.landmarks:
        #     return Operation.Outcome.UNSAT, []

        for other_op_id in mscp.problem.operators_id:
            if other_op_id == self.op_id:
                continue
            mupdates.append(mupdate.MURemoveOperatorFromAPre(apre_op_id=other_op_id, remove_op_id=self.op_id))
            mupdates.append(mupdate.MURemoveOperatorFromAPost(apost_op_id=other_op_id, remove_op_id=self.op_id))

        return Operation.Outcome.SUCCESS, mupdates


@attr.s
class PropLandmarkIncompatibility(Propagation):
    landmark_id: int = attr.ib()
    incom_id: int = attr.ib()

    def test(self, mscp) -> bool:
        if self.landmark_id not in mscp.pb_attr.landmarks:
            return False
        if self.incom_id in mscp.pb_attr.apre[self.landmark_id]:
            return False
        if self.incom_id in mscp.pb_attr.apost[self.landmark_id]:
            return False

        return True

    def propagate(self, mscp) -> tuple[Operation.Outcome, list]:
        mupdates = []

        print(f"Incompatibility between operator {self.incom_id} and landmark {self.landmark_id}")
        mupdates.append(mupdate.MURemoveOperator(self.incom_id))

        return Operation.Outcome.SUCCESS, mupdates


@attr.s
class PropLandmarkConsistency(Propagation):
    landmark_id: int = attr.ib()

    def test(self, mscp) -> bool:
        if self.landmark_id not in mscp.pb_attr.landmarks:
            return False
        return True

    def propagate(self, mscp) -> tuple[Operation.Outcome, list]:
        new_tests = []

        for other_landmark_id in mscp.pb_attr.landmarks:
            new_tests.append(ActionOrderingTest(self.landmark_id, other_landmark_id))
            new_tests.append(ActionOrderingTest(other_landmark_id, self.landmark_id))

        return Operation.Outcome.SUCCESS, new_tests


# Instead added as a consequence of the addition of a landmark
# @attr.s
# class MinOpLandmark(Propagation):
#     op_id: int = attr.ib()
#
#     def test(self, mscp) -> bool:
#         return self.op_id in mscp.pb_attr.landmarks
#
#     def propagate(self, mscp) -> tuple[Operation.Outcome, list]:
#         pass
