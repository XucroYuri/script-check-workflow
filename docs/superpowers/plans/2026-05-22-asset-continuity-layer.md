# Stage 4.5 Asset Continuity Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Stage 4.5 asset continuity layer and third `asset-continuity-ledger` artifact to `script-check-workflow`.

**Architecture:** This is a documentation-first skill update. Add one focused Stage 4.5 rule file, then wire it into the existing `SKILL.md`, handoff protocol, output artifact contract, scoring notes, README, and script template guidance. Stage 4.5 is a non-scoring continuity risk layer that produces a writer-facing ledger, diagnostic findings, low-risk standard-script patches, and compact metrics for Stage 5/7.

**Tech Stack:** Markdown skill files, YAML schema snippets, existing agent skill repository structure.

---

## File Structure

- Create `references/stage4-5-asset-continuity.md`: the authoritative Stage 4.5 rule file.
- Modify `SKILL.md`: insert Stage 4.5 into the pipeline, orchestrator flow, artifact synthesis, delivery rules, quick commands, and file index.
- Modify `references/handoff-protocol.md`: add Stage 4.5 prerequisite payload, finding schema notes, metrics, and downstream dependencies for Stage 5/7.
- Modify `references/output-artifacts.md`: convert default output from two artifacts to three artifacts and define `asset-continuity-ledger`.
- Modify `references/scoring-criteria.md`: explicitly mark Stage 4.5 as non-scoring, preserving the current 100-point scoring system.
- Modify `references/stage5-ai-adapt.md`: add Stage 4.5 continuity metrics to prerequisites and connect visual anchors/negative constraints to continuity findings.
- Modify `references/stage7-industrial.md`: add Stage 4.5 continuity metrics to prerequisites and team handoff checks.
- Modify `assets/template-standard-format.md`: add guidance that only low-risk continuity patches can enter the visual description layer; do not add heavy ledger fields to the clean script format.
- Modify `README.md`: update two-artifact language to three artifacts and describe the writer-facing ledger.

## Task 1: Add Stage 4.5 Rule File

**Files:**
- Create: `references/stage4-5-asset-continuity.md`
- Verify: `references/stage4-5-asset-continuity.md`

- [ ] **Step 1: Create the rule file**

Add `references/stage4-5-asset-continuity.md` with this content:

````markdown
# Stage 4.5: 资产连续性追踪层

## 角色定位

你是 **剧情连续性资产状态审查专家**。
你负责追踪角色、场景、道具在剧情推进过程中的状态继承、状态变化和跳跃式再出现风险。

你的输出服务编剧修改与补充，不替编剧裁决创作意图。你可以提示风险、给出推断链和多方案补写建议，但不能把涉及人物心理、剧情含义、悬念结构的推断当成最终事实。

## 管辖范围

| 资产类型 | 追踪状态 |
|----------|----------|
| 角色 | 位置、姿态、行动能力、伤势、污损、情绪/表演外化、知识状态、持物关系 |
| 场景 | 空间锚点、破坏痕迹、血迹/烟尘/水火、危险区域、光源和环境变化 |
| 道具 | 位置、归属、完整性、外观污染、功能状态、可见性、是否被移动/遗落/遮挡 |

## 核心原则

### 1. 资产状态不会因剧本省略而自动复位

角色、场景、道具只要逻辑上仍存在于剧情中，就会受到中间事件影响。
剧本没有再次明写，不代表状态没有变化。

### 2. 角色、场景、道具相互影响

不要把场景和道具只当成角色附属信息。
角色可以改变道具和场景，道具和场景也可以影响角色行动、信息披露和后续剧情理解。

示例：

```text
镜头1：角色A将刀折断并扔到地上。
中间事件：同一地点发生战场杀戮。
后续镜头：同一地点重新出现。
```

这把刀不应复位为普通完整道具。它的高概率状态是地面上的断刀，可能沾血、被踩偏、被尸体或碎片遮挡，或者被后续角色移动。

### 3. 只追踪对编剧有价值的连续性信息

