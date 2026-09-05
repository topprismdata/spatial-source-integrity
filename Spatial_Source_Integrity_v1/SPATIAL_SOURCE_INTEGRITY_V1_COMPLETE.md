# Spatial Source Integrity v1.0 — Complete Normative Design Set

> This file concatenates the normative package for convenient review. On conflict, the Architecture Baseline / Triple Review section has precedence.


---

<!-- BEGIN 01_SPATIAL_SOURCE_INTEGRITY_V1_BASELINE_TRIPLE_REVIEW.md -->

# Spatial Source Integrity v1.0
# Architecture Baseline — Triple Self-Review & Normative Patch

**Status:** DESIGN BASELINE — READY TO FREEZE  
**Engineering status:** NOT YET ENGINEERING BASELINE  
**Review date:** 2026-09-05

> If this document conflicts with another package document, this document wins.

## 1. Verdict
The architecture passes three independent reviews: standards/facts, cross-document contracts, and adversarial failure review. The design can be frozen. Engineering cannot be frozen until implementation proves non-bypassable admission, subject-level evaluation coverage, sampling boundaries, snapshot lifecycle, and consumer enforcement.

## 2. Core principles
1. Evidence before trust.
2. Shared semantics before local ontology.
3. Raw source immutable.
4. Observation is not reality.
5. Finding is not evidence.
6. Detection is not repair.
7. Repair is not truth.
8. UNKNOWN / CONFLICT / ABSTAIN are valid.
9. Fitness is decision-specific.
10. Global `is_safe` / `is_decision_ready` never authorizes production.
11. Human authority governs ambiguity; human judgment remains provenance-bearing, scoped and revocable evidence.
12. Learning is offline and governed.
13. Gate before publication; publication before consumption.
14. History is never silently rewritten.

## 3. Standards normalization
Use ISO 19157-1:2023 as the geographic-data-quality foundation:
`Evaluation Scope → Quality Measure → Evaluation Method → Measurement Result → Metaquality → Reporting`.

Canonical quality terms: Completeness, Logical Consistency, Positional Accuracy, Temporal Quality, Thematic Accuracy, Metaquality.

Treat ISO 19157-3 as under development until publication; do not freeze project-stage numbers into architecture. Maintain a versioned TopPrism Measure Registry and map later.

Use ISO 19111 and applicable amendments for CRS concepts; pin EPSG dataset and PROJ/resource versions. EPSG/PROJ define/execute known geodetic operations, not arbitrary raw-coordinate forensic inference.

Use ISO 19131 as product-specification/intended-purpose reference; business tolerances are DecisionProfile policy.

Use ISO/TS 19158 only as conditional ongoing supplier/acquisition governance, not core normative basis for one-time off-the-shelf CSV QA.

Use ISO 19160-3 only as an optional Address Quality Profile; ISO 19156 only when the semantics genuinely represent observations/measurements/sampling.

DQV is a W3C Working Group Note for quality metadata vocabulary. PROV-DM and PROV-O are W3C Recommendations. Runtime does not require a triple store.

## 4. Canonical state model
Only three root state levels:
1. **SpatialWorldState** — internal versioned working state; no consumer authority.
2. **DecisionReadyProjection** — subject/candidate representation passed under a specific DecisionProfile/GatePolicy.
3. **TrustedSpatialSnapshot** — collection-level versioned consumer publication artifact.

`TrustedProjection` and ambiguous `TrustedSpatialState` are deprecated canonical terms. `EntityTrustAssessment` may be a view only.

## 5. Remove Gate circularity
GateDecision evaluates:
- subject_ref;
- candidate_spatial_representation_ref;
- evaluation_result_ref;
- versioned profile/policy/consumer context.

Then:
`GateDecision → DecisionReadyProjection`.

## 6. Admission vs governance
AdmissionAction:
- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW
- BLOCK_FOR_PROFILE

GovernanceDisposition:
- NONE
- QUARANTINE_SCOPE
- SUSPEND_SOURCE
- REPAIR_REQUIRED
- INVESTIGATION_REQUIRED

## 7. Claim is mandatory
A shared Claim/Assertion concept is mandatory. Reuse `prism-ontology` if available; otherwise add through ontology governance. SSI must not create a second shared Claim hierarchy.

Entity linking is a claim:
`SourceRecord R refers_to CanonicalEntity E`.

## 8. Canonical evidence DAG
```text
Observation / Measurement / Human Input
                |
             Evidence
                |
         EvidenceRelation
                |
              Claim
                |
         ClaimResolution
           /          \
 QualityFinding   DerivedEstimate
        |
 DecisionImpact
```

EvidenceRelation: SUPPORTS / CONTRADICTS / DOES_NOT_RESOLVE.  
ClaimResolution: SUPPORTED / REFUTED / CONFLICTED / UNRESOLVED.  
FindingStatus: DETECTED / CONFIRMED_ISSUE / DISPUTED / RESOLVED.  
Confidence: LOW / MEDIUM / HIGH.

Severity never determines evidence polarity.

## 9. EvaluationCoverageManifest — P0
Every formal evaluation must prove what was actually covered:
- evaluation / detector execution references;
- eligible scope;
- evaluated scope;
- excluded scope;
- abstained scope;
- sampling scope;
- membership rule/manifest;
- coverage statistics;
- version.

`COMPLETED + zero findings` supports “no detected issue” only for subjects included in evaluated scope.

## 10. Sample evidence boundary — P0
For sampled evaluation, distinguish ObservedScope and InferenceScope.

Record-level admission is legal only if:
1. record-specific evaluation/evidence exists; or
2. DecisionProfile explicitly permits population-level inferential evidence and GatePolicy explicitly accepts its uncertainty.

A passed sample never silently means every record was individually validated.

## 11. Gate version tuple — P0
Bind at least:
- subject state version;
- EvaluationResult version;
- ontology version;
- OperationalProfile version;
- DecisionProfile version;
- GatePolicy version;
- consumer capability version;
- evaluator version.

Reference/detector/model versions should be traceable through EvaluationResult.

## 12. Unique publication authority — P0
One logical **Spatial Admission Publisher** may:
- validate GateDecision;
- validate versions;
- validate CoverageManifest;
- validate UsageLimit compatibility;
- mint DecisionReadyProjection;
- publish TrustedSpatialSnapshot.

Adapters only translate/transport/consume. They never recompute trust or safety.

## 13. Repair normalization — P0
Do not create a new shared truth root `ApprovedDerivedState`.

Approved correction is modeled through:
- existing DerivedEstimate / SpatialRepresentation;
- RepairProposal;
- explicit RepairApproval;
- lifecycle/provenance.

## 14. Learning infrastructure reuse — P0
SSI owns HumanTeachingEvent, LearningEligibility, domain LearningDataset contract, PolicyExperience and spatial benchmark semantics. Reuse TopPrism shared ML/agent training, registry, experiment and promotion infrastructure. Reuse existing entity-resolution capability.

## 15. Human review — P1
Add HumanReviewPolicy for trigger, reviewer role, independent/double review, priority and escalation. Record whether model prediction and evidence bundle were visible. HumanAdjudication is SUPPORT / REFUTE / UNRESOLVED / ESCALATE; repair approval is separate.

## 16. Detector normalizations — P1
D06 core intrinsic scope is peer/source-distribution spatial outlier detection only. Administrative displacement belongs to D05.

D09/Resolver feedback is bounded:
`Preliminary Segmentation → Reference Resolution → Pipeline Validation/Refinement`.
Feedback-loop evidence is not independent evidence.

## 17. Canonical operational metrics
- FTR = Unfit Allowed / All Allowed
- UER = Unfit Allowed / All Truly Unfit
- FBR = Fit Blocked / All Truly Fit
- URR = Fit Unnecessarily Reviewed / All Truly Fit
- overall Review Rate
- False Certainty Rate
- Consumer Bypass Events
- False Repair Rate

## 18. Snapshot status
LifecycleStatus: DRAFT / ACTIVE / SUPERSEDED / EXPIRED / REVOKED / INVALIDATED.  
DeploymentMode: SHADOW / PRODUCTION.  
Only `ACTIVE + PRODUCTION` is production consumable.

For offline/disconnected copies, track revocation reachability and consumption logging coverage; do not claim physical recall unless proven.

## 19. Trust scope
v1 trust roots remain Coordinate, Location, Semantic-Spatial, Source/Provenance. Temporal and completeness remain quality/decision requirements.

Do not claim real-world omission completeness without a justified universe/reference.

## 20. Holdout
CRS/alignment holdouts must account for spatial/pipeline correlation: spatial blocks, city, batch and source pipeline. Random row split alone is insufficient.

## 21. Sparse evidence materialization
Use dense analytical measurements + CoverageManifests + sparse rich Evidence. Rich evidence is materialized for findings, conflicts, human review, Gold/benchmark cases, repairs, Gate-relevant exceptions and audited samples.

## 22. Learning maturity
Required v1: human adjudication/knowledge update, supervised learning, active learning, review prioritization.  
Optional v1+: preference learning, contextual bandit.  
P2: offline constrained RL / next-best-evidence.

RL may optimize evidence acquisition/review routing. It never owns raw mutation, ontology, DecisionProfile requirements, hard Gate constraints, required human approval or publication.

## 23. Canonical benchmark
B0 Paired Mutation  
B1 Adjudicated Real Cases  
B2 Stratified Gold  
B3 Blind Holdout  
B4 Transfer  
B5 Reference Failure & Dependency

Gold independence:
G0 synthetic relation only; G1 single-source adjudicated; G2 multi-source dependency unknown; G3 independently sourced; G4 authoritative/field verified. Grades are Claim-specific.

## 24. Architecture failure conditions
Any of the following is P0:
- consumer gets data without valid GateDecision;
- adapter/consumer mints safe state;
- blocked or REVIEW item enters production snapshot;
- required detector not evaluated but treated as pass;
- sampled evidence silently authorizes unobserved records;
- UsageLimit disappears downstream;
- revoked snapshot remains accepted;
- raw source silently overwritten;
- AI repair changes world truth directly;
- human approval bypasses Gate;
- learned policy bypasses hard constraints;
- dependent evidence counted as verified independent;
- historical snapshot silently rewritten.

## 25. Canonical architecture
```text
SourceAsset
  |
SourceRecordSnapshot
  |
Observation / Claim (incl. EntityLink)
  |
EvaluationPlan
  |
DetectorExecution
  |--------------------|
QualityMeasurement  EvaluationCoverageManifest
  |
Evidence
  |
EvidenceRelation
  |
Claim
  |
ClaimResolution
  |-------------------|
QualityFinding   DerivedEstimate
  |
DecisionImpact
  |-------------------------|
HumanReviewTask        RepairProposal
  |                         |
HumanAdjudication      RepairValidation
                             |
                        RepairApproval
          \                  /
              SpatialWorldState
                     |
            RequirementEvaluation
                     |
             DecisionStability
                     |
                GateDecision
                     |
          DecisionReadyProjection
                     |
       Spatial Admission Publisher
                     |
          TrustedSpatialSnapshot
                     |
                  Consumer
                     |
       SnapshotConsumptionRecord
                     |
             Business Decision
```

## 26. Parallel learning loop
```text
Human Review / Field Outcome / Repair Outcome / Downstream Correction
                         |
                 HumanTeachingEvent
                         |
                  LearningEligibility
                         |
                   LearningDataset
                         |
            Shared ML/Agent Learning Infrastructure
                         |
               Candidate Model / Policy
                         |
                    B0–B5 Evaluation
                         |
                       Shadow
                         |
                 Governance Approval
                         |
                     New Version
```

## 27. Engineering promotion gate
Must prove:
- blocked entity exports 0;
- no GateDecision exports 0;
- ALLOW_WITH_LIMITS enforces limits;
- outside CoverageManifest cannot silently allow;
- sample-only evidence cannot masquerade as individual validation;
- revoked snapshot cannot be newly consumed;
- human correction leaves raw unchanged;
- human review creates new evidence/new GateDecision;
- learned model cannot enter production without benchmark/promotion;
- adapter cannot recompute `is_safe`;
- same entity supports profile-specific readiness;
- one external source/city holdout runs end-to-end.

