"""EG-05: Required Assessment Missing test.

Invariant: required assessment = NOT_EVALUATED -> fail closed.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    QualityMeasurement,
)
from ssi.contracts.runtime.requirement_evaluation import RequirementStatus


def test_missing_required_assessment_fails_closed(
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that omission of an assessment required by GatePolicy blocks publication (Fail-Closed)."""
    # Policy requires ["coordinate_schema", "geographic_range"]
    # We provide only "coordinate_schema"
    incomplete_eval_result = EvaluationResult(
        evaluation_id="eval_incomplete",
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
            # "geographic_range" is intentionally omitted!
        ],
        findings=[],
        status="COMPLETED",
    )

    decision = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=incomplete_eval_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    # Must be blocked fail-closed
    assert decision.is_blocked()
    assert any(
        req.status == RequirementStatus.NOT_EVALUATED
        for req in decision.requirement_evaluations
    )
    assert "Fail-Closed" in decision.justification
