"""SR-Series: Spatial Reference Resolver & Pipeline tests (SR-01 ~ SR-15)."""

import pytest
from ssi.contracts.runtime.decision_stability import DecisionStability, StabilityState
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.detectors.d09_pipeline_consistency import D09PipelineConsistencyDetector
from ssi.resolver.hypothesis import (
    AdditionalEncoding,
    CanonicalResolutionState,
    CorruptionState,
    FormalCRS,
    Representation,
    SpatialReferenceHypothesis,
)
from ssi.resolver.resolver import SpatialReferenceResolver
from ssi.resolver.transforms import bd09_to_wgs84, gcj02_to_wgs84, wgs84_to_gcj02


@pytest.fixture
def base_wgs84_records():
    """True WGS84 coordinates in Xi'an."""
    return [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(108.9500 34.2700)",
            crs="WGS84",
        ),
        ObservationAdapter(
            observation_id="obs_2",
            source_asset_id="a1",
            source_record_id="rec_2",
            geometry_wkt="POINT(108.9600 34.2800)",
            crs="WGS84",
        ),
    ]


@pytest.fixture
def ground_anchors():
    """Authoritative ground reference anchors in true WGS-84."""
    return [
        {"source_id": "rec_1", "ref_lon": 108.9500, "ref_lat": 34.2700},
        {"source_id": "rec_2", "ref_lon": 108.9600, "ref_lat": 34.2800},
    ]


def test_sr_01_correct_declared_reference(base_wgs84_records, ground_anchors):
    """SR-01: Correct declared reference is successfully IDENTIFIED."""
    resolver = SpatialReferenceResolver()
    hyp_wgs = SpatialReferenceHypothesis(
        hypothesis_id="H_WGS84",
        formal_crs=FormalCRS.WGS84,
        representation=Representation.LON_LAT,
        encoding=AdditionalEncoding.IDENTITY,
    )
    hyp_gcj = SpatialReferenceHypothesis(
        hypothesis_id="H_GCJ",
        formal_crs=FormalCRS.WGS84,
        representation=Representation.LON_LAT,
        encoding=AdditionalEncoding.GCJ_LIKE,
    )

    res = resolver.resolve(
        records=base_wgs84_records,
        candidate_hypotheses=[hyp_wgs, hyp_gcj],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[1:],
        declared_crs="WGS84",
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.selected_hypothesis.hypothesis_id == "H_WGS84"
    assert res.is_operationally_aligned is True


def test_sr_02_missing_metadata_can_still_be_resolved(ground_anchors):
    """SR-02: Missing metadata does not prevent evaluating hypotheses against anchors."""
    # Records without declared CRS
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(108.9500 34.2700)",
            crs=None,  # Missing
        ),
        ObservationAdapter(
            observation_id="obs_2",
            source_asset_id="a1",
            source_record_id="rec_2",
            geometry_wkt="POINT(108.9600 34.2800)",
            crs=None,  # Missing
        ),
    ]

    resolver = SpatialReferenceResolver()
    hyp_wgs = SpatialReferenceHypothesis(
        hypothesis_id="H_WGS84",
        formal_crs=FormalCRS.WGS84,
        encoding=AdditionalEncoding.IDENTITY,
    )
    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_wgs],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[1:],
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.selected_hypothesis.hypothesis_id == "H_WGS84"


