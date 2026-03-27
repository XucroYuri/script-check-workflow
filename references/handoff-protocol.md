# 层间传递协议（Handoff Protocol）

本文件定义Stage之间的信息传递规范，确保上下文隔离的同时支撑必要的跨层依赖。

---

## 核心原则

1. **只传metrics，不传findings**：下游Stage不知道上游发现了什么问题
2. **metrics总量≤200 token**：防止上游信息膨胀污染下游判断
3. **只传该Stage声明需要的字段**：按prerequisite contract严格过滤

---

## Finding 输出Schema

每个Stage的sub-agent按此格式输出每条发现：

```yaml
finding:
  location: "SCENE 001 / 镜头 3 / 第12行"
  rule_id: "R1.1"
  rule_name: "主观意图降维"
  severity: "高"          # 高 / 中 / 低
  description: "画面描述中使用了意图性词汇'试图逃跑'"
  original: "胶布试图逃跑，朝出口冲去"
  corrected: "胶布转身面向出口方向，双腿交替快速迈步，上身前倾15度"
  correction_basis: "规则R1.1要求剔除目的性词汇，将意图降维为几何位移"
  confidence: 0.9         # 0-1，纠正建议的置信度
```

---

## Metrics 输出Schema

每个Stage执行完毕后，输出精简metrics摘要：

```yaml
stage_metrics:
  stage_id: "stage1"
  stage_name: "总原则检查"
  findings_count: {high: 3, medium: 5, low: 2}
  pass_rate: 0.72
  key_metrics:
    pronoun_density: 0.15        # 代词占画面描述词数比
    intent_word_count: 8         # 意图性词汇总数
    metaphor_count: 3            # 比喻依赖处数量
    six_layer_coverage: 0.85     # 六层信息覆盖率
```

---

## Prerequisite Contract（各Stage上游依赖）

### Stage 1: 总原则检查
```yaml
prerequisite: null  # 无上游依赖，首个执行
```

### Stage 2: 场景级检查
```yaml
prerequisite:
  from_stage1:
    scene_count: 3              # 剧本包含多少个场景
    scene_boundaries:           # 场景起止位置
      - {id: "S01", start: 1, end: 45}
      - {id: "S02", start: 46, end: 89}
```

### Stage 3: 镜头级检查
```yaml
prerequisite:
  from_stage2:
    scene_boundaries:           # 继承场景边界
      - {id: "S01", start: 1, end: 45}
    anchor_count_per_scene:     # 每场景锚点数量
      - {scene: "S01", anchors: 4}
```

### Stage 4: 动作表演检查
```yaml
prerequisite:
  from_stage3:
    shot_count: 24              # 总镜头数
    risk_distribution:          # 生成难度分布
      low: 12
      medium: 8
      high: 4
```

### Stage 5: AI生成适配检查
```yaml
prerequisite:
  from_stage4:
    action_complexity: 6.2      # 平均动作复杂度(1-10)
    interaction_risk_count: 5   # 高危交互镜头数
  from_stage3:
    shot_count: 24
```

### Stage 6: 台词排版检查
```yaml
prerequisite:
  from_stage1:
    character_count: 4          # 角色数量
    scene_count: 3
```

### Stage 7: 工业化检查
```yaml
prerequisite:
  all_previous_metrics_summary:  # 全部前序Stage的metrics摘要
    stage1_pass_rate: 0.72
    stage2_pass_rate: 0.80
    stage3_pass_rate: 0.65
    stage4_pass_rate: 0.78
    stage5_pass_rate: 0.60
    stage6_pass_rate: 0.90
    total_high_findings: 12
    total_findings: 35
    shot_count: 24
    scene_count: 3
```

---

## Orchestrator聚合规范

### 收集阶段
Orchestrator在每个Stage完成后：
1. 保存完整findings列表（用于最终报告）
2. 提取metrics摘要（用于下游prerequisite注入）
3. **不向下游传递findings原文**

### 冲突检测
当两个Stage对同一location提出不同correction时：
1. 记录冲突：`{location, stage_a, correction_a, stage_b, correction_b}`
2. 按SKILL.md中的冲突解决优先级规则裁决
3. 在最终报告中记录冲突及解决依据

### 报告生成
汇总全部findings → 按severity排序 → 按scoring-criteria计算得分 → 生成结构化报告
