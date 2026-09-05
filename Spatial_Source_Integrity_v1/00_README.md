# Spatial Source Integrity v1.0 — Normative Design Package

**Project:** TopPrism Spatial Source Integrity  
**Parent capability:** `spatial-decision-intelligence`  
**Package status:** Architecture Design Baseline  
**Engineering status:** Not yet Engineering Baseline  
**Packaging date:** 2026-09-05

## Purpose
This package consolidates the Spatial Source Integrity specifications into an implementation-facing **design-only** normative set.

It defines semantic ownership, evaluation/evidence contracts, HITL governance, learning boundaries, repair governance, decision-specific admission, publication/lifecycle control, benchmark and traceability. It does **not** prescribe implementation code, databases, message buses, frameworks or concrete algorithm thresholds.

## Precedence
If documents conflict:
1. `docs/01_SPATIAL_SOURCE_INTEGRITY_V1_BASELINE_TRIPLE_REVIEW.md`
2. Topic specifications in `docs/`
3. Historical/superseded material in `historical/`

## Final normalized terminology
- Canonical state: `SpatialWorldState → DecisionReadyProjection → TrustedSpatialSnapshot`.
- `TrustedProjection` is deprecated as a canonical name.
- `GateDecision` evaluates source/candidate state and then produces `DecisionReadyProjection`.
- Admission: `ALLOW / ALLOW_WITH_LIMITS / REVIEW / BLOCK_FOR_PROFILE`.
- `QUARANTINE_SCOPE` is a governance disposition, not an admission action.
- `Claim / Assertion` is mandatory shared semantics.
- `EvaluationCoverageManifest` is mandatory.
- Sample evidence cannot silently become record-level authorization.
- Human review is first-class; human judgment is evidence, not automatic truth.
- Learning is offline/governed and cannot bypass hard Gate constraints.
- Raw source is immutable.
- Production consumption requires an ACTIVE production snapshot and a valid profile-specific GateDecision.

## Core invariant
> **No evidence-backed, profile-specific, human-governed valid GateDecision → no DecisionReadyProjection → no production TrustedSpatialSnapshot → no consumer access.**

Learning invariant:
> **No benchmarked and governed promotion → no learned behavior may change production semantics.**

## Scope
v1 is Point-first for external structured spatial data: POI, stores, communities, customers, address points and geocoded records.

Core trust dimensions:
- Coordinate Trust
- Location Trust
- Semantic-Spatial Trust
- Source / Provenance Trust

Explicitly outside v1 core: universal GIS QA, generic raster/network/polygon QA, automatic truth reconstruction, unconstrained repair, general MLOps, general annotation platform and autonomous production RL.

See `MANIFEST.md` for file order and `SHA256SUMS.txt` for integrity hashes.
