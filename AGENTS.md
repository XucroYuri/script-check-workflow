# AGENTS.md — AI可执行剧本检查表V3.2

<!-- MANUAL: true -->
<!-- Parent: (root) -->

## Purpose

Contract-validated, fail-closed agent skill for checking, correcting, and standardizing AI-executable screenplays through a fixed 7-stage linear pipeline. Translates scripts into concrete visual language suitable for directing, storyboarding, AI generation, and production collaboration.

## Key Files

| File | Role |
|------|------|
| `SKILL.md` | Skill entrypoint — trigger conditions, two modes (checking vs. explanation), 3-artifact output spec |
| `README.md` | Public documentation — install instructions, usage examples, multi-platform support |
| `CHANGELOG.md` | Version history |
| `contracts/workflow-contract.json` | Machine-readable workflow contract for stage validation |
| `assets/template-standard-format.md` | Canonical standardized script output format |
| `agents/openai.yaml` | UI metadata for OpenAI-compatible tool platforms |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `references/` | 12 reference files: per-stage rules (stage1-7), scoring criteria, output artifacts spec, handoff protocol, security model |
| `scripts/` | Python validation: contract integrity, scoring logic, workflow policy enforcement |
| `tests/` | Python test suite: test_contract.py, test_scoring.py, test_security_policy.py, test_workflow_order.py |
| `contracts/` | Machine-readable workflow-contract.json |
| `assets/` | Output templates and standard format definitions |
| `agents/` | Platform-specific agent metadata |
| `evals/` | Evaluation data for testing and quality assurance |
| `docs/` | Supplementary documentation |

## For AI Agents

### Working Instructions
1. Entry point is `SKILL.md` — detect mode first (checking vs. explanation)
2. When checking: run 7-stage linear pipeline, respect fail-closed policy
3. Stage handoff uses metrics only (`references/handoff-protocol.md`) — do not cross-contaminate findings between stages
4. Hard gate failures produce `BLOCKED` regardless of score
5. Output 3 artifacts: standardized/candidate script, diagnostics record, asset continuity ledger
6. Physical layer: 0 psychological words, 0 subjective intent, 0 pronouns
7. Emotion/performance annotations isolated to dialogue regions only

### Testing
```bash
python -m pytest tests/ -v
```

### Patterns
- Linear pipeline with contract-validated stage handoffs
- Fail-closed: any hard gate failure or incomplete evidence = BLOCKED
- Delivery status determined by hard gates + score thresholds (90.0 / 70.0)
- Explanation mode: direct Q&A, no document generation
- Checking mode: full pipeline execution with 3-artifact output

### Dependencies
- Python 3.x (stdlib only for validation scripts and tests)
- No external Python packages required
- Markdown skill definition (no runtime build step)
