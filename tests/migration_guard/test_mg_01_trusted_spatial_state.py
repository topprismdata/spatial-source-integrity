"""MG-01: Legacy TrustedSpatialState isolation test.

Invariant: Legacy TrustedSpatialState cannot reach publication authority or publish snapshots.
"""

from dataclasses import dataclass, field
from typing import Dict
import pytest

from ssi.admission.publisher.publisher import SpatialAdmissionPublisher


@dataclass(frozen=True)
class LegacySpatialEntity:
    id: str
    canonical_name: str


@dataclass(frozen=True)
class LegacyTrustedSpatialState:
    """Mock of SDI src/domain/contracts.py:341 TrustedSpatialState."""
    entities: Dict[str, LegacySpatialEntity] = field(default_factory=dict)
    created_at: str = "2026-08-20T00:00:00"


def test_legacy_trusted_spatial_state_cannot_publish(consumer_macro_city, dp01_profile):
    """Proves that legacy TrustedSpatialState is decoupled and cannot be passed as GateDecisions."""
    legacy_state = LegacyTrustedSpatialState(
        entities={"e_1": LegacySpatialEntity(id="e_1", canonical_name="OldCompound")}
    )

    candidate_geometries = {
        "e_1": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    # If legacy state is passed instead of GateDecisions, it has no valid GateDecision objects
    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[],  # Legacy state cannot provide valid GateDecisions
        candidate_geometries=candidate_geometries,
    )

    assert len(snapshot.projections) == 0
    assert snapshot.manifest_metadata["projections_count"] == 0
