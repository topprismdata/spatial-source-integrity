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
