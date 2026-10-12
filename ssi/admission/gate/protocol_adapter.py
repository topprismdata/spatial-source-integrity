"""Protocol adapter: SSI GateDecision -> TopPrism DQ Verdict Protocol v1.0.1.

Maps the SSI admission contract (ssi/contracts/runtime/gate_decision.py) to the
unified vocabulary published by geospatial-data-governance
protocol/dq_verdict_protocol_v1.json (MS-PROP-023, proposed).

Mapping invariants:
- BLOCK_FOR_PROFILE -> BLOCK (profile kept in scope)
- QUARANTINE_SCOPE -> QUARANTINE
- RequirementStatus UNRESOLVED / NOT_EVALUATED -> FAIL (fail-closed: absent
  evidence never reads as satisfaction)
- severity = UNSPECIFIED (SSI requirements carry no C0-C3 grading; the protocol
  forbids silent defaults, so we declare it explicitly)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ssi.contracts.runtime.gate_decision import (
    AdmissionAction,
    GateDecision,
    GovernanceDisposition,
)
from ssi.contracts.runtime.requirement_evaluation import RequirementStatus

SSI_GATE_REGISTRY = "ssi-gate"
SSI_GATE_VERSION = "v0.1"

_ACTION_MAP = {
    AdmissionAction.ALLOW: "ALLOW",
    AdmissionAction.ALLOW_WITH_LIMITS: "ALLOW_WITH_LIMITS",
    AdmissionAction.REVIEW: "REVIEW",
    AdmissionAction.BLOCK_FOR_PROFILE: "BLOCK",
}

_DISPOSITION_MAP = {
    GovernanceDisposition.NONE: "NONE",
    GovernanceDisposition.QUARANTINE_SCOPE: "QUARANTINE",
    GovernanceDisposition.SUSPEND_SOURCE: "SUSPEND_SOURCE",
    GovernanceDisposition.REPAIR_REQUIRED: "REPAIR_REQUIRED",
    GovernanceDisposition.INVESTIGATION_REQUIRED: "INVESTIGATION_REQUIRED",
}

_STATUS_MAP = {
    RequirementStatus.SATISFIED: "PASS",
    RequirementStatus.NOT_SATISFIED: "FAIL",
    RequirementStatus.UNRESOLVED: "FAIL",       # fail-closed
    RequirementStatus.NOT_EVALUATED: "FAIL",    # fail-closed
    RequirementStatus.NOT_APPLICABLE: "NOT_APPLICABLE",
}


def _rule_id(requirement_name: str) -> str:
    slug = "".join(ch if ch.isalnum() else "-" for ch in requirement_name.upper())
    slug = "-".join(part for part in slug.split("-") if part) or "REQ"
    return f"SSI-REQ-{slug}@{SSI_GATE_REGISTRY}-{SSI_GATE_VERSION}"


def map_action(action: AdmissionAction) -> str:
    return _ACTION_MAP[action]


def map_disposition(disposition: GovernanceDisposition) -> str:
    return _DISPOSITION_MAP[disposition]


def map_requirement_status(status: RequirementStatus) -> str:
    return _STATUS_MAP[status]


def to_protocol_decision(decision: GateDecision, protocol_schema_path: Path) -> Dict[str, Any]:
    """Convert a frozen SSI GateDecision into a protocol v1.0.1 GateDecision dict.

    The output validates against protocol/dq_verdict_protocol_v1.json
    ($defs/GateDecision). Validation is performed by the caller/test suite;
    this function raises ValueError on unmappable enum members (totality is
    covered by tests over the full 4x5 matrix).
    """
    try:
        action = map_action(decision.action)
    except KeyError:
        raise ValueError(f"unmapped AdmissionAction: {decision.action!r}")
    try:
        disposition = map_disposition(decision.disposition)
    except KeyError:
        raise ValueError(f"unmapped GovernanceDisposition: {decision.disposition!r}")

    evaluations = []
    for req in decision.requirement_evaluations:
        try:
            verdict = map_requirement_status(req.status)
        except KeyError:
            raise ValueError(f"unmapped RequirementStatus: {req.status!r}")
        evaluations.append({
            "rule_id": _rule_id(req.requirement_name),
            "verdict": verdict,
            "severity": "UNSPECIFIED",
            "hard_gate": False,
            "evidence_ids": [],
            "measured": {
                "requirement_name": req.requirement_name,
                "observed_value": req.observed_value,
                "threshold": req.threshold,
                "rationale": req.rationale,
                "source_status": req.status.value,
            },
            "evaluated_at": decision.decided_at,
        })

    limits = []
    for lim in decision.applied_usage_limits:
        limits.append(f"{lim.limit_type}: {json.dumps(lim.parameters, ensure_ascii=False, sort_keys=True)}")

    out: Dict[str, Any] = {
        "protocol_version": "1.0.1",
        "action": action,
        "disposition": disposition,
        "scope": {
            "profile": f"{decision.decision_profile_id}@{decision.decision_profile_version}",
            "source": decision.subject_id,
        },
        "evaluations": evaluations,
        # 不产出 hard_gates_all_pass: SSI 契约无此概念, 伪造即违反协议不变量
        "rationale": decision.justification,
        "decided_by": f"ssi-gate-executor/{decision.gate_policy_id}@{decision.gate_policy_version}",
        "decided_at": decision.decided_at,
        "immutable": True,
    }
    if decision.consumer_capability_version:
        out["scope"]["consumer_capability_version"] = decision.consumer_capability_version
    if decision.valid_until:
        out["scope"]["valid_until"] = decision.valid_until
    return out
