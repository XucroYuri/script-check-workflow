# Output Artifacts

## 目录

1. 产物总览
2. 交付模式
3. 文件命名
4. standardized-script 结构
5. diagnostics-record 结构
6. 范围限定规则
7. 交付约束

## 产物总览

`剧本检查表` 的默认产物永远是两份 Markdown 文档：

1. `standardized-script`
2. `diagnostics-record`

旧的“结构化检查报告”不再单独输出；其有效内容并入 `diagnostics-record`。

## 交付模式

### 剧本文件路径输入

如果输入包含源剧本文件路径：

1. 读取源文件
2. 不覆盖源文件
3. 在源文件同目录写出两个 `.md` 文件
4. 回复里只做结果摘要，并返回写入路径

### 纯文本剧本输入

如果输入是直接粘贴的剧本文本：

1. 不主动创建文件
2. 直接内联输出两份完整 Markdown 文档
3. 先输出 `standardized-script`
4. 再输出 `diagnostics-record`

### 说明模式输入

如果输入不是剧本，而是规则、评分、阶段说明：

1. 不生成双文档
2. 按问答方式直接解释

## 文件命名

以源文件 stem 为基准命名。

### 全量检查

- `<stem>.standardized-script.md`
- `<stem>.diagnostics.md`

### 定向 Stage 检查

- `<stem>.stageN.standardized-script.md`
- `<stem>.stageN.diagnostics.md`

例如：

- `episode-01.stage5.standardized-script.md`
- `episode-01.stage5.diagnostics.md`

### 单镜范围检查

- `<stem>.shot-<scope>.standardized-script.md`
- `<stem>.shot-<scope>.diagnostics.md`

`<scope>` 应优先使用稳定的镜头标识，例如：

- `s01-03`
- `scene2-shot4`

避免使用空格、中文标点或临时描述词。

## standardized-script 结构

`standardized-script` 是干净终稿，不是 diff，不是批注稿，不是报告。

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

- 总分
- 评级
- 场景数
- 镜头数
- 高 / 中 / 低严重性问题数

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

## 范围限定规则

### 全量检查

- `standardized-script` 必须是完整标准稿
- `diagnostics-record` 覆盖全剧

### 定向 Stage 检查

- `diagnostics-record` 只写该 Stage 结果
- `standardized-script` 只重写该 Stage 直接影响到的用户指定范围
- 文首必须标注“范围限定稿”

### 单镜检查

- `diagnostics-record` 只覆盖该镜或该片段
- `standardized-script` 只输出该镜或该片段的标准化版本
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
