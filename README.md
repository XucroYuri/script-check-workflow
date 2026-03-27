# script-check-workflow

`script-check-workflow` 是一个面向 AI 可执行剧本的 Agent Skill，用于对 AI 视频、动画、分镜执行剧本做 7-stage 线性检查、纠正与标准化输出。

它不是文学评论器，也不是故事优劣打分器。它的目标是把剧本翻译成更适合导演、分镜、AI 生成、制作协作与工业化验收的标准化执行文档。

## 这个 Skill 做什么

- 保留固定的 7-stage 检查流程、评分逻辑、终审 12 问和层间隔离原则
- 在输入为剧本文本、剧本文件路径、剧本附件、单场景或单镜原稿时，默认输出双产物
- 支持全量检查、指定 Stage 检查、单镜检查和复查
- 在只问规则、评分、阶段说明时进入说明模式，不强制生成文档

## 默认双产物

当输入的是剧本而不是规则咨询时，默认输出两份 Markdown 文档：

1. `standardized-script`
   基于 [`assets/template-standard-format.md`](assets/template-standard-format.md) 生成的标准剧本文档，不混入评分、批注、诊断说明或过程性注释。
2. `diagnostics-record`
   高细粒度诊断记录，至少包含运行范围、总分与评级、各 Stage 摘要、逐条问题、规则依据、修改策略、修改前后对照、优先级排序、冲突裁决、终审 12 问结果和复查建议。

命名规则、范围行为与交付约束见 [`references/output-artifacts.md`](references/output-artifacts.md)。

## 核心约束

- 画面层目标是 `0 心理词 / 0 主观意图 / 0 代词`
- 情绪与表演提示必须隔离在台词专属区域
- Stage 间通过精简 metrics 传递，不直接互相污染 findings
- 不用检查报告替代标准剧本文档

## 仓库结构

```text
script-check-workflow/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── template-standard-format.md
└── references/
    ├── handoff-protocol.md
    ├── output-artifacts.md
    ├── scoring-criteria.md
    ├── stage1-principles.md
    ├── stage2-scene.md
    ├── stage3-shot.md
    ├── stage4-action.md
    ├── stage5-ai-adapt.md
    ├── stage6-dialogue.md
    └── stage7-industrial.md
```

## 快速使用

安装完成后，可以直接这样触发：

```text
Use $script-check-workflow to 检查、诊断并标准化这份 AI 可执行剧本。
```

也可以给出更具体的范围：

```text
Use $script-check-workflow to 只检查这份剧本的 Stage 5 AI 生成适配问题。
Use $script-check-workflow to 只复查镜头 12-18，并输出范围限定稿与诊断档。
Use $script-check-workflow to 解释这套工作流的评分标准和终审 12 问。
```

## 安装

下面假设你的仓库地址是：

```bash
REPO_URL="https://github.com/XucroYuri/script-check-workflow.git"
```

如果你的远程地址不同，把下面命令中的仓库 URL 替换掉即可。

### Claude Code

官方 Skills 文档：<https://code.claude.com/docs/en/skills>

个人全局安装：

```bash
mkdir -p ~/.claude/skills
git clone "$REPO_URL" ~/.claude/skills/script-check-workflow
```

项目级安装：

```bash
mkdir -p .claude/skills
git clone "$REPO_URL" .claude/skills/script-check-workflow
```

说明：

- Claude Code 官方约定的技能入口是 `~/.claude/skills/<name>/SKILL.md` 或 `.claude/skills/<name>/SKILL.md`
- 项目级 skills 可以随仓库提交，适合团队共享

### Codex

官方配置参考：<https://developers.openai.com/codex/config-reference/>

Codex 官方支持通过 `~/.codex/config.toml` 中的 `skills.config` 注册技能路径。推荐做法是把仓库 clone 到任意固定目录，然后在配置中显式注册。

安装：

```bash
mkdir -p ~/.codex/skills
git clone "$REPO_URL" ~/.codex/skills/script-check-workflow
```

在 `~/.codex/config.toml` 中加入：

```toml
[[skills.config]]
path = "~/.codex/skills/script-check-workflow"
enabled = true
```

说明：

- 上面的 `[[skills.config]]` 写法是根据 Codex 官方文档中 `skills.config` 为 `array<object>` 推导出的标准 TOML 数组表写法
- 如果你更喜欢把仓库放到别的位置，只需要把 `path` 改成实际绝对路径

