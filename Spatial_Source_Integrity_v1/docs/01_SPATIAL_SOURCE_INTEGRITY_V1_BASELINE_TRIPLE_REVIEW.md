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