Only after all pass: **ENGINEERING BASELINE: FREEZE**.

## 28. Final product definition
> **Spatial Source Integrity is TopPrism's governed spatial admission capability for determining whether externally sourced spatial claims, representations and derived corrections are sufficiently supported by evidence to be published to a specific decision consumer under explicit semantic contracts, human governance and versioned decision policies.**

> **Spatial Source Integrity 是 TopPrism 中受治理的空间准入能力：它通过共享语义契约、可追溯证据、人类治理和版本化决策策略，判断外部空间声明、空间表达及其派生修复是否具备足够依据，可以被正式发布给特定业务决策消费者。**

Final capability:
**KNOW / KNOW THAT IT DOES NOT KNOW / ASK THE RIGHT HUMAN / LEARN WITHOUT BREAKING GOVERNANCE.**


<!-- END 01_SPATIAL_SOURCE_INTEGRITY_V1_BASELINE_TRIPLE_REVIEW.md -->

---

<!-- BEGIN 02_CONTRACT_ALIGNMENT_AND_GATE_EXECUTION_SPEC.md -->

# Contract Alignment & Gate Execution Specification

**Status:** Normative v1 packaged edition  
**Conflict rule:** v1 Baseline wins.

## Objective
Align shared ontology, spatial runtime, world-state aggregation and downstream consumption so trust semantics have one owner and admission has one non-bypassable execution path.

`Shared semantics → Evaluation → Decision requirements → GateDecision → DecisionReadyProjection → TrustedSpatialSnapshot → Consumer`

## Ownership layers
**Shared semantic (`prism-ontology`)**: Observation, Evidence, DerivedEstimate, Claim/Assertion, OperationalProfile, generic DecisionProfile, generic provenance, cross-domain UsageLimit candidate.

**SSI**: spatial quality semantics, SpatialDecisionRequirements, coordinate/reference hypotheses, DecisionImpact, GatePolicy, GateDecision, DecisionReadyProjection, TrustedSpatialSnapshot, Passport, spatial HITL/repair workflow semantics.

**Runtime**: DetectorExecution, EvaluationCoverageManifest, temporary candidates/clusters/residuals and evaluation runs.

**Consumer**: translate/transport/consume snapshots only.

## Canonical state grain
- SpatialWorldState: internal working state, no publish authority.
- DecisionReadyProjection: valid profile/policy-specific admitted representation.
- TrustedSpatialSnapshot: consumer-bound collection artifact.

Do not use ambiguous `TrustedSpatialState`; do not use `TrustedProjection` canonically.

## Source records and entity identity
A vendor row may express observations, claims and metadata. It is not automatically one Observation.

Canonical entity identity is not an immutable SourceRecord fact. Model:
`SourceRecordSnapshot → EntityLinkClaim → Evidence → ClaimResolution`.

## Gate contract
GateDecision evaluates source/candidate state, not a future projection.

AdmissionAction:
ALLOW / ALLOW_WITH_LIMITS / REVIEW / BLOCK_FOR_PROFILE.

GovernanceDisposition is separate.

Required version context includes subject state, evaluation, ontology, OperationalProfile, DecisionProfile, GatePolicy, consumer capability and evaluator.

## Fail closed
Block production publication for:
- missing/invalid GateDecision;
- incompatible profile/policy;
- subject outside required CoverageManifest;
- required evaluation NOT_EVALUATED/FAILED when policy requires it;
- expired/revoked state;
- unsupported UsageLimit;
- REVIEW/BLOCK.

## Coverage
Every formal evaluation has EvaluationCoverageManifest:
eligible, evaluated, excluded, abstained, sampled and inferred scopes plus membership semantics and coverage statistics.

No Finding only has meaning for covered subjects under a COMPLETED execution.

## Sampling boundary
Sampling produces population inference, not hidden record-level validation. Unsampled record admission requires either individual evidence or explicit profile/policy permission to rely on inferential evidence.

## Spatial Admission Publisher
Only the publication authority may validate Gate, versions, coverage, dispositions and UsageLimit compatibility, then mint DecisionReadyProjection and publish Snapshot.

Adapters never derive safety.

## Usage limits
ALLOW_WITH_LIMITS restrictions are machine-readable: operation, distance/resolution, attributes, relationships, geography, time and consumer capabilities. An incompatible consumer is blocked.

## Lifecycle binding
Snapshots bind semantic versions, state/evaluation versions, DecisionProfile, GatePolicy, consumer capability, GateDecision and validity window.

## Mandatory regression scenarios
1. profile-blocking issue → export 0;
2. missing Gate → export 0;
3. ALLOW → export;
4. limits enforced;
5. wrong profile version → block;
6. expired decision/snapshot → block;
7. revoked snapshot → block;
8. same entity different profile readiness;
9. adapter cannot reconstruct safety;
10. snapshot replay determinism;
11. subject outside coverage → block/not evaluated;
12. sampled evidence cannot masquerade as individual validation.

## Migration
Inventory → semantic mapping → deprecate global safety authority → Gate/Coverage contracts → DecisionReadyProjection/Snapshot → shadow consumer → fail-closed enforcement → migrate remaining adapters → retire legacy authority.

> **No valid GateDecision → no DecisionReadyProjection → no Snapshot → no Consumer.**


<!-- END 02_CONTRACT_ALIGNMENT_AND_GATE_EXECUTION_SPEC.md -->

---

<!-- BEGIN 03_CONTRACT_OWNERSHIP_MATRIX.md -->

# Contract Ownership & Migration Matrix

**Status:** Normative v1 packaged edition

## Allowed migration actions
REUSE / SPECIALIZE / ADAPT / DEPRECATE / NEW.  
`NEW` requires semantic-gap analysis and an explicit owner.

## Matrix

| Concept | Canonical owner | Action |
|---|---|---|
| Observation | `prism-ontology` | REUSE/ADAPT |
| Evidence | `prism-ontology` | REUSE |
| DerivedEstimate | `prism-ontology` | SPECIALIZE |
| Claim/Assertion | shared ontology governance | REUSE or GOVERNED NEW |
| OperationalProfile | `prism-ontology` | REUSE |
| DecisionProfile | shared decision semantics | REUSE/SPECIALIZE |
| SpatialDecisionRequirements | SSI | NEW spatial specialization |
| SpatialEntity | shared World Model | REUSE |
| SourceRecordSnapshot | ingestion/runtime | NEW LOCAL |
| EntityLink | Claim | REUSE Claim |
| SpatialWorldState | SSI | ADAPT |
| QualityMeasure Registry | SSI | NEW |
| DetectorExecution | SSI runtime | NEW LOCAL |
| EvaluationCoverageManifest | SSI runtime | NEW LOCAL |
| QualityFinding | spatial specialization | REUSE/SPECIALIZE |
| DecisionImpact | SSI | REUSE |
| GatePolicy | SSI | NEW |
| GateDecision | SSI | NEW |
| UsageLimit | shared candidate; SSI namespaced initially | GOVERN |
| DecisionReadyProjection | SSI | NEW |
| TrustedSpatialSnapshot | SSI | NEW |
| HumanReviewTask | SSI workflow | NEW LOCAL |
| HumanAdjudication | evidence-compatible + workflow | ADAPT |
| RepairProposal | SSI | NEW |
| RepairApproval | SSI | NEW |
| Approved repair output | DerivedEstimate/SpatialRepresentation | REUSE |
| Source Passport | SSI projection | NEW |
| Training/MLOps infrastructure | shared TopPrism capability | REUSE |
| Entity-resolution engine | existing TopPrism capability | REUSE |

## Deprecated authority
- `TrustedSpatialState`: ambiguous canonical name, deprecate.
- `TrustedProjection`: canonical rename to DecisionReadyProjection.
- global `entity.is_decision_ready`: informational/legacy only.
- adapter `is_safe`: derived compatibility representation only; cannot be decision logic.

## Observation / Claim discipline
A vendor row can contain several observations/claims. Evidence targets Claims. Entity identity is a versioned/resolvable relationship, not raw input truth.

## Runtime-only concepts
Detector invocations, residual matrices, clustering workspace, temporary candidate states, benchmark split assignments and similar execution artifacts do not become shared ontology unless a real cross-domain requirement emerges.

## Decision semantics
Generic DecisionProfile belongs to shared decision governance. SSI owns SpatialDecisionRequirements such as coordinate, positional, admin, topology/relationship, temporal-spatial and stability requirements.

## Version compatibility
Publishing must be reproducible against ontology, OperationalProfile, DecisionProfile, GatePolicy, source/world state, EvaluationResult, consumer capability and evaluator versions.

## Deprecation rule
DEPRECATE means: no new semantic dependency, no new producer, read-only compatibility allowed, replacement documented, eventual removal after consumer migration.

## Alignment gate
Must prove:
- one Observation semantic root;
- one Evidence root;
- shared Claim semantics;
- no ambiguous trusted-state name;
- no raw WorldState → consumer;
- no adapter-local safety logic;
- no publish without Gate;
- executable UsageLimits;
- evidence targets claims;
- dependency unknown is not independent;
- EntityLink is revisable;
- evaluation coverage is auditable.

> Shared ontology defines meaning; SSI interprets spatial evidence for decisions; Gate authorizes publication; consumers use only published artifacts.


<!-- END 03_CONTRACT_OWNERSHIP_MATRIX.md -->

---

<!-- BEGIN 04_DECISION_PROFILE_AND_GATE_POLICY_SPEC.md -->

# Decision Profile & Gate Policy Specification

**Status:** Normative v1 packaged edition  
**Conflict rule:** v1 Baseline wins.

## 1. Separation of responsibilities

| Object | Question |
|---|---|
| DecisionProfile | What does this business decision require? |
| GatePolicy | How is sufficiency adjudicated? |
| DecisionStability | Would plausible states change the decision? |
| GateDecision | What was the immutable result of this evaluation? |
| UsageLimit | What machine-enforceable restrictions apply? |

These must never collapse into a generic quality/trust score.

## 2. DecisionProfile

A versioned contract for a business decision.

Minimum semantics:
- identity/version/status;
- decision purpose and target consumer;
- required entity/property/relation semantics;
- coordinate/reference requirements;
- positional requirements;
- administrative requirements;
- topology/relationship requirements;
- temporal/freshness requirements;
- unresolved/conflict tolerance;
- risk class;
- required GatePolicy family.

Business tolerances are TopPrism/customer policy, not ISO defaults.

## 3. SpatialDecisionRequirements

Spatial requirements should separately express:
- coordinate/reference identity or alignment requirements;
- positional distribution/tail/gross-error requirements;
- administrative-assignment stability;
- topology / inside-outside / connectivity requirements;
- spatial relationship requirements;
- temporal-spatial validity;
- DecisionStability requirements.

“max_error=100m” alone is insufficient.

## 4. MVP DecisionProfiles

### DP-01 City Analytics
Requires stable city assignment and absence of catastrophic geographic error. Exact fine position may be irrelevant.

### DP-02 Visit Planning
Requires usable point location, stable relevant admin assignment, adequate routing location, no catastrophic corruption and acceptable freshness.

### DP-03 Fine Geofence
Requires high positional adequacy, validated alignment and stable inside/outside result.

These profiles prove fitness-for-use is not global data quality.

## 5. GatePolicy

A versioned policy mapping:
- RequirementEvaluation;
- ClaimResolution;
- QualityFinding;
- DecisionImpact;
- DecisionStability;
- consumer capabilities;

to an AdmissionAction plus optional GovernanceDisposition.

Recommended evaluation order:
1. semantic/version validity;
2. required DetectorExecution and CoverageManifest;
3. higher-scope blocking dispositions;
4. hard blocking conditions;
5. unresolved/conflicted requirements;
6. DecisionStability;
7. quantitative requirements;
8. UsageLimit feasibility;
9. consumer compatibility;
10. final decision.