进入本层的状态变化必须影响至少一项：

- 剧情逻辑
- 角色行动
- 信息披露
- 视觉锚点
- 伏笔回收
- 后续出场正确性
- 下游制作理解

纯制作资产库级别的服化、VFX、声音、天气、群演细账不进入第一版。

## 风险等级与改写权限

### 低风险：可进入 standardized-script

只补全已有事实支持的可见连续性，不新增人物动机或剧情含义。

例：

- 断裂道具后续仍为断裂状态。
- 角色伤势、污损、持物关系在连续镜头中延续。
- 被破坏场景后续仍保留碎片、血迹、烟尘、水火等留痕。

### 中风险：进入 asset-continuity-ledger，给多方案建议

可能影响画面重点、节奏、伏笔、信息披露或观众注意力。

输出最合理建议和 1-2 个备选方案，并标注 `writer_decision_needed: true`。

### 高风险：只进入 asset-continuity-ledger，必须编剧确认

涉及人物意图、心理判断、关系态度、剧情因果、悬念结构、主题象征或有意反常效果。
不得自动写入 `standardized-script`。

## 检查方法

1. 建立关键资产清单：角色、场景、道具。
2. 记录每个资产的首次出现状态与最后确认状态。
3. 提取中间事件：动作、碰撞、战斗、破坏、遗落、拾取、移动、污染、遮挡、光源变化、空间变化。
4. 推断后续再出现时的高概率状态。
5. 标注事实依据、推断链、置信度、风险等级。
6. 判断是否可低风险补入 `standardized-script`。
7. 对中高风险项输出编剧待确认问题和多方案建议。

## Finding 输出Schema

```yaml
finding:
  location: "SCENE 001 / 镜头 12"
  rule_id: "R4.5.1"
  rule_name: "资产状态跳跃再出现"
  severity: "高"
  asset_type: "prop"
  asset_name: "断刀"
  description: "断刀在战场事件后重新出现，但剧本未说明其状态是否延续或变化"
  original: "镜头回到地面，角色B跨过刀。"
  corrected: "地面上的断刀横在血迹旁，刀刃断口朝向门口。角色B从断刀右侧跨过。"
  correction_basis: "刀已被角色A折断并扔到地上，中间同一位置发生杀戮事件，后续再出现时应保留断裂和环境污染状态"
  writer_decision_needed: false
  confidence: 0.85
```

## Ledger 输出Schema

```yaml
continuity_item:
  id: "ACL-001"
  asset_type: "character | scene | prop"
  asset_name: "角色A / 废弃工厂 / 断刀"
  first_observed: "SCENE 001 / 镜头 2"
  last_confirmed_state: "角色A站立，右手持刀；刀完整"
  intervening_events:
    - "角色A将刀折断并扔到地上"
    - "同一位置发生战场杀戮"
  inferred_current_state:
    primary: "断刀仍在地面，高概率沾有血迹或被踩偏"
    alternatives:
      - "断刀被尸体或碎片部分遮挡"
      - "断刀被后续角色踢到场景边缘"
  confidence: "高 | 中 | 低"
  risk_level: "高 | 中 | 低"
  risk_reason: "后续镜头重新回到同一位置，但未说明断刀状态，可能造成视觉连续性断裂"
  writer_decision_needed: true
  recommended_script_patch:
    low_risk_patch: "地面上的断刀横在血迹旁，刀刃断口朝向门口。"
    options:
      - "保留断刀作为视觉锚点"
      - "让断刀被尸体遮挡，减少画面重点干扰"
      - "明确断刀已被角色B捡走，转为后续道具线索"
  downstream_note: "若保留断刀，Stage 5 应将其作为同一场景的视觉锚点或负向约束"
```

## Metrics 输出

```yaml
stage4_5_metrics:
  tracked_asset_count:
    character: N
    scene: N
    prop: N
  continuity_risk_count:
    high: N
    medium: N
    low: N
  high_risk_asset_jumps:
    - {asset: "资产名", from: "SCENE/镜头", to: "SCENE/镜头"}
  requires_writer_confirmation_count: N
  suggested_visual_anchor_updates:
    - {asset: "资产名", location: "SCENE/镜头", reason: "为什么应作为锚点或负向约束"}
  low_risk_patch_count: N
  pass_rate: 0.XX
```

