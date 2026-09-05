# Contract Inventory & Mapping (Gate -1)

**Status:** APPROVED FOR PHASE 0  
**Baseline:** Spatial Source Integrity v1.0 Normative Design Package  
**Execution Date:** 2026-09-05  
**Inspected Repositories:**
1. `prism-ontology` (`prism-ontology`) — Version: `0.1.0-rc2`
2. `spatial-decision-intelligence` (SDI runtime) (`local-workspace/2026-08-18-17-47-15/src/domain/`)

---

## 1. 现实代码库盘点结论 (Inventory Ground Truth)

经过对本地实际代码库的严格盘查，事实如下：

1. **`prism-ontology` (`prism-ontology`)**：
   - 当前为确定性 W3C RDF/OWL/SHACL/YAML 语义定义库（依赖 `rdflib`, `pyshacl`, `pyyaml`, `jsonschema`）。
   - 定义了 `prism-core:Observation`, `prism-core:Evidence`, `prism-core:DerivedEstimate`, `prism-core:Entity`, `prism-core:SpatialGeometry`, `prism-core:Policy`, `prism-core:Constraint`, `prism-core:Eligibility`, `prism-core:Decision`，以及在 `prism-insight` 中定义了 `prism-insight:InsightClaim`（继承自 `InformationObject`，通过 `groundedInEvidence` 关联 `Evidence`）和 `QualityAssessment`。
   - **关键事实：`prism-ontology` 当前仅发布了 TTL/OWL 与 SHACL 约束规范，尚未发布独立的 Python Pydantic 运行时模型包**。
   - **执行原则**：严格执行 Kickoff 决议——**禁止在 SSI 自立 Canonical Ontology**。在 `ssi/contracts/shared_adapters/` 下建立强类型 Pydantic v2 **Runtime Typed Projection / Adapter**，每个适配器显式绑定 `_canonical_uri`、`_ontology_version` 与 `_runtime_schema_version`。

2. **`spatial-decision-intelligence` (SDI) 现有运行时契约 (`local-workspace/.../src/`)**：
   - `src/domain/contracts.py` 中实现了 `@dataclass(frozen=True)` 的 `Observation`, `SpatialRepresentation`, `SpatialRelation`, `AuthorityAssertion`, `Evidence`, `BoundaryHypothesis`, `ValidationResult`, `SpatialEntity`, 以及 **`TrustedSpatialState`（已被 SSI 规范废弃）**。
   - `src/domain/world_model.py` 中实现了 `QualityFinding`, `DecisionImpact`, `EvidencePacket`。
   - `src/domain/evidence_algebra.py` 中实现了基于 Dempster-Shafer 证据理论与信念区间的 `EvidenceAlgebra`。
   - `src/validation/gate_spec.py` 中实现了声明式门禁解析器 `GateSpec`（`BLOCKED`, `FAILED`, `WARNED`, `PASSED`）。
   - `src/entity_resolution/contract.py` 中实现了 `EntityStructureAssertion` 与 `EntityPairRelation`。

---

## 2. 核心概念所有权与映射矩阵 (Ownership & Mapping Matrix)