### Gemini CLI

官方教程：<https://geminicli.com/docs/cli/tutorials/skills-getting-started/>

Gemini CLI 官方会自动发现 `.gemini/skills`，也支持把 `.agents/skills` 作为更通用的兼容目录。

项目级安装，推荐：

```bash
mkdir -p .gemini/skills
git clone "$REPO_URL" .gemini/skills/script-check-workflow
```

通用兼容安装：

```bash
mkdir -p .agents/skills
git clone "$REPO_URL" .agents/skills/script-check-workflow
```

验证：

```text
/skills list
```

### OpenCode

官方 Skills 文档：<https://opencode.ai/docs/skills/>

OpenCode 原生支持以下目录：

- 项目级：`.opencode/skills/<name>/SKILL.md`
- 全局级：`~/.config/opencode/skills/<name>/SKILL.md`

同时它也兼容：

- `.claude/skills/<name>/SKILL.md`
- `~/.claude/skills/<name>/SKILL.md`
- `.agents/skills/<name>/SKILL.md`
- `~/.agents/skills/<name>/SKILL.md`

项目级原生安装：

```bash
mkdir -p .opencode/skills
git clone "$REPO_URL" .opencode/skills/script-check-workflow
```

全局原生安装：

```bash
mkdir -p ~/.config/opencode/skills
git clone "$REPO_URL" ~/.config/opencode/skills/script-check-workflow
```

如果你已经统一使用 `.agents/skills` 作为跨工具共享目录，也可以直接装在那里。

### OpenClaw

官方 Skills 文档：<https://docs.openclaw.ai/tools/skills>

OpenClaw 的技能加载位置与优先级为：

- 工作区：`<workspace>/skills`
- 本地共享：`~/.openclaw/skills`
- 内置 bundled skills

工作区安装：

```bash
mkdir -p skills
git clone "$REPO_URL" skills/script-check-workflow
```

本机共享安装：

```bash
mkdir -p ~/.openclaw/skills
git clone "$REPO_URL" ~/.openclaw/skills/script-check-workflow
```

说明：

- 同名 skill 冲突时，工作区目录优先于 `~/.openclaw/skills`
- OpenClaw 还支持通过配置额外增加 skill 目录，但默认上面两种安装方式已经足够

### 其他兼容 Agent Skill 的工具

如果某个 AI CLI 支持以 `SKILL.md` 作为技能入口，通常只需要保证目录结构为：

```text
<skill-root>/
└── script-check-workflow/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    └── references/
```

再把 `script-check-workflow/` 放进该工具约定的 skills 搜索路径即可。

## 验证安装是否成功

最稳妥的验证方式不是看目录，而是直接触发一次真实调用：

```text
Use $script-check-workflow to 解释这个技能会输出什么，以及什么时候进入说明模式。
```

如果工具支持列出技能，也应该能看到 `script-check-workflow` 或对应的展示名称 `剧本检查表`。

## 仓库内的重要文档

- [`SKILL.md`](SKILL.md)：skill 主入口，定义触发条件、执行流程与默认输出行为
- [`agents/openai.yaml`](agents/openai.yaml)：给支持 UI 元数据的工具使用
- [`references/output-artifacts.md`](references/output-artifacts.md)：双产物的 schema、命名规则、范围策略
- [`references/scoring-criteria.md`](references/scoring-criteria.md)：评分聚合规则
- [`references/handoff-protocol.md`](references/handoff-protocol.md)：Stage 之间如何通过精简 metrics 传递信息
- [`references/stage1-principles.md`](references/stage1-principles.md) 到 [`references/stage7-industrial.md`](references/stage7-industrial.md)：7 个阶段的规则正文

## 适用输入

- AI 视频剧本
- 动画执行稿
- 分镜脚本
- Shot list 风格的可执行镜头文本
- 已有标准稿的复查稿

## 不适用输入

- 单纯的文学审稿
- 剧情好坏评价
- 导演风格偏好争论
- 不需要产出可执行标准稿的泛创意讨论

## 维护建议

- 修改技能主逻辑时，优先更新 [`SKILL.md`](SKILL.md)
- 变更默认产物契约时，同时更新 [`references/output-artifacts.md`](references/output-artifacts.md)
- 不要把详细规则重新复制回 `README.md`，避免仓库内出现多份规则源
