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
