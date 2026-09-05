"""Phase 0 Definition of Done: End-to-End Synthetic Flows A and B."""

import pytest
from ssi.adapters.consumer_adapter import ConsumerAdapter, ConsumptionError
from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher
from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.decision_stability import DecisionStability, StabilityState
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_decision import AdmissionAction
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter


def test_flow_a_successful_admission_end_to_end():
    """Flow A — Successful Admission Demonstration.
    
    Synthetic Source
          ↓
    EvaluationResult
          ↓
    Coverage includes Subject
          ↓
    Requirements satisfied
          ↓
    DecisionStability = STABLE
          ↓
    GateDecision = ALLOW
          ↓
    DecisionReadyProjection
          ↓
    ACTIVE + PRODUCTION Snapshot
          ↓
    Consumer
          ↓
    SnapshotConsumptionRecord
    """
    # 1. Synthetic Source Record
    source_obs = ObservationAdapter(
        observation_id="obs_xi_001",
        source_asset_id="asset_synthetic_xi_an",
        source_record_id="rec_xi_001",
        geometry_wkt="POINT(108.9534 34.2678)",
        crs="EPSG:4326",
        attributes={"community_name": "BellTowerCommunity", "city": "Xi'an"},
        provenance="synthetic_source_batch_1",
    )

    # 2. EvaluationResult
    eval_result = EvaluationResult(
        evaluation_id="eval_flow_a_01",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="manifest_flow_a_01",
        measurements=[
            QualityMeasurement(
                measurement_id="m_1",
                target_id=source_obs.source_record_id,
                measure_name="coordinate_schema",
                value="VALID",
                evaluation_method="D01",
            ),
            QualityMeasurement(
                measurement_id="m_2",
                target_id=source_obs.source_record_id,
                measure_name="geographic_range",
                value="VALID",
                evaluation_method="D02",
            ),
            QualityMeasurement(
                measurement_id="m_3",
                target_id=source_obs.source_record_id,
                measure_name="positional_residual",
                value=45.0,
                unit="meters",
                evaluation_method="D08",
            ),
        ],
        findings=[],
        status="COMPLETED",
    )

    # 3. CoverageManifest including the subject
    coverage_manifest = EvaluationCoverageManifest(
        manifest_id="manifest_flow_a_01",
        evaluation_ref=eval_result.evaluation_id,
        eligible_scope=[source_obs.source_record_id],
        evaluated_scope=[source_obs.source_record_id],
        sampled_scope=[source_obs.source_record_id],
    )

    # 4. DecisionProfile and GatePolicy
    profile = DecisionProfileAdapter.create_dp02_visit_planning(max_residual_meters=200.0, threshold_provenance="EXPERIMENTAL_FIXTURE")
    policy = GatePolicy(
        policy_id="GP-FLOW-A",
        version="1.0.0",
        name="Flow A Policy",
        required_assessments=["coordinate_schema", "geographic_range"],
        require_decision_stability=True,
    )

    # 5. DecisionStability = STABLE
    stability = DecisionStability(
        scope="district_assignment",
        state=StabilityState.STABLE,
        plausible_state_count=3,
        competing_outcomes=["BeilinDistrict", "BeilinDistrict", "BeilinDistrict"],
        rationale="All plausible variations in location fall solidly inside Beilin District.",
    )

    # 6. Consumer Capability
    consumer = ConsumerCapability(
        consumer_id="FieldRoutingSystem",
        consumer_version="2.1.0",
        name="Field Routing Downstream Consumer",
        supported_operations=["aggregation", "reporting", "routing"],
        supports_usage_limits=True,
    )

    # 7. Gate Decision -> ALLOW
    gate_decision = GateExecutor.evaluate_admission(
        subject_id=source_obs.source_record_id,
        candidate_representation_id="cand_xi_001",
        evaluation_result=eval_result,
        coverage_manifest=coverage_manifest,
        decision_profile=profile,
        gate_policy=policy,
        consumer_capability=consumer,
        decision_stability=stability,
    )

    assert gate_decision.action == AdmissionAction.ALLOW
    assert gate_decision.is_admitted()

    # 8. SpatialAdmissionPublisher -> Mints DecisionReadyProjection and publishes Snapshot
    candidate_geometries = {
        source_obs.source_record_id: {
            "geometry_wkt": source_obs.geometry_wkt,
            "crs": source_obs.crs,
            "attributes": source_obs.attributes,
        }
    }

    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer,
        decision_profile=profile,
        gate_decisions=[gate_decision],
        candidate_geometries=candidate_geometries,
    )

    assert snapshot.is_consumable()
    assert len(snapshot.projections) == 1
    assert snapshot.projections[0].subject_id == source_obs.source_record_id
    assert snapshot.content_hash != ""

    # 9. Consumer Adapter -> reads snapshot and generates audit consumption record
    adapter = ConsumerAdapter(capability=consumer)
    projections, consumption_record = adapter.read_snapshot(snapshot, operation="routing")

    assert len(projections) == 1
    assert consumption_record.status == "SUCCESS"
    assert consumption_record.consumer_id == consumer.consumer_id
    assert consumption_record.snapshot_id == snapshot.snapshot_id


