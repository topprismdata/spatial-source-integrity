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
