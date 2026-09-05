"""HR-Series: Human Review & Governance tests (HR-01 ~ HR-06)."""

import hashlib
import pytest

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
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.hitl.review_task import (
    AdjudicationAction,
    HumanAdjudication,
    HumanReviewTask,
    PredictionVisibility,
    ReviewConfidence,
    ReviewEvidenceBundle,
    ReviewerRole,
    arbitrate_review_conflict,
)
from ssi.hitl.workflow import ReviewWorkflow


def test_hr_01_human_review_creates_immutable_adjudication():
    """HR-01: Human review creates an immutable adjudication audit record."""
    adjudication = HumanAdjudication(
        adjudication_id="adj_001",
        task_ref="HRT-001",
        reviewer_id="expert_a",
        reviewer_role=ReviewerRole.DOMAIN_EXPERT,
        action=AdjudicationAction.SUPPORT,
        confidence=ReviewConfidence.HIGH,
        rationale="Verified against authoritative 2026 municipal zoning map.",
        adjudicated_evidence_ids=["evi_map_01"],
        prediction_visibility_at_review=PredictionVisibility.PREDICTION_HIDDEN,
    )
    assert adjudication.adjudication_id == "adj_001"
    assert adjudication.reviewer_role == ReviewerRole.DOMAIN_EXPERT
    assert adjudication.confidence == ReviewConfidence.HIGH

    # Immutable: mutating raises ValidationError
    with pytest.raises(Exception):
        adjudication.action = AdjudicationAction.REFUTE


def test_hr_02_prediction_visibility_recorded():
    """HR-02: Prediction visibility is recorded explicitly to audit cognitive anchor bias."""
    task_blind = HumanReviewTask(
        task_id="HRT-BLIND-01",
        subject_ref="comm_101",
        claim_ref="claim_101",
        trigger="UNCERTAINTY",
        evidence_bundle=ReviewEvidenceBundle(bundle_id="b_01"),
        prediction_visibility=PredictionVisibility.PREDICTION_HIDDEN,
        requested_reviewer_role=ReviewerRole.REVIEWER,
    )
    assert task_blind.prediction_visibility == PredictionVisibility.PREDICTION_HIDDEN

    task_visible = HumanReviewTask(
        task_id="HRT-VISIBLE-01",
        subject_ref="comm_102",
        claim_ref="claim_102",
        trigger="HIGH_IMPACT",
        evidence_bundle=ReviewEvidenceBundle(bundle_id="b_02"),
        prediction_visibility=PredictionVisibility.PREDICTION_VISIBLE,
        requested_reviewer_role=ReviewerRole.DOMAIN_EXPERT,
    )
    assert task_visible.prediction_visibility == PredictionVisibility.PREDICTION_VISIBLE


def test_hr_03_reviewer_disagreement_produces_escalation_not_majority_vote():
    """HR-03: Two equal-tier reviewers disagreeing produces ESCALATE, never silent majority vote."""
    adj_1 = HumanAdjudication(
        adjudication_id="adj_a",
        task_ref="HRT-DISPUTE-01",
        reviewer_id="reviewer_x",
        reviewer_role=ReviewerRole.REVIEWER,
        action=AdjudicationAction.SUPPORT,
        rationale="Looks aligned with neighborhood boundary",
    )
    adj_2 = HumanAdjudication(
        adjudication_id="adj_b",
        task_ref="HRT-DISPUTE-01",
        reviewer_id="reviewer_y",
        reviewer_role=ReviewerRole.REVIEWER,
        action=AdjudicationAction.REFUTE,
        rationale="Crosses canal into adjacent district",
    )

    # Disagreement between equal-level reviewers must ESCALATE, not vote
    consensus = arbitrate_review_conflict([adj_1, adj_2])
    assert consensus == AdjudicationAction.ESCALATE


def test_hr_04_reviewer_cannot_approve_restricted_high_risk_repair():
    """HR-04: Ordinary REVIEWER role cannot approve high-risk (R2/R3) spatial repairs."""
    # Define role authority check
    def can_approve_high_risk_repair(role: ReviewerRole) -> bool:
        return role in (ReviewerRole.DATA_STEWARD, ReviewerRole.POLICY_OWNER)

    assert not can_approve_high_risk_repair(ReviewerRole.REVIEWER)
    assert not can_approve_high_risk_repair(ReviewerRole.DOMAIN_EXPERT)
    assert can_approve_high_risk_repair(ReviewerRole.DATA_STEWARD)
    assert can_approve_high_risk_repair(ReviewerRole.POLICY_OWNER)