Required information is fail-closed.

## 6. AdmissionAction

Canonical:
- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW
- BLOCK_FOR_PROFILE

## 7. GovernanceDisposition

Separate:
- NONE
- QUARANTINE_SCOPE
- SUSPEND_SOURCE
- REPAIR_REQUIRED
- INVESTIGATION_REQUIRED

A record may have `BLOCK_FOR_PROFILE` while its batch has `QUARANTINE_SCOPE`.

## 8. RequirementEvaluation

Each requirement returns:
- SATISFIED
- NOT_SATISFIED
- UNRESOLVED
- NOT_APPLICABLE
- NOT_EVALUATED

NOT_APPLICABLE means the requirement does not apply. NOT_EVALUATED means it should have been assessed but was not.

A subject outside required CoverageManifest is NOT_EVALUATED.

## 9. DecisionStability

Let `S*` be the plausible state set that current evidence has not rejected.

For discrete decision function `D`:
`STABLE` iff all `D(s)` for `s ∈ S*` are identical.

For continuous outputs, the profile defines a tolerance over plausible results.

States:
- STABLE
- UNSTABLE
- NOT_EVALUATED
- INSUFFICIENT_STATE_COVERAGE

Stability is scoped:
- city assignment;
- district assignment;
- nearest route;
- geofence membership;
- etc.

Stability is not confidence.

## 10. Unknown/conflict semantics

UNRESOLVED or CONFLICTED is not automatically one global Gate result.

If the unresolved fact does not affect a mandatory decision variable—or all plausible states yield the same decision—the profile may still allow use.

Conversely, a small coordinate uncertainty near a boundary can make a discrete decision UNSTABLE.

## 11. UsageLimit

Must be machine-executable, not prose.

Potential constraints:
- allowed/prohibited operations;
- minimum/maximum resolution;
- minimum safe distance scale;
- attribute restrictions;
- relationship restrictions;
- geographic scope;
- temporal scope;
- required consumer capabilities.

Multiple limits compose by intersection of allowed use.

If consumer cannot enforce a limit, block.

## 12. GateDecision contract

Immutable result binding:
- subject/candidate representation;
- EvaluationResult;
- semantic versions;
- DecisionProfile;
- GatePolicy;
- consumer capability;
- evaluated requirement refs;
- relevant claim/finding/stability refs;
- action;
- UsageLimit refs;
- blocking/unresolved justification;
- evaluator/version;
- evaluated time / expiry.

Evidence or policy changes create a new GateDecision; history is never overwritten.

## 13. Profile vs Policy change

Profile change = business requirement changed.  
Policy change = adjudication method changed.

They require separate versions and governance.

## 14. Sampling

Population-level sampled Measurement can support a decision only when:
- profile explicitly permits inferential evidence;
- GatePolicy defines acceptance;
- representativity and uncertainty are recorded.

It never silently becomes individual record validation.

## 15. Publication condition

Only:
- ALLOW; or
- ALLOW_WITH_LIMITS + compatible consumer

may produce DecisionReadyProjection.

REVIEW and BLOCK_FOR_PROFILE do not enter production snapshots.

## 16. Anti-patterns

Forbidden:
- global severity → global block;
- universal confidence threshold;
- official source always wins;
- no finding → allow;
- coordinate exists → safe;
- CRS identified → safe;
- quality score > N → allow;
- sample passed → every record validated;
- prose-only UsageLimit;
- Detector implementation details embedded in DecisionProfile.

## 17. Metrics

Admission benchmark reports per profile:
- FTR;
- UER;
- FBR;
- URR;
- overall Review Rate;
- Incorrect Limitation Rate;
- Unstable Decision Allow Rate;
- Missing Assessment Allow Rate;
- Consumer Bypass Events.

## 18. Principle

> DecisionProfile says **what is required**; GatePolicy says **how sufficiency is judged**; DecisionStability says **whether uncertainty matters**; GateDecision says **what this evaluation allowed**; UsageLimit makes limited use executable.


<!-- END 04_DECISION_PROFILE_AND_GATE_POLICY_SPEC.md -->

---

<!-- BEGIN 05_BENCHMARK_PROTOCOL_AND_EVIDENCE_INDEPENDENCE_SPEC.md -->

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


<!-- END 05_BENCHMARK_PROTOCOL_AND_EVIDENCE_INDEPENDENCE_SPEC.md -->

---

<!-- BEGIN 06_SPATIAL_REFERENCE_RESOLUTION_SPEC.md -->

# Spatial Reference Resolution Specification

**Status:** Normative v1 packaged edition

## 1. Purpose

Resolve incomplete, wrong, mixed or non-standard coordinate-reference interpretation without turning the component into a “guess an EPSG code” black box.

Separate:
- **Reference Identity** — what reference/representation/encoding did the source actually use?
- **Operational Alignment** — can it be transformed into the target analysis space within a validated error envelope?

Identity may remain unresolved while alignment is operationally usable.

## 2. Core hypothesis

`H = (C, R, E, K)`

- **C** Formal Coordinate Reference
- **R** Coordinate Representation
- **E** Additional provider/regional Encoding/Transform
- **K** Corruption State

These layers must remain separate.

## 3. C — Formal reference

Examples:
- WGS 84 geographic;
- CGCS2000 geographic;
- UTM;
- Gauss-Krüger;
- Web Mercator;
- local/engineering;
- compound/dynamic;
- unknown.

When identified, preserve authority/code or complete definition, coordinate system, datum/reference frame, axes, units, area of use and epoch where relevant.

## 4. R — Representation

Examples:
- axis/order;
- transport-field order;
- units;
- dimensionality;
- longitude/latitude vs latitude/longitude;
- height/epoch representation.

Axis/order ambiguity is a representation hypothesis, not automatically corruption.

Do not silently collapse CRS84 and EPSG:4326 semantics when format/order matters.

## 5. E — Additional encoding

Examples:
- IDENTITY;
- GCJ-like transform family;
- BD-like transform family;
- documented provider transform;
- unknown systematic transform;
- local empirical adjustment.

GCJ/BD-like are not ordinary EPSG CRS peers in the data model. Represent formal reference + additional transform separately.

Do not use a fixed longitude offset as a universal GCJ/BD detector.

## 6. K — Corruption

At minimum:
- NONE;
- MISSING_LEADING_DIGIT;
- DIGIT_DELETION / INSERTION;
- DECIMAL_SHIFT;
- SCALE_ERROR;
- SIGN_ERROR;
- FIELD_SHIFT;
- TRUNCATION;
- DEFAULT_COORDINATE;
- CENTROID_FALLBACK;
- CONSTANT_OFFSET;
- PARSE_ERROR;
- UNKNOWN_CORRUPTION.

`K=NONE` is mandatory to avoid assuming data are broken.

## 7. ResolutionContext

Mandatory context includes:
- declared reference;
- file/format semantics;
- geography hint/expected extent;
- provider/product/source/batch/time;
- geometry/schema/units/dimensions;
- available references and semantic attributes;
- requested alignment target.

Bare coordinates with insufficient context may legitimately return INSUFFICIENT_EVIDENCE.

## 8. Resolution hierarchy

Start:
`Dataset → Source/Batch → Stable Cluster → Feature Exception`.

CRS/reference is usually a source/pipeline property. Per-record CRS guessing is not the primary architecture.

Feature deviations from a strong batch hypothesis are initially treated as feature anomalies unless evidence supports a distinct stable pipeline.

## 9. Pipeline stages

R0 Input interpretation  
R1 Dataset profiling  
R2 Formal CRS candidates  
R3 Representation hypotheses  
R4 Encoding hypotheses  
R5 Corruption hypotheses  
R6 Candidate evaluation  
R7 Out-of-set rejection  
R8 Holdout validation  
R9 Pipeline segmentation/validation  
R10 Operational alignment assessment  
R11 Plausible states handed to DecisionStability

## 10. Candidate generation

Use:
- declared metadata;
- provider metadata;
- range/unit behavior;
- geography/area of use;
- projection family;
- EPSG registry.

PROJ/EPSG define/execute known candidates. TopPrism determines why a candidate is considered and evaluates evidence.

Always retain an out-of-set possibility; do not force a winner.

## 11. Candidate evaluation axes

Evaluate separately:
1. Relative Preference
2. Absolute Adequacy
3. Holdout Generalization
4. Decision Stability impact

Best relative candidate may still be absolutely inadequate.

Example: 300m residual may beat 900m and 2km but still fail a 20m decision requirement.

## 12. Fitting vs validation

Fit/select candidate using one evidence set; validate on held-out evidence.

Holdout design must respect spatial and pipeline correlation.

Evidence from the same upstream provider is not independent even if records differ.

## 13. Resolution states

Canonical:
- IDENTIFIED
- INDISTINGUISHABLE_AT_CURRENT_RESOLUTION
- ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
- OUT_OF_CANDIDATE_SET
- INSUFFICIENT_EVIDENCE

Dataset-level:
- MIXED_REFERENCE_PIPELINES

`WGS84/CGCS2000 compatible` should be expressed as indistinguishable at current evidence resolution, not formal equivalence.

## 14. Mixed pipeline

Mixed pipeline means repeated systematic production mechanisms, not “a few bad rows”.

Evidence may include:
- residual clusters;
- precision families;
- source IDs;
- time/batch;
- schema variants;
- metadata;
- spatial clusters.

Result:
`Dataset=MIXED_REFERENCE_PIPELINES` with segment hypotheses and unresolved segments.

Segmentation requires repeatability/coherence/stability. Clustering output alone does not prove a production pipeline.

## 15. D09 bounded refinement

Avoid circular self-confirmation.

Use:
`Preliminary segmentation → Reference resolution → Pipeline validation/refinement`.

Rounds are bounded and versioned. Evidence generated within the feedback loop is not counted as independent evidence.

## 16. Operational alignment

Alignment contract includes:
- source hypothesis;
- target reference;
- operation chain;
- transformation class: registered / documented provider / empirical;
- validation evidence;
- residual distribution;
- geographic/time validity envelope;
- known limitations;
- versioned resource dependencies.

Empirical alignment never invents formal source CRS identity.

## 17. Residual reporting

Prefer:
- median;
- quantiles;
- RMSE;
- trimmed RMSE;
- gross error rate;
- directional vectors;
- spatial residual pattern.

Mean alone is insufficient.

## 18. Plausible states

Resolver supplies a plausible-state set to DecisionStability. Only candidates passing a minimum absolute plausibility criterion enter that set.

The Resolver never directly outputs AdmissionAction.

## 19. Source preservation

Raw coordinates remain immutable. Every transformed/aligned/repaired coordinate is a derived representation with provenance.

Declared CRS is preserved even if conflicting; resolved reference is derived state.

## 20. Findings

Typical:
- DECLARED_REFERENCE_MISSING
- DECLARED_REFERENCE_CONFLICT
- REPRESENTATION_AMBIGUOUS
- AXIS_INTERPRETATION_CONFLICT
- FORMAL_CRS_UNRESOLVED
- ENCODING_UNRESOLVED
- OUT_OF_CANDIDATE_SET
- MIXED_REFERENCE_PIPELINES
- OPERATIONAL_ALIGNMENT_INADEQUATE
- COORDINATE_CORRUPTION_SUSPECTED/CONFIRMED
- FALLBACK_COORDINATE_SUSPECTED

## 21. Benchmark priorities

Primary:
- False Identity Confirmation;
- Out-of-Set Rejection;
- Operational Alignment Adequacy;
- Mixed Pipeline Recall;
- Abstention Quality;
- transfer degradation;
- reference-failure robustness.

False Identity Confirmation is a core failure because it manufactures certainty.

## 22. MVP cases

