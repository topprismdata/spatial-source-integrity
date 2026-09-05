# Migration Matrix & Cutover Rules (Gate -1)

**Status:** APPROVED FOR PHASE 0  
**Baseline:** Spatial Source Integrity v1.0 Normative Design Package  
**Execution Date:** 2026-09-05  

---

## 1. 废弃与更替清单 (Deprecated & Superseded Concepts)

| 现有 / 历史实现概念 | 缺陷与语义坍缩风险 | SSI v1.0 目标更替架构 | 迁移与处置规则 (Cutover Rule) |
|---|---|---|---|
| **`TrustedSpatialState`**<br>(SDI `contracts.py:341`) | 混淆了“内部融合工作态”与“外部发布信任态”，使未经验证的假说可能被下游直接读取。 | **`SpatialWorldState`**（内部工作态，无消费权）<br>+<br>**`TrustedSpatialSnapshot`**（不可变对外发布快照） | **全面废弃**。内部世界模型仅保留 `SpatialWorldState`；对外提供数据仅允许消费指定版本的 `TrustedSpatialSnapshot`。 |
| **`TrustedProjection`**<br>(历史术语) | 命名存在歧义，未体现与特定业务决策（DecisionProfile）绑定的准入特性。 | **`DecisionReadyProjection`** | **全面废弃**。所有准入表达必须显式绑定 `decision_profile_id` 与 `gate_decision_id`。 |
| **`ValidationResult.decision_ready: bool`**<br>(SDI `contracts.py:326`) | 全局布尔值。导致“只要某个规则通过就全场景可用”的严重坍缩，忽视不同决策容差差异。 | **`GateDecision`**<br>+<br>**`DecisionStability`** | **全面废弃**。禁止任何 `is_safe` 或 `decision_ready: bool` 字段。准入必须是四态之一（ALLOW / ALLOW_WITH_LIMITS / REVIEW / BLOCK_FOR_PROFILE）。 |
| **`FindingSeverity.CRITICAL` 阻断全局**<br>(SDI `world_model.py:35`) | 单点严重性直接绑死全局消费，导致低精度场景被误杀或高精度场景被漏过。 | **`DecisionImpact`**<br>+<br>**`RequirementEvaluation`** | **解耦**。Finding 仅记录客观质量缺陷与测量偏差；是否阻断由具体 `DecisionProfile` 与 `GatePolicy` 判定。 |
| **单向 `AuthorityAssertion`**<br>(SDI `contracts.py:290`) | 仅支持单向正向断言，缺乏可证伪性、反向反驳证据与冲突仲裁。 | **`Claim`**<br>+<br>**`EvidenceRelation`**<br>+<br>**`ClaimResolution`** | **升级重构**。实体归属、参考系宣称、坐标有效性均转为 `Claim`，支持 SUPPORTS / CONTRADICTS / DOES_NOT_RESOLVE 证据组合。 |
| **单字段 `disposition=approved`**<br>(SDI `disposition.py`) | 将“确认原值有错（Human Adjudication）”与“批准新候选坐标（Repair Approval）”混为一谈。 | **`HumanAdjudication`**（针对错误发现）<br>与<br>**`RepairApproval`**（针对修复提案）**严格两权分立** | **禁止混用**。审核人否定某项发现不等于批准生成新坐标；批准修改必须有独立的验证证据与明确治理审批记录。 |
| **就地修改数据库状态**<br>(`UPDATE table SET trusted=true`) | 破坏审计追踪与可重放性，快照可被外部并发静默修改。 | **基于 Parquet/GeoParquet 的不可变目录快照** | **物理禁止**。发布物为包含内容哈希与元数据清单的文件目录，发布后只读（Read-Only），变更必须升版生成新 Snapshot。 |
| **缺失覆盖率的 0 缺陷通过**<br>(SDI 北京 CRS 空跑 Bug 模式) | 探测器跳过或静默返回空时，被误判为“0 findings = 100% 合格通过”。 | **`EvaluationCoverageManifest`**（P0 级 Fail-Closed 机制） | **强制校验**。无有效 CoverageManifest 或主体处于未评估（NOT_EVALUATED）范围的，门禁一律 Fail-Closed 判定不予准入。 |

---

## 2. 演进与实施阶段规划 (Evolutionary Phases)

```text
[Phase -1] 契约盘点与映射 (Contract Inventory & Mapping) —— [已完成: 本文档与 CONTRACT_MAPPING.md]
    │
    ▼
[Phase 0] 准入主链与 Engineering Gate 回归防线 (Admission Spine & EG-01~12)
    │  - 纯合成夹具驱动，先跑通不可绕过的 Gate / Publisher / Snapshot
    │  - 固化 EG-01 ~ EG-12 自动化防线
    ▼
[Phase 1] 点源基础探测器与空间参考解析器 (Thin Detectors D01~D09 & Resolver)
    │  - 实现 D01~D09 基础薄切片与 H=(C,R,E,K) 解析器
    │  - 绑定 CoverageManifest 生成
    ▼
[Phase 2] 人机协同与修复闭环 (HITL & Repair Thin Loop)
    │  - 实现 Review Pack（工单、证据包、HTML 地图）
    │  - 分立 HumanAdjudication 与 RepairApproval，验证原始数据永不被篡改
    ▼
[Phase 3] 真实场景端到端验证 (Xi'an Real-World Vertical Slice)
    │  - 接入西安真实commercial listing dataset种子语料
    │  - 执行 Holdout 隔离与候选比对，交付完整业务报告与不可变 Snapshot
```

---

## 3. 切割期硬约束 (Cutover Invariants)

在系统实施过程中，必须严格遵守以下 5 条硬隔离约束：
1. **禁止旁路发布**：下游适配器（Adapter）仅具备读取与格式转换能力，**严禁自行推算或回写 `is_safe`**。
2. **拒绝通用魔法阈值**：任何距离容差、残差阈值只能由 `DecisionProfile` 定义或从外部注入，代码中禁止出现全局默认硬编码（如 `if dist < 50`）。
3. **样本不等于全量**：抽样评估的结论仅代表抽样推断（InferenceScope），未抽样记录无个体独立证据时，除非 Profile 显式声明允许推断证据，否则一律按 NOT_EVALUATED 拦截。
4. **撤销具有传染性**：一旦某个 Snapshot 发生 REVOKED 或 INVALIDATED，系统必须能沿着依赖图定位到所有受影响的消费记录（SnapshotConsumptionRecord），禁止静默忽略。
5. **原始记录绝对只读**：Raw Source 文件必须在只读模式下加载，系统计算产生的一切新坐标只能作为 `DerivedEstimate` 存入派生层。
