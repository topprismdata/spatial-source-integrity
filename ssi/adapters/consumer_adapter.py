"""ConsumerAdapter: downstream interface for consuming TrustedSpatialSnapshots."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Tuple

from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.decision_ready_projection import DecisionReadyProjection
from ssi.contracts.runtime.trusted_spatial_snapshot import (
    SnapshotConsumptionRecord,
    TrustedSpatialSnapshot,
)


class ConsumptionError(RuntimeError):
    """Raised when a consumer attempts to consume an unauthorized or revoked snapshot."""


class ConsumerAdapter:
    """Downstream consumer adapter.
    
    Invariants:
    1. Adapter only reads, filters, and transports.
    2. Adapter cannot derive, forge, or alter Gate decisions or safety (EG-08).
    3. Revoked or expired snapshots are rejected immediately (EG-12).
    """

    def __init__(self, capability: ConsumerCapability):
        self.capability = capability

    def read_snapshot(
        self,
        snapshot: TrustedSpatialSnapshot,
        operation: str,
    ) -> Tuple[List[DecisionReadyProjection], SnapshotConsumptionRecord]:
        """Consumes a TrustedSpatialSnapshot and produces an audit consumption record."""
        consumption_id = f"csr_{uuid.uuid4().hex[:12]}"

        # EG-12: Revoked, expired, or non-production snapshots are blocked
        if not snapshot.is_consumable():
            record = SnapshotConsumptionRecord(
                consumption_id=consumption_id,
                snapshot_id=snapshot.snapshot_id,
                consumer_id=self.capability.consumer_id,
                consumer_version=self.capability.consumer_version,
                operation=operation,
                status=f"REJECTED_{snapshot.lifecycle_status.value}",
            )
            raise ConsumptionError(
                f"Consumption blocked: Snapshot '{snapshot.snapshot_id}' is not consumable "
                f"(status={snapshot.lifecycle_status.value}, mode={snapshot.deployment_mode.value})."
            )

        # Check operation support
        if operation not in self.capability.supported_operations:
            record = SnapshotConsumptionRecord(
                consumption_id=consumption_id,
                snapshot_id=snapshot.snapshot_id,
                consumer_id=self.capability.consumer_id,
                consumer_version=self.capability.consumer_version,
                operation=operation,
                status="REJECTED_UNSUPPORTED_OPERATION",
            )
            raise ConsumptionError(
                f"Consumption blocked: Operation '{operation}' is not supported by consumer '{self.capability.consumer_id}'."
            )

        # Check limits attached to snapshot
        for limit in snapshot.usage_limits:
            if limit.limit_type == "OPERATION_RESTRICTION":
                prohibited_ops = limit.parameters.get("prohibited_ops", [])
                if operation in prohibited_ops:
                    record = SnapshotConsumptionRecord(
                        consumption_id=consumption_id,
                        snapshot_id=snapshot.snapshot_id,
                        consumer_id=self.capability.consumer_id,
                        consumer_version=self.capability.consumer_version,
                        operation=operation,
                        status="REJECTED_LIMIT_VIOLATION",
                    )
                    raise ConsumptionError(
                        f"Consumption blocked: Operation '{operation}' violates UsageLimit '{limit.limit_id}'."
                    )

        applied_limits = [l.limit_id for l in snapshot.usage_limits]
        record = SnapshotConsumptionRecord(
            consumption_id=consumption_id,
            snapshot_id=snapshot.snapshot_id,
            consumer_id=self.capability.consumer_id,
            consumer_version=self.capability.consumer_version,
            operation=operation,
            applied_limits=applied_limits,
            status="SUCCESS",
        )

        return snapshot.projections, record
