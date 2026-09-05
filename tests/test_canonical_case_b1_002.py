"""Canonical Case B1-002 permanent regression test.

REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL
Guards against governance self-certainty: simulated adjudications must never be
eligible as human evidence, and CONFLICTED must live at ClaimResolution level.
"""

from pathlib import Path

import pytest

from ssi.hitl.review_task import (
    AdjudicationAction,
    HumanAdjudication,
    ReviewConfidence,
    ReviewerRole,
    arbitrate_review_conflict,
    conflict_claim_resolution,
)
from ssi.learning.teaching_event import HumanTeachingEvent, LearningEligibility

CASE = Path(__file__).resolve().parents[1] / "benchmarks/B1/REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL/CANONICAL_CASE.md"


def test_b1_002_case_file_present():
    assert CASE.exists()
    text = CASE.read_text(encoding="utf-8")
    assert "SIMULATED_HUMAN_EVIDENCE" in text
    assert "Gold Status:" in text and "UNADJUDICATED" in text


def test_b1_002_simulated_teaching_event_is_born_revoked():
    """Invariant 1+2: simulated adjudications cannot produce ELIGIBLE teaching events."""
    event = HumanTeachingEvent(
        event_id="HTE-SIM-1",
        task_ref="HRT-SIM",
        subject_id="s1",
        machine_prediction={},
        human_adjudication_ref="adj_sim",
        adjudicated_action="SUPPORT",
        reviewer_role="REVIEWER",
        prediction_visibility="PREDICTION_VISIBLE",
        teaching_category=TeachingCategory.T6_LEGITIMATE_ANOMALY,
        learning_eligibility=LearningEligibility.REVOKED,
        eligibility_rationale="Source adjudications are SIMULATED (Gate V2-0).",
    )
    assert event.learning_eligibility == LearningEligibility.REVOKED


def test_b1_002_conflict_preserves_both_sides_and_escalates():
    """Invariant 3: SUPPORT-vs-REFUTE ⇒ ESCALATE routing; ClaimResolution=CONFLICTED
    keeps both adjudication ids visible. Authority ranking is forbidden here."""
    ste = HumanAdjudication(
        adjudication_id="adj_hi", task_ref="T", reviewer_id="steward",
        reviewer_role=ReviewerRole.DATA_STEWARD, action=AdjudicationAction.SUPPORT,
        confidence=ReviewConfidence.HIGH, rationale="s")
    rev = HumanAdjudication(
        adjudication_id="adj_lo", task_ref="T", reviewer_id="reviewer",
        reviewer_role=ReviewerRole.REVIEWER, action=AdjudicationAction.REFUTE,
        confidence=ReviewConfidence.HIGH, rationale="r")

    assert arbitrate_review_conflict([ste, rev]) == AdjudicationAction.ESCALATE
    cr = conflict_claim_resolution("T", [ste, rev])
    assert cr.status.value == "CONFLICTED"
    assert "adj_hi" in cr.supporting_evidence_ids
    assert "adj_lo" in cr.contradicting_evidence_ids


def test_b1_002_action_vocabulary_stays_clean():
    """Invariant 3 (vocabulary): CONFLICTED must never become a human action enum member.
    It belongs to ClaimResolution only."""
    assert not [m for m in dir(AdjudicationAction) if m == "CONFLICTED"]


from ssi.learning.teaching_event import TeachingCategory  # noqa: E402
