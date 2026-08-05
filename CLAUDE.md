# CLAUDE.md — AI可执行剧本检查表V3.2

## Project Identity
- **Name**: script-check-workflow (内部 skill ID: `script-check-workflow`)
- **Display Name**: AI可执行剧本检查表V3.2
- **Type**: Agent Skill — contract-validated, fail-closed checker + standardizer
- **Stack**: Python 3 (validation scripts + tests) + Markdown (skill definition + reference rules)
- **Remote**: `origin` = git@github.com:XucroYuri/script-check-workflow.git
- **Last Active**: 2026-07-17 (most recently active of the literary-creation group)
- **Version**: V3.2 (stable — install with `--branch v3.2.0`)

## Quick Reference

```bash
python --version                       # Python 3.x required for tests
python -m pytest tests/ -v            # Run contract, scoring, security, workflow tests
python scripts/workflow_policy.py     # Workflow policy validation
```

## What This Is

A contract-validated, fail-closed agent skill that checks, corrects, and standardizes AI-executable screenplays through a fixed 7-stage pipeline. It translates scripts into visual language — concrete, shootable, decomposable, and verifiable by production teams.

**Not** a literary review tool or story quality judge. It is a checker + standardizer for production-ready scripts.

### Pipeline: 7 Stages

```
Stage 1: 总原则检查 (Physical reduction, de-pronoun, de-metaphor, 6-layer info)
Stage 2: 场景级检查 (Spatial anchors, initial state, atmosphere source, cross-scene consistency)
Stage 3: 镜头级检查 (Shot-level precision)
Stage 4: 动作层 (Action description standardization)
Stage 4.5: 资产连续性 (Asset continuity ledger for characters, scenes, props)
Stage 5: AI生成适配 (AI generation adaptation checks)
Stage 6: 台词层 (Dialogue isolation, emotional annotations)
Stage 7: 工业化验收 (Industrial delivery standards)
```

### Delivery States

| State | Meaning |
|-------|---------|
| `READY` | All hard gates passed, score >= 90.0 |
| `CONDITIONAL` | All hard gates passed, score 70.0-89.9 |
| `REWORK` | All hard gates passed, score < 70.0 |
| `BLOCKED` | Hard gate failed or contract/security incomplete |

### Default Three Artifacts (when input is a script)

1. `standardized-script` or `candidate-script` (based on delivery state)
2. `diagnostics-record` (fine-grained per-stage diagnostics)
3. `asset-continuity-ledger` (character/scene/prop continuity tracking)

## Architecture

```
Input (script text / file path)
  → SKILL.md (orchestration, mode detection, trigger logic)
    → Stage 1-7 pipeline (linear, contract-validated, fail-closed)
      → references/stage1-principles.md ... stage7-industrial.md (per-stage rules)
        → references/scoring-criteria.md (aggregation)
        → references/output-artifacts.md (delivery rules)
        → references/handoff-protocol.md (stage-to-stage metrics handoff)
      → scripts/ (Python validation: contract, scoring, workflow)
      → tests/ (Python tests for contracts, scoring, security, workflow order)
```

### Directory Map

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Skill entrypoint — trigger conditions, execution flow, default outputs |
| `references/` | 12 reference files: 7 stage rules + scoring + output artifacts + handoff + security + asset continuity |
| `scripts/` | Python validation: contract.py, scoring.py, workflow_policy.py |
| `tests/` | Python tests: contract, scoring, security policy, workflow order |
| `contracts/` | workflow-contract.json — machine-readable workflow contract |
| `assets/` | template-standard-format.md — script formatting template |
| `agents/` | openai.yaml — UI metadata for OpenAI-compatible tools |
| `evals/` | Evaluation data and test cases |
| `docs/` | Additional documentation |

## Working With This Repo

1. **SKILL.md is the entrypoint** — defines triggers, modes, and execution flow
2. **Stage rules are in references/** — one file per stage, plus scoring, handoff, artifacts
3. **Python validates contracts** — `scripts/` validates structural integrity, `tests/` validates correctness
4. **Fail-closed design** — if contract validation fails, output is `BLOCKED` regardless of score
5. **Assets are templates** — `assets/template-standard-format.md` is the canonical output format

## Agent Working Instructions

- When invoked as `$script-check-workflow`, follow `SKILL.md` execution flow
- Two modes: **checking mode** (script input -> 3 artifacts) and **explanation mode** (rule/scoring questions -> direct answer)
- Respect the linear pipeline — do not skip stages or mix findings across stages
- Stage handoff uses metrics only (defined in `references/handoff-protocol.md`), not raw findings
- Physical layer goal: 0 psychological words, 0 subjective intent, 0 pronouns — pure physical and geometric description
- Emotion/performance annotations must be isolated to dialogue regions only

## Development Rules

1. **Stage rules in references/ are source of truth** — do not duplicate them in SKILL.md or README.md
2. **Test before changing pipeline logic** — `python -m pytest tests/` must pass
3. **Contract changes require contract.json update** — keep `contracts/workflow-contract.json` in sync
4. **Commit format**: `feat:`, `fix:`, `docs:`, `test:` with bilingual descriptions
5. **Version tags**: stable releases tagged with semver (v3.2.0, etc.)

## Avoid

- Adding literary critique to checking logic
- Weakening fail-closed safety rules
- Duplicating reference rules into SKILL.md or README.md
- Mixing checking output with standardized script documents
- Changing stage order or adding stages without updating contract.json and all tests
