"""Base class for all prism-ontology shared adapters in SSI."""

from __future__ import annotations

from typing import ClassVar
from pydantic import BaseModel, ConfigDict


class PrismSharedAdapter(BaseModel):
    """Base model for shared adapters projecting prism-ontology contracts.
    
    Invariants:
    1. Immutable (frozen = True).
    2. Strict schema (extra = "forbid").
    3. Explicit tracking of canonical ontology URI, ontology version, and schema version.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    _canonical_uri: ClassVar[str]
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "STABLE"
