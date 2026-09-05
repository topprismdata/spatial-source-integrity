"""D01 — Coordinate Schema & Parse Detector."""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

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


class D01SchemaParseDetector(BaseDetector):
    """D01: Deterministic evaluation of coordinate field presence, numeric parseability, and dimensionality."""

    detector_id = "D01"
    detector_version = "0.1.0"
    detector_type = DetectorType.INTRINSIC_DETERMINISTIC
    measure_refs = ["coordinate_presence", "coordinate_schema", "dimension_consistency"]

    POINT_REGEX = re.compile(r"^POINT\s*\(\s*([^\s\(\)]+)\s+([^\s\(\)]+)(?:\s+([^\s\(\)]+))?\s*\)$", re.IGNORECASE)

    @classmethod
    def extract_raw_coords(cls, record: ObservationAdapter) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
        """Extracts raw (x, y, z) coordinate representations from geometry_wkt or attributes."""
        if record.geometry_wkt:
            match = cls.POINT_REGEX.match(record.geometry_wkt.strip())
            if match:
                return match.group(1), match.group(2), match.group(3)

        attrs = record.attributes
        for x_key in ("lng", "lon", "longitude", "x"):
            for y_key in ("lat", "latitude", "y"):
                if x_key in attrs and y_key in attrs:
                    return attrs[x_key], attrs[y_key], attrs.get("z")

        return None, None, None

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d01_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d01_{uuid.uuid4().hex[:8]}"

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            raw_x, raw_y, raw_z = self.extract_raw_coords(record)

            # 1. Coordinate presence check
            has_presence = raw_x is not None and raw_y is not None
            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d01_pres_{rec_id}",
                    target_id=rec_id,
                    measure_name="coordinate_presence",
                    measure_id=MEASURE_REGISTRY["coordinate_presence"].measure_id,
                    value=has_presence,
                    unit="boolean",
                    evaluation_method="D01_SchemaParse",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

            if not has_presence:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d01_missing_{rec_id}",
                        target_id=rec_id,
                        category="CORRUPTED_COORDINATE",
                        measure_name="coordinate_presence",
                        finding_code="F-D01-MISSING",
                        finding_status=FindingStatus.CONFIRMED_ISSUE,
                        severity=FindingSeverity.CRITICAL,
                        explanation="Coordinate fields are missing or empty in record.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                continue

            # 2. Numeric parse check
            parse_success = False
            parsed_x, parsed_y = None, None
            try:
                parsed_x = float(str(raw_x).strip())
                parsed_y = float(str(raw_y).strip())
                parse_success = True
            except (ValueError, TypeError):
                parse_success = False

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d01_parse_{rec_id}",
                    target_id=rec_id,
                    measure_name="coordinate_schema",
                    measure_id=MEASURE_REGISTRY["coordinate_schema"].measure_id,
                    value="VALID" if parse_success else "INVALID",
                    unit="status",
                    evaluation_method="D01_SchemaParse",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

            if not parse_success:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d01_parse_{rec_id}",
                        target_id=rec_id,
                        category="CORRUPTED_COORDINATE",
                        measure_name="coordinate_schema",
                        finding_code="F-D01-PARSE-FAIL",
                        finding_status=FindingStatus.CONFIRMED_ISSUE,
                        severity=FindingSeverity.CRITICAL,
                        explanation=f"Cannot parse coordinate values to float: x='{raw_x}', y='{raw_y}'.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
                continue

            # 3. Dimension consistency check
            dim = 3 if raw_z is not None else 2
            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d01_dim_{rec_id}",
                    target_id=rec_id,
                    measure_name="dimension_consistency",
                    measure_id=MEASURE_REGISTRY["dimension_consistency"].measure_id,
                    value=f"{dim}D",
                    unit="dimension",
                    evaluation_method="D01_SchemaParse",
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
