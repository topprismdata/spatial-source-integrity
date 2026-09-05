"""D03 — Coordinate Precision Fingerprint Detector."""

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


class D03PrecisionFingerprintDetector(BaseDetector):
    """D03: Descriptive and statistical analysis of coordinate precision and precision families.
    
    Core invariant: Never interpret more decimal places as greater positional accuracy.
    A coordinate with 15 decimals may still have a 500m gross positional error.
    """

    detector_id = "D03"
    detector_version = "0.1.0"
    detector_type = DetectorType.INTRINSIC_STATISTICAL
    measure_refs = ["decimal_precision"]

    @classmethod
    def get_decimal_places(cls, val_str: str) -> int:
        """Counts significant decimal digits after decimal point."""
        s = val_str.strip()
        if "." in s:
            decimals = s.split(".")[1]
            return len(decimals)
        return 0

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d03_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d03_{uuid.uuid4().hex[:8]}"

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is None or raw_y is None:
                continue

            dec_x = self.get_decimal_places(str(raw_x))
            dec_y = self.get_decimal_places(str(raw_y))
            min_dec = min(dec_x, dec_y)
            max_dec = max(dec_x, dec_y)

            # Assign family
            family = "STANDARD_GEO_5_6"
            if min_dec < 3:
                family = "TRUNCATED_OR_COARSE"
            elif min_dec in (3, 4):
                family = "APPROXIMATE_3_4"
            elif min_dec in (5, 6):
                family = "STANDARD_GEO_5_6"
            else:
                family = "SYNTHETIC_HIGH_PRECISION"

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d03_prec_{rec_id}",
                    target_id=rec_id,
                    measure_name="decimal_precision",
                    measure_id=MEASURE_REGISTRY["decimal_precision"].measure_id,
                    value=min_dec,
                    unit="decimal_places",
                    evaluation_method="D03_PrecisionFingerprint",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                    metaquality={"family": family, "x_decimals": dec_x, "y_decimals": dec_y},
                )
            )

            # Severe truncation finding (< 2 decimals: error > 1km)
            if min_dec <= 2:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d03_trunc_{rec_id}",
                        target_id=rec_id,
                        category="COORDINATE_PRECISION",
                        measure_name="decimal_precision",
                        finding_code="F-D03-PRECISION-DEGRADATION",
                        finding_status=FindingStatus.DETECTED,
                        severity=FindingSeverity.WARNING,
                        explanation=f"Severe precision truncation: coordinate has only {min_dec} decimal places (~1km-10km quantization).",
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
