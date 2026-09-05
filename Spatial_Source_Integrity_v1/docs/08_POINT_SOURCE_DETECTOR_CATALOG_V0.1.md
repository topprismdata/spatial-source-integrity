# Point Source Detector Catalog v0.1

**Status:** Normative v1 packaged edition  
**Geometry scope:** Point  
**Source types:** POI / store / community / customer / address point / geocoded record

## 1. Purpose

Use a small, explainable first detector set to prove the full chain:
`Source → Evaluation → Measurement → Finding → Claim Resolution → Human/Repair where needed → DecisionImpact → DecisionStability → Gate`.

Detectors produce evidence/signals, not truth or admission decisions.

## 2. v0.1 detector set

| ID | Detector | Type | Main role |
|---|---|---|---|
| D01 | Coordinate Schema & Parse | deterministic | coordinate structure |
| D02 | Geographic Range & Representation | deterministic | coordinate representation |
| D03 | Coordinate Precision Fingerprint | descriptive/statistical | source fingerprint |
| D04 | Coordinate Reuse & Fallback Signal | hybrid | source/location |
| D05 | Administrative Consistency | reference deterministic | location/semantic |
| D06 | Intrinsic Spatial Outlier | statistical/hybrid | intrinsic location pattern |
| D07 | Declared Spatial Reference Consistency | hybrid | coordinate/source |
| D08 | External Reference Residual | reference-based | coordinate/location |
| D09 | Batch & Pipeline Consistency | statistical/hybrid | source pipeline |
| D10 | Semantic-Spatial Consistency | hybrid | semantic/location |

Spatial Reference Resolver is not an 11th detector; it consumes multiple detector outputs.

## 3. Common contract

Every detector defines:
- identity/version/maturity;
- purpose;
- measure refs;
- applicable scope;
- required/optional inputs;
- reference dependencies;
- execution type;
- abstention conditions;
- measurements/signals/findings/evidence outputs;
- known false-positive/false-negative cases;
- dependencies;
- B0/B1/B5 mapping.

Execution states: COMPLETED / SKIPPED / ABSTAINED / FAILED.

## 4. D01 — Coordinate Schema & Parse

Measures:
- coordinate field presence;
- numeric parse rate;
- dimension/cardinality consistency.

Findings:
- field missing;
- parse failure;
- dimension inconsistent;
- representation mapping suspected.

May abstain when coordinate-field semantics cannot be identified.

DMS-like text failing decimal parsing is not automatically invalid coordinate data.

B0: blanks, non-numeric, locale separator, field shift, dimension mutation.

## 5. D02 — Geographic Range & Representation

Measures:
- legal range under a representation;
- representation compatibility;
- axis interpretation compatibility.

Findings:
- value outside representation range;
- representation ambiguous;
- axis interpretation conflict;
- unit/scale interpretation suspected.

Global coordinate-range validity does not imply correct location. A wrong but globally legal point can pass D02.

B0: axis swap, range violation, degree/radian or scale-like mutation.

## 6. D03 — Coordinate Precision Fingerprint

Measures:
- decimal/significant-digit distributions;
- precision family structure/entropy;
- batch precision consistency.

Primarily descriptive.

Findings only with evidence:
- precision pipeline heterogeneity;
- suspected precision degradation.

Never interpret more decimal places as greater positional accuracy.

B0: rounding/precision-family injection.  
B5 counterexample: many decimals + poor reference accuracy.

## 7. D04 — Coordinate Reuse & Fallback Signal

Measures:
- reuse frequency distribution;
- cross-city/district reuse;
- semantic diversity at shared coordinate;
- known centroid match;
- source concentration.

Findings:
- high reuse;
- cross-region reuse;
- fallback suspected;
- known centroid fallback suspected.

Legitimate counterexamples must be benchmarked:
- mall centroid;
- community centroid;
- shared office entrance.

Duplicate coordinate ≠ error.

## 8. D05 — Administrative Consistency

Reference-based deterministic spatial operations; reference suitability remains metaquality/evidence governance.

Measures:
- country/province/city/district containment agreement;
- admin hierarchy consistency;
- boundary-proximity distance.

Findings:
- country/province/city/district conflict;
- admin hierarchy conflict;
- near-boundary ambiguity.

Bind boundary version/time. Abstain when admin name/reference/time is unresolved.

B5 includes stale/historical/conflicting admin boundaries.

## 9. D06 — Intrinsic Spatial Outlier

