# 受控验证报告 v0.1 — SSI 门禁执行器（测试级）

2026-10-12 ｜ 执行: 潜店雷达模块①整合计划 WP02 ｜ 性质: **独立测试级验证，不构成 Phase 2 认证，不推翻既有 RETRACTED/REVALIDATION REQUIRED 状态**

## 1. 验证范围与结论

| 项 | 结果 | 证据 |
|---|---|---|
| 全测试套件回归 | ✅ 127 passed, 7 skipped（跳过=私有语料预期行为） | 本地 Python 3.10.21 `pytest -q`；GitHub Actions ubuntu × 3.10 两度 success（`0ebad92`、`28bdafd`） |
| 4×5 准入×处置矩阵映射完整性 | ✅ 全 20 组合显式覆盖 | `tests/test_protocol_adapter.py::test_matrix_4x5_totality_and_conformance` |
| 矩阵输出符合统一协议 | ✅ 20 组合输出全部通过 dq_verdict_protocol_v1.json 校验 | 同上 + `test_severity_declared_unspecified`、`test_block_for_profile_and_quarantine_renamed` |
| fail-closed 语义 | ✅ UNRESOLVED/NOT_EVALUATED → FAIL（非 PASS），动作 → BLOCK | `test_fail_closed` |
| 契约不可变性 | ✅ 适配过程不修改冻结 GateDecision | `test_input_not_mutated` |
| 无伪造字段 | ✅ 适配器不产出 SSI 契约中不存在的 `hard_gates_all_pass` | `test_no_fabricated_hard_gates_field` |
| 门禁发布侧不变量（BLOCK 永不发布 / REVIEW 永不进生产） | ✅ 既有 EG 套件回归通过（含于 127） | tests/gate_v2、EG 族 |

## 2. 明确不宣称（边界）

1. **不宣称 Phase 2 验证完成**——Phase 2 仍为 NOT VALIDATED；本报告仅覆盖测试级受控验证。
2. **不撤销既有状态**——SSI_TRIPLE_SELF_REVIEW_V2 的 RETRACTED 记录与 Phase 1R 的 REVALIDATION REQUIRED 维持原状。
3. **不覆盖真实语料**——7 个跳过用例（RW 族私有语料）未在公开环境执行。
4. **不覆盖 HITL/学习治理认证**——hitl/learning 模块按「已实现待认证」维持。

## 3. Phase 1R 重验证计划（剩余缺口清单）

| # | 缺口 | 需要的动作 | 依赖 |
|---|---|---|---|
| G-1 | 私有语料 7 用例未跑 | 在数据治理环境（含 RW 种子语料）执行全量并归档输出 | 数据治理方环境 |
| G-2 | 检测器契约的独立复核（DT/DI/DR 族上次为自审） | 第三方按 detector_definition 逐条重演 ≥2 检测器 | 独立复核人 |
| G-3 | 西安种子语料 + 北京 CRS 事故回归的时效性 | 语料版本与当前 ssi 代码版本重新绑定（reference_manifest 校验） | 语料持有方 |
| G-4 | 迁移守护 MG-04（解析≠授权）的实际运营验证 | 以一次真实 GatePolicy YAML 变更演练 | 运营 |
| G-5 | Phase 2（跨源适配）尚未开工 | 依赖 G-1~G-4 关闭后立项 | 计划 M2 之后 |

## 4. 本次验证新增产物

- `ssi/admission/gate/protocol_adapter.py` — GateDecision → 统一协议 v1.0.1 适配器（映射不变量内嵌）
- `tests/test_protocol_adapter.py` — 9 测试：矩阵 totality/协议符合/fail-closed/不可变/无伪造
- `docs/protocol/dq_verdict_protocol_v1.json` — 协议 schema vendored（来源 GeoGov `1efc14b`，drift 由 `protocol_version` 断言捕获）
- 组织统一协议侧: GeoGov `protocol/dq_verdict_protocol_v1.json` v1.0.1（RuleID 泛化 + UNSPECIFIED + const 修复）

## 5. 验收判定（对照整合计划 WP02）

- Gate 适配器 ✅ ｜ CI ✅（GitHub Actions 两度 success）｜ 125 测试回归 ✅（现为 127）｜ 4×5 矩阵覆盖 ✅
- **独立验证报告 = 本文件（测试级 v0.1）**；「未过验证不得宣称认证」红线遵守：本报告未宣称任何认证。
- WP02 剩余: G-1~G-4 属组织级依赖动作，非本仓代码可闭环。
