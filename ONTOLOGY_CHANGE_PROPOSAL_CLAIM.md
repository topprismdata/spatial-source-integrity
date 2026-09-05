# Ontology Change Proposal: Generic Claim & Evidence Relation

**Proposal ID:** OCP-2026-001  
**Target Repository:** `prism-ontology` (`ontology/core/`)  
**Proposer:** TopPrism Spatial Source Integrity (SSI) Team  
**Status:** PROPOSED (Governance Review Pending)  
**Date:** 2026-09-05  

---

## 1. 为什么现有 `InsightClaim` 不足 (Why `InsightClaim` is Insufficient)

在 `prism-ontology` 当前实现中，仅在 `ontology/insight/insight-artifact.ttl` 中定义了 `prism-insight:InsightClaim`：
* `InsightClaim` 继承自 `prism-core:InformationObject`，其定位为：
  > “系统基于观测数据与确定性计算输出的分析结论观点（Claim）。严禁直接作为客观既成世界事实，更不得自动回写世界模型。”
* **局限性**：
  1. **语义局限在分析洞察阶段**：`InsightClaim` 强依赖于分析意图（`AnalysisIntent`）与受管度量（`MetricDefinition`），属于 L2+ 的下游分析产物。
  2. **无法支撑数据准入与输入层断言**：在输入层（Source Admission），外部供应商数据本身携带的大量断言（例如：“该坐标属于该实体”、“该点位位于西安市未央区”、“该供应商数据采用 CGCS2000 坐标系”）并不是业务分析洞察，而是**原始主张（Source Claim）**或**对齐假说（Alignment Claim）**。
  3. **无法表达双向证伪与仲裁**：数据准入需要对输入主张进行判定（SUPPORTED / REFUTED / CONFLICTED / UNRESOLVED），将数据输入层断言硬套在 `InsightClaim` 会造成概念扭曲。

因此，L1 通用核心（`prism-core`）必须拥有通用的 `prism-core:Claim`。

---

## 2. Generic Claim 的最小语义定义 (Minimal Semantics of Generic Claim)

```turtle
prism-core:Claim a owl:Class ;
    rdfs:subClassOf prism-core:InformationObject ;
    rdfs:label "命题主张"@zh , "Claim"@en ;
    rdfs:comment "行动主体、外部数据源或算法模型提出的关于现实世界状态的可检验命题陈述。主张本身不是世界事实，必须经过证据关联与裁决才能作为派生状态或准入依据。" .

prism-core:claimSubject a owl:ObjectProperty ;
    rdfs:domain prism-core:Claim ;
    rdfs:label "主张主体"@zh , "claimSubject"@en .

prism-core:claimPredicate a owl:DatatypeProperty ;
    rdfs:domain prism-core:Claim ;
    rdfs:range xsd:string ;
    rdfs:label "主张谓词"@zh , "claimPredicate"@en .

prism-core:claimObject a owl:ObjectProperty ;
    rdfs:domain prism-core:Claim ;
    rdfs:label "主张客体"@zh , "claimObject"@en .
```

* **必要最小元数据**：
  * `claim_id`: 唯一标识
  * `claim_type`: 主张类型（如 `ENTITY_IDENTITY`, `SPATIAL_LOCATION`, `SPATIAL_REFERENCE`, `ADMIN_ASSIGNMENT`）
  * `subject_ref`: 主体引用（如 SourceRecord 或 Entity）
  * `predicate`: 关系谓词（如 `refers_to`, `located_at`, `uses_crs`）
  * `asserted_value`: 宣称的目标值或客体引用
  * `asserted_by`: 宣称来源（供应商标识、批次号或模型 ID）
  * `asserted_at`: 宣称时间戳

---

## 3. `InsightClaim` 是否应该成为 Generic Claim 的子类？

**结论：是（YES）。**

