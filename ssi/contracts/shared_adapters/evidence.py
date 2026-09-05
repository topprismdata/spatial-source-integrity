"""Evidence shared adapter projecting prism-core:Evidence."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import Field

from ssi.contracts.shared_adapters.base import PrismSharedAdapter


class EvidenceRelationPolarity(str, Enum):
    """Polarity of evidence with respect to a Claim."""
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DOES_NOT_RESOLVE = "DOES_NOT_RESOLVE"


class EvidenceConfidence(str, Enum):
    """Calibrated confidence of the evidence."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EvidenceDependencyStatus(str, Enum):
    """Dependency relationship to other evidence in the claim."""
    VERIFIED_INDEPENDENT = "VERIFIED_INDEPENDENT"
    KNOWN_DEPENDENT = "KNOWN_DEPENDENT"
    DEPENDENCY_UNKNOWN = "DEPENDENCY_UNKNOWN"


class EvidenceAdapter(PrismSharedAdapter):
    """Runtime projection of prism-core:Evidence + SDI EvidencePacket."""

    _canonical_uri: ClassVar[str] = "prism://ontology/core/Evidence"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "REUSED_AND_ADAPTED"

    evidence_id: str = Field(description="Unique evidence identifier")
    evidence_type: str = Field(description="Type category: MEASUREMENT, STATISTICAL, EXTERNAL_REFERENCE, HUMAN")
    source_ref: str = Field(description="Detector, model, reference dataset, or human reviewer ID")
    content_summary: str = Field(description="Human-readable explanation of what this evidence shows")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantitative diagnostic measurements")
    visual_artifacts: List[str] = Field(default_factory=list, description="Optional paths or URIs to visual proof")
    confidence: EvidenceConfidence = Field(default=EvidenceConfidence.MEDIUM, description="Confidence grade")
    dependency_status: EvidenceDependencyStatus = Field(
        default=EvidenceDependencyStatus.DEPENDENCY_UNKNOWN,
        description="Whether this evidence has verified independent provenance",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp of evidence generation",
    )


class EvidenceRelation(PrismSharedAdapter):
    """Binds an Evidence item to a Claim with explicit polarity and independence tracking."""

    _canonical_uri: ClassVar[str] = "prism://ontology/core/hasEvidence"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "REUSED_AND_ADAPTED"

    relation_id: str = Field(description="Unique identifier of this evidence relation")
    evidence_id: str = Field(description="Reference to the EvidenceAdapter")
    claim_id: str = Field(description="Reference to the Claim being supported or contradicted")
    polarity: EvidenceRelationPolarity = Field(description="Logical relation to the claim")
    confidence: EvidenceConfidence = Field(default=EvidenceConfidence.MEDIUM)
    dependency_status: EvidenceDependencyStatus = Field(default=EvidenceDependencyStatus.DEPENDENCY_UNKNOWN)
    rationale: str = Field(default="", description="Why this evidence supports or contradicts the claim")
