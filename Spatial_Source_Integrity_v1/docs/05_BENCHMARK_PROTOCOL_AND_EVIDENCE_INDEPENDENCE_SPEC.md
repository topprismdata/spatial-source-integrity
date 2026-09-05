# Benchmark Protocol & Evidence Independence Specification

**Status:** Normative v1 packaged edition

## 1. Purpose

SSI benchmark must prevent:
- train/test leakage;
- entity/source/pipeline leakage;
- reference circularity;
- human adjudication leakage;
- dependent evidence being counted as independent;
- anomaly-enriched samples being reported as deployment prevalence;
- sampled validation becoming record-level admission evidence.

Evaluation must separately answer:
1. Detection — did we notice the problem?
2. Diagnosis — did we identify the right failure mechanism?
3. Admission — did Gate act correctly for the DecisionProfile?
4. Generalization — does it transfer across source/city/time/pipeline?

## 2. Benchmark is a governed versioned asset

Each BenchmarkRelease records:
- ID/version;
- source/city/provider/time/geometry scope;
- B0–B5 sets;
- protocol version;
- Gold policy;
- evidence-independence policy;
- freeze/release time;
- allowed/prohibited uses.

Primary endpoints and split rules freeze before detector tuning.

## 3. B0 — Paired Mutation

Use `(R, R')` with a known mutation. This proves response to a controlled change; it does not prove `R` is universal ground truth.

Mutation families:
- axis/representation changes;
- scale/decimal changes;
- leading-digit/digit corruption;
- sign/field shifts;
- known transform families;
- fallback/default coordinates;
- city/district semantic swaps;
- mixed pipeline mutations.

Include subtle, moderate, severe and catastrophic mutations.

B0 does not estimate deployment error rate.

## 4. B1 — Adjudicated Real Cases

Every real case requires:
- claim under review;
- label;
- evidence bundle;
- evidence usage roles;
- source dependency state;
- adjudicator;
- method;
- temporal/geographic scope;
- Gold independence grade;
- limitations.

“Human confirmed” alone is insufficient.

## 5. Gold Independence Grade

- G0 — synthetic relation only
- G1 — single-source adjudicated
- G2 — multi-source, dependency unknown
- G3 — independently sourced evidence
- G4 — authoritative or field verified for the specific claim

Grade is not a probability and is always claim-specific.

## 6. B2 — Stratified Gold

Use two streams:

### Population-representative
Supports deployment-oriented estimates.

### Risk-enriched
Covers rare/severe/boundary/conflict/unknown/mixed-pipeline cases.

Never mix both into one unqualified rate.

Stratify by relevant dimensions:
- provider;
- city/region;
- batch/time;
- coordinate precision family;
- urban/suburban context;
- boundary proximity;
- pipeline family;
- anomaly family;
- reference availability;
- metadata quality.

## 7. B3 — Blind Holdout

Blind cases are hidden from:
- detector design;
- threshold tuning;
- prompt/model selection;
- rule construction.

Once diagnostic labels are revealed, that release is no longer a true blind set.

## 8. B4 — Transfer

Evaluate across:
- city;
- provider;
- source format;
- time;
- pipeline;
- region.

Report the transfer envelope. Never extrapolate “tested in five cities” to universal nationwide capability.

## 9. B5 — Reference Failure & Dependency

Deliberately test:
- stale reference;
- incorrect reference;
- low-resolution reference;
- shared upstream;
- conflicting independent reference;
- temporal boundary mismatch;
- semantic-scope mismatch;
- wrong declared CRS.

Correct system behavior may be UNRESOLVED / CONFLICTED / REVIEW / BLOCK, not “pick the highest priority source”.

## 10. EvidenceUsage role

Evidence role is contextual:
- CANDIDATE_GENERATION
- CANDIDATE_FITTING
- CANDIDATE_VALIDATION
- GOLD_ADJUDICATION
- BENCHMARK_SCORING

Same upstream evidence used across roles must be disclosed.

## 11. Evidence dependency

- VERIFIED_INDEPENDENT
- KNOWN_DEPENDENT
- DEPENDENCY_UNKNOWN

Unknown never counts as verified independent.

Agreement ≠ independence.

## 12. Candidate fitting vs validation

Fit/select on one anchor/evidence set; validate on held-out evidence.

