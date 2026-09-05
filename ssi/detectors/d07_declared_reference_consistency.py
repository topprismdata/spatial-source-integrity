"""D07 — Declared Spatial Reference Consistency Detector."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import (
    FindingSeverity,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.evaluation.detector_definition import BaseDetector, DetectorType
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus
from ssi.evaluation.quality_measure import MEASURE_REGISTRY


class D07DeclaredReferenceConsistencyDetector(BaseDetector):
    """D07: Evaluates consistency between declared spatial reference metadata and observed evidence.
    
    Core invariant: Does NOT identify the replacement CRS.
    If declared CRS conflicts with observations, it emits a DECLARED_REFERENCE_CONFLICT finding
    with resolution UNRESOLVED, handing hypotheses off to the Spatial Reference Resolver.
    """

    detector_id = "D07"
    detector_version = "0.1.0"
    detector_type = DetectorType.HYBRID
    measure_refs = ["declared_reference_consistency"]

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d07_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d07_{uuid.uuid4().hex[:8]}"
        context = context or {}

        # Optional observed systematic residual from context or previous detector executions
        systematic_residual = context.get("systematic_residual_meters", 0.0)

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            declared_crs = (record.crs or "").strip().upper()

            # 1. Missing declaration
            if not declared_crs:
                measurements.append(
                    QualityMeasurement(
                        measurement_id=f"m_d07_crs_{rec_id}",
                        target_id=rec_id,
                        measure_name="declared_reference_consistency",
                        measure_id=MEASURE_REGISTRY["declared_reference_consistency"].measure_id,
                        value="MISSING_DECLARATION",
                        unit="status",
                        evaluation_method="D07_DeclaredReferenceConsistency",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d07_missing_{rec_id}",
                        target_id=rec_id,
                        category="REFERENCE_METADATA",
                        measure_name="declared_reference_consistency",
                        finding_code="F-D07-DECLARED-CRS-MISSING",
                        finding_status=FindingStatus.DETECTED,
                        severity=FindingSeverity.WARNING,
                        explanation="Spatial reference declaration is completely absent in record.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                continue

            # 2. Check for conflict with observed systematic residual
            # e.g. Declared WGS84 or EPSG:4326, but systematic offset > 300m observed
            has_conflict = False
            if declared_crs in ("WGS84", "EPSG:4326", "CGCS2000", "EPSG:4490") and systematic_residual > 300.0:
                has_conflict = True

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d07_crs_{rec_id}",
                    target_id=rec_id,
                    measure_name="declared_reference_consistency",
                    measure_id=MEASURE_REGISTRY["declared_reference_consistency"].measure_id,
                    value="CONFLICT" if has_conflict else "CONSISTENT",
                    unit="status",
                    evaluation_method="D07_DeclaredReferenceConsistency",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                    metaquality={"declared_crs": declared_crs, "systematic_residual": systematic_residual},
                )
            )

            if has_conflict:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d07_conflict_{rec_id}",
                        target_id=rec_id,
                        category="REFERENCE_CONFLICT",
                        measure_name="declared_reference_consistency",
                        finding_code="F-D07-DECLARED-CRS-CONFLICT",
                        finding_status=FindingStatus.DETECTED,
                        severity=FindingSeverity.WARNING,
                        explanation=(
                            f"Record declares '{declared_crs}', but evidence shows {systematic_residual:.1f}m systematic bias. "
                            "Declared reference is inconsistent with observed ground frame."
                        ),
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )

        manifest = EvaluationCoverageManifest(
            manifest_id=manifest_id,
            evaluation_ref=execution_id,
            eligible_scope=[r.source_record_id for r in records],
            evaluated_scope=evaluated_ids,
            sampled_scope=evaluated_ids,
        )

        return DetectorExecution(
            execution_id=execution_id,
            detector_id=self.detector_id,
            detector_version=self.detector_version,
            execution_status=ExecutionStatus.COMPLETED,
            coverage_manifest_ref=manifest.manifest_id,
            measurements=measurements,
            findings=findings,
        )
