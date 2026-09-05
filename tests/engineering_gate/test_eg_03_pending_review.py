"""EG-03: Pending Review test.

Invariant: REVIEW -> production publish count = 0.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    FindingSeverity,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.runtime.trusted_spatial_snapshot import SnapshotDeploymentMode


def test_review_status_never_enters_production_snapshot(
    consumer_macro_city,
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that a subject flagged for human review is blocked from production publication."""
    review_eval_result = EvaluationResult(
        evaluation_id="eval_run_review",
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
        ],
        findings=[
            QualityFinding(
                finding_id="f_review_1",
                target_id="rec_101",
                category="ADMIN_CONFLICT",
                measure_name="admin_consistency",
                finding_status=FindingStatus.DETECTED,
                severity=FindingSeverity.WARNING,
                explanation="Near-boundary ambiguity across district line",
            )
        ],
        status="COMPLETED",
    )

    decision = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=review_eval_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    assert decision.is_review()

    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    # Production publication attempt must export 0
    prod_snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[decision],
        candidate_geometries=candidate_geometries,
        deployment_mode=SnapshotDeploymentMode.PRODUCTION,
    )

    assert len(prod_snapshot.projections) == 0
