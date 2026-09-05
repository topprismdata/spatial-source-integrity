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
