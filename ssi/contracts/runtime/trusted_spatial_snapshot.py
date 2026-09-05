"""TrustedSpatialSnapshot and ConsumptionRecord runtime contracts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.runtime.decision_ready_projection import DecisionReadyProjection
from ssi.contracts.runtime.usage_limit import UsageLimit


class SnapshotLifecycleStatus(str, Enum):
    """Lifecycle state of a published snapshot."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    INVALIDATED = "INVALIDATED"


class SnapshotDeploymentMode(str, Enum):
    """Deployment audience for the snapshot."""
    SHADOW = "SHADOW"
    PRODUCTION = "PRODUCTION"


class TrustedSpatialSnapshot(BaseModel):
    """Immutable, content-addressable collection publication artifact.
    
    Invariants:
    1. Immutable.
    2. Only `ACTIVE + PRODUCTION` is consumable by production consumers.
    3. Revocation or expiration immediately blocks new consumption.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_id: str = Field(description="Unique snapshot ID (content-addressable)")
    version: str = Field(description="Semantic version of this publication")
    consumer_id: str = Field(description="Target consumer authorized to consume this snapshot")
    decision_profile_id: str = Field(description="DecisionProfile this snapshot satisfies")
    lifecycle_status: SnapshotLifecycleStatus = Field(default=SnapshotLifecycleStatus.ACTIVE)
    deployment_mode: SnapshotDeploymentMode = Field(default=SnapshotDeploymentMode.PRODUCTION)
    valid_from: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_until: Optional[str] = Field(default=None)
    projections: List[DecisionReadyProjection] = Field(default_factory=list)
    usage_limits: List[UsageLimit] = Field(default_factory=list)
    gate_decision_ids: List[str] = Field(default_factory=list)
    content_hash: str = Field(default="", description="SHA-256 over projections and usage limits")
    manifest_metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_consumable(self) -> bool:
        """Production consumption predicate: only ACTIVE + PRODUCTION is consumable."""
        return (
            self.lifecycle_status == SnapshotLifecycleStatus.ACTIVE
            and self.deployment_mode == SnapshotDeploymentMode.PRODUCTION
        )

    @classmethod
    def compute_hash(cls, projections: List[DecisionReadyProjection], limits: List[UsageLimit]) -> str:
        """Computes deterministic SHA-256 hash over included projections and limits."""
        payload = {
            "projections": [p.model_dump() for p in sorted(projections, key=lambda x: x.projection_id)],
            "limits": [l.model_dump() for l in sorted(limits, key=lambda x: x.limit_id)],
        }
        raw_json = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()


class SnapshotConsumptionRecord(BaseModel):
    """Audit record capturing downstream consumer usage of a snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consumption_id: str = Field(description="Unique consumption audit record ID")
    snapshot_id: str = Field(description="ID of consumed snapshot")
    consumer_id: str = Field(description="ID of consuming system")
    consumer_version: str = Field(description="Version of consuming system")
    operation: str = Field(description="Operation executed (e.g. routing, aggregation)")
    consumed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    applied_limits: List[str] = Field(default_factory=list)
    status: str = Field(default="SUCCESS", description="SUCCESS | REJECTED_REVOKED | REJECTED_EXPIRED | REJECTED_LIMIT")
