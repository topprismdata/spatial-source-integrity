# SSI 三重自审 V2 — 诚实复审报告（Evidence-Verified, Adversarial）

**审查日期:** 2026-09-05  
**审查对象:** `SSI` 全部文档、代码、运行产物 @ HEAD `6eb2279`  
**方法声明:** 本轮所有结论均以**文件级证据**（file:line / 字段 / 哈希 / 重放）核验，不依赖记忆与既有报告的转述。

---

## 0. 总裁定（先说结论）

**V1 自审报告（《SSI_DOCUMENT_INVENTORY_AND_TRIPLE_SELF_REVIEW.md》）整体不可信，正式撤回（RETRACTED）。**

它犯了自己审查的对象最忌讳的错：**把声明当证据、把报告当代码、把模拟当人工**。V1 宣称"ALL PASSED"的同时，至少有 3 项 CRITICAL 级失实存在于它所称赞的产物中。

当前真实状态：
- **Phase 0（准入主干）与 Phase 1 Core（探测器/解析器/门禁）**：经本轮文件级核验，**真实成立**（94 项测试重放通过、原始哈希未变、数学关系可复现）。
- **Phase 1R 报告层与 Phase 2"人工证据"层**：**存在系统性诚信缺陷**，基线封板宣言（"SEALED"）部分失实，应降级为 **"SEALED WITH RESERVATIONS — 待整改"**。

---

## 1. 发现清单（按严重度排序，全部附文件级证据）

### CRITICAL

#### C1 — 所谓"88 单人工审核闭环"实为脚本模拟，却在 Passport 与 Phase 2 报告中被呈现为 Human Review Coverage
**证据：**
- `runs/xian_seed_001/review_queue/adjudications.jsonl`：89 条裁决全部来自 4 个虚构身份（`steward_a` / `reviewer_b` / `reviewer_d` / `reviewer_e`），由生成脚本按 `int(subject_id) % 3 == 0` 之类启发式批量产出；
- Passport v1.2.0 §7 "Human Review Operational Closure"、`PHASE_2_FINAL_REPORT.md` DoD#1 "HumanReviewTask → HumanAdjudication 真闭环 ✅"：均把该模拟数据表述为真实人审；
- 由其派生的 `learning/human_teaching_events.jsonl`（89 条）与 "13 ELIGIBLE" 等治理统计随之失真。
**违反：** Phase 2 指令 §3（"跑真实审核闭环"）、HITL 规范（人类判断必须具备真实 provenance）、SSI 核心原则"Human judgment is evidence"——模拟数据不是任何人的证据。
**这是全工程最严重的问题：不是某个 bug，而是把仿真包装成了治理成果。**

#### C2 — CLOSE-01 降级只改了报告和 JSON，没有改代码；重放即与冻结 Passport 矛盾
**证据：**
- `ssi/resolver/resolver.py:213-223`：BD_LIKE（非 EMPIRICAL_TRANSFORM）最终落入 "Clean Identified State" 分支，**代码仍返回 `IDENTIFIED`**；
- `runs/.../passport/SOURCE_PASSPORT.md` §5 与 `resolver/phase_b_results.json`：对外口径为 `ALIGNABLE_BUT_IDENTITY_UNCONFIRMED`。
**后果：** 任何人重跑 pipeline 将得到 `IDENTIFIED`，直接推翻冻结 Passport 中最重要的规范降级。"good fit ≠ identity" 这条 B1-001 立案原则，在代码层并未被执行。

#### C3 — 运行产物被事后手工改写，违反系统自身强制的运行不可变原则
**证据：**
- `runs/.../resolver/phase_b_results.json` 中存在 `resolution_state_original: "IDENTIFIED"` 与 `status_downgrade_reason` 字段——这是 CLOSE-01 事后编辑的铁证；
- CLOSE-01~04 的正确载体应是**版本化修订记录（Passport vNext / amendment）**，而非原地改写 run 输出。规范 13 明言 "history is never silently rewritten"，本次虽留了痕迹字段，但顶层 `resolution_state` 已被覆盖，重放一致性被破坏。

### HIGH

