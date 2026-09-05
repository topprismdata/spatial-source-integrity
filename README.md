<p align="center">
  <img src="https://raw.githubusercontent.com/topprismdata/.github/main/assets/brand/topprism-repo-header.png" alt="TopPrism" width="640">
</p>

# Spatial Source Integrity (SSI)

> **Language / 语言:** English primary · 中文概览如下。

> ### Trust no label. Verify every coordinate.
> Every external spatial dataset carries a story — "this is WGS84", "this is accurate", "this is the same community as last month". Half of those stories are wrong, and the wrong ones look perfectly normal until a decision depends on them. **SSI is the gate that catches them first**: it interrogates the data, quantifies the doubt, and hands you a verdict with a full evidence chain and a human confidence ledger — *before* the bad record reaches your model, your map, or your P&L.

`FAIL-CLOSED ADMISSION` · `ISO 19157-1 GROUNDED` · `H = (C, R, E, K) REFERENCE RESOLUTION` · `EVIDENCE BEFORE TRUST` · `EVALUATION-ONLY` · `MIT`

> **Core Question:** *Can externally sourced spatial data — its declared coordinate reference, positional accuracy, entity identity, and mixed production lineage — actually be consumed by business decisions? And is every verdict backed by traceable evidence plus an explicit human confidence ledger?*

**Spatial Source Integrity is TopPrism's governed spatial data-quality assessment engine** — the admission gate between raw external data and business consumption. It finds what vendors won't tell you: mislabeled coordinate systems, synthetic precision fingerprints, identity doubts, mixed production pipelines. Human feedback exists for exactly one purpose: to increase or calibrate the machine's confidence in its own conclusions. **SSI never repairs data** — it tells you exactly what to trust, and why.

### 中文概览

> **不信标签，只信证据。** 每一份外部空间数据进决策之前，先过 SSI 这道门：坐标声明是否可信、精度是真还是"造"出来的、同名小区是不是同一个小区——机器发现问题 → 量化 → 出结论，每一条结论都有可追溯的证据链和人工信心台账。**不做数据修复、不做坐标变换交付、不替业务定阈值**；只告诉你：什么能用，为什么。本仓库只含代码与规范文档，不含任何商业数据。

---

## 1. Position in the TopPrism Decision OS

SSI is the **evaluation spine** in front of every externally sourced spatial dataset. It produces *verdicts*, not data; downstream decision engines consume the verdict artifact, never a "repaired" dataset.

```
 External Source            Machine Reasoning                 Governed Output
 ┌──────────────┐   Evidence   ┌───────────────────────┐      ┌──────────────────────┐
 │ Raw extract  ├─────────────►│ D01–D09 detectors     │      │ Evaluation report    │
 │ + vendor CRS ├─────────────►│ H=(C,R,E,K) resolver  ├─────►│ + confidence ledger  │
 │ declaration  │   Fail-closed│ abstain on conflict   │ Gate │ + admission decision ├─► Decision-specific
 └──────┬───────┘   admission  └───────────┬───────────┘      └──────────┬───────────┘   trusted snapshot
        │                                  │ conflict / abstain          │
        │                                  ▼                             ▼
        │                       ┌────────────────────┐        Immutable publication
        └──────────────────────►│ Human confidence   │        (evaluation verdict only;
          Raw source untouched  │ ledger (map-click, │         no repaired data ever
                                │ option-based)      │         leaves this path)
                                └────────────────────┘
```

