# Human-in-the-Loop & Learning Specification

**Status:** Normative v1 packaged edition  
**Core principle:** Human Authority + Evidence Governance + Safe Learning

## 1. Why HITL is first-class

Spatial integrity includes inherently ambiguous cases:
- unknown/indistinguishable CRS;
- reference conflicts;
- unclear lineage;
- fallback vs legitimate centroid;
- changing administrative semantics;
- ambiguous entity matching;
- new source pipelines;
- multiple plausible repairs.

The correct machine behavior is sometimes **ASK / ABSTAIN / ESCALATE**, not forced prediction.

## 2. Human is not an oracle

Human judgment can be wrong, biased or reference-dependent. Therefore:
`Human Decision != automatic Ground Truth`.

Every human output has:
- provenance;
- scope;
- reviewer role/expertise;
- evidence;
- prediction visibility;
- confidence/uncertainty;
- revocability.

## 3. Human roles

At least:
- Reviewer — individual ambiguous cases;
- Domain Expert — business/source/geographic semantics;
- Data Steward — data correction/quarantine approval;
- Policy Owner — DecisionProfile/GatePolicy/override governance.

Permissions must not be conflated.

## 4. HumanReviewTask

Contains:
- subject/profile;
- trigger/reason;
- claim under review;
- candidate hypotheses;
- supporting/contradicting evidence;
- dependency status;
- business impact;
- requested reviewer role;
- priority/lifecycle.

The reviewer should see why the machine abstained, not only “is this point correct?”.

## 5. HumanAdjudication

Canonical adjudication decisions:
- SUPPORT
- REFUTE
- UNRESOLVED
- ESCALATE

Repair approval is **not** HumanAdjudication; it is separate governance.

Record prediction/evidence visibility, especially for Gold.

## 6. HumanReviewPolicy

Policy defines:
- trigger rules;
- reviewer role;
- independent/double review requirements;
- priority;
- escalation;
- review blind-mode requirements where relevant.

It may be referenced by EvaluationPlan and GatePolicy.

## 7. Review disagreement

Conflicting reviewers produce CONFLICTED or escalation unless a governed adjudication procedure resolves it.

Do not silently majority-vote a “truth” where uncertainty remains.

## 8. Human correction

Human may:
- confirm an issue;
- propose correction;
- request evidence;
- reject candidate;
- escalate.

“Old value is wrong” and “new value is correct” are separate claims.

All corrections re-enter evidence/evaluation/Gate.

## 9. Review triggers

Families:
- UNCERTAINTY
- CONFLICT
- NOVELTY
- HIGH_IMPACT
- POLICY_REQUIRED

Uncertainty alone does not always require human review: if relevant DecisionStability is stable and policy permits, automation may continue.

## 10. Review prioritization

Conceptually prioritize using:
- uncertainty;
- impact;
- novelty;
- representativity;
- information value;
- urgency.

Do not use uncertainty sampling alone. Preserve random/representative audits to catch confident systematic errors.

## 11. HumanTeachingEvent

A governed record connecting:
- input state;
- machine output;
- human adjudication/correction;
- evidence context;
- disagreement type;
- learning eligibility;
- teaching category.

A teaching event never changes production model immediately.

## 12. Learning eligibility

- ELIGIBLE
- CONDITIONALLY_ELIGIBLE
- NOT_ELIGIBLE
- REVOKED

Examples not automatically eligible:
- reviewer unsure;
- dependent evidence only;
- temporary policy override;
- adjudication later overturned.

## 13. Learning maturity

### L0 — Rule / knowledge update
Often best for explicit source-pipeline knowledge. Do not train a model when a versioned rule is the right artifact.

### L1 — Supervised learning
Suitable for fallback classification, source-pipeline classification, entity match assistance, anomaly classification, repair candidate ranking.

### L1 — Active learning
Select valuable examples for human labeling while controlling selection bias.

### L2 — Preference / ranking / contextual bandit
Useful when humans compare candidate repairs/evidence bundles or for review/evidence routing.

### L3 — Offline constrained RL (P2 research)
Only for genuine sequential decision problems such as next-best-evidence acquisition.

