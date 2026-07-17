# 评分标准与交付分类

## 规则清单

合同 `workflow-contract.json` 声明 35 条计分规则和 7 条非计分风险/建议规则；两类规则互斥，合计 42 条。

### 计分规则（35 条）

| Stage | 规则 | 权重 |
|---|---|---:|
| 1 | R1.1、R1.2、R1.3、R1.4 | 7、7、5、6 |
| 2 | R2.5、R2.6、R2.7、R2.8 | 4、4、4、3 |
| 3 | R3.9、R3.10、R3.11、R3.12、R3.13、R3.14 | 5、4、3、3、3、2 |
| 4 | R4.15、R4.16、R4.16.5、R4.17、R4.18、R4.19 | 4、4、3、2、1、1 |
| 5 | R5.20、R5.21、R5.22、R5.23、R5.24、R5.25、R5.26 | 3、3、3、2、2、1、1 |
| 6 | R6.28、R6.29、R6.30、R6.31 | 2、1、1、1 |
| 7 | R7.34、R7.35、R7.36、R7.37 | 2、2、0.5、0.5 |

以上权重合计 100.0。计分规则 ID 与权重以合同为唯一机器可读来源。

### 非计分风险/建议规则（7 条）

`R4.5.1`、`R4.5.2`、`R4.5.3`、`R4.5.4`、`R5.27`、`R6.32`、`R6.33` 只输出风险或建议，不参与数值总分。Stage 4.5 资产连续性追踪也属于此风险层。

## 确定性评分

对每条计分规则记录：

- `applicable`：候选稿中该规则适用的检查单元数。
- `passed`：适用单元中通过的数量。
- 必须满足 `0 <= passed <= applicable`。

单规则通过率：`passed / applicable`。`applicable = 0` 的规则标记为 N/A，不参与分母。

总分：

`100 × Σ(适用规则权重 × 规则通过率) / Σ(适用规则权重)`

结果四舍五入到 1 位小数，范围固定为 0.0–100.0。finding 严重性不再重复参与扣分，而是进入硬门槛。

## 硬门槛

评分前必须全部满足：

1. `contract_valid`
2. `post_synthesis_review_complete`
3. `unresolved_high_findings_zero`
4. `unresolved_high_writer_confirmations_zero`
5. `final_review_red_count_zero`
6. `artifact_schema_valid`
7. `target_profile_declared`
8. `input_budget_valid`

任一项失败，状态为 `BLOCKED`，无论数值分数多高都不得进入生产。

## 交付分类

| 条件 | 状态 | 含义 |
|---|---|---|
| 任一硬门槛失败 | `BLOCKED` | 不得输出 standardized-script |
| 门槛全过且 90.0–100.0 | `READY` | 可进入下一制作环节，仍需按项目验收流程执行 |
| 门槛全过且 70.0–89.9 | `CONDITIONAL` | 允许交付，但必须按 diagnostics 继续优化 |
| 门槛全过且 0.0–69.9 | `REWORK` | 保留 `candidate-script` 名称；候选稿需要重做，不进入生产 |