Correct declared reference; missing/wrong declaration; axis ambiguity; WGS84/CGCS2000 indistinguishability; GCJ-like; BD-like; missing leading digit; scale error; fallback centroid; mixed pipeline; all candidates poor; alignable identity-unknown; near-boundary instability; reference conflict.

## 23. Principle

> “Best candidate” does not mean “correct”. “Good alignment” does not prove source identity. “Unknown identity” does not imply every business use must be blocked.


<!-- END 06_SPATIAL_REFERENCE_RESOLUTION_SPEC.md -->

---

<!-- BEGIN 07_DETECTOR_REGISTRY_AND_QUALITY_MEASURE_SPEC.md -->

# Detector Registry & Quality Measure Specification

**Status:** Normative v1 packaged edition

## 1. Core separation

| Concept | Meaning |
|---|---|
| QualityMeasure | What is measured? |
| Detector | Which engineering method produces measurements/signals? |
| DetectorExecution | Did this detector actually run successfully? |
| QualityMeasurement | What value/result was measured over what scope? |
| QualityFinding | What governed quality interpretation follows? |
| RequirementEvaluation | Does a decision requirement pass? |

Never collapse these.

## 2. ISO 19157 mapping

Use:
`Evaluation Scope → Measure → Method → Measurement Result → Metaquality → Reporting`.

TopPrism operational Measure Registry sits under ISO 19157 quality concepts and above detector implementations.

ISO quality dimensions are not TopPrism Trust dimensions.

## 3. Evaluation Scope

Possible scopes:
- Dataset;
- SourceAsset;
- Batch;
- Cluster;
- Entity set;
- Entity;
- candidate representation;
- geometry;
- attribute;
- relationship;
- region;
- time window.

A value without scope is not a valid quality result.

## 4. QualityMeasure

Versioned definition includes:
- measure ID/namespace/version;
- name/definition;
- ISO quality mapping;
- applicability;
- numerator/denominator where applicable;
- value type/unit/range;
- evaluation method family;
- reference requirements;
- aggregation semantics;
- interpretation direction;
- limitations;
- governance.

Use TopPrism namespace such as `tp.ssi.*`. Do not pretend custom measures are ISO register identifiers.

## 5. Measure lifecycle

DRAFT / ACTIVE / DEPRECATED / RETIRED.

Formula/semantic changes require new version.

Same friendly name with different denominator is forbidden.

## 6. Detector

A detector is an implementation, not a quality concept.

One detector may implement multiple measures; one measure may have multiple detector implementations.

Detector contract:
- ID/version/maturity;
- purpose;
- measure refs;
- inputs;
- applicable scopes;
- reference dependencies;
- execution family;
- abstention conditions;
- known failure modes;
- benchmark requirements;
- cost class.

Execution families:
- DETERMINISTIC;
- STATISTICAL;
- ML_MODEL;
- EXTERNAL_REFERENCE;
- HYBRID.

Detectors do not output GateAction.

## 7. DetectorExecution

States:
- COMPLETED
- SKIPPED
- ABSTAINED
- FAILED

No Finding is interpretable only when execution is COMPLETED and the subject is covered by EvaluationCoverageManifest.

ABSTAINED is a legitimate boundary-aware result, not a runtime failure.

## 8. EvaluationCoverageManifest

First-class companion to DetectorExecution/QualityEvaluation.

Records:
- eligible/evaluated/excluded/abstained sets;
- sampled ObservedScope;
- inferential scope;
- membership semantics;
- coverage;
- version.

This prevents unexecuted subjects from being silently treated as PASS.

## 9. QualityMeasurement

A concrete Measure result binds:
- Measure/version;
- evaluation scope;
- value/unit;
- method;
- DetectorExecution;
- references;
- measured time;
- uncertainty;
- coverage;
- provenance;
- validity.

Measurement ≠ Finding ≠ Decision.

## 10. EvaluationMethod

Families:
- DIRECT
- INDIRECT
- REFERENCE_BASED
- INTRINSIC
- SAMPLED
- STATISTICAL_INFERENCE
- HUMAN_ADJUDICATED
- HYBRID

Intrinsic and extrinsic/reference-based evidence must remain distinguishable.

## 11. QualityFinding

Finding is a governed interpretation based on one or more measurements/signals/evidence.

Basis:
- DETERMINISTIC_RULE
- QUALITY_MEASUREMENT
- STATISTICAL_SIGNAL
- REFERENCE_COMPARISON
- MULTI_SOURCE_EVIDENCE
- HUMAN_ADJUDICATION

Fields include subject/scope, finding type, quality element, trust influences, measurement/evidence refs, status, severity, confidence, affected claims/projections, limits and provenance.

## 12. Finding semantics

Status:
DETECTED / CONFIRMED_ISSUE / DISPUTED / RESOLVED.

Severity:
INFO / LOW / MEDIUM / HIGH / CRITICAL.

Confidence:
LOW / MEDIUM / HIGH until calibrated probability is proven.

Severity and confidence are orthogonal.

## 13. Threshold layers

Separate:
1. measurement threshold — intrinsic only where inherent to measure;
2. finding threshold — when to create an anomaly interpretation;
3. decision threshold — whether a business profile accepts it.

Detector score must not directly become business safety.

## 14. Denominator and coverage

Every rate defines its denominator. SKIPPED/ABSTAINED/FAILED cannot be silently counted as PASS or FAIL.

Coverage is reported separately.

Example: `99.9% agreement, coverage=20%` is very different from 99.9% over the whole eligible population.

## 15. Metaquality

At least:
- measurement confidence;
- representativity;
- homogeneity;
- reference adequacy;
- evidence independence;
- coverage;
- temporal relevance.

Metaquality describes the quality of the quality evaluation itself.

## 16. DQV mapping

When useful:
- quality dimension → `dqv:Dimension`;
- Measure definition → `dqv:Metric`;
- QualityMeasurement → `dqv:QualityMeasurement`;
- quality metadata collection → `dqv:QualityMetadata`;
- policy where appropriate → `dqv:QualityPolicy`.

DQV is semantic representation; it does not replace ISO 19157.

## 17. Point-first measure families

### Structural
Coordinate presence, numeric parse, dimension consistency, legal representation range, ID uniqueness, exact record duplicates.

### Reference
Declared reference completeness/consistency, candidate absolute fit, holdout alignment residual, hypothesis coverage, mixed pipeline segment measures.

### Location
Admin containment, boundary proximity, intrinsic spatial outlier, gross displacement where reference-based.

### Semantic-spatial
Admin attribute/geometry agreement, address geography agreement, geocode residual, entity-candidate spatial agreement.

### Source/pipeline
Coordinate reuse distribution, cross-region reuse, fallback signals, precision-family heterogeneity, residual cluster structure, batch consistency, metadata consistency.

## 18. EvaluationPlan

Versioned plan declares:
- scope;
- measures;
- detectors;
- references;
- sampling;
- required/optional/conditional status;
- expected coverage.

QualityEvaluationResult contains executions, CoverageManifests, Measurements, Findings, coverage/metaquality summaries and unresolved evaluations.

It is not GateDecision.

## 19. Sparse evidence

At large scale, full rich Evidence per subject/detector is not required.

Use dense measurements + CoverageManifest + sparse Evidence materialization for significant cases. Auditability is retained through replayable source/evaluation/detector/measure/version contracts.

## 20. Mature library reuse

Do not implement geometry kernels/CRS math from scratch. Prefer mature GIS libraries such as GEOS/GDAL/PROJ/PostGIS/DuckDB Spatial where appropriate. TopPrism's unique IP is semantic evaluation, evidence governance, resolution and admission.

## 21. LLM boundary

LLM may assist metadata interpretation, source investigation, review explanation and conflict summarization. It is not the primary deterministic geometry/range/CRS transformation detector and cannot alter Gate state.

## 22. Detector promotion

EXPERIMENTAL → BENCHMARKED → APPROVED → DEPRECATED.

APPROVED requires benchmark evidence, applicability, failure/abstention behavior and governance.

## 23. Principle

> Measure defines **what** is measured; Detector defines **how**; Execution says **whether it ran**; Measurement says **what was observed**; Finding says **what it may mean**; RequirementEvaluation and Gate decide **whether it is usable**.


<!-- END 07_DETECTOR_REGISTRY_AND_QUALITY_MEASURE_SPEC.md -->

---

<!-- BEGIN 08_POINT_SOURCE_DETECTOR_CATALOG_V0.1.md -->

# Point Source Detector Catalog v0.1

**Status:** Normative v1 packaged edition  
**Geometry scope:** Point  
**Source types:** POI / store / community / customer / address point / geocoded record

## 1. Purpose

Use a small, explainable first detector set to prove the full chain:
`Source → Evaluation → Measurement → Finding → Claim Resolution → Human/Repair where needed → DecisionImpact → DecisionStability → Gate`.

Detectors produce evidence/signals, not truth or admission decisions.

## 2. v0.1 detector set

| ID | Detector | Type | Main role |
|---|---|---|---|
| D01 | Coordinate Schema & Parse | deterministic | coordinate structure |
| D02 | Geographic Range & Representation | deterministic | coordinate representation |
| D03 | Coordinate Precision Fingerprint | descriptive/statistical | source fingerprint |
| D04 | Coordinate Reuse & Fallback Signal | hybrid | source/location |
| D05 | Administrative Consistency | reference deterministic | location/semantic |
| D06 | Intrinsic Spatial Outlier | statistical/hybrid | intrinsic location pattern |
| D07 | Declared Spatial Reference Consistency | hybrid | coordinate/source |
| D08 | External Reference Residual | reference-based | coordinate/location |
| D09 | Batch & Pipeline Consistency | statistical/hybrid | source pipeline |
| D10 | Semantic-Spatial Consistency | hybrid | semantic/location |

Spatial Reference Resolver is not an 11th detector; it consumes multiple detector outputs.

## 3. Common contract

Every detector defines:
- identity/version/maturity;
- purpose;
- measure refs;
- applicable scope;
- required/optional inputs;
- reference dependencies;
- execution type;
- abstention conditions;
- measurements/signals/findings/evidence outputs;
- known false-positive/false-negative cases;
- dependencies;
- B0/B1/B5 mapping.

Execution states: COMPLETED / SKIPPED / ABSTAINED / FAILED.

## 4. D01 — Coordinate Schema & Parse

Measures:
- coordinate field presence;
- numeric parse rate;
- dimension/cardinality consistency.

Findings:
- field missing;
- parse failure;
- dimension inconsistent;
- representation mapping suspected.

May abstain when coordinate-field semantics cannot be identified.

DMS-like text failing decimal parsing is not automatically invalid coordinate data.

B0: blanks, non-numeric, locale separator, field shift, dimension mutation.

## 5. D02 — Geographic Range & Representation

Measures:
- legal range under a representation;
- representation compatibility;
- axis interpretation compatibility.

Findings:
- value outside representation range;
- representation ambiguous;
- axis interpretation conflict;
- unit/scale interpretation suspected.

Global coordinate-range validity does not imply correct location. A wrong but globally legal point can pass D02.

B0: axis swap, range violation, degree/radian or scale-like mutation.

## 6. D03 — Coordinate Precision Fingerprint

Measures:
- decimal/significant-digit distributions;
- precision family structure/entropy;
- batch precision consistency.

Primarily descriptive.

Findings only with evidence:
- precision pipeline heterogeneity;
- suspected precision degradation.

Never interpret more decimal places as greater positional accuracy.

B0: rounding/precision-family injection.  
B5 counterexample: many decimals + poor reference accuracy.

## 7. D04 — Coordinate Reuse & Fallback Signal

Measures:
- reuse frequency distribution;
- cross-city/district reuse;
- semantic diversity at shared coordinate;
- known centroid match;
- source concentration.

Findings:
- high reuse;
- cross-region reuse;
- fallback suspected;
- known centroid fallback suspected.

Legitimate counterexamples must be benchmarked:
- mall centroid;
- community centroid;
- shared office entrance.

Duplicate coordinate ≠ error.