| SSI 规范概念 | 权威所有者 (Canonical Owner) | 现有运行时物理契约 (Existing Runtime Contract) | 工程处置动作 (Action) | 适配与实现路径 (Implementation Path) |
|---|---|---|---|---|
| **Observation** | `prism-ontology`<br>(`prism-core:Observation`) | SDI `src/domain/contracts.py:Observation` (dataclass) | **REUSE / ADAPT** | 在 `ssi/contracts/shared_adapters/observation.py` 建立 Pydantic v2 适配层，继承 SDI 字段，打上 `prism-core:Observation` 规范注解。 |
| **Evidence** | `prism-ontology`<br>(`prism-core:Evidence`) | SDI `src/domain/contracts.py:Evidence` + `world_model.py:EvidencePacket` | **REUSE / ADAPT** | 在 `ssi/contracts/shared_adapters/evidence.py` 建立适配层，支持 `EvidenceRelation`（SUPPORTS / CONTRADICTS / DOES_NOT_RESOLVE）及证据依赖链。 |
| **Claim** | `prism-ontology`<br>(`prism-insight:InsightClaim`) | SDI `src/domain/contracts.py:AuthorityAssertion` | **REUSE / ADAPT** | 废弃单向 Assertion，适配为双向可反驳的 `Claim`。实体链接表达为 `EntityLinkClaim`。打通 `ClaimResolution`。 |
| **DerivedEstimate** | `prism-ontology`<br>(`prism-core:DerivedEstimate`) | SDI `src/domain/contracts.py:SpatialRepresentation` (origin=DERIVED) | **REUSE** | 在 `ssi/contracts/shared_adapters/derived_estimate.py` 投影，作为所有纠偏、对齐、几何补全的唯一合法承载实体，严禁覆写原始观测。 |
| **OperationalProfile** | `prism-ontology`<br>(`profiles/`) | 无直接 Python 类，仅有 YAML 配置与 SHACL 图 | **REUSE / ADAPT** | 在 `ssi/contracts/shared_adapters/operational_profile.py` 建立 Profile 契约校验器，读取受管概念与指标。 |
| **DecisionProfile** | Shared / Business Policy | SDI `src/adapters/decision_adapters.py` (隐式) | **SPECIALIZE** | 在 `ssi/contracts/spatial/decision_profile.py` 显式定义。特化 `DP-01 City Analytics` 与 `DP-02 Visit Planning`，绑定具体容差，禁止硬编码全局阈值。 |
| **SpatialWorldState** | SDI Domain Layer | SDI `src/domain/contracts.py:TrustedSpatialState` (混淆态) | **ADAPT** | 从混淆的 `TrustedSpatialState` 解耦。作为内部多源融合、假说共存的工作态，**无任何下游发布与消费授权**。 |
| **EntityLink** | Entity Resolution Capability | SDI `src/entity_resolution/contract.py:EntityPairRelation` | **REUSE** | 在 `ssi/contracts/spatial/entity_link.py` 复用，将其作为 `Claim` 的一个特化子类型参与证据裁决。 |
| **QualityFinding** | SDI Validation Layer | SDI `src/domain/world_model.py:QualityFinding` | **SPECIALIZE** | 标准化对齐 ISO 19157-1:2023（质量元素、测量方法、测量结果、元质量），关联 `FindingStatus` 与 `DecisionImpact`。 |
| **DecisionImpact** | SDI World Model | SDI `src/domain/world_model.py:DecisionImpact` | **REUSE / SPECIALIZE** | 保留 `risk_level`, `polluted_decisions`, `blocked_consumers`，与 `DecisionStability` 计算对接。 |
| **GateDecision** | **SSI Core** | 无（旧系统仅有 `ValidationResult.decision_ready: bool`） | **NEW** | 在 `ssi/contracts/runtime/gate_decision.py` 全新实现。包含不可变八元组版本绑定、`AdmissionAction`、`GovernanceDisposition`。 |
| **EvaluationCoverageManifest** | **SSI Runtime** | 无（导致了北京 CRS 硬编码空跑出假 92% 发布的根因） | **NEW** | 在 `ssi/contracts/runtime/coverage_manifest.py` 全新实现。定义 eligible/evaluated/excluded/sampled/abstained 范围，未覆盖则 Fail-Closed。 |
| **DecisionReadyProjection** | **SSI Core** | 无（旧系统直接消费 `SpatialRepresentation`） | **NEW** | 在 `ssi/contracts/runtime/projection.py` 全新实现。只有合法 `GateDecision`（ALLOW 或经校验消费者能力的 ALLOW_WITH_LIMITS）才能铸造。 |
| **TrustedSpatialSnapshot** | **SSI Core** | 无（旧系统通过打标 `trusted=True` 假充快照） | **NEW** | 在 `ssi/contracts/runtime/snapshot.py` 全新实现。集合级、不可变、带内容哈希、面向特定消费者发布的 Parquet/GeoParquet 目录包。 |
| **UsageLimit** | **SSI Core** | 无 | **NEW** | 在 `ssi/contracts/runtime/usage_limit.py` 实现机器可强制执行的约束（空间范围、分辨率下限、禁止的操作、时间有效性）。 |

---

## 3. Shared Adapters 强类型约束规范

所有位于 `ssi/contracts/shared_adapters/` 下的 Pydantic 模型必须具备以下类元属性：

```python
class PrismSharedAdapter(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    _canonical_uri: ClassVar[str]
    _ontology_version: ClassVar[str] = "0.1.0-rc2"
    _runtime_schema_version: ClassVar[str] = "1.0.0"
```

这确保了：
1. 运行时类型与上游 `prism-ontology` 严格一一对应；
2. 任何字段变更必须经过 Schema 版本号升级；
3. 未来 `prism-ontology` 原生发布 Python 运行库时，适配层可以直接切换为无损继承或别名，彻底消除两个事实标准的隐患。
