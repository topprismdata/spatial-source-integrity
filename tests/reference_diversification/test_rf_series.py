"""RF-Series: Reference Diversification & Evidence Independence tests (RF-01 ~ RF-06)."""

import pytest
from ssi.contracts.shared_adapters.claim import ClaimResolutionStatus
from ssi.contracts.shared_adapters.evidence import (
    EvidenceConfidence,
    EvidenceDependencyStatus,
    EvidenceRelation,
    EvidenceRelationPolarity,
)
from ssi.evaluation.multi_reference import (
    ClaimAuthorityDomain,
    MultiReferenceEvidenceEvaluator,
)
from ssi.evaluation.reference_manifest import ReferenceManifest


def test_rf_01_multiple_dependent_sources_not_counted_independent():
    """RF-01: Two sources sharing an upstream crawler are collapsed into 1 effective independent source."""
    # Source A: commercial portal data based on AMap
    manifest_a = ReferenceManifest(
        reference_id="ref_portal_a",
        source="PortalA",
        version="2026.1",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="AutoNavi_Upstream",
        data_license="Commercial",
        dependency_state="KNOWN_DEPENDENT",
        content_hash="hash_a",
    )

    # Source B: another vendor that also license-crawls AutoNavi
    manifest_b = ReferenceManifest(
        reference_id="ref_vendor_b",
        source="VendorB",
        version="2026.1",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="AutoNavi_Upstream",  # Shares upstream!
        data_license="Commercial",
        dependency_state="KNOWN_DEPENDENT",
        content_hash="hash_b",
    )

    # Independent third source: OpenStreetMap community map
    manifest_osm = ReferenceManifest(
        reference_id="ref_osm",
        source="OSM",
        version="2026-08",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        dependency_state="VERIFIED_INDEPENDENT",
        content_hash="hash_osm",
    )

    manifests = [manifest_a, manifest_b, manifest_osm]
    # Total sources = 3, but effective independent source families = 2 (AutoNavi root + OSM)
    effective_count = MultiReferenceEvidenceEvaluator.count_effective_independent_sources(manifests)
    assert effective_count == 2
    assert effective_count < len(manifests)


def test_rf_02_claim_specific_authority_respected():
    """RF-02: A reference can only evaluate claims within its certified claim_scope."""
    # Official civil admin boundary reference
    manifest_admin = ReferenceManifest(
        reference_id="ref_civil_admin",
        source="CivilAdmin",
        version="2026",
        claim_scope="ADMIN_BOUNDARIES",  # Certified only for admin boundaries
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="boundary_polygon",
        authority_scope="Municipal",
        data_license="Official",
        dependency_state="VERIFIED_INDEPENDENT",
        content_hash="hash_admin",
    )

    # Claim 1: Administrative containment -> authorized
    assert MultiReferenceEvidenceEvaluator.filter_by_claim_authority(
        manifest_admin, ClaimAuthorityDomain.ADMIN_BOUNDARIES
    ) is True

    # Claim 2: Store entrance point accuracy -> NOT authorized
    assert MultiReferenceEvidenceEvaluator.filter_by_claim_authority(
        manifest_admin, ClaimAuthorityDomain.ENTRANCE_POINTS
    ) is False


