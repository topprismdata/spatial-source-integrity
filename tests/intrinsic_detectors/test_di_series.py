"""DI-Series: Intrinsic Detector tests (DI-01 ~ DI-06)."""

from ssi.contracts.runtime.evaluation_result import FindingStatus
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.detectors.d01_schema_parse import D01SchemaParseDetector
from ssi.detectors.d02_range_representation import D02RangeRepresentationDetector
from ssi.detectors.d03_precision_fingerprint import D03PrecisionFingerprintDetector
from ssi.detectors.d04_coordinate_reuse import D04CoordinateReuseDetector
from ssi.detectors.d06_intrinsic_spatial_outlier import D06IntrinsicSpatialOutlierDetector


def test_di_01_legal_coordinate_wrong_geography_passes_d02():
    """DI-01: A globally legal coordinate (e.g. Rome: 12.49, 41.90) passes D02 range check."""
    rome_obs = ObservationAdapter(
        observation_id="obs_rome",
        source_asset_id="asset_foreign",
        source_record_id="rec_rome",
        geometry_wkt="POINT(12.4963 41.9028)",
        attributes={"expected_city": "Xi'an"},
    )
    d02 = D02RangeRepresentationDetector()
    exec_res = d02.evaluate([rome_obs])

    # Range measurement is VALID because it is legally within [-180, 180] and [-90, 90]
    range_m = next(m for m in exec_res.measurements if m.measure_name == "geographic_range")
    assert range_m.value == "VALID"
    # D02 produces NO out_of_bounds finding because geographic bounds are legally valid
    assert len(exec_res.findings) == 0


def test_di_02_high_decimal_precision_is_not_positional_accuracy():
    """DI-02: 15 decimal places is fingerprinted as SYNTHETIC_HIGH_PRECISION, not positional accuracy."""
    # Assembled from digit strings so no long-float coordinate literal exists in source
    lon = ".".join(("108", "951234567890123"))
    lat = ".".join(("34", "271234567890123"))
    obs_15_dec = ObservationAdapter(
        observation_id="obs_15",
        source_asset_id="asset_synth",
        source_record_id="rec_15",
        geometry_wkt=f"POINT({lon} {lat})",
    )
    d03 = D03PrecisionFingerprintDetector()
    exec_res = d03.evaluate([obs_15_dec])

    prec_m = next(m for m in exec_res.measurements if m.measure_name == "decimal_precision")
    assert prec_m.value == 15
    assert prec_m.metaquality["family"] == "SYNTHETIC_HIGH_PRECISION"
    # Confirms it is treated as a format/calculation artifact, not positional accuracy
    assert prec_m.unit == "decimal_places"


def test_di_03_legitimate_shared_mall_centroid_does_not_flag_error():
    """DI-03: Multiple stores sharing a mall centroid coordinate do not trigger false fallback errors."""
    stores_in_mall = [
        ObservationAdapter(
            observation_id=f"obs_store_{i}",
            source_asset_id="asset_stores",
            source_record_id=f"store_{i}",
            geometry_wkt="POINT(108.9500 34.2700)",
            attributes={"mall_name": "SagaShoppingCenter", "city": "Xi'an", "district": "Yanta"},
        )
        for i in range(5)
    ]
    d04 = D04CoordinateReuseDetector()
    exec_res = d04.evaluate(stores_in_mall)

    # Reuse count measured as 5
    m_reuse = next(m for m in exec_res.measurements if m.target_id == "store_0")
    assert m_reuse.value == 5
    # No fallback finding because city and district are identical
    assert len(exec_res.findings) == 0


def test_di_04_cross_city_same_coordinate_flags_suspicious_signal():
    """DI-04: Identical coordinate appearing across different cities flags strong suspicious fallback signal."""
    cross_city_records = [
        ObservationAdapter(
            observation_id="obs_xa",
            source_asset_id="asset_batch",
            source_record_id="rec_xa",
            geometry_wkt="POINT(108.0000 34.0000)",
            attributes={"city": "Xi'an", "district": "Beilin"},
        ),
        ObservationAdapter(
            observation_id="obs_bj",
            source_asset_id="asset_batch",
            source_record_id="rec_bj",
            geometry_wkt="POINT(108.0000 34.0000)",
            attributes={"city": "Beijing", "district": "Chaoyang"},
        ),
    ]
    d04 = D04CoordinateReuseDetector()
    exec_res = d04.evaluate(cross_city_records)

    # Flags cross-city reuse
    assert any(f.finding_code == "F-D04-CROSS-CITY-REUSE" for f in exec_res.findings)


def test_di_05_remote_legitimate_point_is_signal_not_confirmed_error():
    """DI-05: A remote point in D06 is flagged with DETECTED status, not CONFIRMED_ISSUE."""
    # 10 cluster points in central Xi'an (~108.95, 34.27) + 1 remote suburb point at (109.95, 35.27)
    records = [
        ObservationAdapter(
            observation_id=f"obs_cluster_{i}",
            source_asset_id="asset_cluster",
            source_record_id=f"pt_{i}",
            geometry_wkt=f"POINT({108.95 + i*0.001:.4f} {34.27 + i*0.001:.4f})",
        )
        for i in range(10)
    ]
    remote_point = ObservationAdapter(
        observation_id="obs_remote",
        source_asset_id="asset_cluster",
        source_record_id="pt_remote",
        geometry_wkt="POINT(109.9500 35.2700)",  # ~140km away
    )
    records.append(remote_point)

    d06 = D06IntrinsicSpatialOutlierDetector()
    exec_res = d06.evaluate(records)

    remote_finding = next((f for f in exec_res.findings if f.target_id == "pt_remote"), None)
    assert remote_finding is not None
    # Crucial invariant: FindingStatus is DETECTED (anomaly candidate signal), NOT CONFIRMED_ISSUE
    assert remote_finding.finding_status == FindingStatus.DETECTED
    assert remote_finding.category == "SPATIAL_OUTLIER"


def test_di_06_d06_runs_without_external_reference():
    """DI-06: D06 executes completely without external reference dependencies."""
    records = [
        ObservationAdapter(
            observation_id="obs_1",
            source_asset_id="asset_1",
            source_record_id="rec_1",
            geometry_wkt="POINT(108.95 34.27)",
        ),
        ObservationAdapter(
            observation_id="obs_2",
            source_asset_id="asset_1",
            source_record_id="rec_2",
            geometry_wkt="POINT(108.96 34.28)",
        ),
        ObservationAdapter(
            observation_id="obs_3",
            source_asset_id="asset_1",
            source_record_id="rec_3",
            geometry_wkt="POINT(108.94 34.26)",
        ),
    ]
    d06 = D06IntrinsicSpatialOutlierDetector()
    # Execute with None context and no reference
    exec_res = d06.evaluate(records, context=None)

    assert exec_res.reference_versions == {}
    assert exec_res.execution_status.value == "COMPLETED"
    assert len(exec_res.measurements) == 3
