# Canonical Real-World Case B1-001

## DOUBLE_MISLABEL_AND_DERIVED_COORDINATES

**Case ID:** `REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES`  
**Corpus:** Xi'an commercial listing dataset 2026-08 (Real-World Seed Corpus #1)  
**Archived:** 2026-09-05  
**Phase:** 1R Closure  
**Purpose:** Long-term regression case against "looks certain" class of errors.

---

## 1. Case Summary

Two vendor files carried seemingly clear, mutually distinct CRS labels:

- `file1`: labeled `GCJ02`
- `file2`: labeled `WGS84`

SSI's evaluation revealed that **both labels are factually wrong**, and that the actual relationship between the two files is a **deterministic mathematical derivation** rather than a semantic coordinate-system duality.

This case demonstrates why SSI's evidence hierarchy must separate:

1. **Raw Declaration** (vendor label, preserved verbatim)
2. **Mathematical Relation** (function-level reproducibility)
3. **Production Lineage Claim** (which file actually produced which)
4. **Reference Identity** (what coordinate reference system the values actually use)
5. **Operational Alignment** (whether a validated transform produces usable coordinates)

These five layers are logically independent and must NOT be conflated.

---

## 2. Evidence Layers (resolved)

### Layer 1: Raw Declaration
```text
file1.declared_reference_raw = "GCJ02"  # vendor filename label
file2.declared_reference_raw = "WGS84"  # vendor filename label
declared_reference_resolution = CONFLICTED  # both labels contradict observed evidence
```

### Layer 2: Mathematical Relation (C1a) — `CONFIRMED`
```text
file1[i] = round6(wgs84_to_gcj02(file2[i]))  for all i in 12505 records
Exact match at 6-decimal quantization: 12505 / 12505 = 100.00%
Max residual (pre-quantization): P50=0.04m, P95=0.061m, max=0.072m
Implementation: Krassovsky a=6378245.0, ee=0.00669342162296594323
```

This is a pure **mathematical function equality**. No geodetic semantic claim is implied.

### Layer 3: Production Lineage (C1b) — `SUPPORTED`
```text
Status: SUPPORTED (not CONFIRMED)
Evidence: decimal precision (14 vs 6), file mtimes (file2 18:18, file1 18:21), mathematical reproducibility
Caveat: Without upstream provenance metadata, we cannot prove which file was "produced first"
        in a business sense; we can only prove mathematical precedence.
```

### Layer 4: Reference Identity
```text
file1: OUT_OF_CANDIDATE_SET / UNRESOLVED
file2: UNCONFIRMED

file2 Encoding Family: BD_LIKE_STRONGLY_SUPPORTED
Reason for not upgrading to IDENTIFIED:
  - Only 7.5% of records have anchor evidence
  - Reference feature semantics is centroid, not entrance
  - No upstream provider metadata confirms encoding identity
  - SSI normative rule: good fit ≠ identity
```

### Layer 5: Operational Alignment
```text
alignment_state: VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE
alignment_target: WGS84 (OSM residential parcel centroids)
validation_scope: HOLDOUT (212) + BLIND (170)
holdout_p50 = 41.81m, holdout_p95 = 185.1m
blind_p50 = 34.7m, blind_p95 = 246.7m
coverage: 937 / 12505 = 7.5%
is_operationally_aligned = True (CONVENIENCE FIELD ONLY — carries zero gate authority)
```

---

## 3. Why This Case Matters

This case is a **canonical regression** against several classes of "looks certain" errors:

### Error class 1: Trusting the label
A naive pipeline would read `GCJ02` / `WGS84` from the filename and apply the corresponding transforms, producing wrong results silently. SSI's `D07 → Resolver` detected the conflict.

### Error class 2: Confusing mathematical fact with business lineage
The bit-exact reproducibility (`round6(wgs84_to_gcj02(file2)) == file1`) is stunning evidence of a **transformation**, but it does not prove that anyone actually ran that transformation as a business process. SSI splits C1a from C1b.

