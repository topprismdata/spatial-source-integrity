"""EG-06: Coverage Boundary test.

Invariant: subject ∉ required evaluated_scope -> cannot silently pass.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.contracts.runtime.requirement_evaluation import RequirementStatus


def test_subject_outside_coverage_scope_cannot_pass(
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
    clean_evaluation_result,
):
    """Proves that a subject not included in the EvaluationCoverageManifest evaluated_scope is blocked."""
    # 'rec_999' is not in standard_coverage_manifest (which only covers rec_101, rec_102)
    decision = GateExecutor.evaluate_admission(
        subject_id="rec_999",
        candidate_representation_id="cand_999",
        evaluation_result=clean_evaluation_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    assert decision.is_blocked()
    assert any(
        req.requirement_name == "evaluation_coverage" and req.status == RequirementStatus.NOT_EVALUATED
        for req in decision.requirement_evaluations
    )
    assert "outside evaluated_scope" in decision.justification