## 8. D05 — Administrative Consistency

Reference-based deterministic spatial operations; reference suitability remains metaquality/evidence governance.

Measures:
- country/province/city/district containment agreement;
- admin hierarchy consistency;
- boundary-proximity distance.

Findings:
- country/province/city/district conflict;
- admin hierarchy conflict;
- near-boundary ambiguity.

Bind boundary version/time. Abstain when admin name/reference/time is unresolved.

B5 includes stale/historical/conflicting admin boundaries.

## 9. D06 — Intrinsic Spatial Outlier

**Final v1 normalization:** D06 core-intrinsic logic must not require an administrative reference.

Measures:
- distance/isolation relative to robust source/batch peer distribution;
- intrinsic cluster/outlier scores;
- source-distribution regional outlier rates.

Findings:
- intrinsic spatial outlier;
- source-distribution outlier.

Administrative polygon displacement belongs to D05.

Peer outlier ≠ confirmed location error; legitimate remote/new-development locations exist.

## 10. D07 — Declared Spatial Reference Consistency

Measures:
- declaration completeness/parseability;
- area-of-use compatibility;
- representation compatibility;
- evidence consistency.

Findings:
- declaration missing/invalid;
- area conflict;
- representation conflict;
- evidence conflict.

Declared metadata is evidence, not truth. D07 does not identify the replacement CRS; it hands conflicts to Resolver.

## 11. D08 — External Reference Residual

Prerequisite: a sufficiently supported entity/reference match.

Measures:
- matched-reference distance;
- residual vector/distribution;
- held-out residual;
- gross residual rate;
- match coverage.

Findings:
- positional residual elevated;
- systematic residual;
- reference match ambiguous;
- holdout alignment inadequate.

Always preserve match ambiguity and reference feature-definition differences (entrance vs centroid vs sales office).

Fit and held-out residuals are separate.

## 12. D09 — Batch & Pipeline Consistency

Consumes precision, residuals, metadata, reuse, source IDs, time/batch and schema variants.

Measures:
- family heterogeneity;
- residual cluster structure;
- metadata/precision cluster coherence;
- change-point signal;
- candidate pipeline stability.

Findings:
- source pipeline heterogeneity;
- mixed reference pipeline suspected;
- pipeline change point;
- unexplained batch shift.

Clustering ≠ pipeline truth.

Final bounded interaction:
`Phase A preliminary segmentation → Resolver → Phase B validation/refinement`.
No unbounded self-confirming loop.

## 13. D10 — Semantic-Spatial Consistency

MVP relations:
- city ↔ coordinate;
- district ↔ coordinate;
- address geography ↔ coordinate;
- resolved entity candidate ↔ coordinate.

Measures:
- admin attribute agreement;
- address geography agreement;
- geocode residual;
- entity-candidate spatial agreement;
- semantic-spatial conflict count.

Reuse existing TopPrism entity-resolution capability. Similar name ≠ same entity.

May abstain when address/entity candidate resolution is insufficient.

## 14. Dependency graph

Conceptually:
```text
D01 → D02
       |
       +→ D03 → D04
       +→ D07
       +→ D05
       +→ D06
D05/D07 → D08
D05/D08/entity-resolution → D10
D03/D04/D06/D07/D08 → D09 Phase A/B
D02/D03/D05/D07/D08/D09/D10 → Spatial Reference Resolver
```

Runtime may parallelize; this expresses semantic dependency, not threads.

## 15. Intrinsic vs reference-enhanced

### Core intrinsic
D01, D02, D03, D04, D06, D09-preliminary.

### Reference-enhanced
D05, D07, D08, D10 plus Resolver/reference validation.

Do not label intrinsic signal as externally validated. Do not treat external reference as truth.

## 16. Sampling / expensive references

External API and human review are not default per-record operations for hundreds of thousands of points.

Use:
- versioned batch reference datasets where feasible;
- representative samples;
- risk-enriched samples;
- review queues.

Always record sample design, coverage and inference scope.

## 17. Finding scope

Dataset/batch findings remain dataset/batch findings. Do not duplicate them onto every record.

Higher-scope GovernanceDisposition may still block child publication.

## 18. Detector promotion

Initially EXPERIMENTAL.  
BENCHMARKED requires B0 + relevant real cases + false-positive cases.  
APPROVED requires blind evidence, applicability and controlled failure/abstention behavior; high-risk mandatory detectors should include transfer/reference-failure evidence.

## 19. Architecture cases

Must cover:
- fields present but location catastrophically wrong;
- legal range but wrong city;
- legitimate repeated mall centroid;
- wrong reference source;
- declared CRS correct + bad reference match;
- declared CRS wrong + systematic encoding;
- mixed batch;
- missing reference → ABSTAIN;
- same measurement → different profile Gate;
- multiple detectors sharing one upstream reference not independent.

## 20. Principle

> A Detector is a source of auditable measurements/evidence. It does not own truth, repair authority or business admission.


<!-- END 08_POINT_SOURCE_DETECTOR_CATALOG_V0.1.md -->

---

<!-- BEGIN 09_POINT_SOURCE_QUALITY_EVALUATION_PLAN_V0.1.md -->

# Point Source Quality Evaluation Plan v0.1

**Status:** Normative v1 packaged edition

## 1. Objective

Define the first complete Point-source evaluation flow:

`Source → structural/intrinsic evaluation → reference resolution → external/semantic evidence → claim resolution → human review where useful → DecisionStability → Gate → Snapshot`.

The plan produces Measurements, Findings, unresolved claims, review tasks and decision-specific readiness. It does not produce one quality score.

## 2. Pipeline

```text
E0 Intake & reproducibility freeze
 |
E1 Structural evaluation
 |
E2 Intrinsic profiling
 |
E3 Spatial reference resolution
 |
E4 External / semantic evidence
 |
E5 Claim resolution
 |
E6 Human review / evidence acquisition
 |
E7 Decision stability
 |
E8 Gate evaluation
 |
Spatial Admission Publisher
 |
TrustedSpatialSnapshot
```

Human review can be triggered before the final stage whenever evidence is insufficient/conflicted/high-impact.

## 3. E0 — Reproducibility

Freeze:
- SourceAsset hash/version;
- parser version;
- ontology/OperationalProfile version;
- EvaluationPlan version;
- reference inventory/version;
- detector/model versions through evaluation context.

Raw source stays immutable.

## 4. E1 — Structural

Required:
- D01 Schema/Parse
- D02 Range/Representation

The goal is interpretable coordinate structure, not location correctness.

If a required execution fails, affected requirements are NOT_EVALUATED, not “no issue”.

## 5. E2 — Intrinsic profiling

Required/core:
- D03 Precision Fingerprint
- D04 Reuse/Fallback signal
- D06 Intrinsic Spatial Outlier
- D09 preliminary source/pipeline segmentation

Outputs:
- source fingerprint;
- precision families;
- reuse patterns;
- intrinsic outliers;
- preliminary batch/pipeline structure.

No external reference required.

## 6. Evaluation scope hierarchy

`Dataset → Batch → Cluster → Record/Entity/CandidateRepresentation`.

Keep Findings at their real scope. Dataset findings are not duplicated to all records; a handful of record failures do not automatically become dataset findings.

## 7. EvaluationCoverageManifest

Every execution/result must expose:
- eligible/evaluated/excluded/abstained scopes;
- sample ObservedScope;
- InferenceScope where used;
- membership rule/manifest;
- coverage.

This is required before Gate can interpret “no finding”.

## 8. E3 — Spatial reference resolution

Consumes:
- D02 representation evidence;
- D03 precision;
- D07 declaration evidence;
- D08 residuals when available;
- D09 segmentation;
- ResolutionContext.

Produces:
- formal reference candidates;
- representation candidates;
- encoding hypotheses;
- corruption hypotheses;
- mixed-pipeline state;
- operational alignment;
- plausible spatial states.

Must support INS UFFICIENT_EVIDENCE, OUT_OF_CANDIDATE_SET and indistinguishability rather than forcing certainty.

## 9. E4 — Reference / semantic enhancement

Conditional/profile-required:
- D05 Administrative Consistency
- D07 Declared Reference Consistency
- D08 External Reference Residual
- D10 Semantic-Spatial Consistency

If reference evidence is unavailable, the reference-enhanced portion can be PARTIAL/UNAVAILABLE while intrinsic evaluation remains valid.

## 10. E5 — Claim resolution

`Measurements + Evidence + EvidenceRelations → ClaimResolution`.

States:
SUPPORTED / REFUTED / CONFLICTED / UNRESOLVED.

Do not convert detector severity directly into evidence polarity or truth.

## 11. Human Review triggers

Candidate triggers:
- CONFLICTED claim;
- high-impact UNRESOLVED;
- Resolver out-of-set;
- suspected mixed pipeline;
- repair candidate requiring approval;
- independent references disagree;
- decision result UNSTABLE;
- large population affected;
- novel failure family;
- policy-mandated review.

HumanReviewPolicy determines whether/how to route.

## 12. Human review is evidence production

Human output creates HumanAdjudication and/or new evidence/correction instruction.

It does not bypass the Gate.

Path:
`Review → new evidence/adjudication → new resolution/evaluation → stability → new GateDecision`.

Human correction never overwrites raw source.

## 13. DecisionStability

Evaluate each business variable under plausible states:
- city/district assignment;
- visit location/route assignment;
- geofence inclusion;
- other profile-required relations.

Unresolved reference identity can still yield stable business decisions.

## 14. Gate

Gate reads:
- profile;
- policy;
- RequirementEvaluation;
- Findings;
- ClaimResolution;
- DecisionImpact;
- DecisionStability;
- CoverageManifest;
- UsageLimit/consumer compatibility.

Admission is ALLOW / ALLOW_WITH_LIMITS / REVIEW / BLOCK_FOR_PROFILE. Governance disposition is separate.

## 15. Evaluation profiles

### Core Intrinsic
D01, D02, D03, D04, D06, preliminary D09.

### Reference Enhanced
Adds D05, D07, D08, D10 and Resolver validation where references are adequate.

### Human Enhanced
Adds governed review/adjudication/evidence acquisition.

## 16. Required vs conditional

A Required detector may legitimately ABSTAIN. GatePolicy determines whether the required decision requirement can remain usable.

A missing reference does not turn intrinsic evaluation into an execution failure.

## 17. Population vs sampling

Cheap deterministic detectors generally run over the full eligible population.

Expensive reference/human evaluation may use:
- representative samples;
- risk-enriched samples;
- targeted review.

Never hide the sampling design or convert sample evidence into subject evidence.

## 18. Review sampling

Do not select only uncertain cases.

Review prioritization must preserve some mix of:
- uncertainty;
- business impact;
- novelty;
- representativity;
- rare catastrophic failures;
- random audit;
- information value.

This avoids blind spots from confidently wrong models.

## 19. Source-level escalation

Repeated record anomalies with stable source/batch association can support a cluster/batch hypothesis, but only through explicit aggregation evidence.

A higher-scope GovernanceDisposition may quarantine/suspend a scope.

## 20. Re-evaluation after human/repair

New evidence or approved derived representation creates:
`new EvaluationResult → new RequirementEvaluation → new GateDecision`.

Old evaluation/Gate history remains immutable.

## 21. Passport output

Evaluation feeds Source Passport with:
- source/evaluation context;
- coverage;
- reference state;
- measurements;
- findings;
- open conflicts;
- human-review status;
- repair status;
- profile-specific readiness;
- versions/validity.

Passport is explanation, not enforcement.

## 22. End-to-end cases

A. clean-enough automatic ALLOW  
B. obvious catastrophic error → BLOCK  
C. uncertain → ABSTAIN/UNRESOLVED → human → re-evaluate  
D. human disagrees with AI → preserve AI history, add evidence  
E. reviewers disagree → CONFLICTED/escalate  
F. human proposes repair → validate/approve/re-Gate  
G. human identifies novel failure → teaching event/taxonomy/benchmark candidate

