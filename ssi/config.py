"""Path configuration for SSI tooling.

Private data (raw corpora, run artifacts, external references) lives OUTSIDE
the shipped repository; no absolute paths are hardcoded anywhere. Tools and
tests resolve every artifact through these roots so the public tree runs
green with synthetic fixtures only.

Environment variables:
    SSI_DATA_ROOT     root containing raw/, corpus/, runs/  (default: repo root)
    SSI_REF_ROOT      root holding external reference geojson (default: <repo>/refs)
    SSI_MASTER_CSV    master crawl CSV consumed by tools/split_master_by_city.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("SSI_DATA_ROOT", str(REPO_ROOT)))          # raw/, corpus/, runs/
REF_ROOT = Path(os.environ.get("SSI_REF_ROOT", str(REPO_ROOT / "refs")))  # external reference geojson

_PLACEHOLDER_ROSTER = [
    {"reviewer_id": "reviewer_a", "display": "Reviewer A", "role": "DATA_STEWARD"},
    {"reviewer_id": "reviewer_b", "display": "Reviewer B", "role": "DOMAIN_EXPERT"},
    {"reviewer_id": "reviewer_c", "display": "Reviewer C", "role": "REVIEWER"},
]


def load_review_roster(run_dir: str | Path) -> list[dict]:
    """Reviewer roster for a review-pack run.

    Real rosters are private (``runs/<run>/review_roster.json`` — not shipped);
    the placeholder fallback keeps the generators runnable on synthetic data
    without embedding identities in published code.
    """
    p = Path(run_dir) / "review_roster.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return [dict(r) for r in _PLACEHOLDER_ROSTER]
