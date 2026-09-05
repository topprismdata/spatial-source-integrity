"""D05DetectorConfig: versioned detector configuration for D05 boundary policy."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class D05DetectorConfig(BaseModel):
    """Versioned configuration for D05 Administrative Consistency Detector.
    
    Invariants:
    1. Near-boundary envelope is a versioned heuristic, not a hidden constant.
    2. When config is EXPERIMENTAL_HEURISTIC, this must be surfaced to finding consumers.
    3. The envelope value should ultimately be derived from reference resolution accuracy,
       known boundary uncertainty, and the alignment tolerance of the target decision.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    config_version: str = Field(default="0.1.0", description="Version of D05 policy configuration")
    near_boundary_envelope_meters: float = Field(
        default=50.0,
        description="Distance threshold below which a boundary discrepancy is classified as boundary ambiguity.",
    )
    config_status: str = Field(
        default="EXPERIMENTAL_HEURISTIC",
        description="EXPERIMENTAL_HEURISTIC | VALIDATED_WITHIN_ENVELOPE | CUSTOMER_APPROVED",
    )
    reference_resolution_basis: str = Field(
        default="placeholder: to be derived from reference manifest accuracy envelope",
        description="Formal derivation of near_boundary_envelope from reference data uncertainty.",
    )
    notes: str = Field(
        default="50m is a placeholder heuristic pending formal reference resolution; "
                "must NOT be treated as universal truth or promoted to DecisionProfile tolerance.",
    )

    @classmethod
    def experimental_default(cls) -> D05DetectorConfig:
        """Returns the frozen v0.1 experimental default for Phase 1R."""
        return cls(
            config_version="0.1.0",
            near_boundary_envelope_meters=50.0,
            config_status="EXPERIMENTAL_HEURISTIC",
        )
