"""DetectorExecution runtime contract."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.runtime.evaluation_result import QualityFinding, QualityMeasurement


class ExecutionStatus(str, Enum):
    """Execution state of a detector run."""
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    ABSTAINED = "ABSTAINED"
    FAILED = "FAILED"


class DetectorExecution(BaseModel):
    """Audit record capturing an execution run of a specific detector.
    
    Invariants:
    1. Immutable.
    2. Explicit tracking of status (COMPLETED, SKIPPED, ABSTAINED, FAILED).
    3. Mandatory binding to an EvaluationCoverageManifest.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(description="Unique execution ID")
    detector_id: str = Field(description="Identifier of executing detector (e.g. D01, D08)")
    detector_version: str = Field(description="Semantic version of detector")
    execution_status: ExecutionStatus = Field(description="Run status")
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    coverage_manifest_ref: str = Field(description="Reference to the required EvaluationCoverageManifest")
    measurements: List[QualityMeasurement] = Field(default_factory=list)
    findings: List[QualityFinding] = Field(default_factory=list)
    reference_versions: Dict[str, str] = Field(
        default_factory=dict,
        description="Version mapping of external references used (e.g. {'OSM': '2026-08'})",
    )
    configuration_version: str = Field(default="1.0.0")
    skip_reason: Optional[str] = Field(default=None)
    abstention_reason: Optional[str] = Field(default=None)
    failure_reason: Optional[str] = Field(default=None)
