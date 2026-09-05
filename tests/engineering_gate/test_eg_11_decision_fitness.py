"""EG-11: Decision-Specific Fitness test.

Invariant: Same Entity: DP-01 = ALLOW, DP-02 = BLOCK_FOR_PROFILE must be valid.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_decision import AdmissionAction


def test_decision_specific_fitness_different_outcomes_for_same_entity(
    dp01_profile,
    dp02_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that data fitness is decision-specific: a 350m residual is allowed for DP-01 but blocked for DP-02."""
    # Positional residual = 350 meters
    eval_result_350m = EvaluationResult(
        evaluation_id="eval_350m",
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
                value=350.0,
                unit="meters",
                evaluation_method="D08",
            ),
        ],
        findings=[],
        status="COMPLETED",
    )

    # 1. Evaluate against DP-01 (City Analytics: max acceptable residual = 5000m)
    decision_dp01 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=eval_result_350m,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )
    assert decision_dp01.action == AdmissionAction.ALLOW

    # 2. Evaluate against DP-02 (Visit Planning: max acceptable residual = 200m)
    decision_dp02 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=eval_result_350m,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp02_profile,
        gate_policy=standard_gate_policy,
    )
    assert decision_dp02.action == AdmissionAction.BLOCK_FOR_PROFILE
    assert "exceeds profile tolerance" in decision_dp02.justification