Sibling TopPrism repos — [`spatial-decision-intelligence`](https://github.com/topprismdata/spatial-decision-intelligence), [`Territory-IR`](https://github.com/topprismdata/Territory-IR) — consume SSI **verdicts** as upstream grounding.

## 2. What SSI Is NOT (charter, boss-ratified)

These exclusions are binding scope decisions, not missing features:

1. **No repair.** No fix actions are produced, recommended, or scheduled. Repair-governance code (`ssi/repair/`, shadow derived state, RPROP/RAPPROVE ledgers) is *sealed capability* — it sits outside the assessment path and produces no external deliverable.
2. **No coordinate-transformation service.** Transform hypotheses exist solely as *diagnostic evidence* of metadata distortion; converted coordinates are never shipped.
3. **No threshold decisions.** SSI reports deviation distributions and human-adjudicated boundary facts; where the business draws the line stays with the business.
4. **No extrapolation of unlabeled samples.** Coverage claims state exactly what was verified; unverified records stay unverified.
5. **Not a GIS viewer.** Basemaps appear only inside human-review packs, and only to let a reviewer point at ground truth.

## 3. How an Assessment Flows

| Stage | Component | Guarantee |
|---|---|---|
| Evidence intake | `ssi.contracts` / `ssi.adapters` | Raw declaration preserved verbatim; every transform is a derived representation with lineage |
| Machine finding | D01–D09 detectors (`ssi.detectors`) | Each finding quantified; out-of-detection-set ⇒ explicit NOT_EVALUATED, never silence |
| Reference resolution | `ssi.resolver` — hypothesis `H = (C, R, E, K)` | CRS candidate set (C), reference features (R), evidence bundle (E), residual knowledge (K); FIT/HOLDOUT/BLIND discipline; out-of-set segments stay UNRESOLVED |
| Admission gate | `ssi.admission` | Fail-closed: missing evidence ⇒ block; operational alignment alone never grants admission (`GateDecision` required) |
| Human feedback | `ssi.hitl` | Option-based / map-click only; zero free text; identity from frozen roster; verdict *derived by the system* from the reviewer's observation |
| Learning governance | `ssi.learning` | Teaching events carry eligibility; simulated adjudications are born REVOKED and can never enter learning |
| Publication | `ssi.admission.publisher` | Immutable snapshot of the **evaluation verdict**; projections only from admitted claims |

## 4. Engineering Baseline Status (honest, at publication time)

| Track | Status |
|---|---|
| Phase 0 — Admission spine (three-state model, coverage manifests, fail-closed gate, single publisher, consumer audit) | **PASS** |
| Phase 1 — Core detectors + reference resolver | **PASS** |
| Phase 1R — Revalidation replay | **REVALIDATION REQUIRED** (replay executed; certification pending) |
| Phase 2 — Human evidence | **NOT VALIDATED** (pilot review batches executed; closure claims PROHIBITED until certified) |
| Superseded | V1 self-review **RETRACTED**; Phase 2 PASS **REVOKED** (see `SSI_TRIPLE_SELF_REVIEW_V2.md`, `SSI_ENGINEERING_BASELINE_MANIFEST_V2.md`) |

Counter-evidence boundaries are documented, not hidden: dataset-level encoding hypotheses (e.g. "BD-like family") are weak evidence until blind per-record adjudication confirms them; label misdirection on individual review tasks has occurred and is recorded as a canonical case.

## 5. Canonical Lessons (regression-locked)

- **B1-001 — double mislabel + derived coordinates.** Five evidence layers (raw declaration, mathematical relation, production lineage, reference identity, operational alignment) must stay strictly decoupled. Locked by `tests/test_canonical_case_b1_001.py`.
- **B1-002 — governance self-certainty.** Simulated human evidence was once signed off as real; the system now renders such teaching events REVOKED at birth and routes SUPPORT-vs-REFUTE conflicts to ESCALATE with both sides preserved. Locked by `tests/test_canonical_case_b1_002.py`.

## 6. Quick Start

```bash
git clone https://github.com/topprismdata/spatial-source-integrity.git
cd spatial-source-integrity
python3.10 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q          # conformance harness runs green; private-corpus tests skip automatically
```

No dataset is required to run the suite: the shipped tests are self-contained. To run assessment tooling against your own data, set `SSI_DATA_ROOT` / `SSI_REF_ROOT` / `SSI_MASTER_CSV` — see [`docs/DATA.md`](docs/DATA.md).

## 7. Repository Layout

```
ssi/                       engine: contracts, detectors, resolver, admission, hitl, learning
tests/                     conformance harness (EG / MG / DT / DI / DR / SR / RW / HR / HT / RP families + B1 cases)
tools/                     corpus split, review-pack generators, sanitizer build gate
benchmarks/B1/             canonical case files (regression-locked)
Spatial_Source_Integrity_v1/   normative design package (specs, contracts, gate policy)
PROJECT_CHARTER.md         evaluation-only positioning, boss-ratified
docs/DATA.md               data policy + environment variables
```

## 8. License

MIT — see [LICENSE](LICENSE).
