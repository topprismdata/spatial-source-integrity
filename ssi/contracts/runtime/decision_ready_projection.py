"""DecisionReadyProjection runtime contract: admitted spatial representation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.runtime.usage_limit import UsageLimit


class DecisionReadyProjection(BaseModel):
    """An admitted spatial representation approved for a specific DecisionProfile.
    
    Invariants:
    1. Immutable.
    2. Only instantiated upon a valid, admissible GateDecision (ALLOW or compliant ALLOW_WITH_LIMITS).
    3. Preserves all machine-readable UsageLimits.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    projection_id: str = Field(description="Unique projection ID")
    subject_id: str = Field(description="Subject entity or record identifier")
    admitted_geometry_wkt: str = Field(description="Admitted WKT geometry")
    admitted_crs: str = Field(description="Coordinate reference system for this projection")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Projected attributes")
    gate_decision_id: str = Field(description="Authorizing GateDecision ID")
    decision_profile_id: str = Field(description="DecisionProfile ID this projection serves")
    usage_limits: List[UsageLimit] = Field(
        default_factory=list,
        description="Machine-enforceable limits attached to this projection",
    )
    minted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
