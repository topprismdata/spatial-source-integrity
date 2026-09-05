"""SR-16 — Canonical Behavioral Invariant (Gate V2-1 / B1-001 principle in code).

"Good fit != identity."

A strong BD-like fit with excellent holdout residuals and NO identity provenance
MUST NOT return CanonicalResolutionState.IDENTIFIED. This test is a permanent
canonical invariant upgraded from the REAL_XIAN_001 finding: residual quality can
prove operational alignment, never reference-system identity.
"""

import pytest

from ssi.contracts.shared_adapters.observation import ObservationAdapter
from ssi.resolver.hypothesis import (
    AdditionalEncoding,
    CanonicalResolutionState,
    FormalCRS,
    SpatialReferenceHypothesis,
)
from ssi.resolver.resolver import SpatialReferenceResolver


def _records_with_bd_like_coords():
    """Records whose coordinates behave exactly like BD-09 encoding of known ground truth."""
    from ssi.resolver.transforms import bd09_to_wgs84, wgs84_to_gcj02
    import math

    def wgs_to_bd(lon, lat):
        glon, glat = wgs84_to_gcj02(lon, lat)
        z = math.sqrt(glon ** 2 + glat ** 2) + 0.00002 * math.sin(glat * math.pi * 3000.0 / 180.0)
        theta = math.atan2(glat, glon) + 0.000003 * math.cos(glon * math.pi * 3000.0 / 180.0)
        return z * math.cos(theta) + 0.0065, z * math.sin(theta) + 0.006

    grounds = [(108.95 + i * 0.01, 34.27 + i * 0.01) for i in range(4)]
    records = []
    for i, (glon, glat) in enumerate(grounds):
        blon, blat = wgs_to_bd(glon, glat)
        records.append(ObservationAdapter(
            observation_id=f"o_{i}",
            source_asset_id="a1",
            source_record_id=f"rec_{i}",
            geometry_wkt=f"POINT({blon} {blat})",
        ))
        # paired reference anchor in true WGS84
    anchors = [
        {"source_id": f"rec_{i}", "ref_lon": g[0], "ref_lat": g[1]}
        for i, g in enumerate(grounds)
    ]
    return records, anchors


def test_sr_16_strong_bd_like_fit_without_provenance_must_not_identify():
    """Canonical invariant: excellent BD-like fit + holdout + zero provenance != IDENTIFIED."""
    records, anchors = _records_with_bd_like_coords()
    resolver = SpatialReferenceResolver()
    hyp_bd = SpatialReferenceHypothesis(
        hypothesis_id="H_BD_LIKE",
        formal_crs=FormalCRS.WGS84,
        encoding=AdditionalEncoding.BD_LIKE,
    )

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_bd],
        fit_anchors=anchors[:2],
        holdout_anchors=anchors[2:],
        adequacy_threshold_meters=50.0,
        # identity_provenance deliberately absent — no metadata, no production script
    )

    # MUST NOT return IDENTIFIED
    assert res.resolution_state != CanonicalResolutionState.IDENTIFIED
    assert res.resolution_state == CanonicalResolutionState.ALIGNABLE_BUT_IDENTITY_UNCONFIRMED
    # Operational alignment may be validated...
    assert res.is_operationally_aligned is True
    # ...and the encoding family is strongly supported...
    assert res.selected_hypothesis.encoding == AdditionalEncoding.BD_LIKE
    # ...but reference identity stays UNCONFIRMED and the limitation is explicit.
    assert res.alignment_limitations is not None
    assert "UNCONFIRMED" in res.alignment_limitations


def test_sr_16b_identity_provenance_is_the_only_path_to_identified():
    """IDENTIFIED requires verified identity_provenance; fit quality alone never suffices."""
    records, anchors = _records_with_bd_like_coords()
    resolver = SpatialReferenceResolver()
    hyp_bd = SpatialReferenceHypothesis(
        hypothesis_id="H_BD_LIKE",
        formal_crs=FormalCRS.WGS84,
        encoding=AdditionalEncoding.BD_LIKE,
    )

    res = resolver.resolve(
        records=records,
        candidate_hypotheses=[hyp_bd],
        fit_anchors=anchors[:2],
        holdout_anchors=anchors[2:],
        adequacy_threshold_meters=50.0,
        identity_provenance={
            "verified": True,
            "description": "Vendor API specification explicitly declares BD-09 output coordinates.",
        },
    )
    assert res.resolution_state == CanonicalResolutionState.IDENTIFIED
    assert res.alignment_state == "IDENTIFIED_WITH_PROVENANCE"