#### H1 — 5000m / 200m 作为工厂默认值硬编码进 `DecisionProfileAdapter`，无任何 fixture 标记
**证据：** `ssi/contracts/shared_adapters/decision_profile.py:50`（`max_acceptable_residual_meters=5000.0`）及 `create_dp02_visit_planning(max_residual_meters=200.0)` 默认参数；全库 grep `fixture_only` **零命中**。
**违反：** Phase 1R 指令 §40（"不得硬编码 5000m / 200m…必须标 fixture_only 或同等语义"）。

#### H2 — Shadow 比对中"原始状态 DP-02 = 0/937"是断言，不是计算
**证据：** `repair/SHADOW_STATE_GATE_COMPARISON.json` 的 raw_state 数字为脚本内手写字面量；`gate/` 目录中**不存在**任何对原始（未对齐）坐标执行 `GateExecutor` 的运行记录（937 条决策全部来自 `eval_xian_seed_001_v2` = 对齐坐标）。结论方向上可信（~1142m > 200m），但证据等级是 assertion 而非 execution。

#### H3 — 分歧仲裁无法表达 CONFLICTED；不对等角色分歧被行政权限静默裁决
**证据：** `ssi/hitl/review_task.py` 的 `AdjudicationAction` 枚举仅 SUPPORT/REFUTE/UNRESOLVED/ESCALATE（**无 CONFLICTED**），而同文件 docstring 第 125 行声称 "produces CONFLICTED or ESCALATE"；`arbitrate_review_conflict` 对不对等角色分歧直接采信高职级意见，无 CONFLICTED/升级路径；`HR-03` 只测了平级分歧。规范 §9 要求分歧产出 CONFLICTED 或 ESCALATE。

#### H4 — 分歧演练脚本静默失败 2/3，审稿分歧统计失真
**证据：** 脚本硬编码 3 个预期分歧任务 `HRT-DP02-308132 / 300602 / 879480`，实测仅 `879480` 存在于队列（另两个 ID 不存在，脚本无存在性校验即静默跳过）；`review_run_summary.json` 因此只报 `disagreement_count: 1`。

### MEDIUM

| # | 发现 | 证据 |
|---|---|---|
| M1 | `SEED_CORPUS_MANIFEST.md` 是 Markdown 冒充 JSON（`json.load` 直接 JSONDecodeError） | 文件头 80 字符为 `# Seed Corpus Manifest…` |
| M2 | 基线"冻结"于 `34eef60` 后又落了 `6eb2279`；各文档分别引用 0c4b566 / 34eef60 / 6eb2279 三个不同 commit 为权威 | `git log --oneline -6`；run_manifest vs baseline manifest vs V1 审查报告 |
| M3 | DuckDB 与 GeoParquet（获批技术栈两大支柱）**从未被使用**：`ssi/` 下 `import duckdb` 零命中；lockfile 锁定了一个未用引擎 | grep 结果为空 |
| M4 | 产物布局漂移：`findings.parquet` 与 `findings.jsonl` 双份并存（行数一致 1015，但无权威标记）；`runs/cross_file_*.json` 游离在 `runs/` 根而非 `xian_seed_001/resolver/`；`coverage/` 目录为空；`ssi/evaluation/coverage/` 仅剩 `__init__` 空壳 | 文件清单实测 |
| M5 | RW-06 / RW-08（部分 RW-04）是**手工构造对象的形状检查**，不驱动真实管线行为 | `tests/real_world/test_rw_series.py` 对应函数体 |
| M6 | D09↔Resolver 反馈环证据独立性（Phase 1R DoD #11）**无任何测试** | tests/ 全目录 grep 无对应用例 |
| M7 | B1-001 标注 `evidence_grade: G1`（single-source adjudicated），但 EM3=0——没有任何人工裁定的锚点 | CANONICAL_CASE.md yaml vs split_manifest |

### META — 对 V1 自审本身的红队结论
V1 在未打开文件的情况下断言"全库代码已 100% 采用…"（与 C2 矛盾）、"废[弃]概念清零"（与 H1/H3 矛盾）、三审"ALL PASSED"。**V1 的方法缺陷是：用报告验证报告。** 本 V2 的每一条结论均可由上述 file:line 复核。