### Error class 3: Confusing good fit with identity
`H_BD_LIKE` achieves 41.8m holdout residual — very good by spatial-data standards. But SSI does NOT allow this to be reported as "file2 IS BD-09". The honest statement is:
> "Encoding family BD_LIKE is strongly supported; formal reference identity is UNCONFIRMED."

### Error class 4: Confusing alignment with admission
Even with a validated operational alignment (VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE), the gate still blocks 33/937 records under DP-02 and refuses DP-03 outright. `is_operationally_aligned` is a convenience observation, not permission.

### Error class 5: Hiding coverage gaps
Only 7.5% of records have positional evidence. SSI requires this to be a primary reported metric, not a footnote.

---

## 4. 938 → 937 Anchor Reconciliation

A duplicate row in the upstream candidate pool (source_record_id `rec_id`, 样本小区, OSM parcel `1988`) caused accepted anchor rows (938) to exceed unique subjects (937). Gate denominator correctly uses 937 unique subjects. No data loss; no hidden exclusion.

---

## 5. Canonical Case Metadata

```yaml
case_id: REAL_XIAN_001_DOUBLE_MISLABEL_AND_DERIVED_COORDINATES
benchmark_family: B1 canonical real case
gold_status: UNADJUDICATED
gold_independence_grade: N/A
note: G1 grade removed by Gate V2-4/M7 — no human adjudication exists (EM3=0). Grade assignment deferred until real adjudication.
temporal_validity: 2026-08
geographic_scope: Xi'an, Shaanxi, China
source_provider: commercial listing dataset (commercial listing dataset)
reference_provider: OpenStreetMap
reference_feature_semantics: residential_polygon_centroid
transformation_function: wgs84_to_gcj02 (Krassovsky a=6378245.0, ee=0.00669342162296594323)
resolver_state_file1: OUT_OF_CANDIDATE_SET
resolver_state_file2: ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
encoding_family_file2: BD_LIKE_STRONGLY_SUPPORTED
reference_identity_file2: UNCONFIRMED
operational_alignment_file2: VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE
mathematical_relation: CONFIRMED (12505/12505 exact at 6-decimal)
production_lineage: SUPPORTED (not confirmed)
anchor_coverage: 937 / 12505 = 7.5%
gate_decisions:
  DP-01: ALLOW=934, BLOCK=3, REVIEW=0 (total=937)
  DP-02: ALLOW=904, BLOCK=33, REVIEW=0 (total=937)
unsupported_uses:
  - DP-03 Fine Geofence (no approved profile, no geofence-specific stability evaluation)
  - Entrance-level routing (reference is centroid)
  - Unanchored records as verified locations
  - file1 as WGS84
regression_tags:
  - label_misuse
  - mathematical_vs_geodetic_conflation
  - good_fit_identity_conflation
  - alignment_authority_conflation
  - coverage_gap_conflation
```

---

## 6. Long-Term Regression Role

This case serves as a **permanent architectural regression test**: any future SSI change that conflates any of the five evidence layers (Raw Declaration / Mathematical Relation / Production Lineage / Reference Identity / Operational Alignment) should fail the canonical-case check.

Specifically, any future implementation that:
- Trusts vendor CRS labels without resolver adjudication
- Claims `IDENTIFIED` based solely on good alignment residuals
- Merges `mathematical relation` with `production lineage`
- Treats `is_operationally_aligned` as a Gate permission
- Omits coverage as a primary metric

...should be caught by a version of this case.

---

## 7. References

- Phase 1R Report: `runs/xian_seed_001/PHASE_1R_REPORT.md`
- Source Passport: `runs/xian_seed_001/passport/SOURCE_PASSPORT.md` (v1.1.0)
- Seed Corpus Manifest: `runs/xian_seed_001/SEED_CORPUS_MANIFEST.md`
- Resolver Results (CLOSE-01/02 applied): `runs/xian_seed_001/resolver/phase_b_results.json`
- Anchor Reconciliation (CLOSE-03): `runs/xian_seed_001/gate/anchor_population_reconciliation.json`
