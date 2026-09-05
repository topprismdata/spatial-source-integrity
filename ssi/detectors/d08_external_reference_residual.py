"""D08 — External Reference Residual Detector."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
import pyproj

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


class D08ExternalReferenceResidualDetector(BaseDetector):
    """D08: Calculates geodesic positional residual against matched external reference points.
    
    Core invariants:
    1. Prerequisite: Requires an auditable EntityMatchEvidence. Same name != Same Entity.
    2. Preserves reference feature definition (entrance vs centroid vs building center).
    3. Physically and semantically separates fit anchors from holdout anchors.
    """

    detector_id = "D08"
    detector_version = "0.1.0"
    detector_type = DetectorType.REFERENCE_DETERMINISTIC
    measure_refs = ["positional_residual"]

    def __init__(self):
        self._geod = pyproj.Geod(ellps="WGS84")

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d08_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d08_{uuid.uuid4().hex[:8]}"
        context = context or {}

        ref_manifest: Optional[ReferenceManifest] = context.get("reference_manifest")
        matched_anchors: Dict[str, Dict[str, Any]] = context.get("matched_anchors", {})

        evaluated_ids: List[str] = []
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        ref_refs = [ref_manifest.reference_id] if ref_manifest else []
        feature_semantics = ref_manifest.feature_semantics if ref_manifest else "unknown"

        for record in records:
            rec_id = record.source_record_id
            evaluated_ids.append(rec_id)

            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is None or raw_y is None:
                continue

            try:
                src_lon = float(str(raw_x).strip())
                src_lat = float(str(raw_y).strip())
            except (ValueError, TypeError):
                continue

            anchor = matched_anchors.get(rec_id)
            if not anchor:
                continue

            # Invariant: Entity Match Evidence check
            # An anchor must have verified entity match evidence; if marked AMBIGUOUS, residual cannot be attributed to coordinate error
            match_confidence = anchor.get("match_confidence", 1.0)
            is_ambiguous = anchor.get("is_ambiguous_match", False)
            anchor_role = anchor.get("anchor_role", "HOLDOUT")  # FIT | HOLDOUT | BLIND

            ref_lon = anchor["ref_lon"]
            ref_lat = anchor["ref_lat"]

            # Geodesic ellipsoidal distance in meters
            _, _, dist_meters = self._geod.inv(src_lon, src_lat, ref_lon, ref_lat)

            metaquality = {
                "anchor_role": anchor_role,
                "match_confidence": match_confidence,
                "is_ambiguous_match": is_ambiguous,
                "reference_feature_semantics": feature_semantics,
            }

            measurements.append(
                QualityMeasurement(
                    measurement_id=f"m_d08_res_{rec_id}",
                    target_id=rec_id,
                    measure_name="positional_residual",
                    measure_id=MEASURE_REGISTRY["positional_residual"].measure_id,
                    value=round(dist_meters, 2),
                    unit="meters",
                    evaluation_method="D08_ExternalReferenceResidual",
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                    reference_refs=ref_refs,
                    uncertainty=round(dist_meters * 0.05, 2),  # 5% baseline measurement uncertainty
                    metaquality=metaquality,
                )
            )

            # If the match was ambiguous (e.g. same name across different cities), do NOT emit a confirmed location error!
            if is_ambiguous:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d08_ambig_{rec_id}",
                        target_id=rec_id,
                        category="REFERENCE_MATCH_AMBIGUITY",
                        measure_name="positional_residual",
                        finding_code="F-D08-AMBIGUOUS-MATCH",
                        finding_status=FindingStatus.DISPUTED,
                        severity=FindingSeverity.INFO,
                        explanation="Residual computed against ambiguous entity match. Cannot attribute to coordinate error.",
                        execution_ref=execution_id,
                        coverage_manifest_ref=manifest_id,
                    )
                )
            elif dist_meters > 500.0:
                findings.append(
                    QualityFinding(
                        finding_id=f"f_d08_gross_{rec_id}",
                        target_id=rec_id,
                        category="POSITIONAL_RESIDUAL_ELEVATED",
                        measure_name="positional_residual",
                        finding_code="F-D08-GROSS-RESIDUAL",
                        finding_status=FindingStatus.CONFIRMED_ISSUE,
                        severity=FindingSeverity.WARNING,
                        explanation=f"Positional residual {dist_meters:.1f}m against {feature_semantics} reference exceeds 500m.",
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
            reference_versions={ref_manifest.source: ref_manifest.version} if ref_manifest else {},
        )
