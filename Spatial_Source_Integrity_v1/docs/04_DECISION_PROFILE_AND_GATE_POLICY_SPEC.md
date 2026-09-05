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
