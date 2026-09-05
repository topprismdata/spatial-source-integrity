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
