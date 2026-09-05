"""EG-01: Missing Gate test.

Invariant: No GateDecision -> publish count = 0.
"""

from ssi.admission.publisher.publisher import SpatialAdmissionPublisher


def test_missing_gate_cannot_publish(consumer_macro_city, dp01_profile):
    """Proves that candidate geometries without a valid GateDecision are never published."""
    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }
    # Pass empty gate decisions list
    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[],
        candidate_geometries=candidate_geometries,
    )
    assert len(snapshot.projections) == 0
    assert snapshot.manifest_metadata["projections_count"] == 0
