"""MG-02: Legacy decision_ready isolation test.

Invariant: decision_ready = True alone cannot publish.
"""

from dataclasses import dataclass
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher


@dataclass(frozen=True)
class LegacyValidationResult:
    """Mock of SDI src/domain/contracts.py:320 ValidationResult."""
    id: str
    decision_ready: bool = True


def test_legacy_decision_ready_alone_cannot_publish(consumer_macro_city, dp01_profile):
    """Proves that a legacy decision_ready=True flag cannot publish any snapshot projections."""
    legacy_val = LegacyValidationResult(id="val_legacy_1", decision_ready=True)
    assert legacy_val.decision_ready is True

    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    # An old pipeline attempting to pass legacy_val without a GateDecision exports 0
    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[],  # GateDecision is mandatory
        candidate_geometries=candidate_geometries,
    )

    assert len(snapshot.projections) == 0
