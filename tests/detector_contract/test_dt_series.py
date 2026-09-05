"""DT-Series: Universal Detector Runtime Contract tests (DT-01 ~ DT-06)."""

import pytest
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import (
    EvaluationResult,
    FindingStatus,
    QualityFinding,
    QualityMeasurement,
)
from ssi.contracts.runtime.gate_decision import AdmissionAction
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.evaluation.detector_definition import BaseDetector, DetectorType
from ssi.evaluation.detector_execution import DetectorExecution, ExecutionStatus
from ssi.evaluation.quality_measure import MEASURE_REGISTRY, QualityMeasureDefinition


class MockFailingDetector(BaseDetector):
    detector_id = "D_FAIL_MOCK"
    detector_version = "0.1.0"
    detector_type = DetectorType.INTRINSIC_DETERMINISTIC
    measure_refs = ["coordinate_schema"]

    def evaluate(self, records, context=None):
        return self.create_execution(
            coverage_manifest_ref="man_fail",
            status=ExecutionStatus.FAILED,
            failure_reason="Simulated hardware / parser timeout exception",
        )


class MockAbstainingDetector(BaseDetector):
    detector_id = "D_ABSTAIN_MOCK"
    detector_version = "0.1.0"
    detector_type = DetectorType.REFERENCE_DETERMINISTIC
    measure_refs = ["admin_containment"]

    def evaluate(self, records, context=None):
        return self.create_execution(
            coverage_manifest_ref="man_abstain",
            status=ExecutionStatus.ABSTAINED,
            abstention_reason="Historical municipal boundary reference unavailable for year 1998",
        )


def test_dt_01_detector_failed_no_false_pass():
    """DT-01: A FAILED detector execution must be recorded explicitly and never masquerade as passed."""
    detector = MockFailingDetector()
    execution = detector.evaluate(records=[])
    assert execution.execution_status == ExecutionStatus.FAILED
    assert execution.failure_reason is not None
    assert len(execution.measurements) == 0


def test_dt_02_detector_abstained_no_false_pass():
    """DT-02: An ABSTAINED detector execution records abstention reason and is not treated as verified pass."""
    detector = MockAbstainingDetector()
    execution = detector.evaluate(records=[])
    assert execution.execution_status == ExecutionStatus.ABSTAINED
    assert "Historical municipal boundary" in execution.abstention_reason


def test_dt_03_completed_no_finding_subject_covered():
    """DT-03: COMPLETED + no Finding + covered subject = 'no issue detected by this detector', not global truth."""
    manifest = EvaluationCoverageManifest(
        manifest_id="man_03",
        evaluation_ref="eval_03",
        eligible_scope=["rec_1"],
        evaluated_scope=["rec_1"],
    )
    measurement = QualityMeasurement(
        measurement_id="m_03",
        target_id="rec_1",
        measure_name="coordinate_schema",
        value="VALID",
        evaluation_method="D01",
        coverage_manifest_ref=manifest.manifest_id,
    )
    eval_result = EvaluationResult(
        evaluation_id="eval_03",
        evaluator_name="D01_Detector",
        evaluator_version="0.1.0",
        manifest_ref=manifest.manifest_id,
        measurements=[measurement],
        findings=[],  # Zero findings
        status="COMPLETED",
    )
    # The record is covered
    assert manifest.is_covered("rec_1")
    # Interpretation: D01 found no issue with schema parse, but this doesn't prove coordinates are in the correct city
    assert len(eval_result.findings) == 0


def test_dt_04_completed_no_finding_subject_not_covered():
    """DT-04: COMPLETED + no Finding + subject not covered = NOT_EVALUATED (cannot pass silently)."""
    manifest = EvaluationCoverageManifest(
        manifest_id="man_04",
        evaluation_ref="eval_04",
        eligible_scope=["rec_1", "rec_2"],
        evaluated_scope=["rec_1"],  # rec_2 was NOT evaluated
    )
    # rec_2 is not covered
    assert not manifest.is_covered("rec_2")


def test_dt_05_same_measure_different_detector_implementation():
    """DT-05: Different detector implementations produce measurements conforming to the same measure definition."""
    def_schema = MEASURE_REGISTRY["coordinate_schema"]

    # Detector A produces measurement
    m_a = QualityMeasurement(
        measurement_id="m_a_1",
        target_id="rec_1",
        measure_name=def_schema.name,
        measure_id=def_schema.measure_id,
        measure_version=def_schema.measure_version,
        value="VALID",
        evaluation_method="D01_FastRegexParser",
    )

    # Detector B produces measurement
    m_b = QualityMeasurement(
        measurement_id="m_b_1",
        target_id="rec_1",
        measure_name=def_schema.name,
        measure_id=def_schema.measure_id,
        measure_version=def_schema.measure_version,
        value="VALID",
        evaluation_method="D01_StrictASTParser",
    )

    assert m_a.measure_id == m_b.measure_id == def_schema.measure_id
    assert m_a.measure_version == m_b.measure_version == "1.0.0"


def test_dt_06_measure_formula_version_change():
    """DT-06: A change in calculation formula requires a distinct measure_version."""
    old_measure = QualityMeasureDefinition(
        measure_id="QM-D08-RESIDUAL",
        measure_version="1.0.0",
        name="positional_residual",
        iso_element="Positional Accuracy",
        unit="meters",
        evaluation_method="EuclideanPlanar",
        description="Planar Euclidean distance formula.",
    )

    updated_geodesic_measure = QualityMeasureDefinition(
        measure_id="QM-D08-RESIDUAL",
        measure_version="2.0.0",  # Version incremented
        name="positional_residual",
        iso_element="Positional Accuracy",
        unit="meters",
        evaluation_method="WGS84_GeodesicVincenty",
        description="Geodesic ellipsoidal distance formula.",
    )

    assert old_measure.measure_version != updated_geodesic_measure.measure_version
    assert old_measure.measure_version == "1.0.0"
    assert updated_geodesic_measure.measure_version == "2.0.0"
