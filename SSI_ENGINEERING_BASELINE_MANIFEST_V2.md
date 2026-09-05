# SSI Engineering Baseline Manifest — v2.0 (Remediation Complete, Candidate)

**Status:** BASELINE CANDIDATE v2.0 — awaiting boss re-certification  
**Binding Commit:** `b8e58b7` (exact SHA for this candidate; supersedes 34eef60/6eb2279 claims)  
**Date:** 2026-09-05  
**Supersedes:** v1.0 manifest (WITHDRAWN after V2 audit findings C1–C3)

---

## 0. Certification status (honest)

| Layer | Status |
|---|---|
| Architecture Design v1 core principles | **VALID** |
| V1 self-review / completion conclusions | **RETRACTED** |
| Phase 0 Admission Spine | **PASS** |
| Phase 1 Core | **PASS** |
| Phase 1R | **REVALIDATION REQUIRED** (replay `run_xian_002_v2_replay` complete; boss re-review pending) |
| Phase 2 Human Evidence | **NOT VALIDATED** (real human review still pending — Review Batch V2 defined, awaiting real reviewers) |
| Phase 2 PASS | **REVOKED** |
| Engineering Baseline | **WITHDRAWN → CANDIDATE v2.0 pending boss re-certification** |
| Governing audit | **V2 (`SSI_TRIPLE_SELF_REVIEW_V2.md`)** + Gates V2-0…V2-5 executed |

---

## 1. Architecture baseline
`Spatial Source Integrity v1.0 Normative Design Package` (unchanged) + 
`SPEC_ADDENDUM_CONFORMANCE_CLAIMS.md` (new, Gate V2): conformance claims require
executable traceability — reports/test-counts alone are void.

## 2. Engineering commit
`b8e58b7` — includes all Gate V2-0…V2-5 remediation code, tests, and artifacts.

## 3. Conformance tests (now 108)
94 baseline tests + 14 new: SR-16 identity-provenance invariant (2), HR Gov V2 H3/H4 (4),
H1 CI no-fallback proof (2), M5 behavioral RW-06/08 (2), M6 D09↔Resolver dependency (1),
B1-002 canonical assertions (4 minus overlap → net +14). All 108 pass.

## 4. Real-world evidence
- `run_xian_002_v2_replay` (RunArtifact ACTIVE, parent=xian_seed_001, commit `b8e58b7`):
  - Resolver: `ALIGNABLE_BUT_IDENTITY_UNCONFIRMED`, encoding family BD_LIKE_STRONGLY_SUPPORTED,
    reference identity UNCONFIRMED (code now enforces; SR-16 locks it).
  - Gates computed on BOTH states from D08 residuals:
    RAW DP-01 934/3, DP-02 0/937 · SHADOW DP-01 934/3, DP-02 904/33.
- Review queue: OPEN (88 tasks carried forward, 0 human adjudications — honest).
- Teaching events: all 89 REVOKED (simulation invalidation AMEND-V2-0-001).
- Raw corpus SHA-256 unchanged.

## 5. Explicitly unsupported (unchanged + additions)
DP-03 Fine Geofence NOT VALIDATED; entrance routing NOT VALIDATED; 92.5% unanchored
records NOT individually validated; file1 OUT_OF_CANDIDATE_SET; nationwide completeness
NOT EVALUATED; cross-city extrapolation PROHIBITED; **any claim of human-review closure
PROHIBITED until real reviewers execute Review Batch V2** (identity/role/evidence-bundle/
visibility/timestamps required per protocol).

## 6. Canonical cases (mandatory regression)
- B1-001 `REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES` (gold_status=UNADJUDICATED)
- B1-002 `REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL`
