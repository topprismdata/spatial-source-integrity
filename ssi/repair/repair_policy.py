"""RepairPolicy contract: governs repair validation standards, approver authority, and promotion rules."""

from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class RepairPolicy(BaseModel):
    """Policy defining validation rigor and required authorization tiers for repair proposals."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str = Field(default="REPAIR-POLICY-STANDARD")
    version: str = Field(default="1.0.0")
    require_holdout_validation: bool = Field(default=True)
    require_shadow_state_first: bool = Field(default=True)
    allowed_approver_roles: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "R0_LOW": ["REVIEWER", "DOMAIN_EXPERT", "DATA_STEWARD", "POLICY_OWNER"],
            "R1_MODERATE": ["DOMAIN_EXPERT", "DATA_STEWARD", "POLICY_OWNER"],
            "R2_HIGH": ["DATA_STEWARD", "POLICY_OWNER"],
            "R3_CRITICAL": ["POLICY_OWNER"],
        }
    )

    def can_approve(self, role: str, risk_class: str) -> bool:
        """Determines if a given human reviewer role has authority to approve a repair risk tier."""
        permitted_roles = self.allowed_approver_roles.get(risk_class, [])
        return role in permitted_roles