For spatial reference/alignment, holdout must account for spatial and pipeline correlation, not just random rows:
- spatial blocks;
- cities;
- batches;
- source pipelines.

Same upstream provider across fit/validation supports provider-family generalization, not independent reality validation.

## 13. Gold adjudication

High-value Gold flow:
`define Claim → prepare evidence → hide system prediction where feasible → human adjudication → dependency assessment → freeze label → score`.

Reviewer disagreement may produce DISPUTED_GOLD / UNRESOLVED. Benchmark need not force binary truth.

Record prediction visibility because non-blind operational review is weaker independent evidence than prediction-blind Gold adjudication.

## 14. Task-layer labels

Do not use one `bad` label.

A case can have:
- detector truth;
- diagnosis truth;
- claim resolution truth;
- profile-specific admission truth.

Example:
- coordinate corruption = true;
- corruption family = leading digit loss;
- city claim = supported after governed repair;
- CityAnalytics = allow;
- VisitPlanning = block before repair.

## 15. Core metrics

### Detector
Precision, Recall, Specificity/FPR, Abstention Rate, Coverage, Catastrophic Error Recall.

### Resolution
Resolution Accuracy, Conflict Recall, False Certainty Rate.

### CRS/reference
Identity Accuracy, Alignment Accuracy, Out-of-Set Rejection, Abstention Quality, Mixed Pipeline Recall.

### Admission
FTR, UER, FBR, URR, overall Review Rate, Incorrect Limitation Rate, Unstable Decision Allow Rate, Missing Assessment Allow Rate, Consumer Bypass Events.

### Repair
Approved Repair Precision, False Repair Rate, Repair Coverage, Revocation Rate.

## 16. FTR/UER/FBR/URR

For profile p:

`FTR_p = unfit allowed / all allowed`

`UER_p = unfit allowed / all truly unfit`

`FBR_p = fit blocked / all truly fit`

`URR_p = fit unnecessarily reviewed / all truly fit`

Report confidence intervals/upper bounds and the target population.

Zero observed failures must be reported as `0/N observed` plus an uncertainty bound, not “zero production risk”.

## 17. Coverage and sampling

Every benchmark/evaluation must record:
- ObservedScope;
- InferenceScope;
- EvaluationCoverageManifest;
- sampling design;
- representativity;
- uncertainty.

A challenge set is not a deployment prevalence estimate.

## 18. Cluster dependence

Spatial/source rows are not i.i.d. by default. Report record count plus effective structure:
- providers;
- batches;
- cities;
- pipeline families;
- time periods.

For pipeline faults report both record-level and batch/pipeline-level performance.

## 19. Leakage taxonomy

- L1 Record leakage
- L2 Entity leakage
- L3 Source/pipeline leakage
- L4 Reference leakage
- L5 Human-adjudication leakage

Reference leakage is particularly serious for SSI.

## 20. Benchmark maturity

- E0 synthetic only
- E1 real cases
- E2 stratified internal Gold
- E3 blind
- E4 transfer
- E5 adversarial reference robustness

Capability claims cannot exceed evidence maturity and transfer envelope.

## 21. commercial listing dataset role

commercial listing dataset is `Real-World Seed Corpus #1`, not the universe of SSI. It is useful for Point-source China community data with uncertain coordinate lineage, but transfer requires other providers/cities/times/source types.

## 22. Architecture-level benchmark invariants

Failures include:
- missing Gate but consumer receives data;
- blocked/review item enters production snapshot;
- UsageLimit lost;
- revoked snapshot consumed;
- consumer recomputes `is_safe`;
- dependent references counted as independent;
- sample-only evidence masquerades as individual evaluation;
- subject outside CoverageManifest treated as clean.

## 23. Reporting template

Include:
1. benchmark release;
2. scope;
3. evidence maturity;
4. sampling;
5. Gold independence distribution;
6. source/city/batch composition;
7. detector results;
8. resolution results;
9. Gate results by profile;
10. FTR/UER/FBR/URR;
11. review burden;
12. transfer;
13. reference-failure results;
14. confidence/statistical limitations;
15. known limitations;
16. unsupported claims.

## 24. Principle

> No independent evidence → no claim of independent validation. No representative sample → no deployment-rate claim. No real Gate enforcement → no claim of safe decision consumption.
