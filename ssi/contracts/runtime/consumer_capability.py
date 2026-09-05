"""ConsumerCapability runtime contract."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, ConfigDict, Field

from ssi.contracts.runtime.usage_limit import UsageLimit


class ConsumerCapability(BaseModel):
    """Declared and verified operational capabilities of a downstream consumer."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consumer_id: str = Field(description="Consumer system identifier")
    consumer_version: str = Field(description="Version of consumer software")
    name: str = Field(description="Consumer name")
    supported_operations: List[str] = Field(
        default_factory=lambda: ["aggregation", "reporting"],
        description="Operations this consumer performs (e.g. routing, geofencing, aggregation)",
    )
    supports_usage_limits: bool = Field(
        default=True,
        description="Whether this consumer is certified to enforce machine-readable UsageLimits",
    )
    supported_limit_types: List[str] = Field(
        default_factory=lambda: ["OPERATION_RESTRICTION", "MIN_RESOLUTION", "GEOGRAPHIC_BOUNDARY", "TIME_HORIZON"],
        description="Limit types this consumer can actively enforce",
    )

    def is_compatible_with(self, usage_limits: List[UsageLimit]) -> bool:
        """Determines if this consumer is permitted to receive data carrying these usage limits."""
        if not usage_limits:
            return True
        if not self.supports_usage_limits:
            return False

        for limit in usage_limits:
            # Check if consumer can enforce this limit type
            if limit.limit_type not in self.supported_limit_types:
                return False

            # If it's an operation restriction, check if any prohibited op is in consumer's operations
            if limit.limit_type == "OPERATION_RESTRICTION":
                prohibited_ops = limit.parameters.get("prohibited_ops", [])
                for op in prohibited_ops:
                    if op in self.supported_operations:
                        return False

        return True
