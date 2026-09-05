"""SpatialAdmissionPublisher: single non-bypassable authority for minting projections and snapshots."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.decision_ready_projection import DecisionReadyProjection
from ssi.contracts.runtime.gate_decision import AdmissionAction, GateDecision
from ssi.contracts.runtime.trusted_spatial_snapshot import (
    SnapshotDeploymentMode,
    SnapshotLifecycleStatus,
    TrustedSpatialSnapshot,
)
from ssi.contracts.shared_adapters.decision_profile import DecisionProfileAdapter


class PublicationError(RuntimeError):
    """Raised when publication invariant is violated."""


class SpatialAdmissionPublisher:
    """Sole authorized entity permitted to mint DecisionReadyProjection and publish TrustedSpatialSnapshot."""

    @classmethod
    def mint_projection(
        cls,
        gate_decision: GateDecision,
        admitted_geometry_wkt: str,
        admitted_crs: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> DecisionReadyProjection:
        """Mints an immutable DecisionReadyProjection from an admissible GateDecision."""
        if not gate_decision.is_admitted():
            raise PublicationError(
                f"Cannot mint DecisionReadyProjection: GateDecision '{gate_decision.decision_id}' "
                f"has non-admissible action '{gate_decision.action.value}'."
            )

        projection_id = f"drp_{uuid.uuid4().hex[:12]}"
        return DecisionReadyProjection(
            projection_id=projection_id,
            subject_id=gate_decision.subject_id,
            admitted_geometry_wkt=admitted_geometry_wkt,
            admitted_crs=admitted_crs,
            attributes=dict(attributes or {}),
            gate_decision_id=gate_decision.decision_id,
            decision_profile_id=gate_decision.decision_profile_id,
            usage_limits=list(gate_decision.applied_usage_limits),
        )

    @classmethod
    def publish_snapshot(
        cls,
        consumer: ConsumerCapability,
        decision_profile: DecisionProfileAdapter,
        gate_decisions: List[GateDecision],
        candidate_geometries: Dict[str, Dict[str, Any]],
        deployment_mode: SnapshotDeploymentMode = SnapshotDeploymentMode.PRODUCTION,
        version: str = "1.0.0",
        valid_until: Optional[str] = None,
    ) -> TrustedSpatialSnapshot:
        """Publishes an immutable, content-addressable TrustedSpatialSnapshot.
        
        Enforces Fail-Closed invariants:
        - Only subjects with valid GateDecision are evaluated.
        - BLOCK_FOR_PROFILE is never published.
        - REVIEW is never published to PRODUCTION.
        - ALLOW_WITH_LIMITS requires verified consumer capability compatibility.
        """
        projections: List[DecisionReadyProjection] = []
        admitted_gate_decision_ids: List[str] = []
        all_limits = []

        for dec in gate_decisions:
            # Missing or mismatched profile
            if dec.decision_profile_id != decision_profile.profile_id:
                continue

            # Invariant: BLOCK_FOR_PROFILE never publishes (EG-02)
            if dec.is_blocked():
                continue

            # Invariant: REVIEW never publishes to production (EG-03)
            if dec.is_review() and deployment_mode == SnapshotDeploymentMode.PRODUCTION:
                continue

            # Invariant: ALLOW_WITH_LIMITS enforces consumer capability (EG-04)
            if dec.action == AdmissionAction.ALLOW_WITH_LIMITS:
                if not consumer.is_compatible_with(dec.applied_usage_limits):
                    continue

            # Subject must have candidate geometry
            cand = candidate_geometries.get(dec.subject_id)
            if not cand:
                continue

            proj = cls.mint_projection(
                gate_decision=dec,
                admitted_geometry_wkt=cand["geometry_wkt"],
                admitted_crs=cand.get("crs", "EPSG:4326"),
                attributes=cand.get("attributes", {}),
            )
            projections.append(proj)
            admitted_gate_decision_ids.append(dec.decision_id)
            all_limits.extend(dec.applied_usage_limits)

        content_hash = TrustedSpatialSnapshot.compute_hash(projections, all_limits)
        snapshot_id = f"snap_{decision_profile.profile_id.lower()}_{uuid.uuid4().hex[:8]}"

        return TrustedSpatialSnapshot(
            snapshot_id=snapshot_id,
            version=version,
            consumer_id=consumer.consumer_id,
            decision_profile_id=decision_profile.profile_id,
            lifecycle_status=SnapshotLifecycleStatus.ACTIVE,
            deployment_mode=deployment_mode,
            valid_from=datetime.now(timezone.utc).isoformat(),
            valid_until=valid_until,
            projections=projections,
            usage_limits=all_limits,
            gate_decision_ids=admitted_gate_decision_ids,
            content_hash=content_hash,
            manifest_metadata={
                "projections_count": len(projections),
                "consumer_version": consumer.consumer_version,
                "profile_version": decision_profile.version,
            },
        )

    @classmethod
    def revoke_snapshot(cls, snapshot: TrustedSpatialSnapshot, reason: str) -> TrustedSpatialSnapshot:
        """Revokes an active snapshot due to upstream retraction or defect."""
        return TrustedSpatialSnapshot(
            snapshot_id=snapshot.snapshot_id,
            version=snapshot.version,
            consumer_id=snapshot.consumer_id,
            decision_profile_id=snapshot.decision_profile_id,
            lifecycle_status=SnapshotLifecycleStatus.REVOKED,
            deployment_mode=snapshot.deployment_mode,
            valid_from=snapshot.valid_from,
            valid_until=snapshot.valid_until,
            projections=snapshot.projections,
            usage_limits=snapshot.usage_limits,
            gate_decision_ids=snapshot.gate_decision_ids,
            content_hash=snapshot.content_hash,
            manifest_metadata={**snapshot.manifest_metadata, "revocation_reason": reason},
        )