## 非计分说明

Stage 4.5 是连续性风险层，不直接改变总分 100 分权重。
它的 findings 进入 `diagnostics-record`，低风险补写可进入 `standardized-script`，完整账本进入 `asset-continuity-ledger`。
它的精简 metrics 会传递给 Stage 5 和 Stage 7，用于 AI 生成适配和工业化接力检查。
````

- [ ] **Step 2: Verify the file exists and has required sections**

Run:

```bash
rg -n "Stage 4.5|角色定位|风险等级|Ledger 输出Schema|Metrics 输出|非计分说明" references/stage4-5-asset-continuity.md
```

Expected: one or more matching lines for each required section.

- [ ] **Step 3: Commit Task 1**

Run:

```bash
git add references/stage4-5-asset-continuity.md
git commit -m "docs: add asset continuity stage rules"
```

Expected: commit succeeds with one new file.

## Task 2: Update Handoff and Scoring Contracts

**Files:**
- Modify: `references/handoff-protocol.md`
- Modify: `references/scoring-criteria.md`
- Verify: `references/handoff-protocol.md`, `references/scoring-criteria.md`

- [ ] **Step 1: Update the handoff core principle**

In `references/handoff-protocol.md`, keep the existing three core principles and add this fourth principle after them:

```markdown
4. **Stage 4.5只传连续性metrics，不传完整账本**：下游Stage可以使用连续性风险数量、视觉锚点更新和待确认数量，但不接收完整推断链，避免把编剧待确认内容误当事实。
```

- [ ] **Step 2: Add Stage 4.5 prerequisite contract**

In `references/handoff-protocol.md`, add this section after the current Stage 4 prerequisite and before Stage 5:

````markdown
### Stage 4.5: 资产连续性追踪层
```yaml
prerequisite:
  from_stage2:
    scene_boundaries:
      - {id: "S01", start_line: 1, end_line: 45}
    anchor_count_per_scene:
      - {scene: "S01", anchors: 4}
  from_stage3:
    shot_count: 24
    scene_shot_map:
      - {scene: "S01", shots: ["S01-SH01", "S01-SH02"]}
  from_stage4:
    key_action_events:
      - {location: "S01-SH03", actor: "角色A", action: "折断刀并扔到地上", affected_asset: "刀"}
    interaction_risk_count: 5
```
````

- [ ] **Step 3: Update Stage 5 prerequisite**

Replace the current Stage 5 prerequisite block in `references/handoff-protocol.md` with:

````markdown
### Stage 5: AI生成适配检查
```yaml
prerequisite:
  from_stage4:
    action_complexity: 6.2
    interaction_risk_count: 5
  from_stage4_5:
    continuity_risk_count:
      high: 2
      medium: 5
      low: 8
    suggested_visual_anchor_updates:
      - {asset: "断刀", location: "S01-SH12", reason: "same-location reappearance after battle event"}
  from_stage3:
    shot_count: 24
```
````

- [ ] **Step 4: Update Stage 7 prerequisite**

In `references/handoff-protocol.md`, add these fields to `all_previous_metrics_summary`:

```yaml
    stage4_5_pass_rate: 0.75
    continuity_risk_high: 2
    continuity_risk_total: 15
    requires_writer_confirmation_count: 4
```

- [ ] **Step 5: Add Stage 4.5 metrics schema**

After the existing Metrics Output Schema example in `references/handoff-protocol.md`, add:

````markdown
### Stage 4.5 Metrics 输出Schema

