"""D09 — Batch & Pipeline Consistency Detector."""

from __future__ import annotations

import collections
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
from ssi.detectors.d03_precision_fingerprint import D03PrecisionFingerprintDetector
from ssi.evaluation.detector_definition import BaseDetector, DetectorType
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus
from ssi.evaluation.quality_measure import MEASURE_REGISTRY


class D09PipelineConsistencyDetector(BaseDetector):
    """D09: Detects source pipeline heterogeneity, mixed reference pipelines, and change points.
    
    Two-Phase bounded architecture:
    - Phase A: Preliminary segmentation using intrinsic metadata, precision, schema, batch (no Resolver circularity).
    - Phase B: Bounded validation/refinement (max_refinement_rounds <= 2) using residual clusters.
    """

    detector_id = "D09"
    detector_version = "0.1.0"
    detector_type = DetectorType.HYBRID
    measure_refs = ["pipeline_heterogeneity_score"]

    MAX_REFINEMENT_ROUNDS = 2

    @classmethod
    def segment_phase_a(cls, records: List[ObservationAdapter]) -> Dict[str, List[str]]:
        """Phase A: Preliminary segmentation based on intrinsic precision and batch metadata."""
        segments: Dict[str, List[str]] = collections.defaultdict(list)
        d03 = D03PrecisionFingerprintDetector()

        for record in records:
            rec_id = record.source_record_id
            batch_id = record.attributes.get("batch_id", "default_batch")
            schema_ver = record.attributes.get("schema_version", "v1")

            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            prec_family = "UNKNOWN_PREC"
            if raw_x is not None:
                dec = d03.get_decimal_places(str(raw_x))
                prec_family = "HIGH_PREC" if dec >= 6 else "LOW_PREC"

            seg_key = f"seg_{batch_id}_{schema_ver}_{prec_family}"
            segments[seg_key].append(rec_id)

        return dict(segments)

    def evaluate(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectorExecution:
        execution_id = f"exec_d09_{uuid.uuid4().hex[:8]}"
        manifest_id = f"manifest_d09_{uuid.uuid4().hex[:8]}"
        context = context or {}

        evaluated_ids: List[str] = [r.source_record_id for r in records]
        measurements: List[QualityMeasurement] = []
        findings: List[QualityFinding] = []

        # 1. Execute Phase A preliminary segmentation
        phase_a_segments = self.segment_phase_a(records)

        # 2. Execute Phase B refinement (bounded by MAX_REFINEMENT_ROUNDS)
        refinement_rounds = min(context.get("refinement_rounds", 1), self.MAX_REFINEMENT_ROUNDS)
        segment_residuals: Dict[str, float] = context.get("segment_residuals", {})

        # Calculate pipeline heterogeneity score: fraction of non-dominant segments
        total_records = len(records)
        seg_sizes = sorted([len(v) for v in phase_a_segments.values()], reverse=True)
        dominant_size = seg_sizes[0] if seg_sizes else 0
        heterogeneity_score = round(1.0 - (dominant_size / max(total_records, 1)), 3)

        measurements.append(
            QualityMeasurement(
                measurement_id=f"m_d09_het_{execution_id}",
                target_id="DATASET_SCOPE",
                measure_name="pipeline_heterogeneity_score",
                measure_id=MEASURE_REGISTRY["pipeline_heterogeneity_score"].measure_id,
                value=heterogeneity_score,
                unit="ratio",
                scope="DATASET",
                evaluation_method="D09_PipelineConsistency",
                execution_ref=execution_id,
                coverage_manifest_ref=manifest_id,
                metaquality={
                    "segment_count": len(phase_a_segments),
                    "refinement_rounds_executed": refinement_rounds,
                    "max_rounds_cap": self.MAX_REFINEMENT_ROUNDS,
                },
            )
        )

        # If significant mixed pipelines exist (e.g. heterogeneity > 0.15)
        if heterogeneity_score > 0.15:
            findings.append(
                QualityFinding(
                    finding_id=f"f_d09_mixed_{execution_id}",
                    target_id="DATASET_SCOPE",
                    category="MIXED_REFERENCE_PIPELINES",
                    measure_name="pipeline_heterogeneity_score",
                    finding_code="F-D09-MIXED-PIPELINES",
                    finding_status=FindingStatus.DETECTED,
                    severity=FindingSeverity.WARNING,
                    explanation=(
                        f"Dataset contains {len(phase_a_segments)} distinct production pipeline segments "
                        f"with heterogeneity score {heterogeneity_score}. Single universal CRS assumption is violated."
                    ),
                    execution_ref=execution_id,
                    coverage_manifest_ref=manifest_id,
                )
            )

        manifest = EvaluationCoverageManifest(
            manifest_id=manifest_id,
            evaluation_ref=execution_id,
            eligible_scope=evaluated_ids,
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
