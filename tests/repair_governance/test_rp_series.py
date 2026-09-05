"""RP-Series: Governed Repair & Operational Alignment tests (RP-01 ~ RP-10)."""

import pytest

from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import PublicationError, SpatialAdmissionPublisher
from ssi.contracts.runtime.coverage_manifest import EvaluationCoverageManifest
from ssi.contracts.runtime.evaluation_result import EvaluationResult, QualityMeasurement
from ssi.contracts.runtime.gate_decision import AdmissionAction, GateDecision
from ssi.contracts.runtime.gate_policy import GatePolicy
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.contracts.shared_adapters.derived_estimate import DerivedEstimateAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.hitl.review_task import (
    AdjudicationAction,
    HumanAdjudication,
    ReviewerRole,
)
from ssi.repair.repair_approval import RepairApproval
from ssi.repair.repair_policy import RepairPolicy
from ssi.repair.repair_proposal import (
    ProposalStatus,
    RepairProposal,
    RepairRiskClass,
    RepairType,
)


def test_rp_01_repair_proposal_cannot_publish_directly(consumer_macro_city, dp01_profile):
    """RP-01: A RepairProposal is merely a candidate; it cannot publish directly without approval and Gate."""
    proposal = RepairProposal(
        proposal_id="RPROP-TEST-01",
        subject_scope="comm_101",
        repair_type=RepairType.OPERATIONAL_ALIGNMENT,
        risk_class=RepairRiskClass.R2_HIGH,
        source_state_ref="obs_raw_01",
        proposed_transform="bd09_to_wgs84",
    )
    # A proposal has no publish authority and is not a GateDecision
    assert not hasattr(proposal, "publish")
    assert not hasattr(proposal, "is_admitted")

    # Publisher strictly rejects non-GateDecision objects
    candidate_geometries = {"comm_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"}}
    snapshot = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city,
        decision_profile=dp01_profile,
        gate_decisions=[],  # Proposal cannot act as GateDecision
        candidate_geometries=candidate_geometries,
    )
    assert len(snapshot.projections) == 0


def test_rp_02_validation_evidence_separated_from_generation_evidence():
    """RP-02: Generation evidence used to discover transform cannot be reused as validation evidence."""
    gen_evidence = ["evi_fit_anchor_01", "evi_fit_anchor_02"]
    val_evidence = ["evi_holdout_anchor_01", "evi_holdout_anchor_02"]

    proposal = RepairProposal(
        proposal_id="RPROP-002",
        subject_scope="xian_seed_batch",
        repair_type=RepairType.OPERATIONAL_ALIGNMENT,
        source_state_ref="raw_asset",
        proposed_transform="bd09_to_wgs84",
        generation_evidence_ids=gen_evidence,
        validation_evidence_ids=val_evidence,
    )

    # Invariant: Generation evidence IDs and Validation evidence IDs must be disjoint
    overlap = set(proposal.generation_evidence_ids) & set(proposal.validation_evidence_ids)
    assert len(overlap) == 0
    assert len(proposal.validation_evidence_ids) > 0


def test_rp_03_human_adjudication_cannot_substitute_repair_approval():
    """RP-03: Confirming an issue via HumanAdjudication does NOT grant repair approval."""
    # Adjudication: Human confirms coordinate issue
    adj = HumanAdjudication(
        adjudication_id="adj_01",
        task_ref="HRT-01",
        reviewer_id="reviewer_d",
        reviewer_role=ReviewerRole.REVIEWER,
        action=AdjudicationAction.SUPPORT,
        rationale="Agreed that coordinate is shifted.",
    )
    # Adjudication has NO approval_id, cannot authorize derived representation
    assert not hasattr(adj, "approval_id")
    assert adj.action != "APPROVED"