```yaml
stage4_5_metrics:
  stage_id: "stage4_5"
  stage_name: "资产连续性追踪层"
  tracked_asset_count:
    character: 6
    scene: 3
    prop: 9
  continuity_risk_count:
    high: 2
    medium: 5
    low: 8
  high_risk_asset_jumps:
    - {asset: "断刀", from: "S01-SH03", to: "S01-SH12"}
  requires_writer_confirmation_count: 4
  suggested_visual_anchor_updates:
    - {asset: "断刀", location: "S01-SH12", reason: "same-location reappearance after battle event"}
  low_risk_patch_count: 6
  pass_rate: 0.75
```
````

- [ ] **Step 6: Mark Stage 4.5 as non-scoring**

In `references/scoring-criteria.md`, add this section after the weight table:

```markdown
## Stage 4.5 非计分说明

Stage 4.5 资产连续性追踪层是非计分连续性风险层，不改变总分 100 分权重。

它的作用是：

1. 输出 `asset-continuity-ledger`
2. 将连续性 findings 写入 `diagnostics-record`
3. 将低风险连续性补写提供给 `standardized-script`
4. 将精简 metrics 传递给 Stage 5 和 Stage 7

Stage 4.5 的 `pass_rate` 可用于诊断摘要和复查优先级，但不直接参与总分计算。
```

- [ ] **Step 7: Verify handoff and scoring references**

Run:

```bash
rg -n "Stage 4.5|stage4_5|asset-continuity-ledger|非计分" references/handoff-protocol.md references/scoring-criteria.md
```

Expected: matches in both files.

- [ ] **Step 8: Commit Task 2**

Run:

```bash
git add references/handoff-protocol.md references/scoring-criteria.md
git commit -m "docs: wire asset continuity handoff contracts"
```

Expected: commit succeeds with two modified files.

## Task 3: Update Main Skill Pipeline

**Files:**
- Modify: `SKILL.md`
- Verify: `SKILL.md`

- [ ] **Step 1: Add Stage 4.5 to the Pipeline architecture**

In `SKILL.md`, insert this block between Stage 4 and Stage 5 in the pipeline diagram:

```text
┌─────────────────────────────────────────────┐
│ Stage 4.5: 资产连续性追踪层                 │ ← references/stage4-5-asset-continuity.md
│   角色/场景/道具状态账本 · 推断链 · 编剧确认 │
│   上游依赖: scene_shot_map, key_action_events│
└──────────────┬──────────────────────────────┘
               │ metrics: {continuity_risk_count, suggested_visual_anchor_updates}
               ▼
```

- [ ] **Step 2: Update Stage 5 dependencies in the diagram**

In the Stage 5 diagram block in `SKILL.md`, change:

```text
│   上游依赖: action_complexity, shot_count     │
```

to:

```text
│   上游依赖: action_complexity, shot_count, continuity_risk_count │
```

- [ ] **Step 3: Update serial execution wording**

Replace this heading and first sentence:

```markdown
### Step 1-7: 串行执行 7 个 Stage

对每个 Stage：
```

with:

```markdown
### Step 1-7: 串行执行 7 个主 Stage 与 Stage 4.5

按 Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 4.5 → Stage 5 → Stage 6 → Stage 7 的顺序执行。

对每个 Stage：
```

- [ ] **Step 4: Add Stage 4.5-specific orchestrator note**

After the generic sub-agent prompt template in `SKILL.md`, add:

```markdown
**Stage 4.5 额外要求：**

Stage 4.5 必须输出 `asset-continuity-ledger` 条目，并把每条推断明确区分为：

1. 已确认剧本事实
2. 基于中间事件的推断状态
3. 低风险可补写项
4. 中/高风险编剧待确认项

不得把高风险人物心理、剧情含义、悬念结构推断直接写入 `standardized-script`。
```

- [ ] **Step 5: Update artifact synthesis from two artifacts to three**

In `SKILL.md`, replace the Step 10 artifact list with:

