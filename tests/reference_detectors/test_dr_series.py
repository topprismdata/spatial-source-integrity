"""DR-Series: Reference Detector tests (DR-01 ~ DR-06)."""

from ssi.contracts.runtime.evaluation_result import FindingSeverity, FindingStatus
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.detectors.d05_admin_consistency import D05AdminConsistencyDetector
from ssi.detectors.d07_declared_reference_consistency import D07DeclaredReferenceConsistencyDetector
from ssi.detectors.d08_external_reference_residual import D08ExternalReferenceResidualDetector
from ssi.evaluation.detector_execution import ExecutionStatus
from ssi.evaluation.reference_manifest import ReferenceManifest


def test_dr_01_near_admin_boundary_distinguishes_conflict_from_ambiguity():
    """DR-01: D05 distinguishes gross administrative conflict from near-boundary ambiguity."""
    # Box: 108.90 to 109.00 lon, 34.20 to 34.30 lat
    box_wkt = "POLYGON((108.90 34.20, 109.00 34.20, 109.00 34.30, 108.90 34.30, 108.90 34.20))"
    ref_manifest = ReferenceManifest(
        reference_id="ref_admin_xa",
        source="CIVIL_ADMIN_XA",
        version="2026.1",
        claim_scope="ADMIN_BOUNDARIES",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="boundary_polygon",
        authority_scope="Municipal",
        data_license="Official",
        content_hash="hash_xa_admin",
    )

    # Point A: Just 20 meters outside the eastern edge (109.0002, 34.25) -> ~22m away
    obs_near = ObservationAdapter(
        observation_id="obs_near",
        source_asset_id="asset_admin",
        source_record_id="rec_near",
        geometry_wkt="POINT(109.0002 34.25)",
        attributes={"district": "Yanta"},
    )

    # Point B: 5 kilometers outside (109.05, 34.25) -> ~5500m away
    obs_far = ObservationAdapter(
        observation_id="obs_far",
        source_asset_id="asset_admin",
        source_record_id="rec_far",
        geometry_wkt="POINT(109.0500 34.25)",
        attributes={"district": "Yanta"},
    )

    d05 = D05AdminConsistencyDetector()
    context = {"reference_manifest": ref_manifest, "admin_polygons": {"Yanta": box_wkt}}
    exec_res = d05.evaluate([obs_near, obs_far], context=context)

    # Near point triggers NEAR_BOUNDARY_AMBIGUITY with severity INFO
    f_near = next(f for f in exec_res.findings if f.target_id == "rec_near")
    assert f_near.finding_code == "F-D05-NEAR-BOUNDARY-AMBIGUITY"
    assert f_near.severity == FindingSeverity.INFO

    # Far point triggers ADMIN_DISPLACEMENT with severity WARNING
    f_far = next(f for f in exec_res.findings if f.target_id == "rec_far")
    assert f_far.finding_code == "F-D05-ADMIN-DISPLACEMENT"
    assert f_far.severity == FindingSeverity.WARNING


def test_dr_02_stale_admin_reference_triggers_abstention():
    """DR-02: When administrative reference is marked stale or missing, D05 enters ABSTAINED."""
    obs = ObservationAdapter(
        observation_id="obs_1",
        source_asset_id="asset_1",
        source_record_id="rec_1",
        geometry_wkt="POINT(108.95 34.27)",
        attributes={"district": "Yanta"},
    )
    d05 = D05AdminConsistencyDetector()

    # Pass context with reference_stale = True
    ref_manifest = ReferenceManifest(
        reference_id="ref_admin_stale",
        source="CIVIL_ADMIN_XA",
        version="2010.0",
        claim_scope="ADMIN_BOUNDARIES",
        geographic_scope="Xi'an",
        temporal_scope="2010",
        feature_semantics="boundary_polygon",
        authority_scope="Municipal",
        data_license="Official",
        content_hash="hash_stale",
    )
    context = {"reference_manifest": ref_manifest, "reference_stale": True}
    exec_res = d05.evaluate([obs], context=context)

    assert exec_res.execution_status == ExecutionStatus.ABSTAINED
    assert "historically stale" in exec_res.abstention_reason