## 14. RL state/action boundary

Potential state:
findings, claims, evidence, uncertainty, profile, source context, review history.

Permitted research actions:
- request a reference/evidence family;
- run optional evaluation;
- request reviewer/expert/second review;
- escalate;
- stop and abstain.

RL must never own:
- raw mutation;
- world truth;
- ontology change;
- DecisionProfile requirement;
- hard Gate constraint;
- required human approval bypass;
- publication;
- silent repair approval.

## 15. Reward and safety

Reward may include:
- resolution quality;
- false-trusted penalty;
- false-certainty penalty;
- human cost;
- latency/evidence cost;
- successful abstention;
- transfer robustness.

Hard safety constraints are **constraints**, not merely reward penalties:
- no Gate bypass;
- no raw mutation;
- no unapproved repair publication;
- no required-review bypass;
- no unsafe production exploration.

## 16. Learning authority matrix

| Object/behavior | Automatically learn/change? |
|---|---|
| Raw SourceAsset | NO |
| Shared ontology | NO |
| Human adjudication history | store, revocable |
| Detector model parameters | candidate update after validation |
| Statistical thresholds | candidate update only |
| Review prioritization | YES after evaluation/promotion |
| Evidence acquisition order | YES after governance |
| Repair ranking | YES after validation |
| Hard Gate constraints | NO |
| DecisionProfile requirements | NO |
| Publication | NO direct learning authority |

## 17. Production promotion

`Human feedback → LearningDataset → Candidate model/policy → Offline evaluation → Blind/Transfer/B5 → Shadow → Governance approval → New version`.

Never:
`human correction → online weight update → immediate production behavior change`.

## 18. LearningDataset

Versioned with:
- TeachingEvent refs;
- source distribution;
- label policy;
- reviewer distribution;
- Gold independence;
- prediction visibility;
- known biases;
- split policy.

Reviewed cases are selection-biased; preserve selection policy.

## 19. Feedback revocation

If a human adjudication/reference is later overturned:
- revoke TeachingEvent eligibility;
- trace LearningDataset versions;
- analyze affected models;
- reevaluate capability if material.

Do not silently retain corrupted labels.

## 20. Model maturity

EXPERIMENTAL → OFFLINE_VALIDATED → SHADOW → APPROVED → DEPRECATED.

Policy learning receives stricter governance than detector learning.

## 21. PolicyExperience

Record from day one:
- state context;
- available actions;
- chosen action;
- action source;
- behavior-policy version;
- action propensity when available;
- immediate cost;
- evidence acquired;
- human feedback;
- eventual outcome;
- safety events;
- time.

This enables future selection-bias/off-policy analysis without committing v1 to RL.

## 22. Outcome feedback

Field verification, downstream correction, source update, customer dispute, snapshot revocation and repair outcome first become **Evidence** that updates the governed world state. They may also become learning signals second.

Reward never substitutes for evidence.

## 23. Metrics

Human:
- Review Rate;
- Resolution Rate;
- Escalation Rate;
- Reviewer Disagreement;
- Resolution time;
- overturn/reversal rate;
- AI→Human correction;
- Human→Later reversal.

Learning:
- label efficiency;
- review reduction at fixed FTR;
- false-certainty reduction;
- novel failure discovery;
- transfer improvement;
- calibration improvement;
- policy cost/regret where applicable.

## 24. Architecture

```text
Evaluation
  |
AI result / ABSTAIN
  |                \
clear              unclear/high-impact
  |                  |
Gate           HumanReviewTask
                    |
             HumanAdjudication
              /            \
         new Evidence    TeachingEvent
              |             |
        Re-evaluation    Learning Store
              |             |
             Gate       Offline Learning
                            |
                      Candidate Version
                            |
                    Benchmark / Shadow
                            |
                    Governance Approval
                            |
                        New Version
```

Operational correction and model learning are separate.

## 25. Final principle

> Machines automate only what evidence proves they can automate. Humans resolve the high-value remainder. Human work becomes governed teaching data, but learned behavior returns to production only after benchmark and governance.
