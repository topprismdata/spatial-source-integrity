"""D02 — Geographic Range & Representation Detector."""

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
from ssi.detectors.d01_schema_parse import D01SchemaParseDetector
from ssi.evaluation.detector_definition import BaseDetector, DetectorType
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus
from ssi.evaluation.quality_measure import MEASURE_REGISTRY


class D02RangeRepresentationDetector(BaseDetector):
    """D02: Evaluates legal geographic coordinate ranges, axis orientation, and unit scale compatibility.
    
    Core invariant: Valid global coordinate range != valid location.
    A coordinate outside local municipal boundaries but within [-180, 180] and [-90, 90]
    passes D02 as legally valid.
    """

    detector_id = "D02"
    detector_version = "0.1.0"
    detector_type = DetectorType.INTRINSIC_DETERMINISTIC
    measure_refs = ["geographic_range", "axis_interpretation"]

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d02_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d02_{uuid.uuid4().hex[:8]}"

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is None or raw_y is None:
                continue

            try:
                x = float(str(raw_x).strip())
                y = float(str(raw_y).strip())
            except (ValueError, TypeError):
                continue

            # 1. Obvious projected scale conflict (> 1000)
            if abs(x) > 1000.0 or abs(y) > 1000.0:
                measurements.append(
                    QualityMeasurement(
                        measurement_id=f"m_d02_range_{rec_id}",
                        target_id=rec_id,
                        measure_name="geographic_range",
                        measure_id=MEASURE_REGISTRY["geographic_range"].measure_id,
                        value="SCALE_CONFLICT",
                        unit="status",
                        evaluation_method="D02_RangeRepresentation",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d02_scale_{rec_id}",
                        target_id=rec_id,
                        category="SCALE_CONFLICT",
                        measure_name="geographic_range",
                        finding_code="F-D02-PROJECTED-METERS",
                        finding_status=FindingStatus.CONFIRMED_ISSUE,
                        severity=FindingSeverity.CRITICAL,
                        explanation=f"Coordinates ({x}, {y}) exceed degree space; suspected projected meter coordinates.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                continue

            # 2. Axis swap hypothesis check
            # Normal geographic: x in [-180, 180] (lon), y in [-90, 90] (lat)
            # If x in [-90, 90] and 90 < abs(y) <= 180, it is a strong axis swap candidate (lat, lon)
            axis_candidate = "LON_LAT"
            if abs(x) <= 90.0 and 90.0 < abs(y) <= 180.0:
                axis_candidate = "LAT_LON_SWAPPED"
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d02_axis_{rec_id}",
                        target_id=rec_id,
                        category="REPRESENTATION_CONFLICT",
                        measure_name="axis_interpretation",
                        finding_code="F-D02-AXIS-SWAP",
                        finding_status=FindingStatus.DETECTED,
                        severity=FindingSeverity.WARNING,
                        explanation=f"Latitude ({y}) exceeds 90 degrees while longitude ({x}) is within 90; axis swap suspected.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d02_axis_{rec_id}",
                    target_id=rec_id,
                    measure_name="axis_interpretation",
                    measure_id=MEASURE_REGISTRY["axis_interpretation"].measure_id,
                    value=axis_candidate,
                    unit="candidate",
                    evaluation_method="D02_RangeRepresentation",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

            # 3. Legal geographic range
            is_valid_range = (-180.0 <= x <= 180.0) and (-90.0 <= y <= 90.0)
            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d02_range_{rec_id}",
                    target_id=rec_id,
                    measure_name="geographic_range",
                    measure_id=MEASURE_REGISTRY["geographic_range"].measure_id,
                    value="VALID" if is_valid_range else "OUT_OF_BOUNDS",
                    unit="status",
                    evaluation_method="D02_RangeRepresentation",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

            if not is_valid_range and axis_candidate != "LAT_LON_SWAPPED":
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d02_oob_{rec_id}",
                        target_id=rec_id,
                        category="OUT_OF_BOUNDS",
                        measure_name="geographic_range",
                        finding_code="F-D02-OUT-OF-BOUNDS",
                        finding_status=FindingStatus.CONFIRMED_ISSUE,
                        severity=FindingSeverity.CRITICAL,
                        explanation=f"Coordinates ({x}, {y}) fall outside global geographic range [-180, 180], [-90, 90].",
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