**Final v1 normalization:** D06 core-intrinsic logic must not require an administrative reference.

Measures:
- distance/isolation relative to robust source/batch peer distribution;
- intrinsic cluster/outlier scores;
- source-distribution regional outlier rates.

Findings:
- intrinsic spatial outlier;
- source-distribution outlier.

Administrative polygon displacement belongs to D05.

Peer outlier ≠ confirmed location error; legitimate remote/new-development locations exist.

## 10. D07 — Declared Spatial Reference Consistency

Measures:
- declaration completeness/parseability;
- area-of-use compatibility;
- representation compatibility;
- evidence consistency.

Findings:
- declaration missing/invalid;
- area conflict;
- representation conflict;
- evidence conflict.

Declared metadata is evidence, not truth. D07 does not identify the replacement CRS; it hands conflicts to Resolver.

## 11. D08 — External Reference Residual

Prerequisite: a sufficiently supported entity/reference match.

Measures:
- matched-reference distance;
- residual vector/distribution;
- held-out residual;
- gross residual rate;
- match coverage.

Findings:
- positional residual elevated;
- systematic residual;
- reference match ambiguous;
- holdout alignment inadequate.

Always preserve match ambiguity and reference feature-definition differences (entrance vs centroid vs sales office).

Fit and held-out residuals are separate.

## 12. D09 — Batch & Pipeline Consistency

Consumes precision, residuals, metadata, reuse, source IDs, time/batch and schema variants.

Measures:
- family heterogeneity;
- residual cluster structure;
- metadata/precision cluster coherence;
- change-point signal;
- candidate pipeline stability.

Findings:
- source pipeline heterogeneity;
- mixed reference pipeline suspected;
- pipeline change point;
- unexplained batch shift.

Clustering ≠ pipeline truth.

Final bounded interaction:
`Phase A preliminary segmentation → Resolver → Phase B validation/refinement`.
No unbounded self-confirming loop.

## 13. D10 — Semantic-Spatial Consistency

MVP relations:
- city ↔ coordinate;
- district ↔ coordinate;
- address geography ↔ coordinate;
- resolved entity candidate ↔ coordinate.

Measures:
- admin attribute agreement;
- address geography agreement;
- geocode residual;
- entity-candidate spatial agreement;
- semantic-spatial conflict count.

Reuse existing TopPrism entity-resolution capability. Similar name ≠ same entity.

May abstain when address/entity candidate resolution is insufficient.

## 14. Dependency graph

Conceptually:
```text
D01 → D02
       |
       +→ D03 → D04
       +→ D07
       +→ D05
       +→ D06
D05/D07 → D08
D05/D08/entity-resolution → D10
D03/D04/D06/D07/D08 → D09 Phase A/B
D02/D03/D05/D07/D08/D09/D10 → Spatial Reference Resolver
```

Runtime may parallelize; this expresses semantic dependency, not threads.

## 15. Intrinsic vs reference-enhanced

### Core intrinsic
D01, D02, D03, D04, D06, D09-preliminary.

### Reference-enhanced
D05, D07, D08, D10 plus Resolver/reference validation.

Do not label intrinsic signal as externally validated. Do not treat external reference as truth.

## 16. Sampling / expensive references

External API and human review are not default per-record operations for hundreds of thousands of points.

Use:
- versioned batch reference datasets where feasible;
- representative samples;
- risk-enriched samples;
- review queues.

Always record sample design, coverage and inference scope.

## 17. Finding scope

Dataset/batch findings remain dataset/batch findings. Do not duplicate them onto every record.

Higher-scope GovernanceDisposition may still block child publication.

## 18. Detector promotion

Initially EXPERIMENTAL.  
BENCHMARKED requires B0 + relevant real cases + false-positive cases.  
APPROVED requires blind evidence, applicability and controlled failure/abstention behavior; high-risk mandatory detectors should include transfer/reference-failure evidence.

## 19. Architecture cases

Must cover:
- fields present but location catastrophically wrong;
- legal range but wrong city;
- legitimate repeated mall centroid;
- wrong reference source;
- declared CRS correct + bad reference match;
- declared CRS wrong + systematic encoding;
- mixed batch;
- missing reference → ABSTAIN;
- same measurement → different profile Gate;
- multiple detectors sharing one upstream reference not independent.

## 20. Principle

> A Detector is a source of auditable measurements/evidence. It does not own truth, repair authority or business admission.
