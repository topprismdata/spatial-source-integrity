"""EvaluationPipeline: coordinates detector executions into an aggregated EvaluationResult."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.evaluation.detector_definition import BaseDetector
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus


class EvaluationPipeline:
    """Orchestrates multiple detectors over source records and compiles an auditable EvaluationResult."""

    def __init__(self, detectors: List[BaseDetector]):
        self.detectors = detectors

    def run(
        self,
        records: List[ObservationAdapter],
        context: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        eval_id = f"eval_{uuid.uuid4().hex[:12]}"
        manifest_id = f"manifest_composite_{uuid.uuid4().hex[:8]}"
        context = context or {}

        eligible_ids = [r.source_record_id for r in records]
        all_evaluated_ids = set()
        all_abstained_ids = set()
        all_measurements: List[QualityMeasurement] = []
        all_findings: List[QualityFinding] = []
        has_failure = False

        for detector in self.detectors:
            try:
                exec_result: DetectorExecution = detector.evaluate(records, context)
            except Exception as e:
                has_failure = True
                continue

            if exec_result.execution_status == ExecutionStatus.FAILED:
                has_failure = True

            all_measurements.extend(exec_result.measurements)
            all_findings.extend(exec_result.findings)

            if exec_result.execution_status == ExecutionStatus.COMPLETED:
                for m in exec_result.measurements:
                    all_evaluated_ids.add(m.target_id)
            elif exec_result.execution_status == ExecutionStatus.ABSTAINED:
                all_abstained_ids.update(eligible_ids)

        composite_manifest = EvaluationCoverageManifest(
            manifest_id=manifest_id,
            evaluation_ref=eval_id,
            eligible_scope=eligible_ids,
            evaluated_scope=sorted(list(all_evaluated_ids)),
            abstained_scope=sorted(list(all_abstained_ids)),
            sampled_scope=sorted(list(all_evaluated_ids)),
        )

        overall_status = "FAILED" if has_failure else ("COMPLETED" if all_evaluated_ids else "ABSTAINED")

        return EvaluationResult(
            evaluation_id=eval_id,
            evaluator_name="CompositeEvaluationPipeline",
            evaluator_version="1.0.0",
            manifest_ref=composite_manifest.manifest_id,
            measurements=all_measurements,
            findings=all_findings,
            status=overall_status,
        )
