import attr
from finder.mscp import Mscp
from finder.mscp_rules import Propagation


@attr.s
class PropActDel(Propagation):
    def rule(self, mscp: Mscp, params: list):
        op_id = params[0]

        # First half

        # Second half
        # Todo: implement (see document)
