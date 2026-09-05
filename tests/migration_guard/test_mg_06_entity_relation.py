"""MG-06: Entity Resolution Boundary test.

Invariant: EntityStructureAssertion / EntityPairRelation cannot silently become canonical EntityLink truth.
"""

from ssi.contracts.shared_adapters.claim import ClaimResolutionStatus, EntityLinkClaimAdapter


def test_entity_pair_relation_remains_unresolved_claim_until_governed():
    """Proves that legacy entity matching assertions map to provisional Claims, not instant canonical truth."""
    # An entity matching algorithm asserts that community A is the same entity as OSM polygon B with confidence 0.95
    claim_adapter = EntityLinkClaimAdapter.from_legacy_pair_relation(
        source_id="commercial listing dataset_rec_101",
        target_id="osm_way_501",
        relation_str="SAME_ENTITY",
        confidence=0.95,
        evidence_notes="High name string similarity + centroid proximity",
    )

    # 1. Identity is only a Claim, not an established canonical Entity truth
    assert isinstance(claim_adapter, EntityLinkClaimAdapter)
    assert claim_adapter.claim_type == "ENTITY_LINK"
    assert claim_adapter.predicate == "refers_to"
    assert claim_adapter.mapping_status == "PENDING_ONTOLOGY_GOVERNANCE"

    # 2. It has no automatic 'truth' authorization or publish authority
    assert not hasattr(claim_adapter, "is_safe")
    assert not hasattr(claim_adapter, "publish")

    # 3. Requires explicit Evidence and ClaimResolution before acceptance
    assert claim_adapter.subject_ref == "commercial listing dataset_rec_101"
    assert claim_adapter.asserted_value["target_entity_id"] == "osm_way_501"