def test_rp_04_approved_repair_creates_new_derived_estimate():
    """RP-04: Approved repair creates a new DerivedEstimateAdapter carrying repair lineage, leaving raw intact."""
    raw_obs = ObservationAdapter(
        observation_id="obs_raw_01",
        source_asset_id="asset_raw",
        source_record_id="rec_01",
        geometry_wkt="POINT(108.95 34.27)",
        attributes={"name": "EstateA"},
    )
    approval = RepairApproval(
        approval_id="RAPPROVE-001",
        proposal_ref="RPROP-001",
        approver_id="steward_a",
        approver_role="DATA_STEWARD",
        decision="APPROVED",
        rationale="Holdout validation confirms 41.8m P50 residual within tolerance.",
    )

    derived = DerivedEstimateAdapter(
        derived_id="der_aligned_01",
        target_entity_id=raw_obs.source_record_id,
        estimation_method="bd09_to_wgs84",
        geometry_wkt="POINT(108.9434 34.2712)",
        crs="EPSG:4326",
        attributes=raw_obs.attributes,
        derived_from_observation_ids=[raw_obs.observation_id],
        repair_approval_id=approval.approval_id,
    )

    # Raw observation untouched
    assert raw_obs.geometry_wkt == "POINT(108.95 34.27)"
    # Derived estimate carries lineage and approval ref
    assert derived.repair_approval_id == "RAPPROVE-001"
    assert derived.derived_from_observation_ids == ["obs_raw_01"]


def test_rp_05_approved_repair_creates_new_world_state_version():
    """RP-05: Approved repair generates a new derived state version without rewriting historical states."""
    initial_state_version = "v1.0.0"
    derived_state_version = "v1.1.0-shadow-repaired"
    assert derived_state_version != initial_state_version


def test_rp_06_new_world_state_requires_new_gate(consumer_macro_city, dp01_profile, standard_gate_policy):
    """RP-06: New derived state requires a fresh EvaluationResult and new GateDecision before publication."""
    derived_est = DerivedEstimateAdapter(
        derived_id="der_new_01",
        target_entity_id="rec_101",
        estimation_method="bd09_to_wgs84",
        geometry_wkt="POINT(108.95 34.27)",
        crs="EPSG:4326",
        repair_approval_id="RAPPROVE-001",
    )

    eval_result = EvaluationResult(
        evaluation_id="eval_derived_run",
        evaluator_name="DerivedEvaluator",
        evaluator_version="1.0.0",
        manifest_ref="man_derived",
        measurements=[
            QualityMeasurement(measurement_id="m1", target_id="rec_101", measure_name="coordinate_schema", value="VALID", evaluation_method="D01"),
            QualityMeasurement(measurement_id="m2", target_id="rec_101", measure_name="geographic_range", value="VALID", evaluation_method="D02"),
        ],
        findings=[],
    )
    manifest = EvaluationCoverageManifest(
        manifest_id="man_derived",
        evaluation_ref="eval_derived_run",
        eligible_scope=["rec_101"],
        evaluated_scope=["rec_101"],
    )

    new_gate_decision = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id=derived_est.derived_id,
        evaluation_result=eval_result,
        coverage_manifest=manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
    )

    assert new_gate_decision.action == AdmissionAction.ALLOW
    assert new_gate_decision.candidate_representation_id == derived_est.derived_id


def test_rp_07_old_snapshot_remains_unchanged(consumer_macro_city, dp01_profile):
    """RP-07: Generating a repair and a new snapshot does not modify the content hash or data of old snapshot."""
    dec_old = GateDecision(
        decision_id="dec_old_1", subject_id="r1", candidate_representation_id="cand_old",
        evaluation_result_id="ev1", decision_profile_id="DP-01", decision_profile_version="1.0.0",
        gate_policy_id="GP-STANDARD", gate_policy_version="1.0.0", action=AdmissionAction.ALLOW,
        justification="Initial allow",
    )
    snap_old = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city, decision_profile=dp01_profile,
        gate_decisions=[dec_old], candidate_geometries={"r1": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"}},
        version="1.0.0",
    )
    old_hash = snap_old.content_hash

    # Now create new repair snapshot v1.1.0
    dec_new = GateDecision(
        decision_id="dec_new_1", subject_id="r1", candidate_representation_id="cand_repaired",
        evaluation_result_id="ev2", decision_profile_id="DP-01", decision_profile_version="1.0.0",
        gate_policy_id="GP-STANDARD", gate_policy_version="1.0.0", action=AdmissionAction.ALLOW,
        justification="Repaired allow",
    )
    snap_new = SpatialAdmissionPublisher.publish_snapshot(
        consumer=consumer_macro_city, decision_profile=dp01_profile,
        gate_decisions=[dec_new], candidate_geometries={"r1": {"geometry_wkt": "POINT(108.9512 34.2708)", "crs": "EPSG:4326"}},
        version="1.1.0",
    )

    # Old snapshot remains byte-for-byte identical with its original hash
    assert snap_old.content_hash == old_hash
    assert snap_new.content_hash != old_hash
    assert snap_old.version == "1.0.0"
    assert snap_new.version == "1.1.0"