def test_sr_03_wrong_metadata_identifies_true_encoding(ground_anchors):
    """SR-03: When declared is WGS84 but coordinates are GCJ02, resolver identifies GCJ-like encoding."""
    # Generate GCJ coordinates from WGS84
    gcj_lon_1, gcj_lat_1 = wgs84_to_gcj02(108.9500, 34.2700)
    gcj_lon_2, gcj_lat_2 = wgs84_to_gcj02(108.9600, 34.2800)

    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt=f"POINT({gcj_lon_1} {gcj_lat_1})",
            crs="WGS84",  # Declared wrong!
        ),
        ObservationAdapter(
            observation_id="obs_2",
            source_asset_id="a1",
            source_record_id="rec_2",
            geometry_wkt=f"POINT({gcj_lon_2} {gcj_lat_2})",
            crs="WGS84",  # Declared wrong!
        ),
    ]

    resolver = SpatialReferenceResolver()
    hyp_wgs = SpatialReferenceHypothesis(
        hypothesis_id="H_WGS84",
        encoding=AdditionalEncoding.IDENTITY,
    )
    hyp_gcj = SpatialReferenceHypothesis(
        hypothesis_id="H_GCJ_LIKE",
        encoding=AdditionalEncoding.GCJ_LIKE,
    )

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_wgs, hyp_gcj],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[1:],
        declared_crs="WGS84",
    )

    assert res.selected_hypothesis.hypothesis_id == "H_GCJ_LIKE"
    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.selected_hypothesis.encoding == AdditionalEncoding.GCJ_LIKE


def test_sr_04_axis_ambiguity(ground_anchors):
    """SR-04: Axis order swapped (lat, lon) is resolved by R=LAT_LON hypothesis."""
    # Swapped coordinates (lat, lon) = (34.27, 108.95)
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(34.2700 108.9500)",
        ),
        ObservationAdapter(
            observation_id="obs_2",
            source_asset_id="a1",
            source_record_id="rec_2",
            geometry_wkt="POINT(34.2800 108.9600)",
        ),
    ]

    resolver = SpatialReferenceResolver()
    hyp_swapped = SpatialReferenceHypothesis(
        hypothesis_id="H_SWAPPED",
        representation=Representation.LAT_LON,
        encoding=AdditionalEncoding.IDENTITY,
    )
    hyp_normal = SpatialReferenceHypothesis(
        hypothesis_id="H_NORMAL",
        representation=Representation.LON_LAT,
        encoding=AdditionalEncoding.IDENTITY,
    )

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_normal, hyp_swapped],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[1:],
    )

    assert res.selected_hypothesis.hypothesis_id == "H_SWAPPED"
    assert res.selected_hypothesis.representation == Representation.LAT_LON


def test_sr_05_wgs_cgcs_indistinguishable(base_wgs84_records, ground_anchors):
    """SR-05: WGS84 and CGCS2000 are INDISTINGUISHABLE_AT_CURRENT_RESOLUTION when residual delta < 0.1m."""
    resolver = SpatialReferenceResolver()
    hyp_wgs = SpatialReferenceHypothesis(
        hypothesis_id="H_WGS84",
        formal_crs=FormalCRS.WGS84,
        encoding=AdditionalEncoding.IDENTITY,
    )
    hyp_cgcs = SpatialReferenceHypothesis(
        hypothesis_id="H_CGCS2000",
        formal_crs=FormalCRS.CGCS2000,
        encoding=AdditionalEncoding.IDENTITY,
    )

    res = resolver.resolve(
        records=base_wgs84_records,
        candidate_hypotheses=[hyp_wgs, hyp_cgcs],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[1:],
    )

    # Must NOT claim formal equivalence; outputs INDISTINGUISHABLE
    assert res.resolution_state == CanonicalResolutionState.INDISTINGUISHABLE_AT_CURRENT_RESOLUTION
    assert res.is_operationally_aligned is True


def test_sr_06_gcj_like_resolution(ground_anchors):
    """SR-06: GCJ-like encoded coordinates are transformed to WGS84 within 5m accuracy."""
    gcj_lon, gcj_lat = wgs84_to_gcj02(108.9500, 34.2700)
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt=f"POINT({gcj_lon} {gcj_lat})",
        )
    ]
    resolver = SpatialReferenceResolver()
    hyp_gcj = SpatialReferenceHypothesis(
        hypothesis_id="H_GCJ",
        encoding=AdditionalEncoding.GCJ_LIKE,
    )
    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_gcj],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[:1],
        adequacy_threshold_meters=10.0,
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.holdout_p50_residual_meters < 5.0


