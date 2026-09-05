"""HumanTeachingEvent and PolicyExperience contracts for governed offline learning."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TeachingCategory(str, Enum):
    """Classification of human teaching feedback per section 30."""
    T1_FALSE_POSITIVE_DETECTOR = "T1_FALSE_POSITIVE_DETECTOR"
    T2_FALSE_NEGATIVE_DETECTOR = "T2_FALSE_NEGATIVE_DETECTOR"
    T3_REFERENCE_CONFLICT = "T3_REFERENCE_CONFLICT"
    T4_ENTITY_LINK_CORRECTION = "T4_ENTITY_LINK_CORRECTION"
    T5_REFERENCE_FAMILY_CORRECTION = "T5_REFERENCE_FAMILY_CORRECTION"
    T6_LEGITIMATE_ANOMALY = "T6_LEGITIMATE_ANOMALY"
    T7_REPAIR_ACCEPTED = "T7_REPAIR_ACCEPTED"
    T8_REPAIR_REJECTED = "T8_REPAIR_REJECTED"
    T9_NEW_FAILURE_FAMILY = "T9_NEW_FAILURE_FAMILY"
    T10_UNRESOLVED_AMBIGUITY = "T10_UNRESOLVED_AMBIGUITY"


class LearningEligibility(str, Enum):
    """Governance filter determining whether human feedback may enter offline training datasets."""
    ELIGIBLE = "ELIGIBLE"
    CONDITIONALLY_ELIGIBLE = "CONDITIONALLY_ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    REVOKED = "REVOKED"


class HumanTeachingEvent(BaseModel):
    """A governed record connecting human review outcomes to offline learning pipelines.
    
    Invariants:
    1. Human review does NOT automatically become training data (HT-01).
    2. Overturned adjudications propagate revocation to learning eligibility (HT-03).
    3. Prediction visibility is preserved to audit cognitive anchoring in model training (HT-04).
    4. Learned models NEVER update production parameters automatically (HT-05).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    task_ref: str
    subject_id: str
    machine_prediction: Dict[str, Any]
    human_adjudication_ref: str
    adjudicated_action: str
    reviewer_role: str
    prediction_visibility: str
    teaching_category: TeachingCategory
    learning_eligibility: LearningEligibility = Field(default=LearningEligibility.NOT_ELIGIBLE)
    eligibility_rationale: str = Field(default="")
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_revoked: bool = Field(default=False)
    revocation_reason: Optional[str] = Field(default=None)

    def revoke_eligibility(self, reason: str) -> HumanTeachingEvent:
        """Revokes learning eligibility when upstream human adjudication or reference is overturned."""
        return HumanTeachingEvent(
            event_id=self.event_id,
            task_ref=self.task_ref,
            subject_id=self.subject_id,
            machine_prediction=self.machine_prediction,
            human_adjudication_ref=self.human_adjudication_ref,
            adjudicated_action=self.adjudicated_action,
            reviewer_role=self.reviewer_role,
            prediction_visibility=self.prediction_visibility,
            teaching_category=self.teaching_category,
            learning_eligibility=LearningEligibility.REVOKED,
            eligibility_rationale=f"Revoked: {reason}",
            recorded_at=self.recorded_at,
            is_revoked=True,
            revocation_reason=reason,
        )


class PolicyExperience(BaseModel):
    """Audit record capturing sequential decision context for future evidence-routing optimization.
    
    Offline observational record only; no online RL permitted.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    experience_id: str
    state_context: Dict[str, Any]
    available_actions: List[str]
    chosen_action: str
    action_source: str = Field(default="RULE_POLICY", description="RULE_POLICY | HUMAN_EXPERT | MODEL_PROPOSAL")
    evidence_cost: float = Field(default=0.0)
    human_result: Optional[str] = Field(default=None)
    eventual_outcome: str = Field(description="ADMITTED | BLOCKED | REVOKED")
    recorded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