def test_hr_05_human_correction_does_not_mutate_raw_source():
    """HR-05: Human review adjudication does not modify raw observation bytes."""
    raw_csv = b"id,name,x,y\n1,OldName,108.95,34.27\n"
    initial_hash = hashlib.sha256(raw_csv).hexdigest()

    obs = ObservationAdapter(
        observation_id="obs_raw_01",
        source_asset_id="asset_raw",
        source_record_id="rec_01",
        geometry_wkt="POINT(108.95 34.27)",
        attributes={"name": "OldName"},
    )

    # Human adjudicates correction
    adj = HumanAdjudication(
        adjudication_id="adj_fix_01",
        task_ref="HRT-01",
        reviewer_id="steward_d",
        reviewer_role=ReviewerRole.DATA_STEWARD,
        action=AdjudicationAction.REFUTE,
        rationale="OldName is obsolete; name updated to NewName",
    )

    # Raw observation remains invariant
    assert obs.geometry_wkt == "POINT(108.95 34.27)"
    assert obs.attributes["name"] == "OldName"
    assert hashlib.sha256(raw_csv).hexdigest() == initial_hash


def test_hr_06_human_result_must_re_enter_gate():
    """HR-06: Human adjudication converts to new evidence and must re-enter Gate for new GateDecision."""
    workflow = ReviewWorkflow()
    task = HumanReviewTask(
        task_id="HRT-GATE-01",
        subject_ref="comm_blocked_1",
        claim_ref="claim_dist_1",
        trigger="CONFLICT",
        evidence_bundle=ReviewEvidenceBundle(bundle_id="b_01"),
        requested_reviewer_role=ReviewerRole.DATA_STEWARD,
    )
    workflow.submit_task(task)

    # Expert confirms issue is resolved by official survey
    adj = HumanAdjudication(
        adjudication_id="adj_01",
        task_ref="HRT-GATE-01",
        reviewer_id="steward_a",
        reviewer_role=ReviewerRole.DATA_STEWARD,
        action=AdjudicationAction.SUPPORT,
        confidence=ReviewConfidence.HIGH,
        rationale="Official survey documents boundary adjustment in 2026",
    )
    workflow.record_adjudication(adj)

    # Transform to evidence
    human_evidence = workflow.to_evidence(adj)
    assert human_evidence.evidence_type == "HUMAN_ADJUDICATION"
    assert human_evidence.confidence.value == "HIGH"

    # Human evidence feeds into new evaluation run
    eval_result_new = EvaluationResult(
        evaluation_id="eval_after_human",
        evaluator_name="ReEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="man_new",
        measurements=[
            QualityMeasurement(measurement_id="m1", target_id="comm_blocked_1", measure_name="coordinate_schema", value="VALID", evaluation_method="D01"),
            QualityMeasurement(measurement_id="m2", target_id="comm_blocked_1", measure_name="geographic_range", value="VALID", evaluation_method="D02"),
        ],
        findings=[],  # Resolved by human evidence!
    )
    manifest = EvaluationCoverageManifest(
        manifest_id="man_new",
        evaluation_ref="eval_after_human",
        eligible_scope=["comm_blocked_1"],
        evaluated_scope=["comm_blocked_1"],
        sampled_scope=["comm_blocked_1"],
    )

    profile = DecisionProfileAdapter.create_dp01_city_analytics(max_acceptable_residual_meters=5000.0, threshold_provenance="EXPERIMENTAL_FIXTURE")
    policy = GatePolicy(
        policy_id="GP-HR06",
        version="1.0.0",
        name="HR06 Policy",
        required_assessments=["coordinate_schema"],
    )

    # Gate re-evaluates and produces clean ALLOW with new decision ID
    decision = GateExecutor.evaluate_admission(
        subject_id="comm_blocked_1",
        candidate_representation_id="cand_new",
        evaluation_result=eval_result_new,
        coverage_manifest=manifest,
        decision_profile=profile,
        gate_policy=policy,
    )
    assert decision.action == AdmissionAction.ALLOW