---

## 2. 三轮复审正文（浓缩为可核验结论）

### Review 1 — 标准 / 事实 / 实证（复核后仍成立的部分）
以下经本轮**重新执行或逐文件核对**，确认真实：
1. 原始语料 SHA-256 前后一致（file1 `5fbdce74…`、file2 `5c754074…`）；
2. 12,505/12,505 的 QB 关系与 47 万总库 100% 逐字吻合（有独立脚本重放记录）；
3. 938→937 去重账目闭合（`anchor_population_reconciliation.json` 与 parquet 实测 duplicate=1）；
4. 94/94 测试重放通过（2.24s）；
5. 对齐坐标上的 937 条 DP-01/DP-02 门禁决策为真实计算产物（`eval_xian_seed_001_v2`）。
**但** Review 1 同时产出 C1/H2：报告层把"断言/模拟"混入了"实证"陈述。

### Review 2 — 跨文档 / 代码一致性
产出 C2、C3、H1、H3、M1、M2、M4：核心模式是**报告层与代码层已发生分叉**——规范降级、阈值约束、仲裁语义都只存在于文档与手工修补的 JSON 中，代码仍维持旧语义。

### Review 3 — 对抗式红队
除继承 C1-C3/H1-H4 外，新增视角：**最危险的绕过不是技术后门，而是"叙事性绕过"**——通过把模拟数据写入治理产物（Passport/TeachingEvents），系统在无需触碰 Gate 的情况下获得了"已人审"的表象。这正是 SSI 要防的"false certainty"，只是这次发生在 SSI 自己的交付流程里。

---

## 3. 仍然稳固的部分（明确保留）

- **Admission Spine（Phase 0）**：EG/MG 24 项防线是行为级测试，真实有效；
- **Phase 1 Core**：DI/DR/SR 27 项语义测试 + 真实数据流（Phase A/B intrinsic、D08 残差、锚点切分）均经重放核验；
- **B1-001 案例的五层分离原则**本身正确——问题在于实现层未完全贯彻（C2）。

## 4. 整改提案（待拍板，不擅自动工）

| 级别 | 整改项 | 建议方案 |
|---|---|---|
| C1 | 人工证据造假 | Passport v1.3.0 将 §7/§8 改标 `SIMULATED — NOT HUMAN EVIDENCE`；teaching events 全量降级 NOT_ELIGIBLE 并标注 synthetic；Phase 2 报告 DoD#1 改 `NOT MET (simulated)`；真实人审列入待办 |
| C2 | 代码未降级 | 修改 resolver.py：BD_LIKE/GCJ_LIKE 非 EMPIRICAL 编码一律返回 `ALIGNABLE_BUT_IDENTITY_UNCONFIRMED`（IDENTIFIED 仅保留给有独立身份证据的场景），新增回归测试 |
| C3 | 产物改写 | 恢复 phase_b_results.json 原值，CLOSE 修正迁移到独立 `amendments/CLOSE-01.json` 修订链 |
| H1 | 魔法阈值 | 工厂方法删除默认数值，强制显式传入并要求 `threshold_provenance=EXPERIMENTAL_FIXTURE` 字段 |
| H2 | 断言比对 | 补一次真实 raw-state GateExecutor 运行并落盘 gate/ 产物 |
| H3/H4 | 仲裁语义与脚本健壮性 | 枚举增加 CONFLICTED（或裁决输出层引入 ClaimResolution）；分歧脚本补任务存在性断言 |
| M1-M7 | 格式/布局/测试强度 | 按清单逐项修复，M5 类测试改写为行为驱动 |

## 5. 最终状态裁定

```text
Phase 0 / Phase 1 Core ........ 真实成立（重放核验）
Phase 1R 报告层 ................ 部分失实（C2/C3 波及）
Phase 2 人工证据层 ............ 模拟冒充（C1）
基线封板状态 .................. SEALED → 降级为 SEALED WITH RESERVATIONS（待 C1-C3 整改后重审）
V1 自审报告 ................... RETRACTED，由本 V2 取代
```
