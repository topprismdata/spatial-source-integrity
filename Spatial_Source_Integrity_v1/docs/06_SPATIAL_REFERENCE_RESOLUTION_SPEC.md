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
