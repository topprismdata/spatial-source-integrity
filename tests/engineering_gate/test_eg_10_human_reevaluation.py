"""EG-10: Human Re-evaluation test.

Invariant: Human correction -> new Evidence / Derived State -> new Evaluation -> new GateDecision.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    FindingSeverity,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_decision import AdmissionAction
from ssi.contracts.shared_adapters.derived_estimate import DerivedEstimateAdapter
from ssi.contracts.shared_adapters.evidence import EvidenceAdapter, EvidenceConfidence


def test_human_correction_triggers_new_gate_decision_cycle(
    dp01_profile,
    standard_gate_policy,
):
    """Proves that a human correction produces a new evaluation and a distinct new GateDecision."""
    # Round 1: Initial evaluation triggers a review finding
    manifest_v1 = EvaluationCoverageManifest(
        manifest_id="man_v1",
        evaluation_ref="eval_v1",
        eligible_scope=["rec_101"],
        evaluated_scope=["rec_101"],
        sampled_scope=["rec_101"],
    )

    eval_v1 = EvaluationResult(
        evaluation_id="eval_v1",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="man_v1",
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
                finding_id="f_admin_1",
                target_id="rec_101",
                category="ADMIN_CONFLICT",
                measure_name="admin_consistency",
                finding_status=FindingStatus.DETECTED,
                severity=FindingSeverity.WARNING,
                explanation="Conflict between declared district and geographic polygon",
            )
        ],
        status="COMPLETED",
    )

    decision_v1 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_v1",
        evaluation_result=eval_v1,
        coverage_manifest=manifest_v1,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    assert decision_v1.action == AdmissionAction.REVIEW

    # Round 2: Human adjudication confirms issue and provides independent authoritative evidence
    human_evidence = EvidenceAdapter(
        evidence_id="evi_human_01",
        evidence_type="HUMAN_ADJUDICATION",
        source_ref="expert_reviewer_a",
        content_summary="District verified against official 2026 civic survey map",
        confidence=EvidenceConfidence.HIGH,
    )

    approved_derived_state = DerivedEstimateAdapter(
        derived_id="der_v2",
        target_entity_id="rec_101",
        estimation_method="human_adjudicated_district_v1",
        geometry_wkt="POINT(108.95 34.27)",
        crs="EPSG:4326",
        attributes={"district": "Weiyang", "admin_code": "610112"},
        derived_from_observation_ids=["obs_raw_001"],
        derived_from_evidence_ids=[human_evidence.evidence_id],
        repair_approval_id="rep_app_20260905_01",
    )

    # Re-evaluation run with human evidence resolves the conflict
    manifest_v2 = EvaluationCoverageManifest(
        manifest_id="man_v2",
        evaluation_ref="eval_v2",
        eligible_scope=["rec_101"],
        evaluated_scope=["rec_101"],
        sampled_scope=["rec_101"],
    )

    eval_v2 = EvaluationResult(
        evaluation_id="eval_v2",
        evaluator_name="SyntheticEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="man_v2",
        measurements=[
            QualityMeasurement(
                measurement_id="m_v2_1",
                target_id="rec_101",
                measure_name="coordinate_schema",
                value="VALID",
                evaluation_method="D01",
            ),
            QualityMeasurement(
                measurement_id="m_v2_2",
                target_id="rec_101",
                measure_name="geographic_range",
                value="VALID",
                evaluation_method="D02",
            ),
        ],
        findings=[],  # Resolved!
        status="COMPLETED",
    )

    decision_v2 = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id=approved_derived_state.derived_id,
        evaluation_result=eval_v2,
        coverage_manifest=manifest_v2,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    # Invariants:
    # 1. New decision ID generated (history is never overwritten in place)
    assert decision_v2.decision_id != decision_v1.decision_id
    # 2. Status transitioned to clean ALLOW
    assert decision_v2.action == AdmissionAction.ALLOW
    # 3. Old decision remains historically unchanged
    assert decision_v1.action == AdmissionAction.REVIEW
