"""ReferenceManifest runtime contract: inventory of external reference datasets."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReferenceManifest(BaseModel):
    """Provenance and feature semantics contract for an external reference dataset.
    
    Invariants:
    1. Every reference used in evaluation must have an auditable ReferenceManifest.
    2. Explicitly records feature semantics (e.g. entrance vs centroid vs boundary).
    3. Tracks dependency status to prevent circular confirmation.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    reference_id: str = Field(description="Unique reference dataset ID")
    source: str = Field(description="Provider or authority name (e.g. OSM, AMAP, CIVIL_ADMIN)")
    version: str = Field(description="Snapshot or publication version (e.g. 2026-08-15)")
    claim_scope: str = Field(description="Scope of claims this reference can validate")
    geographic_scope: str = Field(description="Municipal or regional envelope (e.g. Shaanxi-Xi'an)")
    temporal_scope: str = Field(description="Validity time window of reference data")
    feature_semantics: str = Field(
        description="Feature definition: entrance | centroid | building_center | boundary_polygon | sales_office | unknown",
    )
    authority_scope: str = Field(description="Statutory authority or community collaborative")
    data_license: str = Field(description="Licensing constraints (e.g. ODbL, Commercial, Proprietary)")
    dependency_state: str = Field(
        default="DEPENDENCY_UNKNOWN",
        description="VERIFIED_INDEPENDENT | KNOWN_DEPENDENT | DEPENDENCY_UNKNOWN",
    )
    content_hash: str = Field(description="SHA-256 hash over reference data artifact")
