"""EG-04: UsageLimit Enforcement test.

Invariant:
- ALLOW_WITH_LIMITS + consumer incompatible -> publication blocked (count = 0).
- ALLOW_WITH_LIMITS + consumer supports limits -> published with limits preserved.
"""

from ssi.admission.gate.executor import GateExecutor
from ssi.admission.publisher.publisher import SpatialAdmissionPublisher
from ssi.contracts.runtime.consumer_capability import ConsumerCapability
from ssi.contracts.runtime.gate_decision import AdmissionAction
from ssi.contracts.runtime.usage_limit import UsageLimit


def test_usage_limit_blocks_incompatible_consumer_and_allows_compatible(
    dp01_profile,
    standard_gate_policy,
    standard_coverage_manifest,
    clean_evaluation_result,
):
    """Proves that ALLOW_WITH_LIMITS strictly enforces consumer capability."""
    routing_prohibited_limit = UsageLimit(
        limit_id="limit_no_routing",
        limit_type="OPERATION_RESTRICTION",
        parameters={"prohibited_ops": ["routing"]},
        enforceable=True,
        description="Coarse location: prohibited from vehicle route dispatching",
    )

    candidate_geometries = {
        "rec_101": {"geometry_wkt": "POINT(108.95 34.27)", "crs": "EPSG:4326"},
    }

    # Consumer A performs routing -> incompatible with 'no routing' limit
    incompatible_router = ConsumerCapability(
        consumer_id="FieldRouter",
        consumer_version="1.0.0",
        name="Field Router",
        supported_operations=["aggregation", "routing"],
        supports_usage_limits=True,
    )

    # Consumer B performs only aggregation -> compatible
    compatible_aggregator = ConsumerCapability(
        consumer_id="CityAggregator",
        consumer_version="1.0.0",
        name="City Aggregator",
        supported_operations=["aggregation"],
        supports_usage_limits=True,
    )

    # 1. Evaluate with incompatible consumer -> Gate blocks it at GateExecutor
    decision_incompatible = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=clean_evaluation_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
        consumer_capability=incompatible_router,
        candidate_usage_limits=[routing_prohibited_limit],
    )
    assert decision_incompatible.is_blocked()

    # 2. Evaluate with compatible consumer -> Gate admits ALLOW_WITH_LIMITS
    decision_compatible = GateExecutor.evaluate_admission(
        subject_id="rec_101",
        candidate_representation_id="cand_101",
        evaluation_result=clean_evaluation_result,
        coverage_manifest=standard_coverage_manifest,
        decision_profile=dp01_profile,
        gate_policy=standard_gate_policy,
        consumer_capability=compatible_aggregator,
        candidate_usage_limits=[routing_prohibited_limit],
    )
    assert decision_compatible.action == AdmissionAction.ALLOW_WITH_LIMITS
    assert len(decision_compatible.applied_usage_limits) == 1

    # 3. Publish to compatible consumer -> published and limit preserved
    snapshot_ok = SpatialAdmissionPublisher.publish_snapshot(
        consumer=compatible_aggregator,
        decision_profile=dp01_profile,
        gate_decisions=[decision_compatible],
        candidate_geometries=candidate_geometries,
    )
    assert len(snapshot_ok.projections) == 1
    assert snapshot_ok.projections[0].usage_limits[0].limit_id == "limit_no_routing"

    # 4. Attempt to publish compatible decision to incompatible consumer -> publisher filters it out
    snapshot_blocked = SpatialAdmissionPublisher.publish_snapshot(
        consumer=incompatible_router,
        decision_profile=dp01_profile,
        gate_decisions=[decision_compatible],
        candidate_geometries=candidate_geometries,
    )
    assert len(snapshot_blocked.projections) == 0
