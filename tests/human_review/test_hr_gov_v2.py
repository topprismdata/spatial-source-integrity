"""HR Governance V2 tests — Gate V2-3 H3/H4 closures."""

import pytest

from ssi.hitl.review_task import (
    AdjudicationAction,
    HumanAdjudication,
    ReviewConfidence,
    ReviewerRole,
    arbitrate_review_conflict,
    conflict_claim_resolution,
)
from ssi.hitl.workflow import reconcile_review_batch
from ssi.contracts.shared_adapters.claim import ClaimResolutionStatus


def _adj(aid, task, reviewer, role, action):
    return HumanAdjudication(
        adjudication_id=aid,
        task_ref=task,
        reviewer_id=reviewer,
        reviewer_role=role,
        action=action,
        confidence=ReviewConfidence.HIGH,
        rationale=f"{action.value} rationale",
    )


def test_hr_v2_unequal_role_disagreement_still_escalates_and_preserves_conflict():
    """H3: A DATA_STEWARD SUPPORT vs REVIEWER REFUTE dispute must ESCALATE for routing,
    and the CLAIM must become CONFLICTED with the reviewer's reverse evidence preserved —
    authority never silently erases it."""
    ste = _adj("adj_ste", "T1", "steward_a", ReviewerRole.DATA_STEWARD, AdjudicationAction.SUPPORT)
    rev = _adj("adj_rev", "T1", "reviewer_b", ReviewerRole.REVIEWER, AdjudicationAction.REFUTE)

    routing = arbitrate_review_conflict([ste, rev])
    assert routing == AdjudicationAction.ESCALATE

    cr = conflict_claim_resolution("T1", [ste, rev])
    assert cr.status == ClaimResolutionStatus.CONFLICTED
    assert cr.supporting_evidence_ids == ["adj_ste"]
    assert cr.contradicting_evidence_ids == ["adj_rev"]


def test_hr_v2_adjudication_action_enum_has_no_conflicted_member():
    """H3: CONFLICTED belongs to ClaimResolution, not to human action vocabulary."""
    assert not hasattr(AdjudicationAction, "CONFLICTED")


def test_hr_v2_reconciliation_fails_closed_on_missing_tasks():
    """H4: If 3 dispute cases are expected and only 1 adjudicated, reconciliation FAILS
    and names the missing task ids — silent skips are forbidden."""
    rec = reconcile_review_batch(
        expected_task_ids=["T1", "T2", "T3"],
        adjudications=[_adj("a1", "T1", "r1", ReviewerRole.REVIEWER, AdjudicationAction.SUPPORT)],
    )
    assert rec["passed"] is False
    assert rec["missing_task_ids"] == ["T2", "T3"]
    assert rec["expected_task_count"] == 3
    assert rec["actual_task_count"] == 1


def test_hr_v2_reconciliation_passes_only_on_exact_match():
    rec = reconcile_review_batch(
        expected_task_ids=["T1", "T2"],
        adjudications=[
            _adj("a1", "T1", "r1", ReviewerRole.REVIEWER, AdjudicationAction.SUPPORT),
            _adj("a2", "T2", "r2", ReviewerRole.REVIEWER, AdjudicationAction.REFUTE),
        ],
    )
    assert rec["passed"] is True
    assert rec["missing_task_ids"] == []
    assert rec["unexpected_task_ids"] == []
