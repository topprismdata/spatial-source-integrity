# SSI Spec Addendum — Conformance Claims Principle (Gate V2)

**Status:** Normative (ratified 2026-09-05, Gate V2 remediation)  
**Binding on:** All future SSI phases, releases, and certification claims.  
**Trigger case:** B1-002 `REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL`

---

## Principle: Conformance Claims Require Executable Traceability

> **No claim of implementation conformance may be accepted solely from generated
> reports or test counts; every critical conformance claim must be traceable to
> executable behavior, immutable run artifacts, and the exact implementation path
> that enforces it.**
>
> 任何“已符合规范”的工程结论，不得仅由报告或测试数量证明；关键合规声明必须能
> 追溯到实际执行行为、不可变运行工件以及真正实施该约束的代码路径。

## Rules

1. **四层证据（4-layer evidence）.** Certification of any phase requires ALL of:
   1. Behavioral tests exercising the enforcing code path;
   2. Immutable replay artifacts (RunArtifact chain, content-hashed);
   3. File/line contract audit (claims traced to the exact enforcing code);
   4. Real human evidence wherever human evidence is claimed
      (`evidence_origin != SIMULATED`, `human_verified = true`, real identity/role/timestamp).
2. **Simulated ≠ human.** Synthetic adjudications may exercise software but earn zero
   governance credit. They must be marked `evidence_origin=SIMULATED`,
   `human_verified=false` at birth and are ineligible for training or reporting.
3. **Run artifacts are append-only.** Corrections create a successor run
   (`parent_run_id`); in-place edits to an ACTIVE run's outputs are a CRITICAL finding.
4. **Code is the source of truth for semantics.** Normative downgrades (e.g.,
   IDENTIFIED → ALIGNABLE_BUT_IDENTITY_UNCONFIRMED) must land in enforcing code with
   a behavioral regression test in the same change; report-only downgrades are invalid.
5. **Report-only claims are void.** "94 tests passed" certifies only the behaviors
   those tests encode. Any conformance narrative exceeding test coverage is void and
   is treated as a B1-002-class finding.

## Permanent regression cases

- **B1-001** `REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES`
  — data-level false certainty (labels/fit/identity conflation).
- **B1-002** `REAL_SSI_001_SIMULATED_HUMAN_EVIDENCE_MISREPRESENTED_AS_REAL`
  — governance-level false certainty (simulated evidence presented as real).

Both must remain green in every future CI run.
