"""QualityMeasure: TopPrism Measure Registry definitions aligning with ISO 19157-1:2023."""

from __future__ import annotations

from typing import Dict
from pydantic import BaseModel, ConfigDict, Field


class QualityMeasureDefinition(BaseModel):
    """Formal definition of a geographic data quality measure."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    measure_id: str = Field(description="Unique measure ID (e.g. QM-D01-PARSE)")
    measure_version: str = Field(default="1.0.0", description="Version of calculation formula")
    name: str = Field(description="Canonical measure name")
    iso_element: str = Field(
        description="ISO 19157 element: Completeness | Logical Consistency | Positional Accuracy | Temporal Quality | Thematic Accuracy | Metaquality",
    )
    unit: str = Field(default="", description="Unit of measurement")
    evaluation_method: str = Field(description="Detector algorithm name")
    description: str = Field(description="Detailed measurement formula and meaning")


# Canonical TopPrism Quality Measure Registry
MEASURE_REGISTRY: Dict[str, QualityMeasureDefinition] = {
    # D01: Coordinate Schema & Parse
    "coordinate_presence": QualityMeasureDefinition(
        measure_id="QM-D01-PRESENCE",
        measure_version="1.0.0",
        name="coordinate_presence",
        iso_element="Completeness",
        unit="boolean",
        evaluation_method="D01_SchemaParse",
        description="Checks presence of coordinate fields in record.",
    ),
    "coordinate_schema": QualityMeasureDefinition(
        measure_id="QM-D01-PARSE",
        measure_version="1.0.0",
        name="coordinate_schema",
        iso_element="Logical Consistency",
        unit="status",
        evaluation_method="D01_SchemaParse",
        description="Verifies numeric parseability of longitude and latitude fields.",
    ),
    "dimension_consistency": QualityMeasureDefinition(
        measure_id="QM-D01-DIM",
        measure_version="1.0.0",
        name="dimension_consistency",
        iso_element="Logical Consistency",
        unit="status",
        evaluation_method="D01_SchemaParse",
        description="Checks dimensionality (2D vs 3D) consistency.",
    ),
    # D02: Geographic Range & Representation
    "geographic_range": QualityMeasureDefinition(
        measure_id="QM-D02-RANGE",
        measure_version="1.0.0",
        name="geographic_range",
        iso_element="Positional Accuracy",
        unit="status",
        evaluation_method="D02_RangeRepresentation",
        description="Checks coordinate bounds against legal representation limits (lon [-180, 180], lat [-90, 90]).",
    ),
    "axis_interpretation": QualityMeasureDefinition(
        measure_id="QM-D02-AXIS",
        measure_version="1.0.0",
        name="axis_interpretation",
        iso_element="Logical Consistency",
        unit="candidate",
        evaluation_method="D02_RangeRepresentation",
        description="Evaluates axis order hypotheses (lon/lat vs lat/lon).",
    ),
    # D03: Precision Fingerprint
    "decimal_precision": QualityMeasureDefinition(
        measure_id="QM-D03-PRECISION",
        measure_version="1.0.0",
        name="decimal_precision",
        iso_element="Metaquality",
        unit="decimal_places",
        evaluation_method="D03_PrecisionFingerprint",
        description="Quantifies significant decimal places in coordinate representation.",
    ),
    # D04: Coordinate Reuse & Fallback Signal
    "coordinate_reuse_count": QualityMeasureDefinition(
        measure_id="QM-D04-REUSE",
        measure_version="1.0.0",
        name="coordinate_reuse_count",
        iso_element="Logical Consistency",
        unit="count",
        evaluation_method="D04_CoordinateReuse",
        description="Counts occurrences of identical coordinate pairs across records in dataset.",
    ),
    # D05: Administrative Consistency
    "admin_containment": QualityMeasureDefinition(
        measure_id="QM-D05-CONTAINMENT",
        measure_version="1.0.0",
        name="admin_containment",
        iso_element="Thematic Accuracy",
        unit="status",
        evaluation_method="D05_AdminConsistency",
        description="Tests geographic containment of point within declared administrative polygons.",
    ),
    "boundary_proximity_meters": QualityMeasureDefinition(
        measure_id="QM-D05-PROXIMITY",
        measure_version="1.0.0",
        name="boundary_proximity_meters",
        iso_element="Positional Accuracy",
        unit="meters",
        evaluation_method="D05_AdminConsistency",
        description="Shortest distance from point to nearest relevant administrative boundary.",
    ),
    # D06: Intrinsic Spatial Outlier
    "intrinsic_outlier_score": QualityMeasureDefinition(
        measure_id="QM-D06-OUTLIER",
        measure_version="1.0.0",
        name="intrinsic_outlier_score",
        iso_element="Positional Accuracy",
        unit="score",
        evaluation_method="D06_IntrinsicSpatialOutlier",
        description="Robust spatial isolation metric relative to peer distribution without external reference.",
    ),
    # D07: Declared Spatial Reference Consistency
    "declared_reference_consistency": QualityMeasureDefinition(
        measure_id="QM-D07-REF-CONSISTENCY",
        measure_version="1.0.0",
        name="declared_reference_consistency",
        iso_element="Logical Consistency",
        unit="status",
        evaluation_method="D07_DeclaredReferenceConsistency",
        description="Checks declared CRS metadata against observed evidence and area of use.",
    ),
    # D08: External Reference Residual
    "positional_residual": QualityMeasureDefinition(
        measure_id="QM-D08-RESIDUAL",
        measure_version="1.0.0",
        name="positional_residual",
        iso_element="Positional Accuracy",
        unit="meters",
        evaluation_method="D08_ExternalReferenceResidual",
        description="Geodesic distance between subject point and matched external reference point.",
    ),
    # D09: Batch & Pipeline Consistency
    "pipeline_heterogeneity_score": QualityMeasureDefinition(
        measure_id="QM-D09-HETEROGENEITY",
        measure_version="1.0.0",
        name="pipeline_heterogeneity_score",
        iso_element="Logical Consistency",
        unit="score",
        evaluation_method="D09_PipelineConsistency",
        description="Quantifies evidence of multiple mixed production pipelines within a source asset.",
    ),
}
