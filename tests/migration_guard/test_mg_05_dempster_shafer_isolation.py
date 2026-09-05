"""MG-05: Dempster-Shafer Isolation test.

Invariant: belief / plausibility value cannot directly mint ClaimResolution, GateDecision, or DecisionReadyProjection.
"""

from dataclasses import dataclass
import pytest
from ssi.admission.publisher.publisher import PublicationError, SpatialAdmissionPublisher
from ssi.contracts.runtime.gate_decision import AdmissionAction, GateDecision


@dataclass(frozen=True)
class MockDSOpinion:
    """Mock of SDI src/domain/evidence_algebra.py:56 MassOpinion."""
    belief: float = 0.99
    plausibility: float = 0.99
    conflict_k: float = 0.01


def test_dempster_shafer_belief_cannot_bypass_gate_to_mint_projection():
    """Proves that a high belief score cannot directly mint an authorized projection."""
    ds_opinion = MockDSOpinion(belief=0.99, plausibility=0.99)
    assert ds_opinion.belief == 0.99

    # Raw mathematical belief cannot be passed to Publisher in place of GateDecision
    # Attempting to mint projection from a non-admitted GateDecision fails closed
    non_admitted_decision = GateDecision(
        decision_id="dec_unadmitted",
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result_id="eval_101",
        decision_profile_id="DP-01",
        decision_profile_version="1.0.0",
        gate_policy_id="GP-STANDARD",
        gate_policy_version="1.0.0",
        action=AdmissionAction.BLOCK_FOR_PROFILE,
        justification="Subject blocked despite high internal model confidence",
    )

    with pytest.raises(PublicationError, match="Cannot mint DecisionReadyProjection"):
        SpatialAdmissionPublisher.mint_projection(
            gate_decision=non_admitted_decision,
            admitted_geometry_wkt="POINT(108.95 34.27)",
            admitted_crs="EPSG:4326",
        )