```markdown
Stage 1-9 完成后，按 [output-artifacts](references/output-artifacts.md) 合成三份默认产物：

1. **standardized-script**
   - 基于 [template-standard-format](assets/template-standard-format.md) 输出
   - 只保留标准化后的剧本正文
   - 可吸收 Stage 4.5 的低风险连续性补写
   - 不夹带评分、批注、诊断说明、过程性注释
2. **diagnostics-record**
   - 吸收旧“结构化检查报告”的全部有效信息
   - 必须保留运行范围、总分评级、Stage摘要、逐条 findings、规则依据、修改策略、修改前后对照、优先级排序、冲突裁决、终审12问结果和复查建议
3. **asset-continuity-ledger**
   - 记录角色、场景、道具的连续性状态轨迹
   - 标明已确认事实、推断状态、风险等级、编剧待确认项和多方案补写建议
   - 不替代 `standardized-script`，不作为自动改稿结论
```

- [ ] **Step 6: Update delivery rules from two documents to three**

In `SKILL.md`, change file-path delivery from "两个 Markdown 文件" to "三个 Markdown 文件", and plain-text delivery from "两个完整 Markdown 文档" to "三个完整 Markdown 文档".

Use this replacement text:

```markdown
### 文件路径输入

如果用户提供剧本文件路径：

1. 不覆盖源文件
2. 在源文件同目录写出三个 Markdown 文件
3. 文件名按 [output-artifacts](references/output-artifacts.md) 的命名规则生成
4. 回复中报告写入结果和文件路径摘要

### 纯文本输入

如果用户直接粘贴剧本文本：

1. 不主动落盘
2. 在回复中内联输出三个完整 Markdown 文档
3. 先给 `standardized-script`
4. 再给 `diagnostics-record`
5. 最后给 `asset-continuity-ledger`
```

- [ ] **Step 7: Update quick commands and file index**

In `SKILL.md`, change quick-command text:

```markdown
| 全量检查 | 7个Stage全部串行执行 + Stage 4.5 + 评分 + 终审12问 + 三产物合成 |
```

Add this file index row after Stage 4:

```markdown
| [references/stage4-5-asset-continuity.md](references/stage4-5-asset-continuity.md) | Stage 4.5 资产连续性追踪规则 | Stage 4.5 执行时 |
```

Change `output-artifacts` description from `双产物 schema、命名和交付规则` to:

```markdown
三产物 schema、命名和交付规则
```

- [ ] **Step 8: Verify SKILL references**

Run:

```bash
rg -n "Stage 4\\.5|asset-continuity-ledger|三份默认产物|三个 Markdown|stage4-5-asset-continuity" SKILL.md
```

Expected: matches for pipeline, artifacts, delivery rules, and file index.

- [ ] **Step 9: Commit Task 3**

Run:

```bash
git add SKILL.md
git commit -m "docs: add asset continuity layer to skill pipeline"
```

Expected: commit succeeds with `SKILL.md` modified.

## Task 4: Update Output Artifacts and Template Guidance

**Files:**
- Modify: `references/output-artifacts.md`
- Modify: `assets/template-standard-format.md`
- Verify: `references/output-artifacts.md`, `assets/template-standard-format.md`

- [ ] **Step 1: Update artifact overview**

In `references/output-artifacts.md`, replace the current overview with:

```markdown
`AI可执行剧本检查表V3` 的默认产物是三份 Markdown 文档：

1. `standardized-script`
2. `diagnostics-record`
3. `asset-continuity-ledger`

旧的“结构化检查报告”不再单独输出；其有效内容并入 `diagnostics-record`。
`asset-continuity-ledger` 是面向编剧的资产连续性账本，用于提示角色、场景、道具在剧情推进中的状态继承、状态变化、跳跃式再出现风险和补写建议。
```

- [ ] **Step 2: Update delivery modes**

In `references/output-artifacts.md`, change file-path delivery to write three files and plain-text delivery to inline three documents. Use:

```markdown
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
3. 先输出 `standardized-script`
4. 再输出 `diagnostics-record`
5. 最后输出 `asset-continuity-ledger`
```

- [ ] **Step 3: Add file naming rules**

In `references/output-artifacts.md`, add these names under the existing naming sections:

