"""MG-03: Severity Coupling Decoupling test.

Invariant: QualityFinding.severity cannot directly determine GateAction.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    FindingSeverity,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_decision import AdmissionAction


def test_severity_does_not_directly_determine_gate_action(
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
):
    """Proves that Finding severity is decoupled from GateAction.
    
    1. A CRITICAL severity finding on an informational/unblocked category does NOT block.
    2. A WARNING severity finding on a hard-blocked category DOES block.
    """
    # Case 1: Finding has CRITICAL severity, but category is COSMETIC_NAME_DISCREPANCY (not in hard-block)
    eval_critical_non_blocking = EvaluationResult(
        evaluation_id="eval_crit",
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
                finding_id="f_crit",
                target_id="rec_101",
                category="COSMETIC_NAME_DISCREPANCY",
                measure_name="name_check",
                finding_status=FindingStatus.DETECTED,
                severity=FindingSeverity.CRITICAL,  # Marked CRITICAL by old rule
                explanation="Pinyin tone mark mismatch",
            )
        ],
        status="COMPLETED",
    )

    decision_1 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=eval_critical_non_blocking,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )
    # Does NOT block just because severity was labeled CRITICAL
    assert decision_1.action == AdmissionAction.ALLOW

    # Case 2: Finding has WARNING severity, but category is OUT_OF_BOUNDS (which IS in hard-block categories)
    eval_warning_blocking = EvaluationResult(
        evaluation_id="eval_warn",
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
                finding_id="f_warn",
                target_id="rec_101",
                category="OUT_OF_BOUNDS",
                measure_name="geographic_range",
                finding_status=FindingStatus.DETECTED,
                severity=FindingSeverity.WARNING,  # Only labeled WARNING
                explanation="Coordinate outside municipal envelope",
            )
        ],
        status="COMPLETED",
    )

    decision_2 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=eval_warning_blocking,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )
    # DOES block because category is in policy's hard block list, regardless of severity level
    assert decision_2.is_blocked()
