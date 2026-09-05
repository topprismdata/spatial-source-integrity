"""EG-07: Sample / Record Boundary test.

Invariant: sample inference ≠ record-specific validation.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    QualityMeasurement,
)
from ssi.contracts.runtime.requirement_evaluation import RequirementStatus


def test_sample_inference_cannot_masquerade_as_individual_validation(
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that a record having only population sample-inferred evidence is blocked when individual evidence is required."""
    # 'rec_102' is in inferred_scope, but NOT in sampled_scope
    eval_result = EvaluationResult(
        evaluation_id="eval_sample_run",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="manifest_20260905_01",
        measurements=[
            QualityMeasurement(
                measurement_id="m_102_1",
                target_id="rec_102",
                measure_name="coordinate_schema",
                value="VALID",
                evaluation_method="D01",
            ),
            QualityMeasurement(
                measurement_id="m_102_2",
                target_id="rec_102",
                measure_name="geographic_range",
                value="VALID",
                evaluation_method="D02",
            ),
        ],
        findings=[],
        status="COMPLETED",
    )

    # By default, dp01_profile has allow_inferential_evidence = False
    assert not dp01_profile.allow_inferential_evidence

    decision = GateExecutor.evaluate_admission(
        subject_id="rec_102",
        candidate_representation_id="cand_102",
        evaluation_result=eval_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    # Must be blocked because profile does not accept inferential evidence for individual record
    assert decision.is_blocked()
    assert any(
        req.requirement_name == "individual_evidence_boundary" and req.status == RequirementStatus.NOT_SATISFIED
        for req in decision.requirement_evaluations
    )
    assert "population sample inference cannot authorize" in decision.justification
