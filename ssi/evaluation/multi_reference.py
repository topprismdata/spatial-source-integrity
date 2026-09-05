"""Multi-source reference diversification, dependency tracking, and claim-specific authority."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.shared_adapters.claim import ClaimResolutionStatus
from ssi.contracts.shared_adapters.evidence import (
    EvidenceAdapter,
    EvidenceConfidence,
    EvidenceDependencyStatus,
    EvidenceRelation,
    EvidenceRelationPolarity,
)
from ssi.evaluation.reference_manifest import ReferenceManifest


class ClaimAuthorityDomain(str, Enum):
    """Domains of spatial claims a reference is certified to evaluate."""
    ADMIN_BOUNDARIES = "ADMIN_BOUNDARIES"
    COMMUNITY_CENTROIDS = "COMMUNITY_CENTROIDS"
    BUILDING_FOOTPRINTS = "BUILDING_FOOTPRINTS"
    ROAD_NETWORK = "ROAD_NETWORK"
    ENTRANCE_POINTS = "ENTRANCE_POINTS"
    COMMERCIAL_POI = "COMMERCIAL_POI"


class MultiReferenceEvidenceEvaluator:
    """Evaluates multiple reference evidence sources against claims with strict dependency and authority governance.
    
    Invariants:
    1. Multiple dependent sources are not counted as independent corroboration (RF-01).
    2. Claim-specific authority: a reference can only validate claims within its certified claim_scope (RF-02).
    3. Contradictory independent references produce CONFLICTED, never silent averaging (RF-03).
    4. Preserves feature semantics (entrance vs centroid) without conflation (RF-04).
    5. Unknown dependency is strictly preserved as DEPENDENCY_UNKNOWN (RF-06).
    """

    @classmethod
    def filter_by_claim_authority(
        cls,
        manifest: ReferenceManifest,
        target_claim_domain: ClaimAuthorityDomain,
    ) -> bool:
        """Checks if a reference has authority to validate claims in the target domain."""
        return target_claim_domain.value in manifest.claim_scope

    @classmethod
    def count_effective_independent_sources(cls, manifests: List[ReferenceManifest]) -> int:
        """Counts only genuinely independent source families, collapsing known dependencies."""
        independent_count = 0
        seen_dependencies = set()

        for m in manifests:
            # Gate V2-4 / M6: self-produced evidence from an internal feedback loop
            # (e.g. D09↔Resolver refinement products) is never independent corroboration.
            authority = (m.authority_scope or "").upper()
            if "INTERNAL" in authority or (m.data_license or "").upper() == "INTERNAL":
                continue

            dep = m.dependency_state
            if dep == "VERIFIED_INDEPENDENT":
                independent_count += 1
            elif dep == "KNOWN_DEPENDENT":
                # Dependent sources share an upstream root; only count the first occurrence
                root = m.authority_scope or m.source
                if root not in seen_dependencies:
                    seen_dependencies.add(root)
                    independent_count += 1
            else:
                # DEPENDENCY_UNKNOWN cannot be credited as independent corroboration
                continue

        return independent_count

    @classmethod
    def resolve_multi_source_claim(
        cls,
        claim_id: str,
        target_domain: ClaimAuthorityDomain,
        evidence_relations: List[EvidenceRelation],
        manifests_by_ref_id: Dict[str, ReferenceManifest],
    ) -> ClaimResolutionStatus:
        """Adjudicates a claim across multiple reference evidence sources."""
        # 1. Filter evidence by reference authority domain
        valid_supporting = []
        valid_contradicting = []

        for rel in evidence_relations:
            if rel.claim_id != claim_id:
                continue
            manifest = manifests_by_ref_id.get(rel.evidence_id)
            if manifest and not cls.filter_by_claim_authority(manifest, target_domain):
                # Dropped: reference lacks authority for this claim domain
                continue

            if rel.polarity == EvidenceRelationPolarity.SUPPORTS:
                valid_supporting.append(rel)
            elif rel.polarity == EvidenceRelationPolarity.CONTRADICTS:
                valid_contradicting.append(rel)

        # 2. Check for contradiction between independent high-confidence evidence
        has_independent_support = any(
            r.dependency_status == EvidenceDependencyStatus.VERIFIED_INDEPENDENT for r in valid_supporting
        )
        has_independent_contradiction = any(
            r.dependency_status == EvidenceDependencyStatus.VERIFIED_INDEPENDENT for r in valid_contradicting
        )

        if has_independent_support and has_independent_contradiction:
            # Irreconcilable contradiction between independent authorities -> CONFLICTED
            return ClaimResolutionStatus.CONFLICTED

        if valid_contradicting and not valid_supporting:
            return ClaimResolutionStatus.REFUTED

        if valid_supporting and not valid_contradicting:
            return ClaimResolutionStatus.SUPPORTED

        return ClaimResolutionStatus.UNRESOLVED
