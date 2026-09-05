"""GateDecision runtime contract: immutable admission determination."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.runtime.decision_stability import DecisionStability
from ssi.contracts.runtime.requirement_evaluation import RequirementEvaluation
from ssi.contracts.runtime.usage_limit import UsageLimit


class AdmissionAction(str, Enum):
    """Canonical admission determination for a specific DecisionProfile."""
    ALLOW = "ALLOW"
    ALLOW_WITH_LIMITS = "ALLOW_WITH_LIMITS"
    REVIEW = "REVIEW"
    BLOCK_FOR_PROFILE = "BLOCK_FOR_PROFILE"


class GovernanceDisposition(str, Enum):
    """Higher-scope governance disposition."""
    NONE = "NONE"
    QUARANTINE_SCOPE = "QUARANTINE_SCOPE"
    SUSPEND_SOURCE = "SUSPEND_SOURCE"
    REPAIR_REQUIRED = "REPAIR_REQUIRED"
    INVESTIGATION_REQUIRED = "INVESTIGATION_REQUIRED"


class GateDecision(BaseModel):
    """Immutable record of gate evaluation binding versioned context to admission action.
    
    Invariants:
    1. Immutable (frozen = True).
    2. Binds subject, candidate, evaluation, profile, policy, and ontology versions.
    3. Production snapshot publication requires ALLOW or compatible ALLOW_WITH_LIMITS.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(description="Unique gate decision ID")
    subject_id: str = Field(description="Subject entity or record identifier")
    candidate_representation_id: str = Field(description="Candidate spatial representation evaluated")
    evaluation_result_id: str = Field(description="Underlying EvaluationResult ID")

    # Version context tuple
    decision_profile_id: str = Field(description="Target DecisionProfile ID")
    decision_profile_version: str = Field(description="Target DecisionProfile version")
    gate_policy_id: str = Field(description="GatePolicy ID")
    gate_policy_version: str = Field(description="GatePolicy version")
    consumer_capability_version: Optional[str] = Field(
        default=None,
        description="Version of consumer capability contract evaluated against",
    )
    ontology_version: str = Field(default="0.1.0-rc2", description="Bound ontology version")

    # Determination
    action: AdmissionAction = Field(description="Admission determination")
    disposition: GovernanceDisposition = Field(
        default=GovernanceDisposition.NONE,
        description="Governance disposition applied to subject or scope",
    )
    applied_usage_limits: List[UsageLimit] = Field(
        default_factory=list,
        description="Machine-readable usage limits if ALLOW_WITH_LIMITS",
    )
    requirement_evaluations: List[RequirementEvaluation] = Field(
        default_factory=list,
        description="Detailed evaluations per required dimension",
    )
    decision_stability: Optional[DecisionStability] = Field(
        default=None,
        description="Stability assessment over plausible states",
    )
    justification: str = Field(description="Audit explanation for this decision")
    decided_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: Optional[str] = Field(default=None, description="Expiration ISO timestamp")

    def is_admitted(self) -> bool:
        """Returns True if the subject is admitted (either clean or with limits)."""
        return self.action in (AdmissionAction.ALLOW, AdmissionAction.ALLOW_WITH_LIMITS)

    def is_blocked(self) -> bool:
        """Returns True if blocked for this profile."""
        return self.action == AdmissionAction.BLOCK_FOR_PROFILE

    def is_review(self) -> bool:
        """Returns True if routed to human review."""
        return self.action == AdmissionAction.REVIEW
