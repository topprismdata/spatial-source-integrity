"""Common test fixtures for SSI Phase 0 Engineering Gates and Migration Guards."""

import pytest
from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.decision_stability import DecisionStability, StabilityState
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    FindingSeverity,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.runtime.usage_limit import UsageLimit
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter


@pytest.fixture
def dp01_profile():
    """DP-01: City Analytics."""
    return DecisionProfileAdapter.create_dp01_city_analytics(max_acceptable_residual_meters=5000.0, threshold_provenance="EXPERIMENTAL_FIXTURE")


@pytest.fixture
def dp02_profile():
    """DP-02: Visit Planning."""
    return DecisionProfileAdapter.create_dp02_visit_planning(max_residual_meters=200.0, threshold_provenance="EXPERIMENTAL_FIXTURE")


@pytest.fixture
def dp03_profile():
    """DP-03: Fine Geofence."""
    return DecisionProfileAdapter.create_dp03_fine_geofence(max_residual_meters=20.0, threshold_provenance="EXPERIMENTAL_FIXTURE")


@pytest.fixture
def standard_gate_policy():
    """Standard Gate Policy requiring schema and coordinate checks."""
    return GatePolicy(
        policy_id="GP-STANDARD",
        version="1.0.0",
        name="Standard Admission Policy",
        required_assessments=["coordinate_schema", "geographic_range"],
        hard_block_finding_categories=["CORRUPTED_COORDINATE", "OUT_OF_BOUNDS"],
        review_trigger_finding_categories=["SUSPECTED_FALLBACK", "ADMIN_CONFLICT"],
        require_decision_stability=True,
    )


@pytest.fixture
def consumer_macro_city():
    """Macro City consumer supporting aggregation only."""
    return ConsumerCapability(
        consumer_id="MacroCityAggregator",
        consumer_version="1.0.0",
        name="Macro City Reporting Consumer",
        supported_operations=["aggregation", "reporting"],
        supports_usage_limits=True,
    )


@pytest.fixture
def consumer_field_routing():
    """Field Routing consumer supporting routing."""
    return ConsumerCapability(
        consumer_id="FieldVisitPlanner",
        consumer_version="1.0.0",
        name="Field Routing Consumer",
        supported_operations=["aggregation", "reporting", "routing"],
        supports_usage_limits=True,
    )


@pytest.fixture
def standard_coverage_manifest():
    """Manifest covering 'rec_101' individually, and 'rec_102' by sample inference."""
    return EvaluationCoverageManifest(
        manifest_id="manifest_20260905_01",
        evaluation_ref="eval_run_01",
        eligible_scope=["rec_101", "rec_102", "rec_103"],
        evaluated_scope=["rec_101", "rec_102"],
        excluded_scope=["rec_103"],
        abstained_scope=[],
        sampled_scope=["rec_101"],
        inferred_scope=["rec_102"],
    )


@pytest.fixture
def clean_evaluation_result():
    """Clean evaluation result satisfying schema, range, and with 50m residual."""
    return EvaluationResult(
        evaluation_id="eval_run_01",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="manifest_20260905_01",
        measurements=[
            QualityMeasurement(
                measurement_id="m_1",
                target_id="rec_101",
                measure_name="coordinate_schema",
                value="VALID",
                evaluation_method="D01",
            ),
            QualityMeasurement(
                measurement_id="m_2",
                target_id="rec_101",
                measure_name="geographic_range",
                value="VALID",
                evaluation_method="D02",
            ),
            QualityMeasurement(
                measurement_id="m_3",
                target_id="rec_101",
                measure_name="positional_residual",
                value=50.0,
                unit="meters",
                evaluation_method="D08",
            ),
        ],
        findings=[],
        status="COMPLETED",
    )