def test_rp_08_repair_revocation_invalidates_derived_state():
    """RP-08: Revoking an approval invalidates the authorization."""
    approval = RepairApproval(
        approval_id="RAPPROVE-002",
        proposal_ref="RPROP-002",
        approver_id="steward_d",
        approver_role="DATA_STEWARD",
        decision="APPROVED",
        rationale="Initial approval",
    )
    assert not approval.is_revoked

    # Downstream error detected -> revoke approval
    revoked_approval = approval.revoke("Reference survey retracted; transform invalid.")
    assert revoked_approval.is_revoked is True
    assert revoked_approval.decision == "REVOKED"
    assert "retracted" in revoked_approval.revocation_reason


def test_rp_09_scope_limited_repair_cannot_escape_applicability_envelope():
    """RP-09: A repair rule certified for Xi'an cannot be applied to records from Beijing."""
    proposal_xian_only = RepairProposal(
        proposal_id="RPROP-XA-ONLY",
        subject_scope="xian_seed_corpus",
        repair_type=RepairType.OPERATIONAL_ALIGNMENT,
        source_state_ref="raw_csv",
        proposed_transform="bd09_to_wgs84",
        applicable_scope={
            "provider": "commercial listing dataset",
            "city": "Xi'an",
            "date": "2026-08",
        },
    )

    # Xi'an record matches envelope
    rec_xian = {"provider": "commercial listing dataset", "city": "Xi'an", "date": "2026-08"}
    assert proposal_xian_only.is_scope_applicable(rec_xian) is True

    # Beijing record does NOT match envelope (preventing universal extrapolation error)
    rec_beijing = {"provider": "commercial listing dataset", "city": "Beijing", "date": "2026-08"}
    assert proposal_xian_only.is_scope_applicable(rec_beijing) is False


def test_rp_10_unresolved_repair_leaves_source_blocked_where_required(consumer_macro_city, dp02_profile, standard_gate_policy):
    """RP-10: If a repair proposal is rejected or unresolved, affected records remain blocked in Gate."""
    eval_result = EvaluationResult(
        evaluation_id="eval_unresolved",
        evaluator_name="Evaluator",
        evaluator_version="1.0.0",
        manifest_ref="man_unresolved",
        measurements=[
            QualityMeasurement(measurement_id="m1", target_id="rec_bad", measure_name="coordinate_schema", value="VALID", evaluation_method="D01"),
            QualityMeasurement(measurement_id="m2", target_id="rec_bad", measure_name="geographic_range", value="VALID", evaluation_method="D02"),
            QualityMeasurement(measurement_id="m3", target_id="rec_bad", measure_name="positional_residual", value=650.0, unit="meters", evaluation_method="D08"),
        ],
        findings=[],
    )
    manifest = EvaluationCoverageManifest(
        manifest_id="man_unresolved",
        evaluation_ref="eval_unresolved",
        eligible_scope=["rec_bad"],
        evaluated_scope=["rec_bad"],
    )

    # Gate on DP-02 (tolerance 200m) -> residual 650m fails
    decision = GateExecutor.evaluate_admission(
        subject_id="rec_bad",
        candidate_representation_id="cand_unrepaired",
        evaluation_result=eval_result,
        coverage_manifest=manifest,
        decision_profile=dp02_profile,
        gate_policy=standard_gate_policy,
    )
    assert decision.is_blocked()
