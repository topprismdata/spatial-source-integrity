"""ReviewWorkflow: executes human review intake, adjudication recording, and Gate re-entry."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ssi.contracts.runtime.gate_decision import GateDecision
from ssi.contracts.shared_adapters.evidence import (
    EvidenceAdapter,
    EvidenceConfidence,
    EvidenceDependencyStatus,
)
from ssi.hitl.review_task import (
    AdjudicationAction,
    HumanAdjudication,
    HumanReviewTask,
    arbitrate_review_conflict,
)


class ReviewWorkflow:
    """Workflow engine managing the lifecycle of human review tasks and their evidence transformation."""

    def __init__(self):
        self._tasks: Dict[str, HumanReviewTask] = {}
        self._adjudications: Dict[str, List[HumanAdjudication]] = {}

    def submit_task(self, task: HumanReviewTask) -> None:
        """Enqueues a HumanReviewTask."""
        self._tasks[task.task_id] = task
        if task.task_id not in self._adjudications:
            self._adjudications[task.task_id] = []

    def record_adjudication(self, adjudication: HumanAdjudication) -> AdjudicationAction:
        """Records an adjudication and returns the current consensus action for the task."""
        if adjudication.task_ref not in self._tasks:
            raise KeyError(f"Task '{adjudication.task_ref}' not found in review workflow.")

        self._adjudications[adjudication.task_ref].append(adjudication)
        return arbitrate_review_conflict(self._adjudications[adjudication.task_ref])

    def to_evidence(self, adjudication: HumanAdjudication) -> EvidenceAdapter:
        """Transforms a human adjudication into an auditable EvidenceAdapter.
        
        Invariant: Human input is evidence, not infallible ground truth.
        """
        conf_map = {
            "LOW": EvidenceConfidence.LOW,
            "MEDIUM": EvidenceConfidence.MEDIUM,
            "HIGH": EvidenceConfidence.HIGH,
        }
        confidence = conf_map.get(adjudication.confidence.value, EvidenceConfidence.MEDIUM)

        return EvidenceAdapter(
            evidence_id=f"evi_human_{uuid.uuid4().hex[:8]}",
            evidence_type="HUMAN_ADJUDICATION",
            source_ref=f"{adjudication.reviewer_role.value}:{adjudication.reviewer_id}",
            content_summary=f"[{adjudication.action.value}] {adjudication.rationale}",
            metrics={
                "adjudication_action": adjudication.action.value,
                "task_ref": adjudication.task_ref,
                "prediction_visibility": adjudication.prediction_visibility_at_review.value,
            },
            confidence=confidence,
            dependency_status=EvidenceDependencyStatus.VERIFIED_INDEPENDENT,
        )

    def get_adjudications(self, task_id: str) -> List[HumanAdjudication]:
        return list(self._adjudications.get(task_id, []))


def reconcile_review_batch(
    expected_task_ids: List[str],
    adjudications: List[HumanAdjudication],
) -> Dict[str, Any]:
    """Gate V2-3 / H4: strict expected-vs-actual reconciliation for a review batch.

    Returns a reconciliation dict; `passed` is True only when every expected task was
    adjudicated and no unexpected task appears. Silent skips are forbidden.
    """
    adjudicated_ids = {a.task_ref for a in adjudications}
    missing = sorted(set(expected_task_ids) - adjudicated_ids)
    unexpected = sorted(adjudicated_ids - set(expected_task_ids))
    return {
        "expected_task_count": len(expected_task_ids),
        "actual_task_count": len(adjudicated_ids),
        "missing_task_ids": missing,
        "unexpected_task_ids": unexpected,
        "passed": not missing and not unexpected,
    }
