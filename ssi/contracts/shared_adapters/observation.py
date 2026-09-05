"""Observation shared adapter projecting prism-core:Observation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional
from pydantic import Field

from ssi.contracts.shared_adapters.base import PrismSharedAdapter


class ObservationAdapter(PrismSharedAdapter):
    """Runtime projection of prism-core:Observation, adapting SDI Observation dataclass.
    
    Represents an objective, provenance-bearing measurement or raw capture from a source.
    """

    _canonical_uri: ClassVar[str] = "prism://ontology/core/Observation"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "REUSED_AND_ADAPTED"

    observation_id: str = Field(description="Unique observation identifier")
    source_asset_id: str = Field(description="Immutable source asset identifier")
    source_record_id: str = Field(description="Row or record identifier within the source asset")
    geometry_wkt: Optional[str] = Field(default=None, description="Observed WKT geometry, if present")
    crs: Optional[str] = Field(default=None, description="Declared CRS / spatial reference string")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Raw observed key-value attributes")
    observed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when the observation was made or recorded",
    )
    provenance: str = Field(default="", description="Lineage and supplier details")
