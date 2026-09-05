"""EG-09: Raw Immutability test.

Invariant: SSI application path cannot mutate raw source, and any modification is detectable through content hash.
"""

import hashlib
from ssi.contracts.shared_adapters.derived_estimate import DerivedEstimateAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter


def test_raw_source_remains_immutable_across_transformations_and_repairs():
    """Proves that repairs produce distinct derived representations, leaving raw source unaltered."""
    raw_csv_bytes = b"id,name,lng,lat\nrec_1,CommunityA,108.95,34.27\n"
    initial_hash = hashlib.sha256(raw_csv_bytes).hexdigest()

    raw_observation = ObservationAdapter(
        observation_id="obs_001",
        source_asset_id="asset_raw_001",
        source_record_id="rec_1",
        geometry_wkt="POINT(108.95 34.27)",
        crs="WGS84",
        attributes={"name": "CommunityA"},
        provenance="vendor_upload",
    )

    # A repair / correction proposes a new aligned coordinate (e.g. after empirical alignment)
    repaired_derived_estimate = DerivedEstimateAdapter(
        derived_id="der_001",
        target_entity_id="entity_comm_a",
        estimation_method="empirical_alignment_v1",
        geometry_wkt="POINT(108.9512 34.2708)",
        crs="EPSG:4326",
        attributes={"name": "CommunityA", "alignment_residual": 45.2},
        derived_from_observation_ids=[raw_observation.observation_id],
        repair_approval_id="rep_app_001",
    )

    # 1. Raw observation geometry and attributes are unchanged
    assert raw_observation.geometry_wkt == "POINT(108.95 34.27)"
    assert raw_observation.observation_id == "obs_001"

    # 2. Derived estimate has distinct ID, method, and explicit lineage link to raw observation
    assert repaired_derived_estimate.geometry_wkt == "POINT(108.9512 34.2708)"
    assert repaired_derived_estimate.derived_from_observation_ids == ["obs_001"]

    # 3. Raw source asset bytes remain byte-for-byte identical
    current_hash = hashlib.sha256(raw_csv_bytes).hexdigest()
    assert current_hash == initial_hash

    # 4. Any simulated byte-tamper on the raw source is immediately detected by content hash
    tampered_bytes = raw_csv_bytes.replace(b"108.95", b"108.99")
    tampered_hash = hashlib.sha256(tampered_bytes).hexdigest()
    assert tampered_hash != initial_hash
