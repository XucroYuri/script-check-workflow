# Output Artifacts

## 目录

1. 产物总览
2. 交付模式
3. 文件命名与 no-clobber
4. standardized-script 结构
5. diagnostics-record 结构
6. asset-continuity-ledger 结构
7. 范围限定规则
8. 交付约束
9. 安全发布事务

## 产物总览

`AI可执行剧本检查表V3` 的默认产物是三份 Markdown 文档。剧本文档名称由硬门槛结果决定：

1. `standardized-script`（仅 `READY` / `CONDITIONAL`）或 `candidate-script`（`BLOCKED`）
2. `diagnostics-record`
3. `asset-continuity-ledger`

旧的“结构化检查报告”不再单独输出；其有效内容并入 `diagnostics-record`。
`asset-continuity-ledger` 是面向编剧的资产连续性账本，用于提示角色、场景、道具在剧情推进中的状态继承、状态变化、跳跃式再出现风险和补写建议。

## 交付模式

### 剧本文件路径输入

如果输入包含源剧本文件路径：

1. 读取源文件
2. 不覆盖源文件
3. 在源文件同目录写出三个 `.md` 文件
4. 回复里只做结果摘要，并返回写入路径

### 纯文本剧本输入

如果输入是直接粘贴的剧本文本：

1. 不主动创建文件
2. 直接内联输出三份完整 Markdown 文档
3. 先输出与交付状态相符的 `standardized-script` 或 `candidate-script`
4. 再输出 `diagnostics-record`
5. 最后输出 `asset-continuity-ledger`

### 说明模式输入

如果输入不是剧本，而是规则、评分、阶段说明：

1. 不生成默认产物文档
2. 按问答方式直接解释

## 文件命名与 no-clobber

每次文件模式运行生成 UTC run ID：`YYYYMMDDTHHMMSSZ`。

通过全部硬门槛：

- `<stem>.<run-id>.standardized-script.md`
- `<stem>.<run-id>.diagnostics.md`
- `<stem>.<run-id>.asset-continuity-ledger.md`

未通过硬门槛：

- `<stem>.<run-id>.candidate-script.md`
- `<stem>.<run-id>.diagnostics.md`
- `<stem>.<run-id>.asset-continuity-ledger.md`

写入策略固定为 `fail-if-exists`。写入前必须同时检查三个目标路径；任一目标已存在时停止并返回 `BLOCKED: OUTPUT_EXISTS`。不得静默覆盖或只写出部分产物。

## 安全发布事务

完整安全规则以 [security-model.md](security-model.md) 为准。发布前必须对三个最终目标做同一次预检，写入并验证三个同目录临时文件。三个重命名操作不是一个原子事务：通过硬门槛时按“diagnostics → asset-continuity-ledger → standardized-script 最后”的顺序发布；候选交付时按“diagnostics → asset-continuity-ledger → candidate-script 最后”的顺序发布。

任一 rename/no-replace 失败时，删除本次已发布的文件和全部临时文件，并返回 `BLOCKED: OUTPUT_COMMIT_FAILED`；不得覆盖既有文件，也不得留下看似完整的标准稿或候选稿。

## standardized-script 结构

`standardized-script` 是干净终稿，不是 diff，不是批注稿，不是报告。
只有候选稿通过全部硬门槛并获得 `READY` 或 `CONDITIONAL` 状态后，才可晋升并命名为 `standardized-script`。`BLOCKED` 时必须保留 `candidate-script` 名称，且不得输出任何名为 `standardized-script` 的产物。

### 必须包含

1. 标准化场景标题
2. 标准化镜头标题
3. 画面描述层
4. 必要时的 `SFX / UI / 屏显`
5. 台词块

### 必须遵守

1. 使用 [../assets/template-standard-format.md](../assets/template-standard-format.md) 的版式
2. 应用检查后接受的修改结果
3. 不插入评分
4. 不插入“问题说明”
5. 不插入“为什么这样改”
6. 不插入 TODO、注释、评语

### 推荐开头

全量检查时直接从剧本正文开始，不需要额外摘要。

范围限定时在文首添加：

```markdown
> 范围限定稿
> 本文仅重写用户指定范围，不代表全剧终稿。
```

## diagnostics-record 结构

`diagnostics-record` 是高细粒度过程记录，必须可追踪、可复查、可排序执行。

### 最小章节

```markdown
# 剧本诊断记录

## 运行范围
## 总览
## 各Stage摘要
## 高优先级修改清单
## 逐条问题记录
## 修改前→修改后对照
## 冲突裁决记录
## 终审12问结果
## 复查建议
```