```markdown
### 全量检查

- `<stem>.standardized-script.md`
- `<stem>.diagnostics.md`
- `<stem>.asset-continuity-ledger.md`

### 定向 Stage 检查

- `<stem>.stageN.standardized-script.md`
- `<stem>.stageN.diagnostics.md`
- `<stem>.stageN.asset-continuity-ledger.md`

Stage 4.5 定向检查也可使用：

- `<stem>.stage4-5.asset-continuity-ledger.md`

### 单镜范围检查

- `<stem>.shot-<scope>.standardized-script.md`
- `<stem>.shot-<scope>.diagnostics.md`
- `<stem>.shot-<scope>.asset-continuity-ledger.md`
```

- [ ] **Step 4: Add ledger structure**

In `references/output-artifacts.md`, add this section after `diagnostics-record`:

````markdown
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
```
````

- [ ] **Step 5: Update range rules**

In `references/output-artifacts.md`, add this line to full-check rules:

```markdown
- `asset-continuity-ledger` 覆盖全剧关键角色、场景、道具连续性状态
```

Add this line to directed Stage rules:

```markdown
- `asset-continuity-ledger` 只覆盖该 Stage 或用户指定范围内可安全判断的连续性问题
```

Add this line to single-shot rules:

```markdown
- `asset-continuity-ledger` 只输出该镜或该片段涉及的资产连续性提示，不得补写未检查区域
```

- [ ] **Step 6: Update template guidance**

In `assets/template-standard-format.md`, add this section before "格式要点速查":

```markdown
## 资产连续性补写原则

`standardized-script` 仍然保持干净剧本格式，不新增资产账本字段。

Stage 4.5 的低风险连续性补写可以进入 `画面描述层`，例如：

- 已折断的道具后续仍写成断裂状态
- 已受伤或沾污的角色后续保持可见状态
- 已破坏的场景后续保留碎片、血迹、烟尘、水火等留痕

中风险和高风险连续性建议不得直接写入标准稿，应保留在 `asset-continuity-ledger` 中供编剧确认。
```

- [ ] **Step 7: Verify output artifact and template references**

Run:

```bash
rg -n "asset-continuity-ledger|资产连续性账本|三份|三个|低风险连续性" references/output-artifacts.md assets/template-standard-format.md
```

Expected: matches in both files.

- [ ] **Step 8: Commit Task 4**

Run:

```bash
git add references/output-artifacts.md assets/template-standard-format.md
git commit -m "docs: define asset continuity ledger artifact"
```

Expected: commit succeeds with two modified files.

## Task 5: Update Stage 5, Stage 7, and README Integration

**Files:**
- Modify: `references/stage5-ai-adapt.md`
- Modify: `references/stage7-industrial.md`
- Modify: `README.md`
- Verify: `references/stage5-ai-adapt.md`, `references/stage7-industrial.md`, `README.md`

- [ ] **Step 1: Update Stage 5 prerequisites**

In `references/stage5-ai-adapt.md`, replace the prerequisite block with:

````markdown
## 上游prerequisite

```yaml
from_stage4:
  action_complexity: N.N
  interaction_risk_count: N
from_stage4_5:
  continuity_risk_count:
    high: N
    medium: N
    low: N
  suggested_visual_anchor_updates:
    - {asset: "资产名", location: "SCENE/镜头", reason: "应作为视觉锚点或负向约束的原因"}
from_stage3:
  shot_count: N
```
````

- [ ] **Step 2: Add Stage 5 continuity note**

In `references/stage5-ai-adapt.md`, add this note after rule R5.22:

```markdown
### Stage 4.5 连续性输入使用说明

如果 Stage 4.5 输出 `suggested_visual_anchor_updates`，Stage 5 应检查这些资产是否需要成为视觉钉子或负向约束。

注意：Stage 5 只使用 Stage 4.5 的精简 metrics，不接收完整推断链。中高风险且需要编剧确认的内容，不得当成已确认事实写入 AI 生成约束。
```

- [ ] **Step 3: Update Stage 7 prerequisites**

In `references/stage7-industrial.md`, add these fields to the prerequisite block:

```yaml
  stage4_5_pass_rate: 0.XX
  continuity_risk_high: N
  continuity_risk_total: N
  requires_writer_confirmation_count: N
