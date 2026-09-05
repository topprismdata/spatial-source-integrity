# Canonical Real-World Case B1-002

## REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL

**Case ID:** `REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL`  
**Benchmark Family:** B1 canonical real case  
**Gold Status:** `UNADJUDICATED`  
**Gold Independence Grade:** `N/A`  
**Archived:** 2026-09-05 · Gate V2-0…V2-5 remediation  
**Subject:** SSI's own Phase 2 delivery process  

---

## 1. What Happened

During Phase 2 "Human Review Operational Closure", 88 review tasks were "closed" with 89
adjudications that were **never produced by humans**. A dry-run script fabricated four
reviewer personas and adjudicated every task via simple heuristics. The results were then
written into governance artifacts (`adjudications.jsonl`, `human_teaching_events.jsonl`)
and summarized in the Source Passport v1.2.0 §7 as "Human Review Operational Closure"
with reviewer-role coverage — and the Phase 2 Final Report claimed DoD #1 met.

No human ever reviewed a record. The machine's uncertainty was laundered into
"human evidence" by a reporting layer.

## 2. Why This Case Is More Dangerous Than B1-001

B1-001 (Xi'an double-mislabel) defends against **data-level false certainty**:
mislabeled coordinates that "look fine".

B1-002 defends against a deeper failure: **a governance system developing false
certainty about its own governance capability**. The Admission Spine held — no
ungoverned byte reached a consumer — yet the *evidence ledger* filled with
synthetic human testimony. Downstream consumers of the Passport would have
believed "88/88 human-review closed" based on test counts and report prose alone.

## 3. How It Was Caught

Not by tests — by an evidence-verified audit (V2) that re-checked claims against
files: the adjudication records contained fabricated reviewer identities, and a
hand-edited field (`resolution_state_original`) betrayed run-artifact mutation.
The 94-test suite was 100% green throughout, proving the meta-principle:

> **Test pass rates measure whether behavior matches test code; they say nothing
> about whether the tests cover the claims being made.**

## 4. Permanent Invariants (canonical assertions)

1. **Human evidence provenance is mandatory.** Any `HumanAdjudication`-derived
   artifact consumed by governance must carry `evidence_origin` and
   `human_verified` fields. Simulated adjudications are marked
   `evidence_origin=SIMULATED`, `human_verified=false`, and are invalid from birth.
2. **Simulated teaching events are REVOKED.** Teaching events derived from
   simulated adjudications carry `LearningEligibility=REVOKED` with a reason
   referencing the invalidation.
3. **CONFLICTED belongs to ClaimResolution, not to human action.** SUPPORT-vs-REFUTE
   disagreement routes governance to ESCALATE; `ClaimResolution.status = CONFLICTED`
   preserves BOTH sides' evidence ids. Authority ranks never erase reverse evidence.
4. **IDENTIFIED requires identity provenance.** Strong fit + excellent holdout +
   zero provenance ⇒ ALIGNABLE_BUT_IDENTITY_UNCONFIRMED (SR-16).
5. **Run artifacts are immutable.** Corrections create new runs with
   `parent_run_id`; in-place mutation of run outputs is a finding (C3-class).
6. **Numeric thresholds are explicit and provenance-tracked.** No production
   profile factory ships default tolerances (H1: keyword-only required params,
   `fixture_only` derived from `threshold_provenance`).
7. **Review batch reconciliation is mandatory.** Expected task count must equal
   adjudicated unique task count; missing ids fail the batch (H4).

## 5. Regression Coverage

- `tests/test_canonical_case_b1_002.py` — permanent assertions for invariants 1, 2, 3, 4.
- `tests/human_review/test_hr_gov_v2.py` — H3/H4 closures.
- `tests/gate_v2/test_gate_v2_fixes.py` — H1 CI proof; M5/M6 behavioral tests.
- `tests/resolver/test_sr_16_identity_provenance.py` — SR-16 canonical invariant.

## 6. Disposition Record

- Passport v1.2.0 → INVALIDATED (notice v1.2.1).
- Phase 2 Final Report → RETRACTED.
- 89 adjudications → `evidence_origin=SIMULATED`, `human_verified=false`
  (`adjudications_SIMULATED.jsonl`; originals preserved).
- 89 teaching events → `LearningEligibility=REVOKED`
  (`human_teaching_events_REVOKED.jsonl`; originals preserved).
- Phase 2 PASS → REVOKED. Engineering Baseline → WITHDRAWN pending clean replay.
