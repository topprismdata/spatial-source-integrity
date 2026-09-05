"""EvaluationResult runtime contract aligning with ISO 19157-1:2023."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FindingStatus(str, Enum):
    """Lifecycle status of a detected finding."""
    DETECTED = "DETECTED"
    CONFIRMED_ISSUE = "CONFIRMED_ISSUE"
    DISPUTED = "DISPUTED"
    RESOLVED = "RESOLVED"


class FindingSeverity(str, Enum):
    """Descriptive severity grade. Note: Severity alone does NOT determine GateAction."""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class QualityMeasurement(BaseModel):
    """An objective measurement produced by an evaluation detector."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    measurement_id: str = Field(description="Unique measurement ID")
    target_id: str = Field(description="Subject record or entity evaluated")
    measure_name: str = Field(description="Name from TopPrism Measure Registry")
    measure_id: str = Field(default="", description="Formal measure ID (e.g. QM-COORD-PARSE-01)")
    measure_version: str = Field(default="1.0.0", description="Version of the measure formula")
    scope: str = Field(default="RECORD", description="RECORD | BATCH | DATASET")
    value: Any = Field(description="Measured quantitative or categorical value")
    unit: str = Field(default="", description="Unit of measurement (e.g. meters, count, ratio)")
    evaluation_method: str = Field(description="Detector or algorithm that computed this value")
    execution_ref: str = Field(default="", description="DetectorExecution reference ID")
    coverage_manifest_ref: str = Field(default="", description="CoverageManifest reference ID")
    reference_refs: List[str] = Field(default_factory=list, description="IDs of external reference sources used")
    uncertainty: Optional[float] = Field(default=None, description="Estimated measurement uncertainty / error bounds")
    metaquality: Dict[str, Any] = Field(default_factory=dict, description="Metadata regarding measurement reliability")
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class QualityFinding(BaseModel):
    """An explainable diagnostic finding on a spatial subject."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str = Field(description="Unique finding ID")
    target_id: str = Field(description="Subject record or entity affected")
    category: str = Field(description="Quality dimension: COORDINATE, LOCATION, REFERENCE, ADMIN, REUSE")
    measure_name: str = Field(description="Triggering measure name")
    finding_code: str = Field(default="", description="Standard finding code (e.g. F-D01-PARSE-FAIL)")
    finding_status: FindingStatus = Field(default=FindingStatus.DETECTED)
    severity: FindingSeverity = Field(default=FindingSeverity.WARNING)
    explanation: str = Field(description="Human-readable explanation of the defect or anomaly")
    evidence_refs: List[str] = Field(default_factory=list, description="IDs of supporting evidence")
    execution_ref: str = Field(default="", description="DetectorExecution reference ID")
    coverage_manifest_ref: str = Field(default="", description="CoverageManifest reference ID")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EvaluationResult(BaseModel):
    """Versioned container for an evaluation execution output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evaluation_id: str = Field(description="Evaluation execution run ID")
    evaluator_name: str = Field(description="Evaluator engine or suite name")
    evaluator_version: str = Field(description="Version of the evaluator code")
    manifest_ref: str = Field(description="Reference to the required EvaluationCoverageManifest")
    measurements: List[QualityMeasurement] = Field(default_factory=list)
    findings: List[QualityFinding] = Field(default_factory=list)
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="COMPLETED", description="COMPLETED | FAILED | ABSTAINED")
