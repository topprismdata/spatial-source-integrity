"""Ingest & validate exported page adjudications (Review Batch V2, click-to-locate v3).

Interaction contract (v3): the human ONLY clicks where the community really is
(and confirms confidence). The verdict is DERIVED here from her click vs the
data points, using machine-readable rules — never from free text, never typed.

Rejects: unknown reviewer ids, missing click where required, off-menu codes,
SIMULATED-origin records. Reconciles against review_manifest (H4 rule).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
DP02_TOL_M = 200.0        # EXPERIMENTAL_FIXTURE provenance (manifest.thresholds)
ANOMALY_TOL_M = 300.0     # click-vs-raw tolerance for remote-legitimacy calls

# manual codes carry their own governance action
MANUAL_CODE_ACTION = {
    "REF_DOUBT": "ESCALATE",          # doubts the reference parcel itself
    "CANNOT_LOCATE": "UNRESOLVED",    # cannot find it on imagery
    "CANNOT_TELL": "UNRESOLVED",
    "NEED_PRODUCER_INTERVIEW": "UNRESOLVED",
    "NEED_LOCAL_KNOWLEDGE": "ESCALATE",
}

# non-click categories: code -> verdict (claim = "block/insufficient/retire" stance)
DIRECT_CODE_VERDICT = {
    "PRECISION_SUFFICIENT": "REFUTE",
    "PRECISION_INSUFFICIENT": "SUPPORT",
    "SOURCE_TRUNCATION": "SUPPORT",
    "MASTER_MATCH_SUFFICIENT": "SUPPORT",
    "CONTRADICTING_INFO": "REFUTE",
}

# V3.1 "三选一": reviewer picks which plotted point IS the real place; verdict derived.
SELECTED_POINT_OF = {"POINT_AT_RAW": "raw", "POINT_AT_CONVERTED": "converted", "POINT_AT_REF": "ref_parcel"}
POINT_AT_RULES = {
    ("DECISION_BLOCKED", "POINT_AT_RAW"): ("REFUTE", "PICK:raw_is_truth→data was already correct; machine mis-killed"),
    ("DECISION_BLOCKED", "POINT_AT_CONVERTED"): ("REFUTE", "PICK:converted_is_truth→aligned record usable; block lifts"),
    ("DECISION_BLOCKED", "POINT_AT_REF"): ("SUPPORT", "PICK:ref_center_is_truth→both data points off; block maintained"),
    ("EXTREME_ANOMALY", "POINT_AT_RAW"): ("SUPPORT", "PICK:raw_is_truth→legit remote location"),
    ("BLIND_CONTROL", "POINT_AT_RAW"): ("SUPPORT", "PICK:raw_is_truth→usable (blind control)"),
}


def derive_verdict(category: str, rec: Dict[str, Any]) -> Tuple[Optional[str], str, Dict[str, Any]]:
    """Returns (verdict, rule_id, detail); verdict None = not derivable."""
    code = rec.get("rationale_code")
    if code in MANUAL_CODE_ACTION:
        return MANUAL_CODE_ACTION[code], f"MANUAL:{code}", {}
    if code in DIRECT_CODE_VERDICT:
        return DIRECT_CODE_VERDICT[code], f"DIRECT:{code}", {}
    if (category, code) in POINT_AT_RULES:
        v, rule = POINT_AT_RULES[(category, code)]
        return v, rule, {"selected_point": SELECTED_POINT_OF[code]}
    if code != "CLICK_DERIVED":
        return None, f"UNKNOWN_CODE:{code}", {}
    d = rec.get("measured_dists_m") or {}
    d_raw, d_conv, d_ref = d.get("raw"), d.get("converted"), d.get("ref_parcel")
    if d_raw is None and d_conv is None:
        return None, "CLICK_DERIVED_NO_MEASUREMENT", {}
    if category == "DECISION_BLOCKED":
        if d_conv is not None and d_conv <= DP02_TOL_M:
            return ("REFUTE", "CLICK:converted_within_tolerance→record usable, block false-positive",
                    {"d_conv": d_conv, "d_raw": d_raw, "d_ref": d_ref})
        if d_raw is not None and d_raw <= DP02_TOL_M and (d_conv is None or d_conv > DP02_TOL_M):
            return ("REFUTE", "CLICK:raw_within_tolerance→transform hypothesis hurt, machine mis-killed",
                    {"d_conv": d_conv, "d_raw": d_raw, "d_ref": d_ref})
        return ("SUPPORT", "CLICK:both_data_points_far_from_truth→block maintained",
                {"d_conv": d_conv, "d_raw": d_raw, "d_ref": d_ref})
    if category == "EXTREME_ANOMALY":
        if d_raw is not None and d_raw <= ANOMALY_TOL_M:
            return ("SUPPORT", "CLICK:raw_at_truth→legit remote location", {"d_raw": d_raw})
        return ("REFUTE", "CLICK:raw_far_from_truth→coordinate anomaly", {"d_raw": d_raw})
    if category == "MATCH_DOUBT":
        # one-click blind duel: click vindicates which point?
        md = rec.get("measured_dists_m") or {}
        d_raw_, d_ref_ = md.get("raw"), md.get("ref_parcel")
        if d_ref_ is not None and d_ref_ <= 100 and (d_raw_ or 0) > 300:
            return ("SUPPORT", "CLICK:parcel_at_truth&raw_far→name match OK, SOURCE DATA corrupted",
                    {"d_raw": d_raw_, "d_ref": d_ref_})
        if d_raw_ is not None and d_raw_ <= 100:
            return ("REFUTE", "CLICK:raw_at_truth&parcel_far→our anchor match was wrong",
                    {"d_raw": d_raw_, "d_ref": d_ref_})
        return ("SUPPORT", "CLICK:both_far_or_ambiguous→block maintained, match audit needed",
                {"d_raw": d_raw_, "d_ref": d_ref_})
    if category == "THRESHOLD_EDGE":
        md = rec.get("measured_dists_m") or {}
        d_ref_ = md.get("ref_parcel")
        bd = (rec.get("_belief") or {}).get("d_BD_m")
        if d_ref_ is not None and d_ref_ <= 60 and bd is not None:
            # truth ≈ parcel; converted-point residual = d_BD_m vs 200m tolerance
            if bd <= DP02_TOL_M:
                return ("REFUTE", f"CLICK:parcel_at_truth&BDresidual {bd}m≤200→post-transform usable",
                        {"d_BD_m": bd, "d_ref": d_ref_})
            return ("SUPPORT", f"CLICK:parcel_at_truth&BDresidual {bd}m>200→block holds",
                    {"d_BD_m": bd, "d_ref": d_ref_})
        return ("UNRESOLVED", "CLICK:insufficient geometry for threshold call", {"d_ref": d_ref_})
    if category == "BLIND_CONTROL":
        if d_raw is not None and d_raw <= DP02_TOL_M:
            return ("SUPPORT", "CLICK:raw_at_truth→usable (blind control)", {"d_raw": d_raw})
        return ("REFUTE", "CLICK:raw_off_truth→not usable (blind control)", {"d_raw": d_raw})
    return None, f"CLICK_UNMAPPED_CATEGORY:{category}", {}


def ingest_export(
    payload: Dict[str, Any],
    manifest: Dict[str, Any],
    tasks_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    roster_ids = {r["reviewer_id"] for r in manifest.get("roster", [])}
    expected: List[str] = list(manifest.get("expected_task_ids", sorted(tasks_by_id.keys())))
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for rec in payload.get("adjudications", []):
        rid = str(rec.get("reviewer_id", ""))
        errs: List[str] = []
        task = tasks_by_id.get(rec.get("task_id")) or {}
        cat = task.get("category", rec.get("category", "UNKNOWN"))

        for field in ("task_id", "rationale_code", "confidence", "reviewer_id", "reviewer_role", "adjudicated_at"):
            if field not in rec:
                errs.append(f"missing_field={field}")
        if rid not in roster_ids:
            errs.append(f"unknown_reviewer_id={rid!r}")
        if rec.get("confidence") not in VALID_CONFIDENCE:
            errs.append(f"invalid_confidence={rec.get('confidence')!r}")
        if rec.get("evidence_origin") == "SIMULATED" or rec.get("human_verified") is False:
            errs.append("simulated_record_rejected")
        if "rationale" in rec and str(rec.get("rationale", "")).strip():
            errs.append("free_text_rationale_forbidden")
        if rec.get("verdict") not in (None,) :
            # page must not send verdict in v3 (system-derived); legacy field allowed only w/ code match
            pass
        code = rec.get("rationale_code")
        allowed_opts = task.get("rationale_options") or []
        allowed = {o[0] for o in allowed_opts} if allowed_opts else set()
        if allowed and code not in allowed:
            errs.append(f"rationale_code_not_in_task_options={code!r}")
        # V3.1: choosing one of the plotted points needs no click; only CLICK_DERIVED does.
        if task.get("click_mode") and code == "CLICK_DERIVED":
            if not rec.get("clicked_display"):
                errs.append("click_derived_but_no_click_recorded")
            if "measured_dists_m" not in rec:
                errs.append("click_missing_measurements")

        verdict = rule = None
        detail: Dict[str, Any] = {}
        if not errs:
            rec_for_deriv = {**rec, "_belief": task.get("machine_belief") or {}}
            verdict, rule, detail = derive_verdict(cat, rec_for_deriv)
            if verdict is None:
                errs.append(f"verdict_not_derivable:{rule}")

        if errs:
            rejected.append({"task_id": rec.get("task_id"), "errors": errs})
        else:
            accepted.append({
                **{k: v for k, v in rec.items() if k != "verdict"},
                "verdict": verdict,
                "verdict_rule": rule,
                "rule_detail": detail,
                "human_verified": True,
                "evidence_origin": "REAL_HUMAN_CLICK",
            })

    adjudicated = {r["task_id"] for r in accepted}
    missing = sorted(set(expected) - adjudicated)
    unexpected = sorted(adjudicated - set(expected))
    reconciliation = {
        "expected_task_count": len(expected),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "missing_task_ids": missing,
        "unexpected_task_ids": unexpected,
        "passed": not missing and not unexpected and not rejected,
    }
    return {"accepted": accepted, "rejected": rejected, "reconciliation": reconciliation}


def ingest_file(export_path: Path, manifest_path: Path, tasks_path: Path, out_path: Path) -> Dict[str, Any]:
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    tasks_by_id: Dict[str, Dict[str, Any]] = {}
    if Path(tasks_path).exists():
        tasks_by_id = {t["task_id"]: t for t in json.loads(Path(tasks_path).read_text(encoding="utf-8"))}
    report = ingest_export(payload, manifest, tasks_by_id)
    Path(out_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


# ── confidence update: human label → machine belief delta ──────────────
HYPOTHESIS_ORDER = ["identity", "GCJ-like→WGS84", "BD-like→WGS84"]

def update_machine_confidence(labels: List[Dict[str, Any]], baseline: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Fold accepted human labels into machine confidence (the purpose of labeling).

    labels: accepted ingest records (with machine_belief snapshot in `baseline` by task_id)
    baseline: task_id -> machine_belief dict from tasks.json
    Returns per-hypothesis confirmation stats + dp02 overturn estimate.
    """
    per_hyp = {h: {"confirm_raw": 0, "confirm_conv": 0, "reject_both": 0, "other": 0} for h in HYPOTHESIS_ORDER}
    dp02 = {"machine_allow_human_confirms": 0, "machine_allow_human_rejects": 0,
            "machine_block_human_confirms": 0, "machine_block_human_overturns": 0}
    no_residential_flags = 0
    for lab in labels:
        b = baseline.get(lab["task_id"], {})
        top = b.get("top_hypothesis")
        code = lab.get("rationale_code")
        if top in per_hyp:
            if code == "POINT_AT_RAW":
                per_hyp[top]["confirm_raw"] += 1      # identity of data already correct at this record
            elif code == "POINT_AT_CONVERTED":
                per_hyp[top]["confirm_conv"] += 1     # transform hypothesis validated by human
            elif code in ("POINT_AT_REF", "CLICK_DERIVED"):
                per_hyp[top]["reject_both"] += 1      # both data points off truth at this record
            else:
                per_hyp[top]["other"] += 1
        if code == "REF_NOT_RESIDENTIAL":
            no_residential_flags += 1
        pred = (b.get("machine_prediction") or "")
        human_block = code in ("POINT_AT_REF", "REF_NOT_RESIDENTIAL", "CANNOT_LOCATE")
        if pred.startswith("ALLOW"):
            (dp02.__setitem__("machine_allow_human_rejects", dp02["machine_allow_human_rejects"] + 1)
             if human_block else dp02.__setitem__("machine_allow_human_confirms", dp02["machine_allow_human_confirms"] + 1))
        elif pred.startswith("BLOCK"):
            (dp02.__setitem__("machine_block_human_overturns", dp02["machine_block_human_overturns"] + 1)
             if code in ("POINT_AT_RAW", "POINT_AT_CONVERTED")
             else dp02.__setitem__("machine_block_human_confirms", dp02["machine_block_human_confirms"] + 1))
    n = len(labels)
    def rate(d, a, b):
        tot = d[a] + d[b]
        return round(d[a] / tot, 3) if tot else None
    return {
        "labels_folded": n,
        "per_hypothesis": per_hyp,
        "dp02_policy": {
            **dp02,
            "false_block_rate_est": rate(dp02, "machine_block_human_overturns", "machine_block_human_confirms"),
            "false_allow_rate_est": rate(dp02, "machine_allow_human_rejects", "machine_allow_human_confirms"),
        },
        "source_definition_violations": no_residential_flags,
        "governance_note": "Updates RULE/hypothesis confidence offline; no online model mutation (SSI Phase 2).",
    }
