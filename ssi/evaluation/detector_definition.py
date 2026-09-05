"""BaseDetector interface and detector definitions."""

from __future__ import annotations

import abc
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import QualityFinding, QualityMeasurement
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus


class DetectorType(str, Enum):
    """Classification of detector logic."""
    INTRINSIC_DETERMINISTIC = "INTRINSIC_DETERMINISTIC"
    INTRINSIC_STATISTICAL = "INTRINSIC_STATISTICAL"
    REFERENCE_DETERMINISTIC = "REFERENCE_DETERMINISTIC"
    REFERENCE_STATISTICAL = "REFERENCE_STATISTICAL"
    HYBRID = "HYBRID"


class BaseDetector(abc.ABC):
    """Abstract base class for all TopPrism spatial quality detectors."""

    detector_id: str
    detector_version: str = "0.1.0"
    detector_type: DetectorType
    measure_refs: List[str]

    @abc.abstractmethod
    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        """Executes the detector evaluation over a batch of records and returns a DetectorExecution."""
        pass

    def create_execution(
        self,
        coverage_manifest_ref: str,
        status: ExecutionStatus = ExecutionStatus.COMPLETED,
        measurements: Optional[List[QualityMeasurement]] = None,
        findings: Optional[List[QualityFinding]] = None,
        reference_versions: Optional[Dict[str, str]] = None,
        abstention_reason: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> DetectorExecution:
        """Helper to create a well-formed DetectorExecution record."""
        return DetectorExecution(
            execution_id=f"exec_{self.detector_id.lower()}_{uuid.uuid4().hex[:8]}",
            detector_id=self.detector_id,
            detector_version=self.detector_version,
            execution_status=status,
            coverage_manifest_ref=coverage_manifest_ref,
            measurements=measurements or [],
            findings=findings or [],
            reference_versions=reference_versions or {},
            abstention_reason=abstention_reason,
            failure_reason=failure_reason,
        )
