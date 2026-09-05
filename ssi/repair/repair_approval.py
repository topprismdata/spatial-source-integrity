"""RepairApproval contract: explicit governance authorization of validated repair proposals."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RepairApproval(BaseModel):
    """Explicit governance authorization required before an approved repair can create derived state.
    
    Invariants:
    1. Standalone object; cannot be substituted by a HumanAdjudication record (RP-03).
    2. Revocation invalidates derived state and triggers downstream impact review (RP-08).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    approval_id: str
    proposal_ref: str = Field(description="Reference to approved RepairProposal")
    approver_id: str = Field(description="Authorized individual or governance board identifier")
    approver_role: str = Field(description="Role: DATA_STEWARD | POLICY_OWNER")
    decision: str = Field(default="APPROVED", description="APPROVED | REJECTED | REVOKED")
    rationale: str = Field(description="Documented justification based on validation evidence")
    repair_policy_version: str = Field(default="1.0.0")
    approved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deployment_scope: str = Field(
        default="SHADOW",
        description="SHADOW | PRODUCTION (high-risk repairs require SHADOW first per section 27)",
    )
    is_revoked: bool = Field(default=False)
    revocation_reason: Optional[str] = Field(default=None)

    def revoke(self, reason: str) -> RepairApproval:
        """Returns a revoked copy of this approval."""
        return RepairApproval(
            approval_id=self.approval_id,
            proposal_ref=self.proposal_ref,
            approver_id=self.approver_id,
            approver_role=self.approver_role,
            decision="REVOKED",
            rationale=self.rationale,
            repair_policy_version=self.repair_policy_version,
            approved_at=self.approved_at,
            deployment_scope=self.deployment_scope,
            is_revoked=True,
            revocation_reason=reason,
        )
