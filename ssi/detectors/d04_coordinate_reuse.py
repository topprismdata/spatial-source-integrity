"""D04 — Coordinate Reuse & Fallback Signal Detector."""

from __future__ import annotations

import collections
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
from ssi.detectors.d01_schema_parse import D01SchemaParseDetector
from ssi.evaluation.detector_definition import BaseDetector, DetectorType
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus
from ssi.evaluation.quality_measure import MEASURE_REGISTRY


class D04CoordinateReuseDetector(BaseDetector):
    """D04: Detects coordinate concentration, repeated centroids, and fallback signals.
    
    Core invariant: Duplicate coordinate != automatic error.
    Legitimate repeated points (mall centroid, community entrance, shared tower)
    are recognized through semantic co-location.
    """

    detector_id = "D04"
    detector_version = "0.1.0"
    detector_type = DetectorType.HYBRID
    measure_refs = ["coordinate_reuse_count"]

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d04_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d04_{uuid.uuid4().hex[:8]}"

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        # First pass: index coordinates and track associated geographic metadata
        coord_map: Dict[Tuple[float, float], List[ObservationAdapter]] = collections.defaultdict(list)
        parsed_records: Dict[str, Tuple[float, float]] = {}

        for record in records:
            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is None or raw_y is None:
                continue
            try:
                x = round(float(str(raw_x).strip()), 7)
                y = round(float(str(raw_y).strip()), 7)
                coord_map[(x, y)].append(record)
                parsed_records[record.source_record_id] = (x, y)
            except (ValueError, TypeError):
                continue

        # Second pass: evaluate reuse and detect cross-region anomalies
        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            if rec_id not in parsed_records:
                continue

            pt = parsed_records[rec_id]
            co_located_records = coord_map[pt]
            reuse_count = len(co_located_records)

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d04_reuse_{rec_id}",
                    target_id=rec_id,
                    measure_name="coordinate_reuse_count",
                    measure_id=MEASURE_REGISTRY["coordinate_reuse_count"].measure_id,
                    value=reuse_count,
                    unit="count",
                    evaluation_method="D04_CoordinateReuse",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

            if reuse_count > 1:
                # Check for cross-city or cross-district reuse (clear indicator of default centroid fallback)
                cities = {r.attributes.get("city") for r in co_located_records if r.attributes.get("city")}
                districts = {r.attributes.get("district") for r in co_located_records if r.attributes.get("district")}

                if len(cities) > 1:
                    findings.append(
                        QualityFinding(
                            finding_id=f"f_d04_cross_city_{rec_id}",
                            target_id=rec_id,
                            category="COORDINATE_FALLBACK",
                            measure_name="coordinate_reuse_count",
                            finding_code="F-D04-CROSS-CITY-REUSE",
                            finding_status=FindingStatus.DETECTED,
                            severity=FindingSeverity.WARNING,
                            explanation=f"Identical coordinate ({pt[0]}, {pt[1]}) reused across {len(cities)} different cities: {cities}. Severe fallback suspected.",
                            execution_ref=execution_id,
                            coverage_manifest_ref=manifest_id,
                        )
                    )
                elif len(districts) > 2:
                    findings.append(
                        QualityFinding(
                            finding_id=f"f_d04_cross_dist_{rec_id}",
                            target_id=rec_id,
                            category="COORDINATE_FALLBACK",
                            measure_name="coordinate_reuse_count",
                            finding_code="F-D04-CROSS-DISTRICT-REUSE",
                            finding_status=FindingStatus.DETECTED,
                            severity=FindingSeverity.WARNING,
                            explanation=f"Identical coordinate reused across {len(districts)} different districts. Municipal centroid fallback suspected.",
                            execution_ref=execution_id,
                            coverage_manifest_ref=manifest_id,
                        )
                    )
                # Note: if reuse is inside same community or mall, no error finding is emitted.

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
