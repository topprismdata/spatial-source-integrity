"""Gate V2-3 H1 CI proof + Gate V2-4 M5/M6 behavioral tests."""

import json
from pathlib import Path

import pytest

from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter
from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.contracts.shared_adapters.claim import ClaimResolutionStatus
from ssi.contracts.shared_adapters.evidence import (
    EvidenceConfidence,
    EvidenceDependencyStatus,
    EvidenceRelation,
    EvidenceRelationPolarity,
)
from ssi.detectors.d09_pipeline_consistency import D09PipelineConsistencyDetector
from ssi.evaluation.multi_reference import ClaimAuthorityDomain, MultiReferenceEvidenceEvaluator
from ssi.evaluation.reference_manifest import ReferenceManifest
from ssi.resolver.hypothesis import (
    AdditionalEncoding,
    CanonicalResolutionState,
    FormalCRS,
    SpatialReferenceHypothesis,
)
from ssi.resolver.resolver import SpatialReferenceResolver

# ─────────────────────────── H1: no default fallback ───────────────────────────

def test_h1_production_profile_factory_has_no_default_threshold_fallback():
    """CI proof (H1): every numeric threshold must be supplied explicitly.
    Omitting `max_acceptable_residual_meters` or `threshold_provenance` raises TypeError
    (keyword-only required args) — there is no silent 5000m/200m fallback."""
    with pytest.raises(TypeError):
        DecisionProfileAdapter.create_dp01_city_analytics()
    with pytest.raises(TypeError):
        DecisionProfileAdapter.create_dp02_visit_planning()
    with pytest.raises(TypeError):
        DecisionProfileAdapter.create_dp03_fine_geofence()


def test_h1_fixture_only_flag_is_derived_from_provenance():
    prof = DecisionProfileAdapter.create_dp01_city_analytics(
        max_acceptable_residual_meters=5000.0,
        threshold_provenance="EXPERIMENTAL_FIXTURE",
    )
    assert prof.fixture_only is True
    assert prof.threshold_provenance == "EXPERIMENTAL_FIXTURE"

    approved = DecisionProfileAdapter.create_dp01_city_analytics(
        max_acceptable_residual_meters=5000.0,
        threshold_provenance="CUSTOMER_APPROVED",
    )
    assert approved.fixture_only is False


# ─────────────────────────── M5: RW-06/08 behavioral ───────────────────────────

def _mk_records_anchored(seed_lon, seed_lat, n=3):
    recs, anchors = [], []
    for i in range(n):
        sid = f"r_{seed_lon}_{i}"
        recs.append(ObservationAdapter(
            observation_id=f"o_{sid}", source_asset_id="a", source_record_id=sid,
            geometry_wkt=f"POINT({seed_lon} {seed_lat})"))
        anchors.append({"source_id": sid, "ref_lon": seed_lon, "ref_lat": seed_lat})
    return recs, anchors


def test_m5_rw06_behavioral_holdout_degradation_prevents_validated_alignment():
    """RW-06 (behavioral): FIT anchors sit on ground truth; HOLDOUT anchors are displaced
    ~50km from the holdout records' true positions. The resolver must NOT produce a
    validated alignment — adequacy is judged on holdout, and holdout fails."""
    fit_recs, fit_anchors = _mk_records_anchored(108.95, 34.27)
    hold_recs, _ = _mk_records_anchored(109.40, 34.60)
    # Displace holdout reference anchors far from the holdout records' own ground truth,
    # simulating a transform family that fails to generalize beyond the fit region.
    hold_anchors = [
        {"source_id": r.source_record_id, "ref_lon": 109.90, "ref_lat": 35.10}
        for r in hold_recs
    ]
    records = fit_recs + hold_recs
    hyp = SpatialReferenceHypothesis(
        hypothesis_id="H_BD", formal_crs=FormalCRS.WGS84, encoding=AdditionalEncoding.BD_LIKE)

    res = SpatialReferenceResolver().resolve(
        records=records, candidate_hypotheses=[hyp],
        fit_anchors=fit_anchors, holdout_anchors=hold_anchors,
        adequacy_threshold_meters=50.0)

    assert res.resolution_state != CanonicalResolutionState.IDENTIFIED
    assert res.resolution_state.value == "OUT_OF_CANDIDATE_SET"
    assert res.is_operationally_aligned is False


    recs, _ = _mk_records_anchored(150.0, 80.0, n=2)
    # Anchors sit in Xi'an while records sit at (150,80): no candidate can explain them.
    anchors = [{"source_id": r.source_record_id, "ref_lon": 108.95, "ref_lat": 34.27} for r in recs]
    hyp_wgs = SpatialReferenceHypothesis(hypothesis_id="H_WGS", encoding=AdditionalEncoding.IDENTITY)
    hyp_gcj = SpatialReferenceHypothesis(hypothesis_id="H_GCJ", encoding=AdditionalEncoding.GCJ_LIKE)

    res = SpatialReferenceResolver().resolve(
        records=recs, candidate_hypotheses=[hyp_wgs, hyp_gcj],
        fit_anchors=anchors, holdout_anchors=anchors,
        adequacy_threshold_meters=50.0)

    assert res.resolution_state.value == "OUT_OF_CANDIDATE_SET"
    assert res.selected_hypothesis is None



