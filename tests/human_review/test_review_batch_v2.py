"""Review Batch V2 / V3 interaction contract tests.

V3 = click-to-locate: the human clicks where the community really is; the
INGEST layer derives the verdict from her click + measurements. Humans never
read coordinates, never type text, never pick SUPPORT/REFUTE themselves.
"""

from pathlib import Path

import pytest

from ssi.config import DATA_ROOT
from ssi.hitl.ingest import derive_verdict, ingest_export

MANIFEST = {
    "batch_id": "review_batch_v2",
    "expected_task_ids": ["T1", "T2"],
    "roster": [
        {"reviewer_id": "reviewer_a", "display": "Steward A", "role": "DATA_STEWARD"},
        {"reviewer_id": "reviewer_b", "display": "Expert B", "role": "DOMAIN_EXPERT"},
    ],
}
TASKS = {
    "T1": {"task_id": "T1", "category": "DECISION_BLOCKED", "click_mode": True,
           "rationale_options": [["CLICK_DERIVED", "x"], ["REF_DOUBT", "y"], ["CANNOT_LOCATE", "z"]]},
    "T2": {"task_id": "T2", "category": "EXTREME_ANOMALY", "click_mode": True,
           "rationale_options": [["CLICK_DERIVED", "x"], ["CANNOT_LOCATE", "z"]]},
}


def _click(**over):
    base = {
        "task_id": "T1", "rationale_code": "CLICK_DERIVED", "confidence": "HIGH",
        "clicked_display": [109.001, 34.260], "measured_dists_m": {"raw": 900, "converted": 35, "ref_parcel": 20},
        "prediction_visibility": "PREDICTION_VISIBLE", "reviewer_id": "reviewer_a",
        "reviewer_role": "DATA_STEWARD", "adjudicated_at": "2026-09-05T11:00:00Z",
        "evidence_bundle_version": "3.0.0",
    }
    base.update(over)
    return base


# ── verdict derivation (the new human-in-the-loop core) ────────

def test_click_converted_near_truth_overrides_dp02_block():
    """蓝点(原值)离真值远、绿点(换算后)近 → 机器不该杀，REFUTE 推翻阻断。"""
    v, rule, _ = derive_verdict("DECISION_BLOCKED", _click())
    assert v == "REFUTE"
    assert "converted_within_tolerance" in rule


def test_click_both_far_keeps_block():
    v, rule, _ = derive_verdict("DECISION_BLOCKED",
        _click(measured_dists_m={"raw": 900, "converted": 850, "ref_parcel": 20}))
    assert v == "SUPPORT"


def test_click_raw_already_correct_transform_hurt():
    v, rule, _ = derive_verdict("DECISION_BLOCKED",
        _click(measured_dists_m={"raw": 60, "converted": 850, "ref_parcel": 20}))
    assert v == "REFUTE"
    assert "transform" in rule


def test_click_anomaly_raw_at_truth_is_legit():
    v, _, _ = derive_verdict("EXTREME_ANOMALY",
        _click(task_id="T2", measured_dists_m={"raw": 120, "converted": 90, "ref_parcel": 400}))
    assert v == "SUPPORT"


def test_click_anomaly_raw_off_truth_is_bad():
    v, _, _ = derive_verdict("EXTREME_ANOMALY",
        _click(task_id="T2", measured_dists_m={"raw": 8000, "converted": 100, "ref_parcel": 400}))
    assert v == "REFUTE"


def test_pick_converted_point_lifts_block():
    v, rule, det = derive_verdict("DECISION_BLOCKED", {"rationale_code": "POINT_AT_CONVERTED"})
    assert v == "REFUTE" and det["selected_point"] == "converted"
    assert "PICK" in rule


def test_pick_ref_center_keeps_block():
    v, _, _ = derive_verdict("DECISION_BLOCKED", {"rationale_code": "POINT_AT_REF"})
    assert v == "SUPPORT"


def test_pick_needs_no_click_record():
    rec = {"task_id": "T1", "rationale_code": "POINT_AT_RAW", "confidence": "HIGH",
           "prediction_visibility": "PREDICTION_VISIBLE", "reviewer_id": "reviewer_a",
           "reviewer_role": "DATA_STEWARD", "adjudicated_at": "2026-09-05T11:30:00Z"}
    tasks = {"T1": {"task_id": "T1", "category": "DECISION_BLOCKED", "click_mode": True,
                    "rationale_options": [["POINT_AT_RAW", "x"], ["CLICK_DERIVED", "y"]]}}
    rep = ingest_export({"adjudications": [rec]}, {**MANIFEST, "expected_task_ids": ["T1"]}, tasks)
    assert len(rep["accepted"]) == 1
    assert rep["accepted"][0]["verdict"] == "REFUTE"