```

- [ ] **Step 4: Add Stage 7 handoff check**

In `references/stage7-industrial.md`, add this check item under `规则R7.35: 是否方便团队接力`:

```markdown
| **编剧/场记交接** | `asset-continuity-ledger` 是否明确列出角色、场景、道具的状态继承、待确认项和下游制作提示 |
```

Add this correction method under R7.35:

```markdown
- 连续性账本缺失或待确认项过多 → 标注需编剧优先确认的资产状态问题
```

- [ ] **Step 5: Update README default artifact language**

In `README.md`, replace "默认双产物" section with:

```markdown
## 默认三产物

当输入的是剧本而不是规则咨询时，默认输出三份 Markdown 文档：

1. `standardized-script`
   基于 [`assets/template-standard-format.md`](assets/template-standard-format.md) 生成的标准剧本文档，不混入评分、批注、诊断说明或过程性注释。
2. `diagnostics-record`
   高细粒度诊断记录，至少包含运行范围、总分与评级、各 Stage 摘要、逐条问题、规则依据、修改策略、修改前后对照、优先级排序、冲突裁决、终审 12 问结果和复查建议。
3. `asset-continuity-ledger`
   面向编剧的角色、场景、道具连续性状态账本，用于提示隐含状态变化、跳跃式再出现风险、编剧待确认项和多方案补写建议。

命名规则、范围行为与交付约束见 [`references/output-artifacts.md`](references/output-artifacts.md)。
```

- [ ] **Step 6: Update README core constraints**

In `README.md`, add this bullet under core constraints:

```markdown
- Stage 4.5 资产连续性追踪层用于输出编剧友好的状态账本；低风险物理连续性可补入标准稿，中高风险创作判断必须留给编剧确认
```

- [ ] **Step 7: Verify integration references**

Run:

```bash
rg -n "stage4_5|Stage 4\\.5|asset-continuity-ledger|默认三产物|编剧待确认" references/stage5-ai-adapt.md references/stage7-industrial.md README.md
```

Expected: matches in all three files.

- [ ] **Step 8: Commit Task 5**

Run:

```bash
git add references/stage5-ai-adapt.md references/stage7-industrial.md README.md
git commit -m "docs: integrate asset continuity with downstream stages"
```

Expected: commit succeeds with three modified files.

## Task 6: Final Verification

**Files:**
- Verify: all repository Markdown files

- [ ] **Step 1: Search for stale two-artifact language**

Run:

```bash
rg -n "双产物|两份默认产物|两个 Markdown|两个完整 Markdown|7个Stage全部串行执行" README.md SKILL.md references
```

Expected: no stale matches, except historical wording only if it explicitly says it has been replaced.

- [ ] **Step 2: Search for Stage 4.5 references**

Run:

```bash
rg -n "Stage 4\\.5|stage4_5|asset-continuity-ledger|资产连续性" README.md SKILL.md references assets
```

Expected: matches across README, SKILL, handoff protocol, output artifacts, stage4-5 rules, Stage 5, Stage 7, scoring, and template guidance.

- [ ] **Step 3: Check Markdown fences and obvious formatting issues**

Run:

```bash
rg -n "^```" README.md SKILL.md references assets docs/superpowers/specs docs/superpowers/plans
```

Expected: every file with fenced code blocks has an even number of fence lines. If the count is odd for any file, fix the nearest fence.

- [ ] **Step 4: Run git diff check**

Run:

```bash
git diff --check
```

Expected: no trailing whitespace or whitespace errors.

- [ ] **Step 5: Review final status**

Run:

```bash
git status --short
```

Expected: clean working tree after all task commits.

- [ ] **Step 6: Final summary**

Report:

```text
Implemented Stage 4.5 asset continuity layer docs, third artifact contract, handoff metrics, downstream Stage 5/7 integration, scoring non-goal, README updates, and template guidance.
```
