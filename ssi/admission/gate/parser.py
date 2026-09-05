"""GatePolicyParser: converts GatePolicy contracts or YAML definitions into GatePolicyIR."""

from __future__ import annotations

from typing import Any, Dict
import yaml

from ssi.admission.gate.ir import (
    GatePolicyIR,
    HardBlockRule,
    RequiredAssessmentRule,
    ReviewTriggerRule,
    StabilityRule,
)
from ssi.contracts.runtime.gate_policy import GatePolicy


class GatePolicyParser:
    """Parses GatePolicy declarations into an executable IR."""

    @classmethod
    def from_contract(cls, policy: GatePolicy) -> GatePolicyIR:
        """Parses a Pydantic GatePolicy contract into GatePolicyIR."""
        return GatePolicyIR(
            policy_id=policy.policy_id,
            version=policy.version,
            name=policy.name,
            hard_block=HardBlockRule(categories=policy.hard_block_finding_categories),
            required_assessments=RequiredAssessmentRule(assessment_names=policy.required_assessments),
            review_triggers=ReviewTriggerRule(categories=policy.review_trigger_finding_categories),
            stability=StabilityRule(
                require_stable=policy.require_decision_stability,
                unstable_action=policy.unstable_disposition,
            ),
            metadata={"description": policy.description},
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> GatePolicyIR:
        """Parses a YAML string into GatePolicyIR."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GatePolicyIR:
        """Parses a dict into GatePolicyIR."""
        return GatePolicyIR(
            policy_id=data["policy_id"],
            version=data.get("version", "1.0.0"),
            name=data.get("name", data["policy_id"]),
            hard_block=HardBlockRule(categories=data.get("hard_block_categories", [])),
            required_assessments=RequiredAssessmentRule(
                assessment_names=data.get("required_assessments", [])
            ),
            review_triggers=ReviewTriggerRule(
                categories=data.get("review_trigger_categories", [])
            ),
            stability=StabilityRule(
                require_stable=data.get("require_stability", True),
                unstable_action=data.get("unstable_action", "BLOCK_FOR_PROFILE"),
            ),
            metadata=data.get("metadata", {}),
        )
