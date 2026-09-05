"""EG-12: Snapshot Revocation test.

Invariant: REVOKED Snapshot -> new consumption blocked.
"""

import pytest
from ssi.adapters.consumer_adapter import ConsumerAdapter, ConsumptionError
from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher
from ssi.contracts.runtime.trusted_spatial_snapshot import SnapshotLifecycleStatus


def test_revoked_snapshot_blocks_new_consumption(
    consumer_macro_city,
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
    clean_evaluation_result,
):
    """Proves that a revoked snapshot blocks any new consumption reads and raises ConsumptionError."""
    # 1. First obtain an active admitted GateDecision and publish an active snapshot
    decision = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=clean_evaluation_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
        consumer_capability=consumer_macro_city,
    )
    assert decision.is_admitted()

    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    active_snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[decision],
        candidate_geometries=candidate_geometries,
    )
    assert active_snapshot.is_consumable()

    adapter = ConsumerAdapter(capability=consumer_macro_city)

    # 2. Consumer reads active snapshot successfully
    projections, record = adapter.read_snapshot(active_snapshot, operation="aggregation")
    assert len(projections) == 1
    assert record.status == "SUCCESS"

    # 3. Upstream authority revokes the snapshot (e.g. underlying source retracted or systematic parser defect discovered)
    revoked_snapshot = SpatialAdmissionPublisher.revoke_snapshot(
        snapshot=active_snapshot,
        reason="Upstream provider retracted survey data due to systemic geodetic shift.",
    )
    assert revoked_snapshot.lifecycle_status == SnapshotLifecycleStatus.REVOKED
    assert not revoked_snapshot.is_consumable()

    # 4. Consumer attempts to read revoked snapshot -> strictly BLOCKED with ConsumptionError
    with pytest.raises(ConsumptionError, match="Consumption blocked: Snapshot .* is not consumable"):
        adapter.read_snapshot(revoked_snapshot, operation="aggregation")