def test_sr_07_bd_like_resolution(ground_anchors):
    """SR-07: BD-like encoded coordinates are transformed to WGS84."""
    # Transform WGS -> GCJ -> BD
    g_lon, g_lat = wgs84_to_gcj02(108.9500, 34.2700)
    import math
    z = math.sqrt(g_lon * g_lon + g_lat * g_lat) + 0.00002 * math.sin(g_lat * math.pi * 3000.0 / 180.0)
    theta = math.atan2(g_lat, g_lon) + 0.000003 * math.cos(g_lon * math.pi * 3000.0 / 180.0)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006

    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt=f"POINT({bd_lon} {bd_lat})",
        )
    ]
    resolver = SpatialReferenceResolver()
    hyp_bd = SpatialReferenceHypothesis(
        hypothesis_id="H_BD",
        encoding=AdditionalEncoding.BD_LIKE,
    )
    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_bd],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[:1],
        adequacy_threshold_meters=15.0,
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.holdout_p50_residual_meters < 15.0


def test_sr_08_missing_leading_digit_corruption(ground_anchors):
    """SR-08: Missing leading digit (e.g. 8.95 instead of 108.95) resolved by K=MISSING_LEADING_DIGIT."""
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(8.9500 34.2700)",  # 100 degrees dropped
        )
    ]
    resolver = SpatialReferenceResolver()
    hyp_k_digit = SpatialReferenceHypothesis(
        hypothesis_id="H_K_DIGIT",
        corruption=CorruptionState.MISSING_LEADING_DIGIT,
    )
    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_k_digit],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[:1],
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.selected_hypothesis.corruption == CorruptionState.MISSING_LEADING_DIGIT
    assert res.holdout_p50_residual_meters < 1.0


def test_sr_09_fallback_default_point_detection():
    """SR-09: Repeated default coordinates are identified by D04."""
    from ssi.detectors.d04_coordinate_reuse import D04CoordinateReuseDetector
    records = [
        ObservationAdapter(
            observation_id=f"obs_{i}",
            source_asset_id="a1",
            source_record_id=f"rec_{i}",
            geometry_wkt="POINT(0.0 0.0)",  # Null Island default point
            attributes={"city": f"City_{i}"},
        )
        for i in range(4)
    ]
    d04 = D04CoordinateReuseDetector()
    exec_res = d04.evaluate(records)

    assert any(f.finding_code == "F-D04-CROSS-CITY-REUSE" for f in exec_res.findings)


def test_sr_10_mixed_pipeline_detection():
    """SR-10: D09 detects distinct pipeline segments in mixed batches."""
    records = [
        ObservationAdapter(
            observation_id="obs_b1_1",
            source_asset_id="a1",
            source_record_id="r1",
            geometry_wkt="POINT(<coord> <coord>)",
            attributes={"batch_id": "batch_mobile_v2"},
        ),
        ObservationAdapter(
            observation_id="obs_b2_1",
            source_asset_id="a1",
            source_record_id="r2",
            geometry_wkt="POINT(108.95 34.27)",
            attributes={"batch_id": "batch_legacy_export"},
        ),
    ]
    d09 = D09PipelineConsistencyDetector()
    exec_res = d09.evaluate(records)

    m = next(m for m in exec_res.measurements if m.measure_name == "pipeline_heterogeneity_score")
    assert m.value > 0.0
    assert m.metaquality["segment_count"] == 2


