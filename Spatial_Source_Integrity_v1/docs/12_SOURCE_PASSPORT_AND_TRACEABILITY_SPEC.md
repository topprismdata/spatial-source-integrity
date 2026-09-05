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
