"""Phase 1 Gate Integration test: connects real Detector outputs directly to Phase 0 GateExecutor."""

from ssi.adapters.consumer_adapter import ConsumerAdapter
from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.decision_stability import DecisionStability, StabilityState
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.detectors.d01_schema_parse import D01SchemaParseDetector
from ssi.detectors.d02_range_representation import D02RangeRepresentationDetector
from ssi.detectors.d03_precision_fingerprint import D03PrecisionFingerprintDetector
from ssi.detectors.d04_coordinate_reuse import D04CoordinateReuseDetector
from ssi.detectors.d06_intrinsic_spatial_outlier import D06IntrinsicSpatialOutlierDetector
from ssi.detectors.d08_external_reference_residual import D08ExternalReferenceResidualDetector
from ssi.evaluation.pipeline import EvaluationPipeline
from ssi.evaluation.reference_manifest import ReferenceManifest


def test_real_detectors_connect_directly_to_phase_0_gate_and_publisher(
    consumer_field_routing,
):
    """Proves that real Detector outputs feed directly into Phase 0 Gate without manual glue code."""
    # 1. Real-world-like observations in Xi'an
    obs_1 = ObservationAdapter(
        observation_id="obs_xa_101",
        source_asset_id="asset_commercial listing dataset_xa",
        source_record_id="comm_101",
        geometry_wkt="POINT(108.9534 34.2678)",
        crs="WGS84",
        attributes={"name": "BellTowerNorth", "city": "Xi'an", "district": "Beilin"},
        provenance="commercial listing dataset_aug_2026",
    )
    obs_2 = ObservationAdapter(
        observation_id="obs_xa_102",
        source_asset_id="asset_commercial listing dataset_xa",
        source_record_id="comm_102",
        geometry_wkt="POINT(108.9610 34.2750)",
        crs="WGS84",
        attributes={"name": "EastGateGarden", "city": "Xi'an", "district": "Beilin"},
        provenance="commercial listing dataset_aug_2026",
    )
    records = [obs_1, obs_2]

    # Reference manifest and matched ground anchors
    ref_manifest = ReferenceManifest(
        reference_id="ref_osm_xa_2026",
        source="OSM",
        version="2026.08",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        content_hash="hash_osm_xa",
    )

    matched_anchors = {
        "comm_101": {"ref_lon": 108.9536, "ref_lat": 34.2680, "anchor_role": "HOLDOUT", "match_confidence": 0.98},
        "comm_102": {"ref_lon": 108.9612, "ref_lat": 34.2752, "anchor_role": "HOLDOUT", "match_confidence": 0.95},
    }

    context = {"reference_manifest": ref_manifest, "matched_anchors": matched_anchors}

    # 2. Run real detector pipeline: D01, D02, D03, D04, D06, D08
    pipeline = EvaluationPipeline([
        D01SchemaParseDetector(),
        D02RangeRepresentationDetector(),
        D03PrecisionFingerprintDetector(),
        D04CoordinateReuseDetector(),
        D06IntrinsicSpatialOutlierDetector(),
        D08ExternalReferenceResidualDetector(),
    ])

    eval_result = pipeline.run(records, context=context)
    assert eval_result.status == "COMPLETED"
    assert len(eval_result.measurements) > 0

    # Build coverage manifest
    coverage_manifest = EvaluationCoverageManifest(
        manifest_id="man_integration_01",
        evaluation_ref=eval_result.evaluation_id,
        eligible_scope=["comm_101", "comm_102"],
        evaluated_scope=["comm_101", "comm_102"],
        sampled_scope=["comm_101", "comm_102"],
    )

    # 3. Direct evaluation against Phase 0 GateExecutor
    profile = DecisionProfileAdapter.create_dp02_visit_planning(max_residual_meters=200.0, threshold_provenance="EXPERIMENTAL_FIXTURE")
    policy = GatePolicy(
        policy_id="GP-REAL-DETECTORS",
        version="1.0.0",
        name="Real Detectors Policy",
        required_assessments=["coordinate_schema", "geographic_range", "positional_residual"],
        hard_block_finding_categories=["CORRUPTED_COORDINATE", "OUT_OF_BOUNDS"],
        require_decision_stability=True,
    )
    stability = DecisionStability(
        scope="district_assignment",
        state=StabilityState.STABLE,
        plausible_state_count=1,
        competing_outcomes=["BeilinDistrict"],
        rationale="Point is well centered within district.",
    )

    # Evaluate comm_101
    decision_101 = GateExecutor.evaluate_admission(
        subject_id="comm_101",
        candidate_representation_id="cand_101",
        evaluation_result=eval_result,
        coverage_manifest=coverage_manifest,
        decision_profile=profile,
        gate_policy=policy,
        consumer_capability=consumer_field_routing,
        decision_stability=stability,
    )

    assert decision_101.is_admitted()

    # 4. Pass directly to SpatialAdmissionPublisher
    candidate_geometries = {
        "comm_101": {"geometry_wkt": obs_1.geometry_wkt, "crs": obs_1.crs, "attributes": obs_1.attributes},
    }

    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_field_routing,
        decision_profile=profile,
        gate_decisions=[decision_101],
        candidate_geometries=candidate_geometries,
    )

    assert snapshot.is_consumable()
    assert len(snapshot.projections) == 1
    assert snapshot.projections[0].subject_id == "comm_101"

    # 5. Downstream Consumer reads snapshot
    adapter = ConsumerAdapter(capability=consumer_field_routing)
    projections, record = adapter.read_snapshot(snapshot, operation="routing")
    assert len(projections) == 1
    assert record.status == "SUCCESS"

    # 6. Verify raw observations are completely untouched
    assert obs_1.geometry_wkt == "POINT(108.9534 34.2678)"
    assert obs_1.source_record_id == "comm_101"
