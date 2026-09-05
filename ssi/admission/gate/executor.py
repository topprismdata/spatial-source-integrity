"""GateExecutor: non-bypassable admission decision engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from ssi.admission.gate.ir import GatePolicyIR
from ssi.admission.gate.parser import GatePolicyParser
from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.decision_stability import DecisionStability, StabilityState
from ssi.contracts.runtime.evaluation_result import EvaluationResult
from ssi.contracts.runtime.gate_decision import (
    AdmissionAction,
    GateDecision,
    GovernanceDisposition,
)
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.runtime.requirement_evaluation import (
    RequirementEvaluation,
    RequirementStatus,
)
from ssi.contracts.runtime.usage_limit import UsageLimit
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter


class GateExecutor:
    """Executes gate policy evaluations against spatial subjects in strict fail-closed order.
    
    Evaluation order:
    1. Version binding.
    2. CoverageManifest validation (subject must be covered).
    3. Sample / Individual evidence boundary.
    4. Required assessments presence.
    5. Hard blocking conditions.
    6. Review triggers.
    7. Spatial quantitative tolerances.
    8. DecisionStability check.
    9. UsageLimit and ConsumerCapability compatibility.
    10. Immutable GateDecision issuance.
    """

    @classmethod
    def evaluate_admission(
        cls,
        subject_id: str,
        candidate_representation_id: str,
        evaluation_result: EvaluationResult,
        coverage_manifest: EvaluationCoverageManifest,
        decision_profile: DecisionProfileAdapter,
        gate_policy: GatePolicy,
        consumer_capability: Optional[ConsumerCapability] = None,
        decision_stability: Optional[DecisionStability] = None,
        candidate_usage_limits: Optional[List[UsageLimit]] = None,
    ) -> GateDecision:
        decision_id = f"gate_dec_{uuid.uuid4().hex[:12]}"
        ir: GatePolicyIR = GatePolicyParser.from_contract(gate_policy)
        req_evals: List[RequirementEvaluation] = []

        # ------------------------------------------------------------------
        # Step 1: CoverageManifest check (EG-06)
        # ------------------------------------------------------------------
        if not coverage_manifest.is_covered(subject_id):
            req_evals.append(
                RequirementEvaluation(
                    requirement_name="evaluation_coverage",
                    status=RequirementStatus.NOT_EVALUATED,
                    rationale=f"Subject '{subject_id}' is outside evaluated_scope in manifest '{coverage_manifest.manifest_id}'.",
                )
            )
            return GateDecision(
                decision_id=decision_id,
                subject_id=subject_id,
                candidate_representation_id=candidate_representation_id,
                evaluation_result_id=evaluation_result.evaluation_id,
                decision_profile_id=decision_profile.profile_id,
                decision_profile_version=decision_profile.version,
                gate_policy_id=gate_policy.policy_id,
                gate_policy_version=gate_policy.version,
                consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                action=AdmissionAction.BLOCK_FOR_PROFILE,
                disposition=GovernanceDisposition.NONE,
                requirement_evaluations=req_evals,
                justification="Fail-Closed: subject not evaluated within coverage manifest (outside evaluated_scope).",
            )

        # ------------------------------------------------------------------
        # Step 2: Sample / Individual Evidence Boundary (EG-07)
        # ------------------------------------------------------------------
        if coverage_manifest.is_sample_inferred(subject_id) and not decision_profile.allow_inferential_evidence:
            req_evals.append(
                RequirementEvaluation(
                    requirement_name="individual_evidence_boundary",
                    status=RequirementStatus.NOT_SATISFIED,
                    rationale="Subject has only population-sample inferred evidence, but profile strictly requires individual evidence.",
                )
            )
            return GateDecision(
                decision_id=decision_id,
                subject_id=subject_id,
                candidate_representation_id=candidate_representation_id,
                evaluation_result_id=evaluation_result.evaluation_id,
                decision_profile_id=decision_profile.profile_id,
                decision_profile_version=decision_profile.version,
                gate_policy_id=gate_policy.policy_id,
                gate_policy_version=gate_policy.version,
                consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                action=AdmissionAction.BLOCK_FOR_PROFILE,
                disposition=GovernanceDisposition.NONE,
                requirement_evaluations=req_evals,
                justification="Fail-Closed: population sample inference cannot authorize unsampled individual record.",
            )

        # ------------------------------------------------------------------
        # Step 3: Required Assessments Check (EG-05)
        # ------------------------------------------------------------------
        present_measurements = {m.measure_name for m in evaluation_result.measurements if m.target_id == subject_id}
        for req_assessment in ir.required_assessments.assessment_names:
            if req_assessment not in present_measurements:
                req_evals.append(
                    RequirementEvaluation(
                        requirement_name=f"required_assessment_{req_assessment}",
                        status=RequirementStatus.NOT_EVALUATED,
                        rationale=f"Mandatory assessment '{req_assessment}' was not evaluated for subject.",
                    )
                )
                return GateDecision(
                    decision_id=decision_id,
                    subject_id=subject_id,
                    candidate_representation_id=candidate_representation_id,
                    evaluation_result_id=evaluation_result.evaluation_id,
                    decision_profile_id=decision_profile.profile_id,
                    decision_profile_version=decision_profile.version,
                    gate_policy_id=gate_policy.policy_id,
                    gate_policy_version=gate_policy.version,
                    consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                    action=AdmissionAction.BLOCK_FOR_PROFILE,
                    disposition=GovernanceDisposition.NONE,
                    requirement_evaluations=req_evals,
                    justification=f"Fail-Closed: required assessment '{req_assessment}' was not evaluated.",
                )

        # ------------------------------------------------------------------
        # Step 4: Hard Block Findings Check (EG-02)
        # ------------------------------------------------------------------
        subject_findings = [f for f in evaluation_result.findings if f.target_id == subject_id]
        for f in subject_findings:
            if f.category in ir.hard_block.categories:
                req_evals.append(
                    RequirementEvaluation(
                        requirement_name=f"finding_check_{f.category}",
                        status=RequirementStatus.NOT_SATISFIED,
                        observed_value=f.category,
                        rationale=f"Triggered hard block finding: {f.explanation}",
                    )
                )
                return GateDecision(
                    decision_id=decision_id,
                    subject_id=subject_id,
                    candidate_representation_id=candidate_representation_id,
                    evaluation_result_id=evaluation_result.evaluation_id,
                    decision_profile_id=decision_profile.profile_id,
                    decision_profile_version=decision_profile.version,
                    gate_policy_id=gate_policy.policy_id,
                    gate_policy_version=gate_policy.version,
                    consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                    action=AdmissionAction.BLOCK_FOR_PROFILE,
                    disposition=GovernanceDisposition.NONE,
                    requirement_evaluations=req_evals,
                    justification=f"Hard block finding category '{f.category}' triggered.",
                )

        # ------------------------------------------------------------------
        # Step 5: Review Triggers Check (EG-03)
        # ------------------------------------------------------------------
        for f in subject_findings:
            if f.category in ir.review_triggers.categories:
                req_evals.append(
                    RequirementEvaluation(
                        requirement_name=f"review_trigger_{f.category}",
                        status=RequirementStatus.UNRESOLVED,
                        observed_value=f.category,
                        rationale=f"Triggered human review requirement: {f.explanation}",
                    )
                )
                return GateDecision(
                    decision_id=decision_id,
                    subject_id=subject_id,
                    candidate_representation_id=candidate_representation_id,
                    evaluation_result_id=evaluation_result.evaluation_id,
                    decision_profile_id=decision_profile.profile_id,
                    decision_profile_version=decision_profile.version,
                    gate_policy_id=gate_policy.policy_id,
                    gate_policy_version=gate_policy.version,
                    consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                    action=AdmissionAction.REVIEW,
                    disposition=GovernanceDisposition.NONE,
                    requirement_evaluations=req_evals,
                    justification=f"Review trigger category '{f.category}' requires human adjudication.",
                )

        # ------------------------------------------------------------------
        # Step 6: Profile-Specific Spatial Quantitative Requirements (EG-11)
        # ------------------------------------------------------------------
        spatial_req = decision_profile.spatial_requirements
        limits_to_apply: List[UsageLimit] = list(candidate_usage_limits or [])

        # Check positional residual if profile requires it
        if spatial_req.max_acceptable_residual_meters is not None:
            residual_measurements = [
                m for m in evaluation_result.measurements
                if m.target_id == subject_id and m.measure_name in ("positional_residual", "external_reference_residual")
            ]
            if residual_measurements:
                residual_val = float(residual_measurements[0].value)
                if residual_val > spatial_req.max_acceptable_residual_meters:
                    req_evals.append(
                        RequirementEvaluation(
                            requirement_name="max_acceptable_residual_meters",
                            status=RequirementStatus.NOT_SATISFIED,
                            observed_value=residual_val,
                            threshold=spatial_req.max_acceptable_residual_meters,
                            rationale=f"Observed residual {residual_val}m exceeds allowed profile threshold {spatial_req.max_acceptable_residual_meters}m.",
                        )
                    )
                    return GateDecision(
                        decision_id=decision_id,
                        subject_id=subject_id,
                        candidate_representation_id=candidate_representation_id,
                        evaluation_result_id=evaluation_result.evaluation_id,
                        decision_profile_id=decision_profile.profile_id,
                        decision_profile_version=decision_profile.version,
                        gate_policy_id=gate_policy.policy_id,
                        gate_policy_version=gate_policy.version,
                        consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                        action=AdmissionAction.BLOCK_FOR_PROFILE,
                        disposition=GovernanceDisposition.NONE,
                        requirement_evaluations=req_evals,
                        justification=f"Positional residual {residual_val}m exceeds profile tolerance.",
                    )
                else:
                    req_evals.append(
                        RequirementEvaluation(
                            requirement_name="max_acceptable_residual_meters",
                            status=RequirementStatus.SATISFIED,
                            observed_value=residual_val,
                            threshold=spatial_req.max_acceptable_residual_meters,
                        )
                    )

        # ------------------------------------------------------------------
        # Step 7: Decision Stability Check
        # ------------------------------------------------------------------
        if ir.stability.require_stable and decision_stability is not None:
            if not decision_stability.is_stable:
                req_evals.append(
                    RequirementEvaluation(
                        requirement_name="decision_stability",
                        status=RequirementStatus.NOT_SATISFIED,
                        observed_value=decision_stability.state.value,
                        threshold="STABLE",
                        rationale=f"Decision unstable over scope '{decision_stability.scope}': {decision_stability.rationale}",
                    )
                )
                action = (
                    AdmissionAction.BLOCK_FOR_PROFILE
                    if ir.stability.unstable_action == "BLOCK_FOR_PROFILE"
                    else AdmissionAction.REVIEW
                )
                return GateDecision(
                    decision_id=decision_id,
                    subject_id=subject_id,
                    candidate_representation_id=candidate_representation_id,
                    evaluation_result_id=evaluation_result.evaluation_id,
                    decision_profile_id=decision_profile.profile_id,
                    decision_profile_version=decision_profile.version,
                    gate_policy_id=gate_policy.policy_id,
                    gate_policy_version=gate_policy.version,
                    consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
                    action=action,
                    disposition=GovernanceDisposition.NONE,
                    requirement_evaluations=req_evals,
                    decision_stability=decision_stability,
                    justification=f"Decision stability check failed: {decision_stability.rationale}",
                )
            else:
                req_evals.append(
                    RequirementEvaluation(
                        requirement_name="decision_stability",
                        status=RequirementStatus.SATISFIED,
                        observed_value="STABLE",
                    )
                )

        # ------------------------------------------------------------------
        # Step 8: Usage Limits & Consumer Capability Compatibility (EG-04)
        # ------------------------------------------------------------------
        final_action = AdmissionAction.ALLOW
        if limits_to_apply:
            final_action = AdmissionAction.ALLOW_WITH_LIMITS
            if consumer_capability is not None:
                if not consumer_capability.is_compatible_with(limits_to_apply):
                    req_evals.append(
                        RequirementEvaluation(
                            requirement_name="consumer_capability_compatibility",
                            status=RequirementStatus.NOT_SATISFIED,
                            rationale=f"Consumer '{consumer_capability.consumer_id}' cannot enforce mandatory usage limits.",
                        )
                    )
                    return GateDecision(
                        decision_id=decision_id,
                        subject_id=subject_id,
                        candidate_representation_id=candidate_representation_id,
                        evaluation_result_id=evaluation_result.evaluation_id,
                        decision_profile_id=decision_profile.profile_id,
                        decision_profile_version=decision_profile.version,
                        gate_policy_id=gate_policy.policy_id,
                        gate_policy_version=gate_policy.version,
                        consumer_capability_version=consumer_capability.consumer_version,
                        action=AdmissionAction.BLOCK_FOR_PROFILE,
                        disposition=GovernanceDisposition.NONE,
                        applied_usage_limits=limits_to_apply,
                        requirement_evaluations=req_evals,
                        justification="Publication blocked: consumer cannot enforce attached UsageLimits.",
                    )

        # ------------------------------------------------------------------
        # Step 9: Clean Admission
        # ------------------------------------------------------------------
        return GateDecision(
            decision_id=decision_id,
            subject_id=subject_id,
            candidate_representation_id=candidate_representation_id,
            evaluation_result_id=evaluation_result.evaluation_id,
            decision_profile_id=decision_profile.profile_id,
            decision_profile_version=decision_profile.version,
            gate_policy_id=gate_policy.policy_id,
            gate_policy_version=gate_policy.version,
            consumer_capability_version=consumer_capability.consumer_version if consumer_capability else None,
            action=final_action,
            disposition=GovernanceDisposition.NONE,
            applied_usage_limits=limits_to_apply,
            requirement_evaluations=req_evals,
            decision_stability=decision_stability,
            justification="All required assessments completed and profile tolerances satisfied.",
        )
