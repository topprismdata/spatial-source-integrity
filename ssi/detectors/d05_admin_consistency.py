"""D05 — Administrative Consistency Detector."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from shapely.geometry import Point, Polygon, shape
from shapely import wkt

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
from ssi.evaluation.reference_manifest import ReferenceManifest


class D05AdminConsistencyDetector(BaseDetector):
    """D05: Reference-based evaluation of administrative boundary containment and hierarchy agreement.
    
    Core invariants:
    1. Distinguishes near-boundary ambiguity from gross administrative displacement.
    2. Explicitly binds ReferenceManifest (version and time). Stale/unresolved references trigger ABSTAINED.
    3. Near-boundary envelope is a versioned DetectorConfig heuristic, not a hidden constant.
    """

    detector_id = "D05"
    detector_version = "0.1.0"
    detector_type = DetectorType.REFERENCE_DETERMINISTIC
    measure_refs = ["admin_containment", "boundary_proximity_meters"]

    def __init__(self, config=None):
        from ssi.detectors.d05_config import D05DetectorConfig
        self.config = config or D05DetectorConfig.experimental_default()

    detector_version = "0.1.0"
    detector_type = DetectorType.REFERENCE_DETERMINISTIC
    measure_refs = ["admin_containment", "boundary_proximity_meters"]

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d05_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d05_{uuid.uuid4().hex[:8]}"
        context = context or {}

        ref_manifest: Optional[ReferenceManifest] = context.get("reference_manifest")
        admin_polygons: Dict[str, Any] = context.get("admin_polygons", {})

        # If reference manifest is missing, or marked stale/unresolved, detector legitimately abstains
        if not ref_manifest or context.get("reference_stale", False):
            manifest = EvaluationCoverageManifest(
                manifest_id=manifest_id,
                evaluation_ref=execution_id,
                eligible_scope=[r.source_record_id for r in records],
                evaluated_scope=[],
                abstained_scope=[r.source_record_id for r in records],
            )
            return self.create_execution(
                coverage_manifest_ref=manifest.manifest_id,
                status=ExecutionStatus.ABSTAINED,
                abstention_reason="Administrative boundary reference dataset is missing or marked historically stale.",
            )

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

            pt = Point(x, y)
            declared_city = record.attributes.get("city")
            declared_district = record.attributes.get("district")

            target_poly = None
            if declared_district and declared_district in admin_polygons:
                target_poly = admin_polygons[declared_district]
            elif declared_city and declared_city in admin_polygons:
                target_poly = admin_polygons[declared_city]

            if target_poly is None:
                continue

            if isinstance(target_poly, str):
                target_geom = wkt.loads(target_poly)
            else:
                target_geom = target_poly

            is_inside = target_geom.contains(pt)

            # Measure boundary proximity (approximate distance in degrees converted to meters: ~111km/deg)
            dist_deg = target_geom.exterior.distance(pt) if hasattr(target_geom, "exterior") else target_geom.distance(pt)
            dist_meters = dist_deg * 111320.0

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d05_prox_{rec_id}",
                    target_id=rec_id,
                    measure_name="boundary_proximity_meters",
                    measure_id=MEASURE_REGISTRY["boundary_proximity_meters"].measure_id,
                    value=round(dist_meters, 1),
                    unit="meters",
                    evaluation_method="D05_AdminConsistency",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                    reference_refs=[ref_manifest.reference_id],
                )
            )

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d05_cont_{rec_id}",
                    target_id=rec_id,
                    measure_name="admin_containment",
                    measure_id=MEASURE_REGISTRY["admin_containment"].measure_id,
                    value="INSIDE" if is_inside else "OUTSIDE",
                    unit="status",
                    evaluation_method="D05_AdminConsistency",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                    reference_refs=[ref_manifest.reference_id],
                )
            )

            if not is_inside:
                # Distinguish near-boundary ambiguity vs gross displacement using versioned DetectorConfig
                if dist_meters <= self.config.near_boundary_envelope_meters:
                    findings.append(
                        QualityFinding(
                            finding_id=f"f_d05_near_{rec_id}",
                            target_id=rec_id,
                            category="ADMIN_NEAR_BOUNDARY",
                            measure_name="boundary_proximity_meters",
                            finding_code="F-D05-NEAR-BOUNDARY-AMBIGUITY",
                            finding_status=FindingStatus.DETECTED,
                            severity=FindingSeverity.INFO,
                            explanation=f"Point is within {dist_meters:.1f}m of boundary line; boundary ambiguity suspected.",
                            execution_ref=execution_id,
                            coverage_manifest_ref=manifest_id,
                        )
                    )
                else:
                    findings.append(
                        QualityFinding(
                            finding_id=f"f_d05_conflict_{rec_id}",
                            target_id=rec_id,
                            category="ADMIN_CONFLICT",
                            measure_name="admin_containment",
                            finding_code="F-D05-ADMIN-DISPLACEMENT",
                            finding_status=FindingStatus.CONFIRMED_ISSUE,
                            severity=FindingSeverity.WARNING,
                            explanation=f"Point is outside declared boundary by {dist_meters:.1f}m. Administrative displacement.",
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
            reference_versions={ref_manifest.source: ref_manifest.version},
        )