## 23. Principle

> HITL is part of evaluation, not an exception handler. Operational correction and model learning are separate loops.


<!-- END 09_POINT_SOURCE_QUALITY_EVALUATION_PLAN_V0.1.md -->

---

<!-- BEGIN 10_HUMAN_IN_THE_LOOP_AND_LEARNING_SPEC.md -->

# Human-in-the-Loop & Learning Specification

**Status:** Normative v1 packaged edition  
**Core principle:** Human Authority + Evidence Governance + Safe Learning

## 1. Why HITL is first-class

Spatial integrity includes inherently ambiguous cases:
- unknown/indistinguishable CRS;
- reference conflicts;
- unclear lineage;
- fallback vs legitimate centroid;
- changing administrative semantics;
- ambiguous entity matching;
- new source pipelines;
- multiple plausible repairs.

The correct machine behavior is sometimes **ASK / ABSTAIN / ESCALATE**, not forced prediction.

## 2. Human is not an oracle

Human judgment can be wrong, biased or reference-dependent. Therefore:
`Human Decision != automatic Ground Truth`.

Every human output has:
- provenance;
- scope;
- reviewer role/expertise;
- evidence;
- prediction visibility;
- confidence/uncertainty;
- revocability.

## 3. Human roles

At least:
- Reviewer — individual ambiguous cases;
- Domain Expert — business/source/geographic semantics;
- Data Steward — data correction/quarantine approval;
- Policy Owner — DecisionProfile/GatePolicy/override governance.

Permissions must not be conflated.

## 4. HumanReviewTask

Contains:
- subject/profile;
- trigger/reason;
- claim under review;
- candidate hypotheses;
- supporting/contradicting evidence;
- dependency status;
- business impact;
- requested reviewer role;
- priority/lifecycle.

The reviewer should see why the machine abstained, not only “is this point correct?”.

## 5. HumanAdjudication

Canonical adjudication decisions:
- SUPPORT
- REFUTE
- UNRESOLVED
- ESCALATE

Repair approval is **not** HumanAdjudication; it is separate governance.

Record prediction/evidence visibility, especially for Gold.

## 6. HumanReviewPolicy

Policy defines:
- trigger rules;
- reviewer role;
- independent/double review requirements;
- priority;
- escalation;
- review blind-mode requirements where relevant.

It may be referenced by EvaluationPlan and GatePolicy.

## 7. Review disagreement

Conflicting reviewers produce CONFLICTED or escalation unless a governed adjudication procedure resolves it.

Do not silently majority-vote a “truth” where uncertainty remains.

## 8. Human correction

Human may:
- confirm an issue;
- propose correction;
- request evidence;
- reject candidate;
- escalate.

“Old value is wrong” and “new value is correct” are separate claims.

All corrections re-enter evidence/evaluation/Gate.

## 9. Review triggers

Families:
- UNCERTAINTY
- CONFLICT
- NOVELTY
- HIGH_IMPACT
- POLICY_REQUIRED

Uncertainty alone does not always require human review: if relevant DecisionStability is stable and policy permits, automation may continue.

## 10. Review prioritization

Conceptually prioritize using:
- uncertainty;
- impact;
- novelty;
- representativity;
- information value;
- urgency.

Do not use uncertainty sampling alone. Preserve random/representative audits to catch confident systematic errors.

## 11. HumanTeachingEvent

A governed record connecting:
- input state;
- machine output;
- human adjudication/correction;
- evidence context;
- disagreement type;
- learning eligibility;
- teaching category.

A teaching event never changes production model immediately.

## 12. Learning eligibility

- ELIGIBLE
- CONDITIONALLY_ELIGIBLE
- NOT_ELIGIBLE
- REVOKED

Examples not automatically eligible:
- reviewer unsure;
- dependent evidence only;
- temporary policy override;
- adjudication later overturned.

## 13. Learning maturity

### L0 — Rule / knowledge update
Often best for explicit source-pipeline knowledge. Do not train a model when a versioned rule is the right artifact.

### L1 — Supervised learning
Suitable for fallback classification, source-pipeline classification, entity match assistance, anomaly classification, repair candidate ranking.

### L1 — Active learning
Select valuable examples for human labeling while controlling selection bias.

### L2 — Preference / ranking / contextual bandit
Useful when humans compare candidate repairs/evidence bundles or for review/evidence routing.

### L3 — Offline constrained RL (P2 research)
Only for genuine sequential decision problems such as next-best-evidence acquisition.

## 14. RL state/action boundary

Potential state:
findings, claims, evidence, uncertainty, profile, source context, review history.

Permitted research actions:
- request a reference/evidence family;
- run optional evaluation;
- request reviewer/expert/second review;
- escalate;
- stop and abstain.

RL must never own:
- raw mutation;
- world truth;
- ontology change;
- DecisionProfile requirement;
- hard Gate constraint;
- required human approval bypass;
- publication;
- silent repair approval.

## 15. Reward and safety

Reward may include:
- resolution quality;
- false-trusted penalty;
- false-certainty penalty;
- human cost;
- latency/evidence cost;
- successful abstention;
- transfer robustness.

Hard safety constraints are **constraints**, not merely reward penalties:
- no Gate bypass;
- no raw mutation;
- no unapproved repair publication;
- no required-review bypass;
- no unsafe production exploration.

## 16. Learning authority matrix

| Object/behavior | Automatically learn/change? |
|---|---|
| Raw SourceAsset | NO |
| Shared ontology | NO |
| Human adjudication history | store, revocable |
| Detector model parameters | candidate update after validation |
| Statistical thresholds | candidate update only |
| Review prioritization | YES after evaluation/promotion |
| Evidence acquisition order | YES after governance |
| Repair ranking | YES after validation |
| Hard Gate constraints | NO |
| DecisionProfile requirements | NO |
| Publication | NO direct learning authority |

## 17. Production promotion

`Human feedback → LearningDataset → Candidate model/policy → Offline evaluation → Blind/Transfer/B5 → Shadow → Governance approval → New version`.

Never:
`human correction → online weight update → immediate production behavior change`.

## 18. LearningDataset

Versioned with:
- TeachingEvent refs;
- source distribution;
- label policy;
- reviewer distribution;
- Gold independence;
- prediction visibility;
- known biases;
- split policy.

Reviewed cases are selection-biased; preserve selection policy.

## 19. Feedback revocation

If a human adjudication/reference is later overturned:
- revoke TeachingEvent eligibility;
- trace LearningDataset versions;
- analyze affected models;
- reevaluate capability if material.

Do not silently retain corrupted labels.

## 20. Model maturity

EXPERIMENTAL → OFFLINE_VALIDATED → SHADOW → APPROVED → DEPRECATED.

Policy learning receives stricter governance than detector learning.

## 21. PolicyExperience

Record from day one:
- state context;
- available actions;
- chosen action;
- action source;
- behavior-policy version;
- action propensity when available;
- immediate cost;
- evidence acquired;
- human feedback;
- eventual outcome;
- safety events;
- time.

This enables future selection-bias/off-policy analysis without committing v1 to RL.

## 22. Outcome feedback

Field verification, downstream correction, source update, customer dispute, snapshot revocation and repair outcome first become **Evidence** that updates the governed world state. They may also become learning signals second.

Reward never substitutes for evidence.

## 23. Metrics

Human:
- Review Rate;
- Resolution Rate;
- Escalation Rate;
- Reviewer Disagreement;
- Resolution time;
- overturn/reversal rate;
- AI→Human correction;
- Human→Later reversal.

Learning:
- label efficiency;
- review reduction at fixed FTR;
- false-certainty reduction;
- novel failure discovery;
- transfer improvement;
- calibration improvement;
- policy cost/regret where applicable.

## 24. Architecture

```text
Evaluation
  |
AI result / ABSTAIN
  |                \
clear              unclear/high-impact
  |                  |
Gate           HumanReviewTask
                    |
             HumanAdjudication
              /            \
         new Evidence    TeachingEvent
              |             |
        Re-evaluation    Learning Store
              |             |
             Gate       Offline Learning
                            |
                      Candidate Version
                            |
                    Benchmark / Shadow
                            |
                    Governance Approval
                            |
                        New Version
```

Operational correction and model learning are separate.

## 25. Final principle

> Machines automate only what evidence proves they can automate. Humans resolve the high-value remainder. Human work becomes governed teaching data, but learned behavior returns to production only after benchmark and governance.


<!-- END 10_HUMAN_IN_THE_LOOP_AND_LEARNING_SPEC.md -->

---

<!-- BEGIN 11_REPAIR_CORRECTION_AND_WORLD_STATE_UPDATE_SPEC.md -->

# Repair, Correction & World-State Update Governance Specification

**Status:** Normative v1 packaged edition

## 1. Purpose

Define how an apparently better correction can become an approved derived representation without overwriting source history or allowing AI/human shortcuts around evidence and Gate.

Canonical flow:
`Finding/Human evidence → RepairHypothesis → RepairProposal → independent validation → approval → DerivedEstimate/SpatialRepresentation → new SpatialWorldState version → re-evaluation → Gate → new Snapshot`.

## 2. Immutable raw source

Forbidden:
`detect → fix → overwrite raw`.

All normalized/transformed/repaired values are derived representations with lineage.

Human correction also cannot overwrite raw.

## 3. Concepts

### RepairHypothesis
Exploratory candidate explanation/change. Not governed truth.

### RepairProposal
Candidate promoted to formal validation.

### CorrectionInstruction
Human-proposed correction. Separate from adjudication and approval.

### RepairApproval
Explicit governance record authorizing a validated proposal.

### Approved output
Existing `DerivedEstimate / SpatialRepresentation` plus repair/approval provenance. Do not create a new shared truth root `ApprovedDerivedState`.

## 4. RepairProposal

Records:
- subject/claim/findings;
- old/proposed values;
- repair type;
- generation method/evidence;
- assumptions;
- applicable scope;
- lifecycle.

Lifecycle:
GENERATED → PROPOSED → UNDER_VALIDATION → VALIDATED → APPROVED/REJECTED → APPLIED/SUPERSEDED/REVOKED.

## 5. Correction vs adjudication

Human may confirm:
“14.778 is wrong.”

That does not prove:
“114.778 is correct.”

Error adjudication and repair approval are separate propositions and governance steps.

## 6. Generation vs validation evidence

Generation evidence asks:
“Why did we propose this?”

Validation evidence asks:
“Why believe it is a better representation of reality?”

Using the same map source for both proves source consistency, not independent reality confirmation.

Track dependency:
VERIFIED_INDEPENDENT / KNOWN_DEPENDENT / DEPENDENCY_UNKNOWN.

## 7. Validation dimensions

As applicable:
- structural validity;
- spatial plausibility;
- semantic consistency;
- reference agreement;
- peer/batch consistency;
- held-out evidence;
- DecisionStability;
- regression risk.

Not all repair types require all dimensions, but RepairPolicy specifies what is required.

## 8. Holdout for bulk rules

Batch/dataset repair rules cannot be discovered and “validated” on the same examples.

Use spatial/source/batch-aware held-out cases and exception analysis.

## 9. RepairPolicy

Separate from GatePolicy.

Defines:
- applicable repair type/scope;
- validation requirements;
- independence;
- required approver role/review count;
- regression checks;
- rollback/revocation requirements;
- publication requirements.

## 10. Risk classes

Conceptual:
- R0 low — semantics-preserving normalization;
- R1 moderate — local obvious field correction;
- R2 high — spatial position correction;
- R3 critical — batch transforms, entity merge/split, large-scale admin reassignment.

Concrete thresholds remain policy.

AI cannot self-approve when human/governance approval is required.

## 11. RepairApproval

Explicit record:
- proposal ref;
- approver/role;
- decision;
- rationale;
- policy version;
- approval time;
- validity/scope.

Do not hide authorization as only `proposal.status=APPROVED`.

## 12. World-state update

Approved output creates a **new derived representation/state version**.

