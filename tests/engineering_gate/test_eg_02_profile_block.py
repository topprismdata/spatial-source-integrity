"""EG-02: Profile Block test.

Invariant: BLOCK_FOR_PROFILE -> production publish count = 0.
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


def test_profile_block_never_enters_snapshot(
    consumer_macro_city,
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that a subject triggering a hard block is never exported to snapshot."""
    blocked_eval_result = EvaluationResult(
        evaluation_id="eval_run_blocked",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="manifest_20260905_01",
        measurements=[
            QualityMeasurement(
                measurement_id="m_1",
                target_id="rec_101",
                measure_name="coordinate_schema",
                value="INVALID",
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
                finding_id="f_1",
                target_id="rec_101",
                category="CORRUPTED_COORDINATE",
                measure_name="coordinate_schema",
                finding_status=FindingStatus.CONFIRMED_ISSUE,
                severity=FindingSeverity.CRITICAL,
                explanation="Non-numeric characters in coordinate string",
            )
        ],
        status="COMPLETED",
    )

    decision = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=blocked_eval_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    assert decision.is_blocked()

    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[decision],
        candidate_geometries=candidate_geometries,
    )

    assert len(snapshot.projections) == 0
