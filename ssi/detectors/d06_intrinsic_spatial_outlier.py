"""D06 — Intrinsic Spatial Outlier Detector."""

from __future__ import annotations

import math
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


class D06IntrinsicSpatialOutlierDetector(BaseDetector):
    """D06: Pure intrinsic spatial outlier detection relative to peer distribution.
    
    Core invariants:
    1. Zero external reference dependencies: does not consume admin polygons or external maps.
    2. Peer outlier != confirmed error. Legitimate remote locations are signals, not errors.
    """

    detector_id = "D06"
    detector_version = "0.1.0"
    detector_type = DetectorType.INTRINSIC_STATISTICAL
    measure_refs = ["intrinsic_outlier_score"]

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d06_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d06_{uuid.uuid4().hex[:8]}"

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        valid_points: List[Tuple[str, float, float]] = []
        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)
            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is None or raw_y is None:
                continue
            try:
                x = float(str(raw_x).strip())
                y = float(str(raw_y).strip())
                valid_points.append((rec_id, x, y))
            except (ValueError, TypeError):
                continue

        if len(valid_points) >= 3:
            # Calculate robust centroid: component-wise median
            xs = sorted([p[1] for p in valid_points])
            ys = sorted([p[2] for p in valid_points])
            mid = len(xs) // 2
            med_x = xs[mid] if len(xs) % 2 != 0 else (xs[mid - 1] + xs[mid]) / 2.0
            med_y = ys[mid] if len(ys) % 2 != 0 else (ys[mid - 1] + ys[mid]) / 2.0

            # Distance of each point to the median centroid (Euclidean in degrees as fast robust proxy)
            dists = [math.hypot(p[1] - med_x, p[2] - med_y) for p in valid_points]
            sorted_dists = sorted(dists)
            med_dist = sorted_dists[len(sorted_dists) // 2]

            # Median Absolute Deviation (MAD) of distances
            abs_devs = sorted([abs(d - med_dist) for d in dists])
            mad = abs_devs[len(abs_devs) // 2]
            mad_sigma = max(mad * 1.4826, 0.001)  # Guard against zero division in dense points

            for (rec_id, x, y), dist in zip(valid_points, dists):
                outlier_score = dist / mad_sigma

                measurements.append(
                    QualityMeasurement(
                        measurement_id=f"m_d06_out_{rec_id}",
                        target_id=rec_id,
                        measure_name="intrinsic_outlier_score",
                        measure_id=MEASURE_REGISTRY["intrinsic_outlier_score"].measure_id,
                        value=round(outlier_score, 3),
                        unit="score",
                        evaluation_method="D06_IntrinsicSpatialOutlier",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                        metaquality={"distance_to_median_deg": round(dist, 5), "mad_sigma": round(mad_sigma, 5)},
                    )
                )

                # Flag extreme peer outlier (score > 4.5 sigma) as a diagnostic signal
                if outlier_score > 4.5:
                    findings.append(
                        QualityFinding(
                            finding_id=f"f_d06_out_{rec_id}",
                            target_id=rec_id,
                            category="SPATIAL_OUTLIER",
                            measure_name="intrinsic_outlier_score",
                            finding_code="F-D06-INTRINSIC-OUTLIER",
                            finding_status=FindingStatus.DETECTED,
                            severity=FindingSeverity.WARNING,
                            explanation=f"Point ({x}, {y}) is {outlier_score:.1f} MAD sigmas away from internal batch median.",
                            execution_ref=execution_id,
                            coverage_manifest_ref=manifest_id,
                        )
                    )
        else:
            # Insufficient points for robust statistical outlier detection
            for rec_id, _, _ in valid_points:
                measurements.append(
                    QualityMeasurement(
                        measurement_id=f"m_d06_out_{rec_id}",
                        target_id=rec_id,
                        measure_name="intrinsic_outlier_score",
                        measure_id=MEASURE_REGISTRY["intrinsic_outlier_score"].measure_id,
                        value=0.0,
                        unit="score",
                        evaluation_method="D06_IntrinsicSpatialOutlier",
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
