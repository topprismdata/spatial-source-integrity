"""GatePolicy runtime contract."""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class GatePolicy(BaseModel):
    """A versioned policy mapping evaluation findings, requirements, and stability to admission.
    
    Invariants:
    1. Versioned and immutable.
    2. Enforces fail-closed behavior on missing assessments.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str = Field(description="Policy identifier (e.g. GP-STANDARD, GP-STRICT)")
    version: str = Field(description="Policy version (e.g. 1.0.0)")
    name: str = Field(description="Policy name")
    required_assessments: List[str] = Field(
        default_factory=list,
        description="Mandatory assessment names that must be evaluated; missing triggers Fail-Closed",
    )
    hard_block_finding_categories: List[str] = Field(
        default_factory=list,
        description="Finding categories that immediately trigger BLOCK_FOR_PROFILE",
    )
    review_trigger_finding_categories: List[str] = Field(
        default_factory=list,
        description="Finding categories that trigger REVIEW",
    )
    require_decision_stability: bool = Field(
        default=True,
        description="Whether UNSTABLE decisions trigger BLOCK_FOR_PROFILE or REVIEW",
    )
    unstable_disposition: str = Field(
        default="BLOCK_FOR_PROFILE",
        description="Action when decision is unstable: BLOCK_FOR_PROFILE | REVIEW",
    )
    description: str = Field(default="")
