"""HumanReviewTask, EvidenceBundle, and HumanAdjudication contracts for SSI HITL governance."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewerRole(str, Enum):
    """Authority hierarchy of human reviewers."""
    REVIEWER = "REVIEWER"
    DOMAIN_EXPERT = "DOMAIN_EXPERT"
    DATA_STEWARD = "DATA_STEWARD"
    POLICY_OWNER = "POLICY_OWNER"


class PredictionVisibility(str, Enum):
    """Visibility of machine prediction to prevent cognitive anchor bias."""
    PREDICTION_HIDDEN = "PREDICTION_HIDDEN"
    PREDICTION_VISIBLE = "PREDICTION_VISIBLE"
    PARTIALLY_VISIBLE = "PARTIALLY_VISIBLE"


class AdjudicationAction(str, Enum):
    """Canonical human adjudication verdicts.
    
    Invariant: APPROVE_REPAIR is strictly excluded. Repair approval is a separate governance proposition.
    """
    SUPPORT = "SUPPORT"
    REFUTE = "REFUTE"
    UNRESOLVED = "UNRESOLVED"
    ESCALATE = "ESCALATE"


class ReviewConfidence(str, Enum):
    """Human confidence assessment. Note: Confidence is not a probability."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ReviewEvidenceBundle(BaseModel):
    """Rich, audit-proof evidence context provided to a human reviewer."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    bundle_id: str
    bundle_version: str = "1.0.0"
    raw_declaration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw coordinate values, declared CRS, and original vendor metadata",
    )
    current_claim: Dict[str, Any] = Field(
        default_factory=dict,
        description="Target proposition under review (e.g. entity link, location adequacy)",
    )
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    reference_provenance: Dict[str, str] = Field(default_factory=dict)
    reference_dependency: str = Field(
        default="DEPENDENCY_UNKNOWN",
        description="VERIFIED_INDEPENDENT | KNOWN_DEPENDENT | DEPENDENCY_UNKNOWN",
    )
    spatial_context: Dict[str, Any] = Field(default_factory=dict)
    relevant_measurements: List[Dict[str, Any]] = Field(default_factory=list)
    resolver_state: Optional[str] = Field(default=None)
    decision_impact: Optional[Dict[str, Any]] = Field(default=None)
    known_limitations: List[str] = Field(default_factory=list)


class HumanReviewTask(BaseModel):
    """A governed task submitted to the human review queue.
    
    Invariants:
    1. Input view is frozen upon creation.
    2. Explicitly captures prediction visibility to audit anchor bias.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str
    subject_ref: str
    claim_ref: str
    trigger: str = Field(description="Trigger reason: UNCERTAINTY | CONFLICT | NOVELTY | HIGH_IMPACT | POLICY_REQUIRED")
    priority: str = Field(default="MEDIUM", description="HIGH | MEDIUM | LOW")
    business_impact: str = Field(default="MEDIUM")
    machine_state: Dict[str, Any] = Field(default_factory=dict)
    prediction_visibility: PredictionVisibility = Field(default=PredictionVisibility.PREDICTION_VISIBLE)
    evidence_bundle: ReviewEvidenceBundle
    requested_reviewer_role: ReviewerRole = Field(default=ReviewerRole.REVIEWER)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    policy_version: str = Field(default="1.0.0")


class HumanAdjudication(BaseModel):
    """The immutable, provenance-bearing verdict of a human reviewer.
    
    Invariants:
    1. Human decisions are revocable evidence, not infallible ground truth.
    2. Binds reviewer identity, role, confidence, and specific evidence.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    adjudication_id: str
    task_ref: str
    reviewer_id: str
    reviewer_role: ReviewerRole
    action: AdjudicationAction
    confidence: ReviewConfidence = Field(default=ReviewConfidence.MEDIUM)
    rationale: str
    adjudicated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    adjudicated_evidence_ids: List[str] = Field(default_factory=list)
    prediction_visibility_at_review: PredictionVisibility = Field(default=PredictionVisibility.PREDICTION_VISIBLE)
    is_revoked: bool = Field(default=False)
    revocation_reason: Optional[str] = Field(default=None)


def arbitrate_review_conflict(adjudications: List[HumanAdjudication]) -> AdjudicationAction:
    """Routes governance for a task given its human adjudications.

    Gate V2-3 / H3 invariants:
    1. CONFLICTED is a ClaimResolution state, NOT a human action. A human never
       "is conflicted"; the CLAIM is conflicted when SUPPORT and REFUTE coexist.
    2. Any SUPPORT-vs-REFUTE disagreement routes to ESCALATE / second review —
       regardless of reviewer authority. A higher-authority reviewer governs the
       routing decision; authority NEVER silently erases the reverse evidence
       produced by a lower-authority reviewer. All adjudications are retained.
    3. Never uses majority voting to manufacture consensus where genuine ambiguity exists.
    """
    if not adjudications:
        return AdjudicationAction.UNRESOLVED

    actions = {a.action for a in adjudications if not a.is_revoked}

    if AdjudicationAction.ESCALATE in actions:
        return AdjudicationAction.ESCALATE

    # SUPPORT-vs-REFUTE disagreement: governance escalates; the CLAIM becomes CONFLICTED
    # (see conflict_claim_resolution). Authority does not collapse the conflict.
    if AdjudicationAction.SUPPORT in actions and AdjudicationAction.REFUTE in actions:
        return AdjudicationAction.ESCALATE

    if AdjudicationAction.SUPPORT in actions:
        return AdjudicationAction.SUPPORT
    if AdjudicationAction.REFUTE in actions:
        return AdjudicationAction.REFUTE

    return AdjudicationAction.UNRESOLVED


def conflict_claim_resolution(
    claim_id: str,
    adjudications: List[HumanAdjudication],
) -> "ClaimResolution":
    """Builds a CONFLICTED ClaimResolution preserving BOTH sides of a reviewer dispute.

    Gate V2-3 / H3: reverse evidence from a lower-authority reviewer is preserved as
    contradicting evidence — never deleted by a higher authority. Resolving the conflict
    requires a governed second review, not authority ranking.
    """
    from ssi.contracts.shared_adapters.claim import ClaimResolution, ClaimResolutionStatus

    supporting = [a for a in adjudications if a.action == AdjudicationAction.SUPPORT and not a.is_revoked]
    contradicting = [a for a in adjudications if a.action == AdjudicationAction.REFUTE and not a.is_revoked]

    has_conflict = bool(supporting) and bool(contradicting)
    return ClaimResolution(
        claim_id=claim_id,
        status=ClaimResolutionStatus.CONFLICTED if has_conflict else ClaimResolutionStatus.UNRESOLVED,
        supporting_evidence_ids=[a.adjudication_id for a in supporting],
        contradicting_evidence_ids=[a.adjudication_id for a in contradicting],
        resolved_by="human_review_policy",
        notes=(
            "Reviewer disagreement preserved: authority governs routing (second review / "
            "escalation) but does not erase reverse evidence."
            if has_conflict
            else "No adjudication conflict."
        ),
    )
