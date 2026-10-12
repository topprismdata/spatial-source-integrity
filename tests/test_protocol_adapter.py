"""WP02: protocol adapter tests.

1. Totality: every (AdmissionAction x GovernanceDisposition) combo in the 4x5
   matrix maps to a valid protocol dict (no unmapped enum escapes).
2. Conformance: every mapped output validates against the published protocol
   schema (geospatial-data-governance protocol/dq_verdict_protocol_v1.json,
   $defs/GateDecision, protocol_version 1.0.1).
3. Fail-closed: UNRESOLVED / NOT_EVALUATED must read FAIL, never PASS.
4. Immutability preserved: adapter must not mutate the input decision.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ssi.admission.gate.protocol_adapter import (
    map_action,
    map_disposition,
    map_requirement_status,
    to_protocol_decision,
)
from ssi.contracts.runtime.gate_decision import (
    AdmissionAction,
    GateDecision,
    GovernanceDisposition,
)
from ssi.contracts.runtime.requirement_evaluation import (
    RequirementEvaluation,
    RequirementStatus,
)
from ssi.contracts.runtime.usage_limit import UsageLimit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SCHEMA = (
    PROJECT_ROOT / "docs" / "protocol" / "dq_verdict_protocol_v1.json"
)


def _make_decision(action, disposition, requirements=(), usage_limits=()):
    return GateDecision(
        decision_id="GD-TEST-0001",
        subject_id="src-crm-202610-batch7",
        candidate_representation_id="cand-geo-001",
        evaluation_result_id="er-2026-000123",
        decision_profile_id="DP-02-visit-planning",
        decision_profile_version="1.3.0",
        gate_policy_id="GP-DEFAULT",
        gate_policy_version="2.0.1",
        action=action,
        disposition=disposition,
        applied_usage_limits=list(usage_limits),
        requirement_evaluations=list(requirements),
        justification="matrix test",
    )


def _req(name="coordinate_residual", status=RequirementStatus.SATISFIED):
    return RequirementEvaluation(
        requirement_name=name,
        status=status,
        observed_value=12.5,
        threshold=50,
        rationale="within profile tolerance",
    )


def _limit():
    return UsageLimit(
        limit_id="UL-001",
        limit_type="GEOGRAPHIC_BOUNDARY",
        parameters={"region": "cn-anhui"},
    )


pytest.importorskip("jsonschema", minversion="4.18")


@pytest.fixture(scope="module")
def protocol_validator():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        "\n".join(l for l in PROTOCOL_SCHEMA.read_text(encoding="utf-8").splitlines()
                  if not l.lstrip().startswith("#")))
    assert schema["protocol_version"] == "1.0.1"
    return jsonschema.Draft202012Validator(schema)


ALL_ACTIONS = list(AdmissionAction)
ALL_DISPOSITIONS = list(GovernanceDisposition)


def test_protocol_schema_present():
    assert PROTOCOL_SCHEMA.exists(), (
        "protocol schema missing; fetch geospatial-data-governance "
        "protocol/dq_verdict_protocol_v1.json into docs/protocol/")


def test_matrix_4x5_totality_and_conformance(protocol_validator):
    """Full 4x5 AdmissionAction x GovernanceDisposition matrix:
    every combo maps, and every mapped dict validates against the protocol."""
    for action in ALL_ACTIONS:
        for disposition in ALL_DISPOSITIONS:
            decision = _make_decision(
                action, disposition,
                requirements=[_req("coordinate_residual", RequirementStatus.SATISFIED),
                              _req("reference_residual", RequirementStatus.UNRESOLVED)],
                usage_limits=[_limit()],
            )
            out = to_protocol_decision(decision, PROTOCOL_SCHEMA)
            errors = list(protocol_validator.iter_errors(out))
            assert not errors, (
                f"protocol violations for {action}/{disposition}: "
                f"{[e.message for e in errors]}")
            assert out["action"] == map_action(action)
            assert out["disposition"] == map_disposition(disposition)


def test_matrix_counts():
    assert len(ALL_ACTIONS) == 4
    assert len(ALL_DISPOSITIONS) == 5
    assert len({map_action(a) for a in ALL_ACTIONS}) == 4
    assert len({map_disposition(d) for d in ALL_DISPOSITIONS}) == 5


@pytest.mark.parametrize("status", [RequirementStatus.UNRESOLVED,
                                    RequirementStatus.NOT_EVALUATED])
def test_fail_closed(status, protocol_validator):
    decision = _make_decision(
        AdmissionAction.BLOCK_FOR_PROFILE, GovernanceDisposition.INVESTIGATION_REQUIRED,
        requirements=[_req("coverage_manifest", status)])
    out = to_protocol_decision(decision, PROTOCOL_SCHEMA)
    assert out["evaluations"][0]["verdict"] == "FAIL"
    assert out["action"] == "BLOCK"
    assert not list(protocol_validator.iter_errors(out))


def test_block_for_profile_and_quarantine_renamed(protocol_validator):
    out = to_protocol_decision(
        _make_decision(AdmissionAction.BLOCK_FOR_PROFILE,
                       GovernanceDisposition.QUARANTINE_SCOPE),
        PROTOCOL_SCHEMA)
    assert out["action"] == "BLOCK"
    assert out["disposition"] == "QUARANTINE"
    assert out["scope"]["profile"].startswith("DP-02-visit-planning@")
    assert not list(protocol_validator.iter_errors(out))


def test_severity_declared_unspecified(protocol_validator):
    out = to_protocol_decision(
        _make_decision(AdmissionAction.ALLOW_WITH_LIMITS, GovernanceDisposition.NONE,
                       requirements=[_req()]), PROTOCOL_SCHEMA)
    assert out["evaluations"][0]["severity"] == "UNSPECIFIED"
    assert not list(protocol_validator.iter_errors(out))


def test_no_fabricated_hard_gates_field(protocol_validator):
    out = to_protocol_decision(
        _make_decision(AdmissionAction.ALLOW, GovernanceDisposition.NONE),
        PROTOCOL_SCHEMA)
    assert "hard_gates_all_pass" not in out  # SSI contract has no such concept


def test_input_not_mutated():
    decision = _make_decision(AdmissionAction.REVIEW, GovernanceDisposition.REPAIR_REQUIRED,
                              requirements=[_req()])
    before = decision.model_dump_json()
    to_protocol_decision(decision, PROTOCOL_SCHEMA)
    assert decision.model_dump_json() == before  # frozen contract intact