Never modify source history.

State lineage must answer:
current value → derived representation → repair proposal → finding/evidence → SourceAsset.

## 13. Competing repairs

Multiple candidates can remain unresolved. Ranking is allowed for review assistance but cannot create approval.

A 0.92 candidate score is not “92% correct” without calibration.

## 14. Impact before approval

Know:
- affected claims;
- affected DecisionProfiles;
- affected stability;
- affected snapshots/consumers if currently published;
- regression effects.

Repair approval does not mutate an existing Snapshot. It triggers a new world state, evaluation, GateDecision and snapshot version.

## 15. Revocation / rollback

If approved repair is later disproven:
- revoke the derived representation/approval;
- restore previous valid governed state or mark unresolved;
- create new world/evaluation/Gate versions;
- run downstream impact analysis.

History remains visible.

Rollback means activate a prior valid governed state, not overwrite the database “back”.

## 16. Temporal update vs repair

Distinguish:
- Repair — past representation was wrong;
- Update — reality changed over time;
- Normalization — semantics unchanged;
- Transformation — standard known coordinate operation;
- Empirical alignment/correction — requires evidence governance.

Example:
2024 district A → 2026 district B is usually temporal update, not rewrite of 2024.

## 17. Repair taxonomy

- NORMALIZATION
- REPRESENTATION_CORRECTION
- COORDINATE_CORRUPTION_REPAIR
- OPERATIONAL_ALIGNMENT
- ATTRIBUTE_REPAIR
- ADMIN_ASSIGNMENT_UPDATE
- ENTITY_LINK_REPAIR
- SOURCE_PIPELINE_RESEGMENTATION

Entity merge/split reuses existing TopPrism entity-resolution capability and requires higher-risk governance.

## 18. Bulk repair

Prefer rule review + representative sample + risk-enriched sample + holdout rather than 20k manual clicks.

Even an approved bulk rule requires exception handling because a minority may belong to another legitimate pipeline.

High-risk repairs may first create SHADOW derived state.

## 19. Learning from repair

Repeated human outcomes may produce RepairRuleCandidate or learned ranking candidate.

They must pass benchmark/shadow/governance before production and continue to **propose**, not silently overwrite.

Rules bind source/batch/geography/time/evidence envelope; never generalize a vendor-specific pattern universally.

## 20. Repair metrics

- Repair Proposal Precision
- Approved Repair Precision
- Repair Coverage
- False Repair Rate
- Human Approval/Rejection Rate
- Later Revocation Rate
- Transfer degradation
- Decision Readiness improvement
- Regression rate

False repair is a high-severity safety failure because plausible false corrections can bypass later anomaly detection.

## 21. Repair abstention

Valid state:
`issue confirmed, correct replacement unresolved`.

The system should block relevant uses rather than fabricate a plausible point.

## 22. Benchmark

B0: controlled mutation repair relation  
B1: real confirmed error + independently adjudicated correction  
B3: blind repair cases  
B4: cross-source/city/time transfer  
B5: misleading/bad references attempting to induce false repair

## 23. Principle

> Detecting an error does not authorize a correction. A correction becomes usable only as a governed derived representation after independent-enough validation, approval, re-evaluation and Gate.


<!-- END 11_REPAIR_CORRECTION_AND_WORLD_STATE_UPDATE_SPEC.md -->

---

<!-- BEGIN 12_SOURCE_PASSPORT_AND_TRACEABILITY_SPEC.md -->

# Spatial Source Passport & Traceability Specification

**Status:** Normative v1 packaged edition

## 1. Purpose

Aggregate the source's current governed assessment into a comprehensible, traceable view of:
- source/provenance;
- evaluation coverage;
- quality measurements;
- spatial-reference state;
- findings/conflicts;
- human review;
- repair;
- profile-specific readiness;
- usage limits;
- version/lifecycle;
- learning maturity.

Passport is a **view**, not a truth store and not an admission engine.

## 2. Passport vs Gate vs Snapshot

- Passport: **what we know, what we do not know, and why**
- Gate: **whether a subject may be admitted for a profile**
- Snapshot: **what a consumer is authorized to use**

Passport may display Gate status but never owns that status.

## 3. No overall trust score

Do not make `Overall Quality/Trust = 87` the primary artifact.

Optional dashboard summary indicators are allowed only for navigation/ranking, must drill down to Measures/Findings, and cannot authorize Gate.

## 4. Passport scope

Primary v1 passports:
- Source / Dataset
- Batch
- Cluster as needed

Do not generate a full rich passport per record by default at 469k scale; use drill-down through underlying objects/manifests.

## 5. Source identity

Show:
- provider/product;
- source/version;
- acquisition time;
- content hash;
- license/usage constraint;
- format/schema;
- declared spatial reference.

Raw source explicitly marked immutable.

## 6. Processing lineage

`SourceAsset → Parser → SourceRecordSnapshot → EvaluationPlan → DetectorExecutions/Coverage → Measurements/Findings/Evidence → Gate → Snapshot`.

Parser changes produce a new evaluation lineage over the same raw content.

## 7. Semantic/version context

Bind:
- ontology version;
- OperationalProfile version;
- EvaluationPlan/result versions.

This prevents later ontology changes from silently reinterpreting old Passport content.

## 8. Evaluation coverage

Show:
- eligible records/scope;
- evaluated coverage;
- abstained/failed/not-applicable;
- representative sample coverage;
- risk-enriched sample coverage;
- human-review coverage;
- external-reference coverage.

Do not say “Human Verified” for a sample of a large dataset.

## 9. Quality section

Display ISO quality dimensions using standard terminology:
- Completeness
- Logical Consistency
- Positional Accuracy
- Temporal Quality
- Thematic Accuracy
- Metaquality

Keep TopPrism trust separate:
- Coordinate Trust
- Location Trust
- Semantic-Spatial Trust
- Source / Provenance Trust

Do not add Temporal Trust/Completeness Trust as v1 root trust dimensions.

## 10. Measure presentation

For each important Measure:
- name/version;
- value/unit;
- evaluation scope;
- coverage;
- method;
- reference/version;
- measured time;
- uncertainty/metaquality;
- limitations.

Prefer distributions over a single average where tail risk matters.

## 11. Completeness claim boundary

Field/attribute completeness can be evaluated intrinsically.

Real-world feature omission completeness requires an appropriate universe/reference. Otherwise display NOT_EVALUATED rather than implying all stores/POIs are present.

## 12. Stratified reporting

Expose relevant strata:
- city;
- batch;
- pipeline;
- precision family;
- time.

A good overall metric must not hide a bad batch.

## 13. Source fingerprint

Display descriptive source characteristics:
- precision families;
- schema variants;
- coordinate reuse;
- pipeline segmentation;
- residual behavior.

Fingerprint is evidence, not source identity proof.

## 14. Spatial reference section

Separate:
- declared reference;
- resolved formal reference;
- representation;
- additional encoding;
- corruption state;
- operational alignment.

Example language:
“WGS84/CGCS2000 indistinguishable at current evidence resolution”, not “equivalent”.

“BD-like strongly supported”, not “CRS=BD09” unless identity is truly established.

## 15. Alignment

Display:
- target reference;
- transformation type: registered/documented/empirical;
- validation scope/time;
- held-out status;
- residual distribution;
- limitations.

## 16. Mixed pipelines

If mixed:
show segment coverage, segment hypotheses and unresolved segments. Never publish only the majority CRS/encoding as the whole-source identity.

## 17. Findings

Separate:
- Confirmed Issues
- Detected Signals
- Disputed Findings
- Resolved Findings

Always show scope, severity, confidence and evidence basis.

## 18. Evidence / claims

Key claims expose:
- supporting evidence;
- contradicting evidence;
- dependency status;
- age/source;
- current ClaimResolution.

Show effective independent source families, not only raw “source count”.

## 19. Human section

Show:
- review status;
- reviewed scope/count;
- representative vs risk-enriched coverage;
- reviewer roles;
- adjudications;
- prediction visibility where relevant;
- disagreement/escalation;
- open review queue.

Human disagreement remains visible.

## 20. Repair section

Show:
- proposals;
- validated;
- approved;
- rejected;
- revoked;
- unresolved.

Approved derived value must remain traceable to original raw value and RepairApproval.

## 21. Learning section

Show learning maturity, not “self-learning enabled”.

Stages:
- L0 governed manual/knowledge;
- L1 supervised + active learning;
- L2 preference/bandit assistance;
- L3 offline constrained RL (research);
- L4 governed adaptive policy only if ever justified.

If learned models influence assessment, show model version, maturity, benchmark release and transfer envelope.

## 22. Decision readiness

Display per DecisionProfile using real GateDecision:
- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW
- BLOCK_FOR_PROFILE

Show UsageLimits and DecisionStability by relevant variable.

Never collapse all profiles into `Source=GOOD/BAD`.

## 23. Open risks / unsupported uses

Mandatory sections:
- Open Risks
- Unsupported Uses
- Unsupported Claims

Examples:
- exact source reference identity unresolved;
- dependency unknown;
- fine entrance accuracy not validated;
- no network/raster/polygon evidence;
- nationwide feature completeness not evaluated.

## 24. Lifecycle

Passport states:
ACTIVE / SUPERSEDED / EXPIRED / INVALIDATED.

It binds validity window and prior/new Passport versions.

Passport invalidation does not rewrite history.

## 25. Snapshot/consumer lineage

Passport links current/historical published snapshots and can trace consumers/jobs that used them.

It may show revocation/impact status but does not execute revocation itself.

## 26. Views

### Executive
Readiness, major risks, open review, material changes.

### Operational
Affected batches, findings, review/repair actions.

### Audit
Measures, detector/execution/coverage, evidence DAG, versions, policies, benchmark maturity.

These are projections of one underlying governed state, not separate reports.

## 27. Delta view

First-class “what changed?”:
- Finding delta;
- Trust/quality delta;
- Review/repair delta;
- Gate delta;
- snapshot delta.

History remains available.

## 28. LLM role

LLM may explain/summarize structured Passport state. It may not:
- invent evidence;
- change Gate status;
- upgrade confidence;
- hide conflict;
- reinterpret raw source independently.

## 29. Integrity/reproducibility

Passport can carry content hash and references to:
- Source hash;
- parser;
- EvaluationPlan;
- Measure/Detector versions;
- reference versions;
- ontology;
- DecisionProfile;
- GatePolicy;
- model/benchmark versions as relevant.

## 30. Acceptance examples

- 100% coordinate presence + catastrophic location errors must not render “excellent”.
- Three agreeing but dependent references must not appear as three independent confirmations.
- 300 reviewed of 469k must show coverage, not “human verified”.
- Approved repair keeps raw visible.
- CRS identity unresolved + CityAnalytics ALLOW can coexist.
- CityAnalytics ALLOW + FineGeofence BLOCK can coexist.
- required detector failed → evaluation partial/not evaluated.
- missing GateDecision → no READY state.

## 31. Principle

> Passport makes quality, evidence, uncertainty, human judgment, repair, learning maturity and decision-use boundaries visible. It does not certify universal truth and does not replace the Gate.


<!-- END 12_SOURCE_PASSPORT_AND_TRACEABILITY_SPEC.md -->

---

<!-- BEGIN 13_TRUSTED_SNAPSHOT_LIFECYCLE_AND_IMPACT_PROPAGATION_SPEC.md -->

# Trusted Snapshot Lifecycle & Impact Propagation Specification

**Status:** Normative v1 packaged edition

## 1. Purpose

Define how published decision-specific spatial state remains governable when source, evidence, reference, human adjudication, repair, policy, model, ontology or consumer capabilities change.

A snapshot is not permanent truth. It is a versioned authorization produced under a specific state/evidence/profile/policy/consumer/time context.

## 2. Snapshot immutability

Published snapshots are immutable.

Any meaningful change creates:
`new evaluation → new GateDecision → new DecisionReadyProjection set → new Snapshot version`.

