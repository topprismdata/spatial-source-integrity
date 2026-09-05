"""Claim shared adapter projecting provisional prism-core:Claim."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, List, Literal, Optional
from pydantic import Field

from ssi.contracts.shared_adapters.base import PrismSharedAdapter


class ClaimResolutionStatus(str, Enum):
    """Adjudicated status of a Claim based on evidence evaluation."""
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    CONFLICTED = "CONFLICTED"
    UNRESOLVED = "UNRESOLVED"


class GenericClaimAdapter(PrismSharedAdapter):
    """Provisional runtime projection of prism-core:Claim.
    
    A proposition about real-world state subject to verification through evidence.
    """

    _canonical_uri: ClassVar[str] = "prism://ontology/core/Claim#provisional"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "PENDING_ONTOLOGY_GOVERNANCE"

    claim_id: str = Field(description="Unique claim identifier")
    claim_type: str = Field(description="Type category: ENTITY_LINK, SPATIAL_LOCATION, REFERENCE_CRS, ADMIN_ASSIGNMENT")
    subject_ref: str = Field(description="Subject identifier (e.g. SourceRecord, Entity)")
    predicate: str = Field(description="Relationship predicate (e.g. refers_to, located_at, uses_reference)")
    asserted_value: Any = Field(description="Asserted value or target object reference")
    asserted_by: str = Field(description="Source or actor who asserted this claim")
    asserted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when the claim was asserted",
    )


class EntityLinkClaimAdapter(GenericClaimAdapter):
    """Specialization of Claim for Entity Resolution without creating a new spatial domain root."""

    claim_type: str = Field(default="ENTITY_LINK")
    predicate: str = Field(default="refers_to")
    source_record_id: str = Field(description="Source record making the link")
    target_entity_id: str = Field(description="Target canonical entity id")

    @classmethod
    def from_legacy_pair_relation(
        cls,
        source_id: str,
        target_id: str,
        relation_str: str,
        confidence: float,
        evidence_notes: str = "",
    ) -> EntityLinkClaimAdapter:
        """Adapts legacy SDI EntityPairRelation into a governed EntityLinkClaimAdapter."""
        return cls(
            claim_id=f"elc_{source_id}_{target_id}",
            subject_ref=source_id,
            source_record_id=source_id,
            target_entity_id=target_id,
            asserted_value={"target_entity_id": target_id, "relation": relation_str, "confidence": confidence},
            asserted_by="legacy_entity_resolution",
        )


class ClaimResolution(PrismSharedAdapter):
    """Resolution of a Claim based on evaluating its associated EvidenceRelations."""

    _canonical_uri: ClassVar[str] = "prism://ontology/core/ClaimResolution#provisional"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "PENDING_ONTOLOGY_GOVERNANCE"

    claim_id: str = Field(description="Reference to the evaluated Claim")
    status: ClaimResolutionStatus = Field(description="Evaluated state")
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    resolved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_by: str = Field(default="system_evaluator")
    notes: str = Field(default="", description="Adjudication rationale")
