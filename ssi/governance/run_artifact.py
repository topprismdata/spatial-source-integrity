"""RunArtifact contract (Gate V2-2): immutable run identity, lineage, and lifecycle.

Core rule (B1-002 lesson): corrections create NEW runs; existing runs are never
edited in place. A run's artifacts are content-addressed and its status can only
transition forward: DRAFT -> ACTIVE -> SUPERSEDED | INVALIDATED (terminal).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class RunStatus(str, Enum):
    """Forward-only lifecycle. No in-place edits after ACTIVE."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    INVALIDATED = "INVALIDATED"


class RunArtifact(BaseModel):
    """Immutable identity record for an evaluation run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(description="Globally unique run identifier, immutable once ACTIVE")
    parent_run_id: Optional[str] = Field(
        default=None,
        description="Present when this run corrects or supersedes a prior run",
    )
    code_commit: str = Field(description="Exact Git SHA this run executed under")
    source_hashes: Dict[str, str] = Field(description="SHA-256 of each raw input asset")
    config_hash: str = Field(description="SHA-256 over the frozen run configuration")
    artifact_hashes: Dict[str, str] = Field(
        default_factory=dict,
        description="SHA-256 over each emitted artifact (path -> hash)",
    )
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: RunStatus = Field(default=RunStatus.DRAFT)
    status_reason: Optional[str] = Field(default=None)
    amendment_refs: Optional[str] = Field(
        default=None,
        description="Pointer to amendment/correction records if status != ACTIVE",
    )

    def supersede(self, reason: str, amendment_ref: str) -> "RunArtifact":
        """Returns a SUPERSEDED copy. Original run artifacts are never edited."""
        return RunArtifact(
            run_id=self.run_id,
            parent_run_id=self.parent_run_id,
            code_commit=self.code_commit,
            source_hashes=self.source_hashes,
            config_hash=self.config_hash,
            artifact_hashes=self.artifact_hashes,
            created_at=self.created_at,
            status=RunStatus.SUPERSEDED,
            status_reason=reason,
            amendment_refs=amendment_ref,
        )

    def invalidate(self, reason: str, amendment_ref: str) -> "RunArtifact":
        """Returns an INVALIDATED copy for runs whose evidence foundation failed audit."""
        return RunArtifact(
            run_id=self.run_id,
            parent_run_id=self.parent_run_id,
            code_commit=self.code_commit,
            source_hashes=self.source_hashes,
            config_hash=self.config_hash,
            artifact_hashes=self.artifact_hashes,
            created_at=self.created_at,
            status=RunStatus.INVALIDATED,
            status_reason=reason,
            amendment_refs=amendment_ref,
        )