History remains queryable.

## 3. Status model

LifecycleStatus:
- DRAFT
- ACTIVE
- SUPERSEDED
- EXPIRED
- REVOKED
- INVALIDATED

DeploymentMode:
- SHADOW
- PRODUCTION

Only `ACTIVE + PRODUCTION` is production consumable.

## 4. Status semantics

**SUPERSEDED**: new snapshot replaces old for future use; old remains historically valid under original context.

**EXPIRED**: validity window ended; not a claim that historical contents were wrong.

**REVOKED**: new evidence/governance means prior authorization should no longer be used.

**INVALIDATED**: evaluation foundation itself became unreliable (e.g. systematic parser/evaluation semantic defect).

## 5. Snapshot binding

Bind:
- snapshot ID/version;
- consumer/version;
- DecisionProfile/version;
- GatePolicy/version;
- ontology/OperationalProfile;
- source/world-state version;
- EvaluationResult;
- included DecisionReadyProjections;
- UsageLimits;
- GateDecision refs;
- lifecycle/validity;
- reference/model/detector lineage through evaluation.

Snapshots are consumer/profile-bound. Do not reuse a VisitPlanning snapshot for FineGeofence.

## 6. Publication prerequisites

Require:
- valid profile/policy;
- sufficient required evaluation and coverage;
- Gate ALLOW or compatible ALLOW_WITH_LIMITS;
- compatible consumer capabilities;
- valid source/world state;
- no higher-scope blocking disposition.

## 7. Dependency graph

Snapshot dependencies include:
- world state;
- EvaluationResult/CoverageManifest;
- GateDecision;
- DecisionProfile/GatePolicy;
- reference sources;
- human adjudications;
- approved repairs;
- detector/model versions;
- ontology/OperationalProfile;
- consumer capability.

This graph enables selective impact analysis.

## 8. TrustRelevantChange

At least:
- REFERENCE_UPDATED / CORRECTED / RETRACTED
- SOURCE_UPDATED
- HUMAN_ADJUDICATION_OVERTURNED
- REPAIR_REVOKED
- PROFILE_UPDATED
- GATE_POLICY_UPDATED
- MODEL_DEPRECATED/DEFECT
- DETECTOR_DEFECT
- ONTOLOGY_CHANGED
- CONSUMER_CAPABILITY_CHANGED

Change does not automatically revoke everything; run Impact Analysis.

## 9. Impact propagation

`Change → affected evidence/state → claims → findings/requirements → GateDecisions → Snapshots → Consumers → Business decisions/jobs`.

Propagation is Claim/Profile-specific and may stop when re-evaluation proves affected decision variables remain stable.

## 10. Impact severity

Conceptual:
- I0 NONE
- I1 INFORMATIONAL
- I2 RE-EVALUATE
- I3 SUSPEND NEW CONSUMPTION
- I4 REVOKE
- I5 INVALIDATE

Policy defines concrete response by risk.

## 11. Change categories

- Reality change — store moved, road closed, admin changed.
- Source change — new batch/corrected provider record/pipeline change.
- Evidence change — new or disproven reference/human evidence.
- Policy change — DecisionProfile/GatePolicy.
- Evaluation change — detector/model/parser defect/improvement.
- Consumer change — new operations/capabilities affecting UsageLimit compatibility.

These have different semantics and must not all be called “data changed”.

## 12. Reference changes

Distinguish:
- NORMAL_UPDATE
- CORRECTION
- RETRACTION

A newer reference does not automatically make historical reference wrong.

Correction/retraction triggers dependency-based impact analysis.

## 13. Human/repair changes

If HumanAdjudication is overturned:
- operational impact path updates claims/evaluation/Gate;
- learning impact path traces TeachingEvents/LearningDatasets/models.

If RepairApproval/derived representation is revoked:
- restore prior valid governed state or mark unresolved;
- re-evaluate;
- issue new Gate/snapshot;
- retain historical snapshot provenance.

## 14. Profile/policy changes

Old snapshot remains bound to old versions.

New Profile does not reinterpret old snapshot.

Policy governance can specify:
- GRANDFATHERED
- RE_EVALUATION_REQUIRED
- IMMEDIATE_REVOKE

Critical safety-policy defects can revoke historical active snapshots.

## 15. Detector/model defects

A defect should trigger selective impact based on:
- exact version used;
- affected conditions/scope;
- measurements/findings dependent on it.

Improvement alone may wait for normal refresh; a defect may require historical review.

A leaked/invalid benchmark lowers capability evidence and may trigger risk review, but does not automatically prove every historical result wrong.

## 16. Consumer consumption record

Every formal consumption produces SnapshotConsumptionRecord:
- snapshot/version;
- consumer/version;
- operation;
- business job/decision refs;
- used time;
- applied UsageLimits;
- outcome ref where available.

Without this, revocation cannot govern historical downstream impact.

## 17. Historical impact review

A revoked/invalidated snapshot does not delete historical business decisions.

Review outcomes may be:
- UNAFFECTED
- POTENTIALLY_AFFECTED
- AFFECTED
- RECOMPUTED
- REVIEWED
- REMEDIATED

Actions can include notify, recompute, review and business-specific remediation.

High-impact/unknown/legal cases trigger human ImpactReviewTask.

## 18. Offline/disconnected copies

Central revocation cannot guarantee physical recall.

Track:
- RevocationReachability;
- ConsumptionLoggingCoverage;
- provenance completeness.

Do not state “all copies revoked” without evidence.

Offline packages carry snapshot version, validity and UsageLimits.

## 19. Consumer capability change

A new consumer version may make old ALLOW_WITH_LIMITS incompatible.

Because snapshots are consumer-bound, revoke/replace the affected consumer snapshot rather than inventing `REVOKED_FOR_CONSUMER`.

## 20. Refresh/validity

Every snapshot has `valid_from/valid_until`.

Refresh can be:
- time-based;
- event-based;
- source-update;
- reference-update;
- on-demand.

Cadence is profile/risk policy, not universal architecture.

## 21. Dependency strength / unknown lineage

Dependencies can be HARD / SOFT / INFORMATIONAL.

If lineage is incomplete, use `DEPENDENCY_UNKNOWN`; do not interpret “no dependency found” as “no impact”.

Impact evaluation itself has metaquality such as dependency/logging coverage.

## 22. Shadow / rollback

High-risk new repair/model/policy results may create `ACTIVE + SHADOW` snapshots for comparison.

Rollback is governed:
- previous snapshot must still satisfy current policy;
- otherwise valid state may be “NO_CURRENT_PUBLISHABLE_STATE”.

Never automatically fall back to an expired/revoked old snapshot.

## 23. Audit trail

Lifecycle events:
CREATE / ACTIVATE / SUPERSEDE / EXPIRE / REVOKE / INVALIDATE / REACTIVATE.

Reactivation requires new validity confirmation.

Possible revocation reasons:
source/reference/repair/human error, policy/model/detector defect, consumer incompatibility, expiry, unknown critical risk.

Invalidation reasons include non-reproducible evaluation, core semantic/parser defects, major benchmark governance failure or unusable lineage.

## 24. Human and learning

Major uncertain impacts, legal consequences, large-scale remediation or unknown scope require human governance.

Incidents/outcomes can later become HumanTeachingEvents, but learning cannot suppress mandatory incident/revocation logging or hard constraints.

## 25. Lifecycle benchmark

At minimum:
- active consumed normally;
- expired blocked;
- superseded not used for new task;
- revoked blocked;
- historical ConsumptionRecord retained;
- reference change + stable decision avoids unnecessary revoke;
- critical reference correction locates affected snapshots;
- new consumer version violates UsageLimit;
- model defect supports selective re-evaluation;
- unknown lineage does not become “no impact”.

## 26. P0 failures

- revoked/expired snapshot still consumed;
- consumer loses snapshot/version lineage;
- blocked projection appears in snapshot;
- UsageLimit lost;
- critical change cannot locate affected snapshots;
- snapshot updated in place;
- history silently rewritten;
- raw WorldState consumed after snapshot revocation.

## 27. Principle

> Every trusted conclusion can be challenged by later evidence; later conclusions create new versions and impact records, never rewrite what was known, decided or consumed in the past.


<!-- END 13_TRUSTED_SNAPSHOT_LIFECYCLE_AND_IMPACT_PROPAGATION_SPEC.md -->

---

<!-- BEGIN 14_REFERENCES_AND_STANDARD_POSITIONING.md -->

# References & Standards Positioning

**Status:** Supporting reference index for the v1 architecture package.  
This file does not replace the normative specs.

## Standards / vocabularies
- ISO 19157-1:2023 — geographic data quality; core quality/evaluation foundation.
- ISO 19111:2019 + applicable published amendments — referencing by coordinates; CRS/coordinate-operation concepts.
- EPSG Geodetic Parameter Dataset — authoritative registry used with pinned versions.
- ISO 19112:2019 — spatial referencing by geographic identifiers; useful for gazetteer/reference semantics, not automatic truth.
- ISO 19115-1:2014 + applicable amendments — metadata concepts; use conceptually/adapters, do not hard-bind the domain model to XML.
- ISO 19131:2022 — data product specification/intended purpose; business tolerances remain project policy.
- ISO/TS 19158:2012 — conditional ongoing supplier/acquisition QA reference; not the core basis for one-time off-the-shelf data QA.
- ISO 19160-3:2020 — address data quality profile; optional Address Profile only.
- ISO 19156:2023 — observations/measurements/samples; map only where source semantics genuinely fit.
- OGC Simple Feature Access Part 1: Common Architecture v1.2.1 (OGC 06-103r4) — geometry/simple-feature concepts.
- W3C PROV-DM — W3C Recommendation, provenance data model.
- W3C PROV-O — W3C Recommendation, OWL ontology for PROV.
- W3C DQV — W3C Working Group Note; useful vocabulary for quality Dimension/Metric/Measurement/Policy.
- ISO 19157-3 — treat as under development until formally published; TopPrism uses a namespaced, versioned internal Measure Registry meanwhile.

## Selected literature used as design context
- Goodchild, M. F., & Li, L. (2012). Assuring the quality of volunteered geographic information. *Spatial Statistics*, 1, 110–120.
- Barron, C., Neis, P., & Zipf, A. (2014). A Comprehensive Framework for Intrinsic OpenStreetMap Quality Analysis. *Transactions in GIS*, 18, 877–895.
- Senaratne, H. et al. (2017). A review of volunteered geographic information quality assessment methods. *International Journal of Geographical Information Science*, 31(1), 139–167.
- Devillers, R., Bédard, Y., Jeansoulin, R., & Moulin, B. (2007). Fitness-for-use / spatial data quality information analysis work in *IJGIS*.
- Zandbergen, P. A. (2008). Positional Accuracy of Spatial Data: Non-Normal Distributions and a Critique of the National Standard for Spatial Data Accuracy. *Transactions in GIS*, 12, 103–130.
- Xu, Y., Lewis, E., & Guan, W. (2019). China map integration / GCJ-02 context. *ISPRS International Journal of Geo-Information*, 8(12), 567.
- Dong, X. L., Berti-Équille, L., & Srivastava, D. (2009). Integrating Conflicting Data: The Role of Source Dependence.
- Truth-discovery literature — useful for source dependence/conflicting claims, but not adopted as v1 runtime truth fusion.
- Human-in-the-loop / active-learning literature — supports selective human intervention and informative sample selection; it does not prove SSI's particular governance contract.
- Safe/offline reinforcement-learning literature — motivates constrained, conservative policy optimization; RL is P2 research in SSI and never owns hard Gate authority.

## Claim discipline
The architecture uses standards and papers as:
- normative conceptual references;
- design precedents;
- terminology checks;
- risk warnings.

It must not claim that a paper proves a TopPrism detector, FTR bound, source truth or business threshold unless the exact evaluation evidence exists.


<!-- END 14_REFERENCES_AND_STANDARD_POSITIONING.md -->