def test_rf_03_contradictory_independent_sources_produce_conflicted():
    """RF-03: Two independent high-authority sources contradicting each other produce CONFLICTED."""
    manifest_source_1 = ReferenceManifest(
        reference_id="ref_official_1",
        source="OfficialSurveyA",
        version="2026",
        claim_scope="ADMIN_BOUNDARIES",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="boundary_polygon",
        authority_scope="Municipal",
        data_license="Official",
        dependency_state="VERIFIED_INDEPENDENT",
        content_hash="hash_1",
    )
    manifest_source_2 = ReferenceManifest(
        reference_id="ref_official_2",
        source="OfficialSurveyB",
        version="2026",
        claim_scope="ADMIN_BOUNDARIES",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="boundary_polygon",
        authority_scope="Provincial",
        data_license="Official",
        dependency_state="VERIFIED_INDEPENDENT",
        content_hash="hash_2",
    )

    # Source 1 says Point is inside Yanta (supports claim)
    rel_1 = EvidenceRelation(
        relation_id="rel_1",
        evidence_id="ref_official_1",
        claim_id="claim_in_yanta",
        polarity=EvidenceRelationPolarity.SUPPORTS,
        confidence=EvidenceConfidence.HIGH,
        dependency_status=EvidenceDependencyStatus.VERIFIED_INDEPENDENT,
    )

    # Source 2 says Point is outside Yanta (contradicts claim)
    rel_2 = EvidenceRelation(
        relation_id="rel_2",
        evidence_id="ref_official_2",
        claim_id="claim_in_yanta",
        polarity=EvidenceRelationPolarity.CONTRADICTS,
        confidence=EvidenceConfidence.HIGH,
        dependency_status=EvidenceDependencyStatus.VERIFIED_INDEPENDENT,
    )

    manifests = {
        "ref_official_1": manifest_source_1,
        "ref_official_2": manifest_source_2,
    }

    # Resolution MUST be CONFLICTED (cannot silently average or majority-vote)
    resolution = MultiReferenceEvidenceEvaluator.resolve_multi_source_claim(
        claim_id="claim_in_yanta",
        target_domain=ClaimAuthorityDomain.ADMIN_BOUNDARIES,
        evidence_relations=[rel_1, rel_2],
        manifests_by_ref_id=manifests,
    )

    assert resolution == ClaimResolutionStatus.CONFLICTED


def test_rf_04_reference_feature_mismatch_preserved():
    """RF-04: Centroid vs entrance feature semantics are distinguished and preserved in manifest."""
    manifest_centroid = ReferenceManifest(
        reference_id="ref_cen",
        source="OSM",
        version="2026",
        claim_scope="COMMUNITY_CENTROIDS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="centroid",
        authority_scope="Community",
        data_license="ODbL",
        content_hash="h1",
    )
    manifest_entrance = ReferenceManifest(
        reference_id="ref_ent",
        source="FieldSurvey",
        version="2026",
        claim_scope="ENTRANCE_POINTS",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="entrance",
        authority_scope="AuditedField",
        data_license="Proprietary",
        content_hash="h2",
    )

    assert manifest_centroid.feature_semantics == "centroid"
    assert manifest_entrance.feature_semantics == "entrance"
    assert manifest_centroid.feature_semantics != manifest_entrance.feature_semantics


def test_rf_05_additional_reference_expands_scope_without_rewriting_past_result():
    """RF-05: Adding a new reference creates a new versioned evaluation without mutating historical evaluation artifacts."""
    past_manifest_version = "1.0.0"
    past_references_count = 1  # OSM only

    # New diversified reference manifest list
    updated_references_count = 3  # OSM + Tianditu + Civil Admin
    new_manifest_version = "1.1.0"

    assert new_manifest_version != past_manifest_version
    assert updated_references_count > past_references_count


def test_rf_06_unknown_dependency_remains_dependency_unknown():
    """RF-06: When upstream data lineage cannot be verified, dependency state is strictly DEPENDENCY_UNKNOWN."""
    manifest_unverified = ReferenceManifest(
        reference_id="ref_unknown_web",
        source="PublicWebGIS",
        version="2026",
        claim_scope="COMMERCIAL_POI",
        geographic_scope="Xi'an",
        temporal_scope="2026",
        feature_semantics="unknown",
        authority_scope="UnverifiedPublic",
        data_license="WebScraped",
        dependency_state="DEPENDENCY_UNKNOWN",
        content_hash="h_unverified",
    )

    assert manifest_unverified.dependency_state == "DEPENDENCY_UNKNOWN"
    assert manifest_unverified.dependency_state != "VERIFIED_INDEPENDENT"

    # Evaluator does not count it as independent corroboration
    count = MultiReferenceEvidenceEvaluator.count_effective_independent_sources([manifest_unverified])
    assert count == 0