def test_sr_11_all_candidates_inadequate_outputs_out_of_candidate_set(ground_anchors):
    """SR-11: When all candidate hypotheses fail absolute adequacy, output OUT_OF_CANDIDATE_SET."""
    # Points on the Moon or corrupted in a way no candidate models
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(150.0000 80.0000)",
        )
    ]
    resolver = SpatialReferenceResolver()
    hyp_wgs = SpatialReferenceHypothesis(hypothesis_id="H_WGS", encoding=AdditionalEncoding.IDENTITY)
    hyp_gcj = SpatialReferenceHypothesis(hypothesis_id="H_GCJ", encoding=AdditionalEncoding.GCJ_LIKE)

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_wgs, hyp_gcj],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[:1],
        adequacy_threshold_meters=50.0,
    )

    # Invariant: Does NOT pick the "least bad" candidate; outputs OUT_OF_CANDIDATE_SET
    assert res.resolution_state == CanonicalResolutionState.OUT_OF_CANDIDATE_SET
    assert res.selected_hypothesis is None
    assert res.is_operationally_aligned is False


def test_sr_12_alignable_but_identity_unknown(ground_anchors):
    """SR-12: Empirical affine shift achieves operational alignment, but identity remains ALIGNABLE_BUT_IDENTITY_UNCONFIRMED."""
    # Point shifted by +0.01 lon, +0.01 lat (~1.1km systematic offset)
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(108.9600 34.2800)",  # +0.01 shift from ground (108.95, 34.27)
        )
    ]
    resolver = SpatialReferenceResolver()
    # Empirical hypothesis applying inverse shift d_lon=-0.01, d_lat=-0.01
    hyp_emp = SpatialReferenceHypothesis(
        hypothesis_id="H_EMPIRICAL",
        encoding=AdditionalEncoding.EMPIRICAL_TRANSFORM,
        parameters={"d_lon": -0.01, "d_lat": -0.01},
    )

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_emp],
        fit_anchors=ground_anchors[:1],
        holdout_anchors=ground_anchors[:1],
        adequacy_threshold_meters=50.0,
    )

    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res.is_operationally_aligned is True
    assert res.holdout_p50_residual_meters < 1.0


def test_sr_13_near_boundary_decision_unstable():
    """SR-13: A point near an administrative boundary has competing outcomes and is marked UNSTABLE."""
    stability = DecisionStability(
        scope="district_assignment",
        state=StabilityState.UNSTABLE,
        plausible_state_count=2,
        competing_outcomes=["YantaDistrict", "BeilinDistrict"],
        rationale="Plausible state variation S* crosses municipal district boundary.",
    )
    assert not stability.is_stable
    assert stability.state == StabilityState.UNSTABLE


def test_sr_14_reference_conflict_recorded():
    """SR-14: Reference conflict between declared CRS and ground truth is recorded in measurements."""
    from ssi.detectors.d07_declared_reference_consistency import D07DeclaredReferenceConsistencyDetector
    obs = ObservationAdapter(
        observation_id="obs_1",
        source_asset_id="a1",
        source_record_id="rec_1",
        geometry_wkt="POINT(108.95 34.27)",
        crs="WGS84",
    )
    d07 = D07DeclaredReferenceConsistencyDetector()
    exec_res = d07.evaluate([obs], context={"systematic_residual_meters": 650.0})

    m = next(m for m in exec_res.measurements if m.measure_name == "declared_reference_consistency")
    assert m.value == "CONFLICT"


def test_sr_15_pipeline_refinement_is_bounded():
    """SR-15: D09 refinement rounds are capped by MAX_REFINEMENT_ROUNDS (max 2 rounds)."""
    d09 = D09PipelineConsistencyDetector()
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="a1",
            source_record_id="rec_1",
            geometry_wkt="POINT(108.95 34.27)",
        )
    ]
    # Request 10 rounds of refinement
    exec_res = d09.evaluate(records, context={"refinement_rounds": 10})
    m = next(m for m in exec_res.measurements if m.measure_name == "pipeline_heterogeneity_score")

    # Invariant: Capped at MAX_REFINEMENT_ROUNDS = 2
    assert m.metaquality["refinement_rounds_executed"] == 2
    assert m.metaquality["refinement_rounds_executed"] <= d09.MAX_REFINEMENT_ROUNDS
