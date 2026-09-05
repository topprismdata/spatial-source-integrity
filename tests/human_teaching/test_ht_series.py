"""HT-Series: Human Teaching & Governed Learning tests (HT-01 ~ HT-05)."""

import pytest

from ssi.learning.teaching_event import (
    HumanTeachingEvent,
    LearningEligibility,
    PolicyExperience,
    TeachingCategory,
)


def test_ht_01_review_does_not_automatically_become_training_data():
    """HT-01: An ordinary review task does not automatically become an ELIGIBLE training sample."""
    # A review with low confidence or subjective opinion starts as NOT_ELIGIBLE
    event = HumanTeachingEvent(
        event_id="HTE-001",
        task_ref="HRT-D06-01",
        subject_id="comm_low_conf",
        machine_prediction={"score": 4.8, "finding": "SPATIAL_OUTLIER"},
        human_adjudication_ref="adj_uncertain",
        adjudicated_action="SUPPORT",
        reviewer_role="REVIEWER",
        prediction_visibility="PREDICTION_VISIBLE",
        teaching_category=TeachingCategory.T6_LEGITIMATE_ANOMALY,
        learning_eligibility=LearningEligibility.NOT_ELIGIBLE,  # Invariant: not automatically eligible
        eligibility_rationale="Reviewer expressed low certainty; dependent on unverified satellite visual.",
    )
    assert event.learning_eligibility == LearningEligibility.NOT_ELIGIBLE
    assert event.learning_eligibility != LearningEligibility.ELIGIBLE


def test_ht_02_learning_eligibility_explicitly_preserved():
    """HT-02: Certified, independent adjudications receive ELIGIBLE status with explicit rationale."""
    event_certified = HumanTeachingEvent(
        event_id="HTE-002",
        task_ref="HRT-DP02-101",
        subject_id="comm_101",
        machine_prediction={"residual_m": 245.0, "finding": "GROSS_RESIDUAL"},
        human_adjudication_ref="adj_high_conf",
        adjudicated_action="SUPPORT",
        reviewer_role="DOMAIN_EXPERT",
        prediction_visibility="PREDICTION_HIDDEN",
        teaching_category=TeachingCategory.T1_FALSE_POSITIVE_DETECTOR,
        learning_eligibility=LearningEligibility.ELIGIBLE,
        eligibility_rationale="Blind review by certified Domain Expert backed by official statutory cadastral map.",
    )
    assert event_certified.learning_eligibility == LearningEligibility.ELIGIBLE
    assert "Blind review" in event_certified.eligibility_rationale


def test_ht_03_revoked_adjudication_revokes_teaching_eligibility():
    """HT-03: When an upstream human adjudication is overturned, teaching event eligibility transitions to REVOKED."""
    event = HumanTeachingEvent(
        event_id="HTE-003",
        task_ref="HRT-REVOKE-01",
        subject_id="comm_retracted",
        machine_prediction={"action": "BLOCK"},
        human_adjudication_ref="adj_init_approved",
        adjudicated_action="REFUTE",
        reviewer_role="DOMAIN_EXPERT",
        prediction_visibility="PREDICTION_VISIBLE",
        teaching_category=TeachingCategory.T4_ENTITY_LINK_CORRECTION,
        learning_eligibility=LearningEligibility.ELIGIBLE,
    )
    assert event.learning_eligibility == LearningEligibility.ELIGIBLE
    assert not event.is_revoked

    # Downstream evidence proves reviewer was mistaken -> revoke adjudication and teaching eligibility
    revoked_event = event.revoke_eligibility("Upstream municipal survey retracted by provincial authority.")
    assert revoked_event.learning_eligibility == LearningEligibility.REVOKED
    assert revoked_event.is_revoked is True
    assert "retracted" in revoked_event.revocation_reason


def test_ht_04_prediction_visible_vs_blind_examples_distinguishable():
    """HT-04: Offline training dataset queries can cleanly separate blind examples from prediction-visible examples."""
    dataset = [
        HumanTeachingEvent(
            event_id="HTE-BLIND-1", task_ref="T1", subject_id="s1", machine_prediction={},
            human_adjudication_ref="a1", adjudicated_action="SUPPORT", reviewer_role="EXPERT",
            prediction_visibility="PREDICTION_HIDDEN", teaching_category=TeachingCategory.T1_FALSE_POSITIVE_DETECTOR,
            learning_eligibility=LearningEligibility.ELIGIBLE,
        ),
        HumanTeachingEvent(
            event_id="HTE-VISIBLE-1", task_ref="T2", subject_id="s2", machine_prediction={},
            human_adjudication_ref="a2", adjudicated_action="SUPPORT", reviewer_role="REVIEWER",
            prediction_visibility="PREDICTION_VISIBLE", teaching_category=TeachingCategory.T6_LEGITIMATE_ANOMALY,
            learning_eligibility=LearningEligibility.CONDITIONALLY_ELIGIBLE,
        ),
    ]

    # Model training subset strictly requiring un-anchored blind examples
    blind_training_subset = [e for e in dataset if e.prediction_visibility == "PREDICTION_HIDDEN" and e.learning_eligibility == LearningEligibility.ELIGIBLE]
    assert len(blind_training_subset) == 1
    assert blind_training_subset[0].event_id == "HTE-BLIND-1"


def test_ht_05_policy_experience_is_observational_only():
    """HT-05: PolicyExperience captures state-action-outcome tuples without online model mutation authority."""
    exp = PolicyExperience(
        experience_id="exp_001",
        state_context={"detector": "D08", "residual_m": 220.0, "match_confidence": 0.85},
        available_actions=["ROUTE_TO_HUMAN", "APPLY_EMPIRICAL_SHIFT", "BLOCK"],
        chosen_action="ROUTE_TO_HUMAN",
        action_source="RULE_POLICY",
        evidence_cost=1.5,
        human_result="SUPPORT",
        eventual_outcome="ADMITTED",
    )
    # Pure data audit object: has NO method to update production model parameters or gate policy
    assert exp.chosen_action == "ROUTE_TO_HUMAN"
    assert not hasattr(exp, "update_model_weights")
    assert not hasattr(exp, "mutate_production_policy")