def test_click_derived_still_requires_click():
    rec = _click()
    rec.pop("clicked_display")
    rep = ingest_export({"adjudications": [rec]}, MANIFEST, TASKS)
    assert any("click_derived_but_no_click" in e for e in rep["rejected"][0]["errors"])


def test_manual_codes_carry_governance_action():
    v, _, _ = derive_verdict("DECISION_BLOCKED", _click(rationale_code="CANNOT_LOCATE",
                                                        clicked_display=None, measured_dists_m=None))
    assert v == "UNRESOLVED"
    v2, _, _ = derive_verdict("DECISION_BLOCKED", _click(rationale_code="REF_DOUBT"))
    assert v2 == "ESCALATE"


# ── ingest validation ───────────────────────────────────────────

def test_ingest_accepts_click_record_and_stamps_origin():
    report = ingest_export({"adjudications": [_click()]}, MANIFEST, TASKS)
    assert len(report["accepted"]) == 1
    rec = report["accepted"][0]
    assert rec["verdict"] == "REFUTE"
    assert rec["evidence_origin"] == "REAL_HUMAN_CLICK"
    assert rec["human_verified"] is True


def test_ingest_rejects_click_mode_without_click():
    rec = _click()
    rec.pop("clicked_display"); rec.pop("measured_dists_m")
    report = ingest_export({"adjudications": [rec]}, MANIFEST, TASKS)
    assert report["rejected"]
    assert any("click_derived_but_no_click" in e for e in report["rejected"][0]["errors"])


def test_ingest_rejects_unknown_reviewer_and_simulated():
    r1 = ingest_export({"adjudications": [_click(reviewer_id="ghost")]}, MANIFEST, TASKS)
    assert any("unknown_reviewer_id" in e for e in r1["rejected"][0]["errors"])
    r2 = ingest_export({"adjudications": [_click(evidence_origin="SIMULATED")]}, MANIFEST, TASKS)
    assert any("simulated_record_rejected" in e for e in r2["rejected"][0]["errors"])


def test_ingest_rejects_offmenu_code():
    report = ingest_export({"adjudications": [_click(rationale_code="MADE_UP")]}, MANIFEST, TASKS)
    assert any("rationale_code_not_in_task_options" in e for e in report["rejected"][0]["errors"])


def test_reconciliation_detects_missing_tasks():
    report = ingest_export({"adjudications": [_click()]}, MANIFEST, TASKS)
    assert report["reconciliation"]["missing_task_ids"] == ["T2"]
    assert report["reconciliation"]["passed"] is False


def test_full_batch_passes():
    recs = [_click(), _click(task_id="T2", rationale_code="CANNOT_LOCATE",
                             clicked_display=None, measured_dists_m=None,
                             reviewer_id="reviewer_b", reviewer_role="DOMAIN_EXPERT")]
    report = ingest_export({"adjudications": recs}, MANIFEST, TASKS)
    assert report["reconciliation"]["passed"] is True


@pytest.mark.skipif(not (DATA_ROOT / "runs/xian_seed_001/review_batch_v2").exists(),
                    reason="private run artifacts not shipped with this repo")
def test_generated_pack_v3_files():
    base = DATA_ROOT / "runs/xian_seed_001/review_batch_v2"
    manifest = __import__("json").loads((base / "review_manifest.json").read_text(encoding="utf-8"))
    assert manifest["input_mode"] == "PICK_ONE_OF_THREE_OR_CLICK + OPTION_ONLY_NO_FREE_TEXT"
    assert manifest["expected_task_count"] == 98
    assert manifest["click_mode_count"] == 93
    assert all(r["reviewer_id"] for r in manifest["roster"])
    html = (base / "review_map.html").read_text(encoding="utf-8")
    assert "点一下" in html and "<textarea" not in html and 'type="text"' not in html
    tasks = __import__("json").loads((base / "tasks.json").read_text(encoding="utf-8"))
    clicky = [t for t in tasks if t.get("click_mode")]
    assert clicky, "click-mode tasks must exist"
    assert all(t.get("default_base") == "amap" for t in clicky)   # vector w/ labels, no satellite default
    assert all("真实位置" in t.get("question", "") for t in clicky)  # every pick task asks the same question
    assert not any("卫星" in t.get("question", "") for t in clicky)
    assert not any("SUPPORT = " in t.get("question", "") for t in clicky)
    # v3.1 option sets: pick-one-of-three exists for DP-02; fallback needs click
    dp02 = [t for t in clicky if t["category"] == "DECISION_BLOCKED"]
    codes = {c for t in dp02 for c, _ in [(o[0], o[1]) for o in t["rationale_options"]]}
    assert {"POINT_AT_RAW", "POINT_AT_CONVERTED", "POINT_AT_REF", "CLICK_DERIVED"} <= codes
