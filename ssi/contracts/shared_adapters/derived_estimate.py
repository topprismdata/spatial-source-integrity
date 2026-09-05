"""DerivedEstimate shared adapter projecting prism-core:DerivedEstimate."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import Field

from ssi.contracts.shared_adapters.base import PrismSharedAdapter


class DerivedEstimateAdapter(PrismSharedAdapter):
    """Runtime projection of prism-core:DerivedEstimate.
    
    Represents an algorithmically derived, aligned, or repaired spatial representation.
    Never overwrites original raw observations.
    """

    _canonical_uri: ClassVar[str] = "prism://ontology/core/DerivedEstimate"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "REUSED"

    derived_id: str = Field(description="Unique derived estimate identifier")
    target_entity_id: str = Field(description="Entity this derived estimate characterizes")
    estimation_method: str = Field(description="Method, model, or alignment pipeline name")
    geometry_wkt: Optional[str] = Field(default=None, description="Derived WKT geometry")
    crs: Optional[str] = Field(default=None, description="Derived or aligned coordinate reference system")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Derived attributes")
    derived_from_observation_ids: List[str] = Field(
        default_factory=list,
        description="Lineage links to raw observations",
    )
    derived_from_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Lineage links to supporting evidence items",
    )
    repair_approval_id: Optional[str] = Field(
        default=None,
        description="Reference to formal RepairApproval if derived via repair governance",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp",
    )
    provenance: str = Field(default="", description="Algorithmic pipeline and parameter details")