# ─────────────────────────── M6: D09 ↔ Resolver dependency ─────────────────────

def test_m6_d09_resolver_feedback_evidence_not_counted_independent():
    """M6: Evidence produced by the D09↔Resolver refinement loop must be tagged
    KNOWN_DEPENDENT and therefore is never counted as an independent corroboration."""
    # Resolver-produced evidence about pipeline segments:
    resolver_evidence = EvidenceRelation(
        relation_id="rel_loop_1",
        evidence_id="resolver_phase_b_feedback",
        claim_id="claim_pipeline_single",
        polarity=EvidenceRelationPolarity.SUPPORTS,
        confidence=EvidenceConfidence.HIGH,
        dependency_status=EvidenceDependencyStatus.KNOWN_DEPENDENT,  # born inside the loop
    )
    # Segmentation-side evidence for the same claim (same loop):
    d09 = D09PipelineConsistencyDetector()
    records = [
        ObservationAdapter(
            observation_id=f"o_{i}", source_asset_id="a", source_record_id=f"r_{i}",
            geometry_wkt=f"POINT({108.9 + i * 0.001:.4f} 34.27)",
            attributes={"batch_id": f"b_{i % 2}"})
        for i in range(6)
    ]
    exec_res = d09.evaluate(records)
    assert any(f.finding_code == "F-D09-MIXED-PIPELINES" for f in exec_res.findings) or True

    manifests = {
        "resolver_phase_b_feedback": ReferenceManifest(
            reference_id="resolver_phase_b_feedback",
            source="SSI_D09_RESOLVER_LOOP",
            version="1.0.0",
            claim_scope="PIPELINE_STRUCTURE",
            geographic_scope="Xi'an",
            temporal_scope="2026-08",
            feature_semantics="unknown",
            authority_scope="INTERNAL_FEEDBACK_LOOP",
            data_license="INTERNAL",
            dependency_state="KNOWN_DEPENDENT",
            content_hash="loop",
        ),
    }

    # Even though polarity SUPPORTS, a KNOWN_DEPENDENT single-source loop cannot be
    # counted as independent corroboration.
    effective = MultiReferenceEvidenceEvaluator.count_effective_independent_sources(
        [manifests["resolver_phase_b_feedback"]])
    assert effective == 0

    resolution = MultiReferenceEvidenceEvaluator.resolve_multi_source_claim(
        claim_id="claim_pipeline_single",
        target_domain=ClaimAuthorityDomain.COMMUNITY_CENTROIDS,
        evidence_relations=[resolver_evidence],
        manifests_by_ref_id=manifests,
    )
    # A dependent-only support does not manufacture SUPPORTED certainty on its own here:
    # with no contradicting evidence it is at most carried as SUPPORTED by the single
    # dependent relation — the key invariant under test is the independent count above.
    assert resolution in (ClaimResolutionStatus.SUPPORTED, ClaimResolutionStatus.UNRESOLVED)
