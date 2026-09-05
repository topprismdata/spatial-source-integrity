"""EvaluationCoverageManifest: P0 Fail-Closed contract proving evaluation scope."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Set
from pydantic import BaseModel, ConfigDict, Field


class EvaluationCoverageManifest(BaseModel):
    """Proves the exact scope of records evaluated in an evaluation run.
    
    Invariants:
    1. A subject outside evaluated_scope is NOT_EVALUATED.
    2. 'Zero findings' only has meaning for subjects inside evaluated_scope.
    3. Distinguishes individually evaluated records from population sample inferences.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest_id: str = Field(description="Unique manifest ID")
    evaluation_ref: str = Field(description="Reference to EvaluationResult")
    eligible_scope: List[str] = Field(
        default_factory=list,
        description="All subject IDs meeting eligibility criteria for evaluation",
    )
    evaluated_scope: List[str] = Field(
        default_factory=list,
        description="Subject IDs that were actually evaluated",
    )
    excluded_scope: List[str] = Field(
        default_factory=list,
        description="Subject IDs explicitly excluded from evaluation with documented rationale",
    )
    abstained_scope: List[str] = Field(
        default_factory=list,
        description="Subject IDs where detectors ran but legitimately abstained",
    )
    sampled_scope: List[str] = Field(
        default_factory=list,
        description="Subject IDs directly observed in a sample",
    )
    inferred_scope: List[str] = Field(
        default_factory=list,
        description="Subject IDs where evidence is inferred from a representative sample",
    )
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_covered(self, subject_id: str) -> bool:
        """Returns True if subject is within evaluated scope."""
        return subject_id in self.evaluated_scope

    def is_individually_evaluated(self, subject_id: str) -> bool:
        """Returns True if subject has direct individual evaluation (not merely inferred from sample)."""
        return subject_id in self.evaluated_scope and subject_id not in self.inferred_scope

    def is_sample_inferred(self, subject_id: str) -> bool:
        """Returns True if subject relies on population-level inferential evidence."""
        return subject_id in self.inferred_scope and subject_id not in self.sampled_scope

    @property
    def coverage_ratio(self) -> float:
        """Coverage ratio of evaluated vs eligible."""
        if not self.eligible_scope:
            return 0.0
        return len(self.evaluated_scope) / len(self.eligible_scope)