def test_dr_03_declared_reference_inconsistent_produces_conflict_not_forced_replacement():
    """DR-03: D07 identifies conflict between declared CRS and observed residual without forcing replacement identity."""
    obs_wgs_declared = ObservationAdapter(
        observation_id="obs_dec",
        source_asset_id="asset_dec",
        source_record_id="rec_dec",
        geometry_wkt="POINT(108.95 34.27)",
        crs="WGS84",
    )
    d07 = D07DeclaredReferenceConsistencyDetector()

    # Context indicates systematic offset > 300m (e.g. 520m typical of GCJ shift)
    context = {"systematic_residual_meters": 520.0}
    exec_res = d07.evaluate([obs_wgs_declared], context=context)

    m_conf = next(m for m in exec_res.measurements if m.target_id == "rec_dec")
    assert m_conf.value == "CONFLICT"

    f_conf = next(f for f in exec_res.findings if f.target_id == "rec_dec")
    assert f_conf.finding_code == "F-D07-DECLARED-CRS-CONFLICT"
    # Status is DETECTED, does NOT invent or force a replacement CRS name like "BD-09"
    assert f_conf.finding_status == FindingStatus.DETECTED
    assert "inconsistent with observed ground frame" in f_conf.explanation


def test_dr_04_wrong_entity_anchor_cannot_turn_residual_into_coordinate_error():
    """DR-04: If an entity match is ambiguous (same name across cities), D08 does not flag a confirmed coordinate error."""
    obs = ObservationAdapter(
        observation_id="obs_sun",
        source_asset_id="asset_sun",
        source_record_id="rec_sun",
        geometry_wkt="POINT(108.95 34.27)",
        attributes={"name": "SunshineGarden"},
    )
    ref_manifest = ReferenceManifest(
        reference_id="ref_osm_xa",
        source="OSM",
        version="2026-08",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        content_hash="hash_osm",
    )

    # Matched anchor has is_ambiguous_match = True (e.g. same name in another city, 100km away)
    matched_anchors = {
        "rec_sun": {
            "ref_lon": 109.95,
            "ref_lat": 35.27,
            "is_ambiguous_match": True,
            "match_confidence": 0.40,
        }
    }

    d08 = D08ExternalReferenceResidualDetector()
    exec_res = d08.evaluate([obs], context={"reference_manifest": ref_manifest, "matched_anchors": matched_anchors})

    # The finding emitted is REFERENCE_MATCH_AMBIGUITY, not a confirmed coordinate error
    f_ambig = next(f for f in exec_res.findings if f.target_id == "rec_sun")
    assert f_ambig.finding_code == "F-D08-AMBIGUOUS-MATCH"
    assert f_ambig.finding_status == FindingStatus.DISPUTED
    assert "Cannot attribute to coordinate error" in f_ambig.explanation


def test_dr_05_fit_and_holdout_residuals_physically_separated():
    """DR-05: Fit anchors and holdout anchors are recorded with explicit role separation."""
    obs_fit = ObservationAdapter(
        observation_id="obs_f", source_asset_id="a_1", source_record_id="rec_fit", geometry_wkt="POINT(108.95 34.27)"
    )
    obs_hold = ObservationAdapter(
        observation_id="obs_h", source_asset_id="a_1", source_record_id="rec_hold", geometry_wkt="POINT(108.96 34.28)"
    )
    ref_manifest = ReferenceManifest(
        reference_id="ref_osm_xa",
        source="OSM",
        version="2026-08",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        content_hash="hash_osm",
    )

    matched_anchors = {
        "rec_fit": {"ref_lon": 108.9501, "ref_lat": 34.2701, "anchor_role": "FIT", "match_confidence": 1.0},
        "rec_hold": {"ref_lon": 108.9605, "ref_lat": 34.2805, "anchor_role": "HOLDOUT", "match_confidence": 1.0},
    }

    d08 = D08ExternalReferenceResidualDetector()
    exec_res = d08.evaluate(
        [obs_fit, obs_hold],
        context={"reference_manifest": ref_manifest, "matched_anchors": matched_anchors},
    )

    m_fit = next(m for m in exec_res.measurements if m.target_id == "rec_fit")
    m_hold = next(m for m in exec_res.measurements if m.target_id == "rec_hold")

    assert m_fit.metaquality["anchor_role"] == "FIT"
    assert m_hold.metaquality["anchor_role"] == "HOLDOUT"
    assert m_fit.metaquality["anchor_role"] != m_hold.metaquality["anchor_role"]


def test_dr_06_same_upstream_reference_dependency_tracked():
    """DR-06: Using the same upstream reference is tracked as dependent, not independent validation."""
    ref_manifest = ReferenceManifest(
        reference_id="ref_osm_dependent",
        source="OSM",
        version="2026-08",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        dependency_state="KNOWN_DEPENDENT",  # Explicitly dependent on same upstream crawler
        content_hash="hash_dep",
    )

    assert ref_manifest.dependency_state == "KNOWN_DEPENDENT"
    assert ref_manifest.dependency_state != "VERIFIED_INDEPENDENT"
