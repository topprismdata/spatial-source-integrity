"""RequirementEvaluation runtime contract."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RequirementStatus(str, Enum):
    """Evaluation status of a specific decision requirement."""
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_EVALUATED = "NOT_EVALUATED"


class RequirementEvaluation(BaseModel):
    """The immutable outcome of testing one requirement against current evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    requirement_name: str = Field(description="Name of the spatial or quality requirement evaluated")
    status: RequirementStatus = Field(description="Evaluation verdict")
    observed_value: Any = Field(default=None, description="Actual measured or observed value")
    threshold: Any = Field(default=None, description="Tolerance threshold required by profile")
    rationale: str = Field(default="", description="Detailed rationale for the evaluation verdict")
