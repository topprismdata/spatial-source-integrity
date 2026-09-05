"""MG-04: GateSpec Parser Decoupling test.

Invariant: GateSpec parse success ≠ successful GateDecision.
"""

from ssi.admission.gate.ir import GatePolicyIR
from ssi.admission.gate.parser import GatePolicyParser


def test_gatespec_parse_success_does_not_equal_gate_decision():
    """Proves that parsing a GateSpec specification into IR is decoupled from GateDecision authorization."""
    yaml_spec = """
    policy_id: "GP-DEMO"
    version: "1.0.0"
    name: "Demo Gate Spec"
    hard_block_categories:
      - "CORRUPTED_COORDINATE"
    required_assessments:
      - "coordinate_schema"
      - "geographic_range"
    """

    # 1. Parsing succeeds and creates GatePolicyIR
    ir = GatePolicyParser.from_yaml(yaml_spec)
    assert isinstance(ir, GatePolicyIR)
    assert ir.policy_id == "GP-DEMO"

    # 2. GatePolicyIR is strictly an abstract rule tree and has NO admission action
    assert not hasattr(ir, "action")
    assert not hasattr(ir, "is_admitted")
    assert not hasattr(ir, "decision_id")
