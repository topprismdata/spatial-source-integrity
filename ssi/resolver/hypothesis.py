"""Spatial Reference Resolver: H = (C, R, E, K) hypothesis models and resolution states."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FormalCRS(str, Enum):
    """C: Formal Coordinate Reference System."""
    WGS84 = "WGS84"
    CGCS2000 = "CGCS2000"
    WEB_MERCATOR = "WEB_MERCATOR"
    UNKNOWN = "UNKNOWN"


class Representation(str, Enum):
    """R: Coordinate Representation & Axis Order."""
    LON_LAT = "LON_LAT"
    LAT_LON = "LAT_LON"
    UNITS_METERS = "UNITS_METERS"


class AdditionalEncoding(str, Enum):
    """E: Additional Regional Encoding or Systematic Transform."""
    IDENTITY = "IDENTITY"
    GCJ_LIKE = "GCJ_LIKE"
    BD_LIKE = "BD_LIKE"
    EMPIRICAL_TRANSFORM = "EMPIRICAL_TRANSFORM"
    UNKNOWN = "UNKNOWN"


class CorruptionState(str, Enum):
    """K: Data Corruption Pattern."""
    NONE = "NONE"
    MISSING_LEADING_DIGIT = "MISSING_LEADING_DIGIT"
    DECIMAL_SHIFT = "DECIMAL_SHIFT"
    SIGN_ERROR = "SIGN_ERROR"
    FIELD_SHIFT = "FIELD_SHIFT"
    TRUNCATION = "TRUNCATION"
    DEFAULT_CENTROID = "DEFAULT_CENTROID"
    UNKNOWN_CORRUPTION = "UNKNOWN_CORRUPTION"


class CanonicalResolutionState(str, Enum):
    """Canonical outcomes of Spatial Reference Resolution."""
    IDENTIFIED = "IDENTIFIED"
    INDISTINGUISHABLE_AT_CURRENT_RESOLUTION = "INDISTINGUISHABLE_AT_CURRENT_RESOLUTION"
    ALIGNABLE_BUT_IDENTITY_UNCONFIRMED = "ALIGNABLE_BUT_IDENTITY_UNCONFIRMED"
    OUT_OF_CANDIDATE_SET = "OUT_OF_CANDIDATE_SET"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class SpatialReferenceHypothesis(BaseModel):
    """H = (C, R, E, K) 4-tuple spatial reference hypothesis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    hypothesis_id: str
    formal_crs: FormalCRS = FormalCRS.WGS84
    representation: Representation = Representation.LON_LAT
    encoding: AdditionalEncoding = AdditionalEncoding.IDENTITY
    corruption: CorruptionState = CorruptionState.NONE
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="")


class CandidateEvaluationResult(BaseModel):
    """Evaluation metrics for a candidate hypothesis across the four required axes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    hypothesis: SpatialReferenceHypothesis
    fit_residual_p50_meters: float
    fit_residual_p95_meters: float
    holdout_residual_p50_meters: float
    holdout_residual_p95_meters: float
    gross_error_rate: float
    is_adequately_aligned: bool
    relative_preference_rank: int


class ResolutionResult(BaseModel):
    """Outcome of running Spatial Reference Resolver on a dataset or pipeline segment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    resolution_id: str
    resolution_state: CanonicalResolutionState
    selected_hypothesis: Optional[SpatialReferenceHypothesis] = None
    candidate_evaluations: List[CandidateEvaluationResult] = Field(default_factory=list)
    is_operationally_aligned: bool = Field(
        default=False,
        description="CONVENIENCE FIELD ONLY. Never carries gate authority; only GateDecision grants admission.",
    )
    alignment_operation_chain: List[str] = Field(default_factory=list)
    holdout_p50_residual_meters: Optional[float] = None
    alignment_state: str = Field(
        default="NOT_EVALUATED",
        description="NOT_EVALUATED | VALIDATED_WITHIN_ENVELOPE | INADEQUATE | UNRESOLVED",
    )
    alignment_target: str = Field(
        default="WGS84",
        description="Target reference frame this alignment maps to",
    )
    validation_scope: str = Field(
        default="HOLDOUT",
        description="FIT | HOLDOUT | BLIND scope used for this validation",
    )
    validation_time: str = Field(
        default="",
        description="ISO timestamp when alignment was validated",
    )
    holdout_p95_residual_meters: Optional[float] = Field(
        default=None,
        description="P95 tail residual on holdout set",
    )
    holdout_gross_error_rate: Optional[float] = Field(
        default=None,
        description="Fraction of holdout records with residual > 500m",
    )
    alignment_coverage: Optional[float] = Field(
        default=None,
        description="Fraction of records covered by this alignment",
    )
    alignment_limitations: str = Field(
        default="",
        description="Explicit limitations of this alignment (e.g. spatial scope, temporal validity)",
    )
    rationale: str = Field(default="")