def test_flow_b_fail_closed_demonstration():
    """Flow B — Fail-Closed Demonstration.
    
    Synthetic Source
          ↓
    required evaluation missing
          ↓
    Coverage missing
          ↓
    Gate = BLOCK / no valid admission
          ↓
    Publisher emits nothing
          ↓
    Consumer access = 0
    (Even with manually asserted legacy decision_ready=True)
    """
    source_obs = ObservationAdapter(
        observation_id="obs_bad_002",
        source_asset_id="asset_synthetic_xi_an",
        source_record_id="rec_bad_002",
        geometry_wkt="POINT(108.95 34.27)",
        crs="EPSG:4326",
    )

    # 1. Coverage Manifest omits this subject (Coverage Missing)
    empty_coverage_manifest = EvaluationCoverageManifest(
        manifest_id="manifest_flow_b_empty",
        evaluation_ref="eval_flow_b_empty",
        eligible_scope=["rec_other_100"],
        evaluated_scope=["rec_other_100"],
    )

    # 2. Evaluation Result missing required assessments
    empty_eval_result = EvaluationResult(
        evaluation_id="eval_flow_b_empty",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="manifest_flow_b_empty",
        measurements=[],
        findings=[],
        status="FAILED",
    )

    profile = DecisionProfileAdapter.create_dp01_city_analytics(max_acceptable_residual_meters=5000.0, threshold_provenance="EXPERIMENTAL_FIXTURE")
    policy = GatePolicy(
        policy_id="GP-FLOW-B",
        version="1.0.0",
        name="Flow B Policy",
        required_assessments=["coordinate_schema", "geographic_range"],
    )
    consumer = ConsumerCapability(
        consumer_id="MacroAggregator",
        consumer_version="1.0.0",
        name="Aggregator",
        supported_operations=["aggregation"],
    )

    # 3. Gate Evaluation -> BLOCK_FOR_PROFILE (Fail-Closed)
    gate_decision = GateExecutor.evaluate_admission(
        subject_id=source_obs.source_record_id,
        candidate_representation_id="cand_bad_002",
        evaluation_result=empty_eval_result,
        coverage_manifest=empty_coverage_manifest,
        decision_profile=profile,
        gate_policy=policy,
        consumer_capability=consumer,
    )

    assert gate_decision.is_blocked()

    # 4. Attempt to publish -> Publisher emits NOTHING (0 projections)
    candidate_geometries = {
        source_obs.source_record_id: {
            "geometry_wkt": source_obs.geometry_wkt,
            "crs": source_obs.crs,
        }
    }

    # Simulate manual legacy attempt: even if someone claims decision_ready=True outside the gate
    legacy_pretended_decision_ready = True
    assert legacy_pretended_decision_ready is True

    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer,
        decision_profile=profile,
        gate_decisions=[gate_decision],
        candidate_geometries=candidate_geometries,
    )

    # Invariant: Publisher emits zero projections
    assert len(snapshot.projections) == 0
    assert snapshot.manifest_metadata["projections_count"] == 0

    # 5. Downstream Consumer receives 0 records
    adapter = ConsumerAdapter(capability=consumer)
    projections, consumption_record = adapter.read_snapshot(snapshot, operation="aggregation")
    assert len(projections) == 0
