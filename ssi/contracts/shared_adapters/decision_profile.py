"""DecisionProfile shared adapter projecting generic DecisionProfile concept."""

from __future__ import annotations

from typing import ClassVar, Optional
from pydantic import Field

from ssi.contracts.shared_adapters.base import PrismSharedAdapter
from ssi.contracts.spatial.spatial_decision_requirements import SpatialDecisionRequirements


class DecisionProfileAdapter(PrismSharedAdapter):
    """Runtime projection of generic DecisionProfile.
    
    A versioned contract specifying what a particular business decision requires.
    """

    _canonical_uri: ClassVar[str] = "prism://ontology/core/DecisionProfile#provisional"
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
    mapping_status: ClassVar[str] = "PENDING_ONTOLOGY_GOVERNANCE"

    profile_id: str = Field(description="Profile identifier (e.g. DP-01, DP-02, DP-03)")
    version: str = Field(description="Profile version (e.g. 1.0.0)")
    name: str = Field(description="Human readable profile name")
    target_decision_consumer: str = Field(description="Target downstream consumer system or solver")
    risk_class: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    spatial_requirements: SpatialDecisionRequirements = Field(
        description="Explicit spatial tolerances and constraints",
    )
    allow_inferential_evidence: bool = Field(
        default=False,
        description="Whether population-level sample evidence may authorize unsampled records",
    )
    description: str = Field(default="", description="Detailed business purpose and context")
    fixture_only: bool = Field(
        default=False,
        description="True when thresholds are synthetic fixture values (threshold_provenance=EXPERIMENTAL_FIXTURE). CI forbids fixture_only profiles in production paths.",
    )
    threshold_provenance: str = Field(
        default="UNSPECIFIED",
        description="EXPERIMENTAL_FIXTURE | CUSTOMER_APPROVED | BENCHMARK_DERIVED. Required for every numeric tolerance.",
    )

    @classmethod
    def create_dp01_city_analytics(
        cls,
        version: str = "1.0.0",
        *,
        max_acceptable_residual_meters: float,
        threshold_provenance: str,
    ) -> DecisionProfileAdapter:
        """DP-01 City Analytics: Requires stable city assignment, coarse positional adequacy.

        Gate V2-3 / H1: `max_acceptable_residual_meters` has NO default. Callers must
        supply the threshold and its provenance explicitly (e.g. EXPERIMENTAL_FIXTURE).
        """
        return cls(
            profile_id="DP-01",
            version=version,
            name="City Analytics",
            target_decision_consumer="MacroCityAggregator",
            risk_class="LOW",
            threshold_provenance=threshold_provenance,
            fixture_only=(threshold_provenance == "EXPERIMENTAL_FIXTURE"),
            spatial_requirements=SpatialDecisionRequirements(
                allowed_crs_families=["WGS84", "CGCS2000"],
                require_formal_crs_identity=False,
                require_operational_alignment=True,
                max_acceptable_residual_meters=max_acceptable_residual_meters,
                require_stable_city_assignment=True,
                require_stable_district_assignment=False,
                require_inside_geofence=False,
                require_stability=True,
                stability_scope=["city_assignment"],
            ),
            allow_inferential_evidence=False,
            description="Macro city-level counting, reporting and market segmentation.",
        )


    @classmethod
    def create_dp02_visit_planning(
        cls,
        version: str = "1.0.0",
        *,
        max_residual_meters: float,
        threshold_provenance: str,
    ) -> DecisionProfileAdapter:
        """DP-02 Visit Planning: Requires routing adequacy and stable district assignment.

        Gate V2-3 / H1: threshold and provenance are required explicitly (no default).
        """
        return cls(
            profile_id="DP-02",
            version=version,
            name="Visit Planning",
            target_decision_consumer="FieldVisitPlanner",
            risk_class="MEDIUM",
            threshold_provenance=threshold_provenance,
            fixture_only=(threshold_provenance == "EXPERIMENTAL_FIXTURE"),
            spatial_requirements=SpatialDecisionRequirements(
                allowed_crs_families=["WGS84", "CGCS2000"],
                require_formal_crs_identity=False,
                require_operational_alignment=True,
                max_acceptable_residual_meters=max_residual_meters,
                require_stable_city_assignment=True,
                require_stable_district_assignment=True,
                require_inside_geofence=False,
                require_stability=True,
                stability_scope=["city_assignment", "district_assignment"],
            ),
            allow_inferential_evidence=False,
            description="Sales representative field routing, stop scheduling and territory assignment.",
        )

    @classmethod
    def create_dp03_fine_geofence(
        cls,
        version: str = "1.0.0",
        *,
        max_residual_meters: float,
        threshold_provenance: str,
    ) -> DecisionProfileAdapter:
        """DP-03 Fine Geofence: Requires high positional accuracy and inside-fence stability.

        Gate V2-3 / H1: threshold and provenance are required explicitly (no default).
        """
        return cls(
            profile_id="DP-03",
            version=version,
            name="Fine Geofence",
            target_decision_consumer="RealtimeGeofenceEngine",
            risk_class="HIGH",
            threshold_provenance=threshold_provenance,
            fixture_only=(threshold_provenance == "EXPERIMENTAL_FIXTURE"),
            spatial_requirements=SpatialDecisionRequirements(
                allowed_crs_families=["WGS84", "CGCS2000"],
                require_formal_crs_identity=True,
                require_operational_alignment=True,
                max_acceptable_residual_meters=max_residual_meters,
                require_stable_city_assignment=True,
                require_stable_district_assignment=True,
                require_inside_geofence=True,
                require_stability=True,
                stability_scope=["geofence_membership"],
            ),
            allow_inferential_evidence=False,
            description="Fine-grained automated customer geofencing, boundary check-in and delivery boundary verification.",
        )
