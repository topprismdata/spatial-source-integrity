"""GatePolicy Intermediate Representation (IR).

Decouples policy syntax/parsing from execution and authorization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HardBlockRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    categories: List[str] = Field(default_factory=list)


class RequiredAssessmentRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    assessment_names: List[str] = Field(default_factory=list)


class ReviewTriggerRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    categories: List[str] = Field(default_factory=list)


class StabilityRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    require_stable: bool = True
    unstable_action: str = "BLOCK_FOR_PROFILE"  # BLOCK_FOR_PROFILE | REVIEW


class GatePolicyIR(BaseModel):
    """Normalized executable Intermediate Representation of a GatePolicy."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str
    version: str
    name: str
    hard_block: HardBlockRule
    required_assessments: RequiredAssessmentRule
    review_triggers: ReviewTriggerRule
    stability: StabilityRule
    metadata: Dict[str, Any] = Field(default_factory=dict)
