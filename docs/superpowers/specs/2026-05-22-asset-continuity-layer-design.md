# Stage 4.5 Asset Continuity Layer Design

## Context

The current `script-check-workflow` skill standardizes AI-executable scripts through a 7-stage linear review pipeline and produces two default artifacts:

1. `standardized-script`
2. `diagnostics-record`

This design adds a third artifact and a new pipeline layer to address a gap in traditional script formats: the script advances linearly through plot, while characters, scenes, and props often appear discontinuously in the text. Even when the script does not restate an asset's state, the asset may have logically changed because of intervening plot events.

The goal is to reduce information loss and friction between the writing layer and later film, animation, AI generation, and production workflows without letting the agent override the writer's creative intent.

## Decision Summary

Add a new independent layer:

```text
Stage 4.5: 资产连续性追踪层
```

Internal identifier:

```text
asset-continuity-layer
```

Add a third default artifact:

```text
asset-continuity-ledger
```

The layer should produce a writer-facing continuity ledger for characters, scenes, and props. It should surface likely state changes, reasoning chains, risk levels, and rewrite options. The writer keeps final authority over creative meaning, character psychology, suspense structure, and intentional omissions.

## Scope

Stage 4.5 tracks continuity states for three asset classes:

| Asset Type | Tracked State Examples |
|---|---|
| Character | location, posture, action capacity, injury, dirt/blood, visible emotional performance, knowledge state, possession state |
| Scene | spatial anchors, damage, blood/smoke/water/fire, danger zones, light source changes, environmental traces |
| Prop | location, owner/holder, integrity, visible contamination, function state, visibility, moved/dropped/hidden state |

The scope is not a full production asset database. The first version tracks only continuity information that affects at least one of these writing-level concerns:

- plot logic
- character action
- information disclosure
- visual anchors
- setup and payoff
- later reappearance correctness
- downstream production interpretation

Pure production-management details such as exhaustive costume, VFX, sound, weather, extras, and department-level asset inventories remain out of scope for the first version.

## Core Principle: Mutual Asset Influence

The layer must not treat scenes and props only as dependencies of characters. Characters, scenes, and props can each have independent state trajectories and can modify one another.

Example:

1. Character A breaks a knife and throws it on the ground.
2. A battle occurs in the same location.
3. Later, the same location reappears.

The knife should not silently reset to an intact or generic prop. Its likely current state may be: a broken knife on the ground, possibly bloodstained, kicked aside, partly covered, or still acting as a visual anchor. The ledger should ask the writer whether to clarify this state, preserve it as a clue, hide it to avoid stealing focus, or explain that another character moved it.

## Pipeline Placement

Insert Stage 4.5 after Stage 4 and before Stage 5:

```text
Stage 1: 总原则检查
  ↓
Stage 2: 场景级检查
  ↓
Stage 3: 镜头级检查
  ↓
Stage 4: 动作表演检查
  ↓
Stage 4.5: 资产连续性追踪层
  ↓
Stage 5: AI生成适配检查
  ↓
Stage 6: 台词排版检查
  ↓
Stage 7: 工业化检查
  ↓
Scoring / Final Review / Artifact Synthesis
```

Rationale:

- Stage 4.5 needs scene boundaries, shot structure, action events, character presence, prop use, and scene changes.
- Stage 4.5 should still run before Stage 5 and Stage 7 so its results can inform AI generation stability, visual anchors, negative constraints, team handoff, and shot acceptance.

## Inputs

Stage 4.5 receives:

1. The original script text.
2. A compact prerequisite payload extracted from upstream stages.

It should not receive full findings from Stage 1-4. This preserves the current pipeline's layer-isolation principle.

Suggested prerequisite payload:

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

## Outputs

Stage 4.5 outputs:

1. Full ledger entries for `asset-continuity-ledger`.
2. Continuity findings for `diagnostics-record`.
3. Low-risk continuity patches that may be applied to `standardized-script`.
4. Compact metrics for Stage 5-7.

Suggested metrics:

```yaml
stage4_5_metrics:
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
```

## Artifact: asset-continuity-ledger

Default file name:

```text
<stem>.asset-continuity-ledger.md
```

Range-specific file names:

```text
<stem>.stage4-5.asset-continuity-ledger.md
<stem>.shot-<scope>.asset-continuity-ledger.md
```

Recommended Markdown structure:

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

Recommended entry schema:

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

## Risk Levels and Rewrite Authority

Stage 4.5 suggestions use three risk levels.

### Low Risk: May Enter standardized-script

Low-risk patches complete visible continuity already supported by explicit script facts. They do not add new motivation, character meaning, or plot causality.

Examples:

- A broken, dropped, damaged, or bloodied prop remains in that physical state when reappearing.
- A visible injury, stain, or held object continues across shots.
- A damaged, flooded, burning, or debris-filled scene retains those traces.
- A light source, spatial anchor, or danger zone continues to exist unless the script removes it.

### Medium Risk: Ledger Recommendation with Options

Medium-risk items may affect shot focus, setup/payoff, pacing, or information disclosure. They should not be silently applied.

Examples:

- A prop can become a visual anchor but might steal attention from the scene focus.
- A character's visible reaction after a frightening event has multiple plausible strengths.
- A scene trace may function as a clue or may remain background texture.
- A prop's movement, concealment, or visibility changes the viewer's attention.

Output format:

- primary recommendation
- one or two alternatives
- reason for recommendation
- `writer_decision_needed: true`

### High Risk: Writer Confirmation Required

High-risk items involve creative intent and must not be written into the final standardized script by default.

Examples:

- Inferring true psychology, character choice, betrayal, concealment, or relationship change.
- Reframing a state as symbolism, theme, or deliberate foreshadowing.
- Changing plot causality, suspense structure, or viewer information order.
- Treating an intentional abnormal state as an error.

Decision rule:

```text
Objective visual fact support → low risk, may patch standardized-script
Presentation strength or focus choice → medium risk, ledger options
Character intent, plot meaning, suspense structure → high risk, writer confirmation
```

## Existing File Changes Needed

Implementation should update the repository as follows:

1. Add `references/stage4-5-asset-continuity.md`.
2. Update `SKILL.md` to include Stage 4.5 in the pipeline and orchestrator steps.
3. Update `references/handoff-protocol.md` with Stage 4.5 prerequisites and metrics.
4. Update `references/output-artifacts.md` so the default artifact set becomes:
   - `standardized-script`
   - `diagnostics-record`
   - `asset-continuity-ledger`
5. Update `README.md` to describe three-artifact output and the writer-facing continuity ledger.
6. Update `assets/template-standard-format.md` only with guidance that low-risk continuity patches may enter the visual description layer. Do not force new fields into the clean script template.

## Non-Goals

- Do not build a production asset database in the first version.
- Do not require writers to accept inferred state changes.
- Do not automatically insert high-risk psychological or plot-meaning deductions into `standardized-script`.
- Do not expand the standard script template with heavy state-tracking fields.
- Do not pass full Stage 4.5 reasoning into downstream stages; pass compact metrics and selected anchor updates.

## Acceptance Criteria

- The skill can explain and run a Stage 4.5 asset continuity pass.
- Script inputs produce three artifacts by default.
- The ledger clearly distinguishes confirmed facts, inferred states, alternatives, and writer-confirmation items.
- Low-risk continuity patches can be applied to `standardized-script` without changing creative meaning.
- Medium/high-risk items remain visible to the writer in the ledger.
- Stage 5 and Stage 7 can consume compact Stage 4.5 metrics without receiving the full ledger.
