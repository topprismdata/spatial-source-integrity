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