* 继承结构设计：
  ```text
  prism-core:InformationObject
          │
          ▼
  prism-core:Claim (L1 Core)
          │
          ├─────────────────────────────┐
          ▼                             ▼
  prism-insight:InsightClaim (L2+)   ssi:EntityLinkClaim (Spatial)
  (面向下游分析洞察结论)              (面向实体链接与参考裁决)
  ```
* **收益**：`InsightClaim` 保持现有向后兼容性，同时继承 `Claim` 的可反驳性、证据关联关系与生命周期管理机制。

---

## 4. `EvidenceRelation` 如何引用 Claim (How `EvidenceRelation` References `Claim`)

证据与主张的关系不能是简单的布尔指针，必须是具备极性（Polarity）的独立关系对象：

```text
       [Evidence]
           │
           ▼
   [EvidenceRelation]
     - evidence_id
     - claim_id
     - polarity: SUPPORTS | CONTRADICTS | DOES_NOT_RESOLVE
     - confidence: LOW | MEDIUM | HIGH
     - dependency_status: INDEPENDENT | DEPENDENT | UNKNOWN
           │
           ▼
        [Claim]
           │
           ▼
   [ClaimResolution]
     - status: SUPPORTED | REFUTED | CONFLICTED | UNRESOLVED
```

* **极性与严重性彻底解耦**：严重性（Severity）属于业务影响，极性（Polarity）属于客观逻辑关系。即使矛盾极其轻微，其极性依然是 `CONTRADICTS`。

---

## 5. `EntityLinkClaim` 如何作为 Claim Specialization 表达

实体链接是空间准入中的核心命题（例如“commercial listing dataset小区记录 R_102 指向 OSM 地块 E_501”）。

在 SSI 中，不建立独立的 `spatial/EntityLink` 领域根对象，而是作为 `GenericClaim` 的特化投影：

```python
class EntityLinkClaimAdapter(GenericClaimAdapter):
    """Specialization of Claim for Entity Resolution without creating a new ontology root."""
    claim_type: Literal["ENTITY_LINK"] = "ENTITY_LINK"
    predicate: Literal["refers_to"] = "refers_to"
    
    # 强类型别名
    source_record_id: str  # maps to subject_ref
    target_entity_id: str  # maps to asserted_value
```

**对现有 SDI 资产的承接**：
* 现有 `src/entity_resolution/contract.py` 中的 `EntityPairRelation` 与 `EntityStructureAssertion`，通过转换函数生成 `EntityLinkClaimAdapter` 与对应的 `Evidence`。
* 彻底消除“实体对齐结果直接变成不可挑战的事实”的隐患。

---

## 6. 是否影响现有的 `outlet-insight` Profile？

**结论：完全向后兼容，零破坏性变更（Zero Breaking Changes）。**

* **原因**：
  1. `outlet-insight` Profile（`0.1.0-rc2`）依赖于 `prism-insight:InsightClaim`，将其父类从 `prism-core:InformationObject` 调整为 `prism-core:Claim`，在 OWL-RL 分类学上属于良性单调扩展（Monotonic Extension）。
  2. 现有 SHACL 约束图与 Competency Questions 校验的是 `InsightClaim` 自身特有的属性（如 `groundedInEvidence`, `appliesMetric`），这些属性和约束保持 100% 不变。
  3. `profiles/outlet-insight/profile-manifest.json` 无需废弃概念，仅需在本体升级到 `0.2.0` 时重新生成发行物清单。

---

## 7. SSI 内部的过渡策略 (Provisional Adapter Strategy in Phase 0)

在 `prism-ontology` 正式发布带有 `prism-core:Claim` 的新版本前：
1. SSI 在 `ssi/contracts/shared_adapters/claim.py` 中实现 `GenericClaimAdapter`。
2. 类元数据显式标记：
   ```python
   _canonical_uri = "prism://ontology/core/Claim#provisional"
   mapping_status = "PENDING_ONTOLOGY_GOVERNANCE"
   ```
3. Phase 0 绝不被本体发版所阻塞，同时在代码身份上保持严格清晰的过渡状态。
