"""RepairProposal contract: governed spatial transformation and correction proposals."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RepairType(str, Enum):
    """Canonical classification of spatial repair actions."""
    OPERATIONAL_ALIGNMENT = "OPERATIONAL_ALIGNMENT"
    NORMALIZATION = "NORMALIZATION"
    REPRESENTATION_CORRECTION = "REPRESENTATION_CORRECTION"
    COORDINATE_CORRUPTION_REPAIR = "COORDINATE_CORRUPTION_REPAIR"
    ATTRIBUTE_REPAIR = "ATTRIBUTE_REPAIR"
    ADMIN_ASSIGNMENT_UPDATE = "ADMIN_ASSIGNMENT_UPDATE"
    ENTITY_LINK_REPAIR = "ENTITY_LINK_REPAIR"


class RepairRiskClass(str, Enum):
    """Governance risk tier determining required review authority."""
    R0_LOW = "R0_LOW"
    R1_MODERATE = "R1_MODERATE"
    R2_HIGH = "R2_HIGH"
    R3_CRITICAL = "R3_CRITICAL"


class ProposalStatus(str, Enum):
    """Lifecycle states of a RepairProposal."""
    GENERATED = "GENERATED"
    PROPOSED = "PROPOSED"
    UNDER_VALIDATION = "UNDER_VALIDATION"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    REVOKED = "REVOKED"


class RepairProposal(BaseModel):
    """A formal proposal to apply a spatial transformation or correction to derived state.
    
    Invariants:
    1. Does NOT publish directly; requires independent validation and formal RepairApproval (RP-01).
    2. Generation evidence MUST be separated from validation evidence (RP-02).
    3. Strictly bounded by an explicit applicability envelope (RP-09).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    proposal_id: str
    subject_scope: str = Field(description="Dataset, batch, or subject identifier target")
    repair_type: RepairType = Field(default=RepairType.OPERATIONAL_ALIGNMENT)
    risk_class: RepairRiskClass = Field(default=RepairRiskClass.R2_HIGH)
    source_state_ref: str = Field(description="Reference to raw source asset or baseline world state")
    proposed_transform: str = Field(description="Algorithm or function specification (e.g. bd09_to_wgs84)")
    transform_parameters: Dict[str, Any] = Field(default_factory=dict)
    generation_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Evidence used to formulate the repair hypothesis",
    )
    validation_evidence_ids: List[str] = Field(
        default_factory=list,
        description="INDEPENDENT held-out evidence proving the repair improves fitness without regression",
    )
    assumptions: List[str] = Field(default_factory=list)
    applicable_scope: Dict[str, Any] = Field(
        default_factory=dict,
        description="Bounding conditions: provider, city, batch, date_range, precision_family",
    )
    expected_decision_effect: Dict[str, str] = Field(
        default_factory=dict,
        description="Expected change on DP-01/DP-02 admission status",
    )
    known_limitations: List[str] = Field(default_factory=list)
    status: ProposalStatus = Field(default=ProposalStatus.PROPOSED)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_scope_applicable(self, record_context: Dict[str, Any]) -> bool:
        """Verifies whether a record falls within this proposal's applicable envelope."""
        for k, required_val in self.applicable_scope.items():
            actual_val = record_context.get(k)
            if actual_val != required_val:
                return False
        return True
