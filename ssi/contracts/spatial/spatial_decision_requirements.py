"""SpatialDecisionRequirements: domain specialization owned by SSI."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SpatialDecisionRequirements(BaseModel):
    """Specification of exact spatial tolerances required for a business decision.
    
    Invariants:
    1. Immutable (frozen = True).
    2. No universal defaults that mask decision-specific fitness.
    3. Distinct requirements for CRS, positional residual, administrative boundary stability,
       and topological decision stability.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Coordinate Reference Requirements
    allowed_crs_families: List[str] = Field(
        default_factory=lambda: ["WGS84", "CGCS2000"],
        description="Acceptable coordinate reference systems or families",
    )
    require_formal_crs_identity: bool = Field(
        default=False,
        description="Whether formal CRS identity is mandatory or validated operational alignment is sufficient",
    )
    require_operational_alignment: bool = Field(
        default=True,
        description="Whether coordinates must have validated operational alignment to target frame",
    )

    # Positional Requirements
    max_acceptable_residual_meters: Optional[float] = Field(
        default=None,
        description="Maximum acceptable residual distance to external reference",
    )
    max_gross_error_rate: Optional[float] = Field(
        default=None,
        description="Maximum acceptable fraction of severe tail errors",
    )

    # Administrative Stability Requirements
    require_stable_city_assignment: bool = Field(
        default=True,
        description="Whether city assignment must be invariant across all plausible spatial states",
    )
    require_stable_district_assignment: bool = Field(
        default=False,
        description="Whether district assignment must be invariant across all plausible spatial states",
    )
    min_boundary_buffer_meters: Optional[float] = Field(
        default=None,
        description="Required minimum distance buffer from administrative boundaries for ambiguous points",
    )

    # Topological Requirements
    require_inside_geofence: bool = Field(
        default=False,
        description="Whether entity must be definitively inside its designated geofence polygon",
    )

    # Decision Stability Requirements
    require_stability: bool = Field(
        default=True,
        description="Whether decision must remain STABLE over all plausible states S*",
    )
    stability_scope: List[str] = Field(
        default_factory=lambda: ["city_assignment"],
        description="Target decision variables over which stability is assessed",
    )
