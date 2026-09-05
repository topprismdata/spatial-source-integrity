"""SpatialReferenceResolver: resolves H = (C, R, E, K) hypotheses against fit and holdout evidence."""

from __future__ import annotations

import math
import uuid
from typing import Any, Dict, List, Optional, Tuple
import pyproj

from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.detectors.d01_schema_parse import D01SchemaParseDetector
from ssi.resolver.hypothesis import (
    AdditionalEncoding,
    CandidateEvaluationResult,
    CanonicalResolutionState,
    CorruptionState,
    FormalCRS,
    Representation,
    ResolutionResult,
    SpatialReferenceHypothesis,
)
from ssi.resolver.transforms import (
    apply_axis_swap,
    apply_empirical_shift,
    apply_missing_leading_digit,
    bd09_to_wgs84,
    gcj02_to_wgs84,
)


class SpatialReferenceResolver:
    """Resolves spatial reference interpretation without black-box guessing.
    
    Invariants:
    1. Evaluates candidates across 4 axes: Relative Preference, Absolute Adequacy, Holdout Generalization, Identity.
    2. Supports OUT_OF_CANDIDATE_SET when all candidates fail absolute adequacy.
    3. WGS84 and CGCS2000 are INDISTINGUISHABLE_AT_CURRENT_RESOLUTION when residual difference < 0.1m.
    4. Separates Reference Identity from Operational Alignment.
    """

    def __init__(self):
        self._geod = pyproj.Geod(ellps="WGS84")

    def transform_point(self, lon: float, lat: float, hyp: SpatialReferenceHypothesis) -> Tuple[float, float]:
        """Applies hypothesis transformations in order: Corruption fix -> Representation -> Encoding to WGS84."""
        cur_lon, cur_lat = lon, lat

        # 1. Corruption fix (K)
        if hyp.corruption == CorruptionState.MISSING_LEADING_DIGIT:
            cur_lon, cur_lat = apply_missing_leading_digit(cur_lon, cur_lat)
        elif hyp.corruption == CorruptionState.DECIMAL_SHIFT:
            scale = hyp.parameters.get("scale", 10.0)
            cur_lon, cur_lat = cur_lon / scale, cur_lat / scale

        # 2. Representation & Axis (R)
        if hyp.representation == Representation.LAT_LON:
            cur_lon, cur_lat = apply_axis_swap(cur_lon, cur_lat)

        # 3. Additional Encoding (E)
        if hyp.encoding == AdditionalEncoding.GCJ_LIKE:
            cur_lon, cur_lat = gcj02_to_wgs84(cur_lon, cur_lat)
        elif hyp.encoding == AdditionalEncoding.BD_LIKE:
            cur_lon, cur_lat = bd09_to_wgs84(cur_lon, cur_lat)
        elif hyp.encoding == AdditionalEncoding.EMPIRICAL_TRANSFORM:
            d_lon = hyp.parameters.get("d_lon", 0.0)
            d_lat = hyp.parameters.get("d_lat", 0.0)
            cur_lon, cur_lat = apply_empirical_shift(cur_lon, cur_lat, d_lon, d_lat)

        return cur_lon, cur_lat

    def _calc_residuals(
        self,
        records_dict: Dict[str, Tuple[float, float]],
        anchors: List[Dict[str, Any]],
        hyp: SpatialReferenceHypothesis,
    ) -> List[float]:
        """Calculates geodesic residual distances for a set of anchors under a hypothesis."""
        residuals = []
        for anchor in anchors:
            rec_id = anchor["source_id"]
            if rec_id not in records_dict:
                continue
            raw_lon, raw_lat = records_dict[rec_id]
            tf_lon, tf_lat = self.transform_point(raw_lon, raw_lat, hyp)
            if abs(tf_lat) > 90.0 or abs(tf_lon) > 180.0:
                residuals.append(1e8)
                continue
            try:
                _, _, dist = self._geod.inv(tf_lon, tf_lat, anchor["ref_lon"], anchor["ref_lat"])
                if math.isnan(dist):
                    dist = 1e8
            except Exception:
                dist = 1e8
            residuals.append(dist)
        return residuals

    def resolve(
        self,
        records: List[ObservationAdapter],
        candidate_hypotheses: List[SpatialReferenceHypothesis],
        fit_anchors: List[Dict[str, Any]],
        holdout_anchors: List[Dict[str, Any]],
        declared_crs: Optional[str] = None,
        adequacy_threshold_meters: float = 50.0,
        identity_provenance: Optional[Dict[str, Any]] = None,
    ) -> ResolutionResult:
        """Resolves reference hypotheses.

        Gate V2-1 invariant: `CanonicalResolutionState.IDENTIFIED` is returned ONLY when
        `identity_provenance` evidence (provider metadata, production script, authoritative
        declaration traceable upstream) is supplied. Residual fit quality — no matter how
        strong — can never produce IDENTIFIED ("good fit != identity").
        Without provenance, an adequate fit yields ALIGNABLE_BUT_IDENTITY_UNCONFIRMED.
        """
        resolution_id = f"res_{uuid.uuid4().hex[:8]}"

        # Parse records
        records_dict: Dict[str, Tuple[float, float]] = {}
        for record in records:
            raw_x, raw_y, _ = D01SchemaParseDetector.extract_raw_coords(record)
            if raw_x is not None and raw_y is not None:
                try:
                    records_dict[record.source_record_id] = (float(str(raw_x)), float(str(raw_y)))
                except (ValueError, TypeError):
                    continue

        if not records_dict or not fit_anchors:
            return ResolutionResult(
                resolution_id=resolution_id,
                resolution_state=CanonicalResolutionState.INSUFFICIENT_EVIDENCE,
                rationale="Insufficient records or fit anchors to evaluate reference hypotheses.",
            )

        evaluations: List[CandidateEvaluationResult] = []

        for hyp in candidate_hypotheses:
            fit_res = sorted(self._calc_residuals(records_dict, fit_anchors, hyp))
            hold_res = sorted(self._calc_residuals(records_dict, holdout_anchors, hyp)) if holdout_anchors else fit_res

            if not fit_res or not hold_res:
                continue

            fit_p50 = fit_res[len(fit_res) // 2]
            fit_p95 = fit_res[int(len(fit_res) * 0.95)]
            hold_p50 = hold_res[len(hold_res) // 2]
            hold_p95 = hold_res[int(len(hold_res) * 0.95)]
            gross_errors = sum(1 for r in hold_res if r > 500.0) / len(hold_res)

            is_adequate = hold_p50 <= adequacy_threshold_meters

            evaluations.append(
                CandidateEvaluationResult(
                    hypothesis=hyp,
                    fit_residual_p50_meters=round(fit_p50, 2),
                    fit_residual_p95_meters=round(fit_p95, 2),
                    holdout_residual_p50_meters=round(hold_p50, 2),
                    holdout_residual_p95_meters=round(hold_p95, 2),
                    gross_error_rate=round(gross_errors, 3),
                    is_adequately_aligned=is_adequate,
                    relative_preference_rank=0,  # ranked below
                )
            )

        if not evaluations:
            return ResolutionResult(
                resolution_id=resolution_id,
                resolution_state=CanonicalResolutionState.INSUFFICIENT_EVIDENCE,
                rationale="No candidate hypotheses could be evaluated.",
            )

        # Sort by holdout P50 residual (Relative Preference)
        evaluations.sort(key=lambda e: e.holdout_residual_p50_meters)
        for rank, ev in enumerate(evaluations, start=1):
            # Update rank
            object.__setattr__(ev, "relative_preference_rank", rank)

        best = evaluations[0]

        # 1. Check OUT_OF_CANDIDATE_SET
        # Invariant: If all candidates fail absolute adequacy, output OUT_OF_CANDIDATE_SET
        if not any(ev.is_adequately_aligned for ev in evaluations):
            return ResolutionResult(
                resolution_id=resolution_id,
                resolution_state=CanonicalResolutionState.OUT_OF_CANDIDATE_SET,
                selected_hypothesis=None,
                candidate_evaluations=evaluations,
                is_operationally_aligned=False,
                rationale=f"All {len(evaluations)} hypotheses failed absolute adequacy threshold ({adequacy_threshold_meters}m). Best holdout P50 was {best.holdout_residual_p50_meters}m.",
            )

        # 2. Check WGS84 vs CGCS2000 indistinguishability
        # If top 2 are WGS84 and CGCS2000 and difference < 0.1m
        if len(evaluations) >= 2:
            top_hyp_names = {evaluations[0].hypothesis.formal_crs, evaluations[1].hypothesis.formal_crs}
            if FormalCRS.WGS84 in top_hyp_names and FormalCRS.CGCS2000 in top_hyp_names:
                diff = abs(evaluations[0].holdout_residual_p50_meters - evaluations[1].holdout_residual_p50_meters)
                if diff <= 0.1 and evaluations[0].is_adequately_aligned:
                    return ResolutionResult(
                        resolution_id=resolution_id,
                        resolution_state=CanonicalResolutionState.INDISTINGUISHABLE_AT_CURRENT_RESOLUTION,
                        selected_hypothesis=evaluations[0].hypothesis,
                        candidate_evaluations=evaluations,
                        is_operationally_aligned=True,
                        alignment_operation_chain=["WGS84_CGCS2000_GEOGRAPHIC_ALIGNMENT"],
                        holdout_p50_residual_meters=evaluations[0].holdout_residual_p50_meters,
                        rationale="WGS84 and CGCS2000 candidates are indistinguishable at current evidence resolution (residual delta <= 0.1m).",
                    )

        # 3. Check Empirical Alignment (identity unconfirmed, but operational alignment achieved)
        if best.hypothesis.encoding == AdditionalEncoding.EMPIRICAL_TRANSFORM:
            return ResolutionResult(
                resolution_id=resolution_id,
                resolution_state=CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED,
                selected_hypothesis=best.hypothesis,
                candidate_evaluations=evaluations,
                is_operationally_aligned=True,
                alignment_operation_chain=["EMPIRICAL_LOCAL_AFFINE_SHIFT"],
                holdout_p50_residual_meters=best.holdout_residual_p50_meters,
                rationale=f"Empirical alignment achieved holdout residual P50={best.holdout_residual_p50_meters}m, but formal CRS identity remains unconfirmed.",
            )

        # 4. Adequate encoding match — identity remains UNCONFIRMED without provenance.
        # Gate V2-1: "good fit != identity". IDENTIFIED requires identity_provenance.
        if identity_provenance and identity_provenance.get("verified", False):
            return ResolutionResult(
                resolution_id=resolution_id,
                resolution_state=CanonicalResolutionState.IDENTIFIED,
                selected_hypothesis=best.hypothesis,
                candidate_evaluations=evaluations,
                is_operationally_aligned=True,
                alignment_operation_chain=[f"{best.hypothesis.encoding.value}_TO_WGS84"],
                holdout_p50_residual_meters=best.holdout_residual_p50_meters,
                alignment_state="IDENTIFIED_WITH_PROVENANCE",
                validation_scope="HOLDOUT",
                holdout_p95_residual_meters=best.holdout_residual_p95_meters,
                holdout_gross_error_rate=best.gross_error_rate,
                rationale=(
                    f"Hypothesis '{best.hypothesis.hypothesis_id}' IDENTIFIED via provenance: "
                    f"{identity_provenance.get('description', 'provider metadata')}. "
                    f"Holdout P50={best.holdout_residual_p50_meters}m."
                ),
            )

        return ResolutionResult(
            resolution_id=resolution_id,
            resolution_state=CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED,
            selected_hypothesis=best.hypothesis,
            candidate_evaluations=evaluations,
            is_operationally_aligned=True,
            alignment_operation_chain=[f"{best.hypothesis.encoding.value}_TO_WGS84"],
            holdout_p50_residual_meters=best.holdout_residual_p50_meters,
            alignment_state="VALIDATED_WITHIN_CURRENT_EVIDENCE_ENVELOPE",
            alignment_target="WGS84",
            validation_scope="HOLDOUT" if holdout_anchors else "FIT",
            holdout_p95_residual_meters=best.holdout_residual_p95_meters,
            holdout_gross_error_rate=best.gross_error_rate,
            alignment_limitations=(
                "Encoding family strongly supported by residual evidence; formal reference "
                "identity UNCONFIRMED — no identity provenance supplied. Good fit never equals identity."
            ),
            rationale=(
                f"Hypothesis '{best.hypothesis.hypothesis_id}' adequately aligned "
                f"(holdout P50={best.holdout_residual_p50_meters}m) but identity provenance "
                f"is absent; state is ALIGNABLE_BUT_IDENTITY_UNCONFIRMED, never IDENTIFIED."
            ),
        )
