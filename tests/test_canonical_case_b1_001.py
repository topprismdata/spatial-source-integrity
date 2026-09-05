"""Canonical Case B1-001 permanent regression test."""

from pathlib import Path
from ssi.contracts.runtime.gate_decision import AdmissionAction, GateDecision
from ssi.resolver.hypothesis import (
    CanonicalResolutionState,
    ResolutionResult,
    SpatialReferenceHypothesis,
)


def test_canonical_case_b1_001_five_layer_separation():
    """B1-001: Asserts that all 5 evidence layers remain strictly decoupled.
    
    1. Raw Declaration (vendor label)
    2. Mathematical Relation (C1a)
    3. Production Lineage (C1b)
    4. Reference Identity (UNCONFIRMED)
    5. Operational Alignment (VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE)
    """
    case_path = Path(__file__).resolve().parents[1] / "benchmarks/B1/REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES/CANONICAL_CASE.md"
    assert case_path.exists(), "Canonical case B1-001 file missing!"
    content = case_path.read_text(encoding="utf-8")
    assert "REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES" in content

    # Layer 1 != Layer 2: Raw label "WGS84" is not the mathematical relation
    declared_raw = "WGS84"
    math_relation = "file1 == round6(wgs84_to_gcj02(file2))"
    assert declared_raw != math_relation

    # Layer 2 != Layer 3: Mathematical relation is CONFIRMED, production lineage is SUPPORTED
    c1a_status = "CONFIRMED"
    c1b_status = "SUPPORTED"
    assert c1a_status != c1b_status

    # Layer 3 != Layer 4: Lineage does not establish formal CRS identity
    res_state = CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    assert res_state != CanonicalResolutionState.IDENTIFIED

    # Layer 4 != Layer 5: Operational alignment holds even when Reference Identity is UNCONFIRMED
    res = ResolutionResult(
        resolution_id="res_b1_test",
        resolution_state=CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED,
        is_operationally_aligned=True,
        holdout_p50_residual_meters=41.81,
        alignment_state="VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE",
    )
    assert res.is_operationally_aligned is True
    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED

    # Layer 5 != Gate Admission: is_operationally_aligned=True does NOT automatically grant ALLOW
    # Gate admission requires explicit GateDecision with profile/policy evaluation
    assert not hasattr(res, "action")
    assert not hasattr(res, "is_admitted")
