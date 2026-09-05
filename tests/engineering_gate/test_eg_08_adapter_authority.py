"""EG-08: Adapter Authority test.

Invariant: consumer adapter cannot derive or forge authorization.
"""

import pytest
from ssi.adapters.consumer_adapter import ConsumerAdapter
from ssi.admission.publisher.publisher import PublicationError, SpatialAdmissionPublisher
from ssi.contracts.runtime.gate_decision import AdmissionAction, GateDecision


def test_consumer_adapter_cannot_mint_or_forge_authorization(consumer_macro_city):
    """Proves that a ConsumerAdapter is strictly a read-only transport and cannot derive safety."""
    adapter = ConsumerAdapter(capability=consumer_macro_city)

    # 1. Adapter has no method to mint projections or publish snapshots
    assert not hasattr(adapter, "mint_projection")
    assert not hasattr(adapter, "publish_snapshot")
    assert not hasattr(adapter, "derive_is_safe")

    # 2. Directly attempting to bypass Gate through publisher raises PublicationError
    fake_blocked_decision = GateDecision(
        decision_id="fake_dec_1",
        subject_id="rec_bad",
        candidate_representation_id="cand_bad",
        evaluation_result_id="eval_bad",
        decision_profile_id="DP-01",
        decision_profile_version="1.0.0",
        gate_policy_id="GP-STANDARD",
        gate_policy_version="1.0.0",
        action=AdmissionAction.BLOCK_FOR_PROFILE,
        justification="Bad record",
    )

    with pytest.raises(PublicationError, match="Cannot mint DecisionReadyProjection"):
        SpatialAdmissionPublisher.mint_projection(
            gate_decision=fake_blocked_decision,
            admitted_geometry_wkt="POINT(0 0)",
            admitted_crs="EPSG:4326",
        )
