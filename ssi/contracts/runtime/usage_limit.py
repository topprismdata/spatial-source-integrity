"""UsageLimit runtime contract."""

from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class UsageLimit(BaseModel):
    """Machine-enforceable constraint applied to admitted spatial data.
    
    If a consumer cannot enforce all attached limits, publication is blocked.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    limit_id: str = Field(description="Unique limit ID")
    limit_type: str = Field(
        description="Type: OPERATION_RESTRICTION, MIN_RESOLUTION, GEOGRAPHIC_BOUNDARY, TIME_HORIZON",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Exact parameter dict (e.g. {'prohibited_ops': ['routing'], 'min_scale_meters': 500})",
    )
    enforceable: bool = Field(default=True, description="Whether this limit is programmatically checkable")
    description: str = Field(default="", description="Human-readable explanation of the restriction")