### 章节要求

#### 运行范围

- 输入来源：文件路径 / 纯文本
- 检查类型：全量 / Stage N / 单镜 / 复查
- 覆盖范围：场景、镜头、行号或用户指定片段
- 交付方式：落盘 / 内联

#### 总览

- `run_id`
- `workflow_version`
- `input_sha256`
- `target_profile`
- `delivery_status`
- `hard_gate_results`
- `original_baseline`：原稿首次审查的 findings、metrics 及可选基线分数，仅用于修改前对照
- `candidate_final`：最终候选稿完整复审的 findings、metrics、终审结果、硬门槛结果及通过门槛后的分数与评级
- 总分（仅来自 `candidate_final`）
- 评级（仅来自 `candidate_final`）
- 场景数
- 镜头数
- 高 / 中 / 低严重性问题数

diagnostics 必须同时包含 `original_baseline` 和 `candidate_final`，但只有 `candidate_final` 控制交付状态。不得用 `original_baseline` 的通过率、问题数、分数或评级覆盖候选稿结论。

#### 各Stage摘要

按 Stage 汇总：

- 得分
- 满分
- 通过率
- 该 Stage 的关键风险
- 该 Stage 的主要修改方向

#### 高优先级修改清单

优先收录高严重性问题；不足时再补中严重性问题。

建议表头：

| # | 定位 | 违反规则 | 严重性 | 问题 | 建议修改 |
|---|------|----------|--------|------|----------|

#### 逐条问题记录

每条问题至少包含：

- 定位
- 违反规则
- 严重性
- 问题描述
- 修改前
- 修改后
- 纠正依据
- 修改策略

#### 修改前→修改后对照

优先展示最影响可生成性、可验收性、可交接性的修改。

#### 冲突裁决记录

若无冲突，明确写：

`本次未发现跨 Stage 冲突。`

若有冲突，至少写明：

- 冲突位置
- 冲突双方
- 双方建议
- 裁决结果
- 裁决依据

#### 终审12问结果

按镜头列出通过数、状态、需改项。

#### 复查建议

输出下一轮最值得复查的范围和顺序。

## asset-continuity-ledger 结构

`asset-continuity-ledger` 是面向编剧的资产连续性账本，不是制作资产数据库，也不是自动改稿结论。

### 最小章节

```markdown
# 资产连续性账本

## 运行范围
## 总览
## 高风险连续性缺口
## 资产状态轨迹
## 状态变化推断链
## 编剧待确认项
## 可进入标准稿的低风险补写
## 多方案补写建议
## 下游制作提示
```

### 条目要求

每条记录至少包含：

- 资产类型：角色 / 场景 / 道具
- 资产名称
- 首次出现位置
- 最后确认状态
- 中间事件
- 推断当前状态
- 置信度
- 风险等级
- 风险原因
- 是否需要编剧确认
- 低风险补写或多方案建议
- 下游制作提示

### 写作约束

1. 已确认事实和推断状态必须分开写。
2. 中高风险项必须标注 `编剧待确认`。
3. 不把人物心理、剧情含义、悬念结构推断写成事实。
4. 不把账本内容混入 `standardized-script`。

## 范围限定规则

### 全量检查

- `standardized-script` 必须是完整标准稿
- `diagnostics-record` 覆盖全剧
- `asset-continuity-ledger` 覆盖全剧关键角色、场景、道具连续性状态

### 定向 Stage 检查

- `diagnostics-record` 只写该 Stage 结果
- `standardized-script` 只重写该 Stage 直接影响到的用户指定范围
- `asset-continuity-ledger` 只覆盖该 Stage 或用户指定范围内可安全判断的连续性问题
- 文首必须标注“范围限定稿”

### 单镜检查

- `diagnostics-record` 只覆盖该镜或该片段
- `standardized-script` 只输出该镜或该片段的标准化版本
- `asset-continuity-ledger` 只输出该镜或该片段涉及的资产连续性提示，不得补写未检查区域
- 不得补写未检查区域

### 只做评分 / 只做终审

- 默认只输出 `diagnostics-record`
- 不强行生成 `standardized-script`

## 交付约束

1. 永远不要覆盖用户原稿。
2. 永远不要把诊断内容混进 `standardized-script`。
3. 永远不要把 `standardized-script` 伪装成全剧终稿，除非本次确实做了全量检查。
4. 写文件时返回明确路径；内联时返回完整 Markdown，而不是摘要占位符。
5. 若信息不足以安全重写某段内容，在 `diagnostics-record` 中显式记录缺口，不要在 `standardized-script` 中编造。
