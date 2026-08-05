---
name: project-onboard
description: |
  Complete onboarding workflow for a new or existing repository. Covers deep exploration,
  AGENTS.md generation via deepinit, Claude Code security policy configuration,
  build verification, dead-code/documentation cleanup, and GitHub push.
  Use when setting up a new project, onboarding an existing repo for AI agent work,
  or when asked to "initialize a project for AI development" or "set up AGENTS.md and
  security policies".
triggers:
  - Initialize this project for AI development
  - Set up AGENTS.md
  - Configure project security policies
  - Onboard the repo
  - Set up project Claude Code settings
  - Do a deepinit
  - Explore and document the codebase
  - Clean up redundant files
  - Push everything to GitHub
allowed-tools:
  - Bash(npm:*, git:*, ls:*, find:*, cat:*, grep:*, head:*, wc:*, date:*, echo:*, mkdir:*, cp:*, mv:*, rm:*, curl:*, sleep:*)
  - Bash(npx:*)
  - Bash(tsc:*)
  - Bash(vite:*)
  - Read
  - Write
  - Edit
  - Agent
  - WebSearch
  - WebFetch
  - LSP
  - Skill
  - AskUserQuestion
version: 1.0.0
author: OpenCLI-Studio
tags: [onboarding, deepinit, security, cleanup, documentation, settings, claude-code, project-setup]
---

# Project Onboard Skill

A complete, repeatable workflow for onboarding any repository for AI-assisted development.
Encodes the decision-making heuristics, constraints, and verification steps learned from
real-world project setup work.

## When to Use

- Taking over a new or existing repository
- Setting up AGENTS.md documentation for AI coding agents
- Configuring Claude Code project-level security policies
- Cleaning up redundant or stale documentation
- After a deepinit or project exploration session

## Workflow (6 Phases)

### Phase 1: Deep Exploration

**Goal**: Understand the project without reading every file.

1. Find the project name (directory, package.json, or git remote)
2. Read ALL config files: `package.json`, `tsconfig.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Makefile`, `Dockerfile`, `.gitignore`
3. Read README (and README_zh.md / README.zh-CN.md if present)
4. Check git remote: `git remote -v` -- is it a fork? original?
5. Check last commit: `git -C <dir> log -1 --format=%ci`
6. List top-level directory: `ls -la`
7. Determine full tech stack: languages, frameworks, key dependencies, runtime requirements

**Output**: A one-page mental model of what the project is, what it's made of, and its current state.

**Verification**: Can you explain the project in one sentence? Can you list the tech stack from memory?

### Phase 2: Deepinit (AGENTS.md Generation)

**Goal**: Create hierarchical AGENTS.md files so AI agents can navigate the codebase.

1. Call the `oh-my-claudecode:deepinit` skill
2. It maps all directories (excluding node_modules, .git, dist, build, etc.)
3. Delegates exploration to parallel sub-agents (explore src/, studio/, extension/, docs/, clis/)
4. Generates AGENTS.md files level by level (parent first, then children)
5. Validates: parent references resolve, no orphans, all required sections present

**Key Design Decisions**:
- Skip leaf directories whose content is already described in parent AGENTS.md (e.g., individual `clis/*` adapters, individual `skills/*` subdirectories)
- Skip empty directories, generated directories, and tooling directories (.omc, .git, dist, node_modules)
- Each AGENTS.md must have: Purpose, Key Files (table), Subdirectories (table), For AI Agents (working instructions, testing, patterns), Dependencies
- All files get `<!-- MANUAL: -->` marker for future hand-edits

**Verification**:
```bash
find . -name "AGENTS.md" -type f | wc -l  # Count
grep -rn "<!-- Parent:" --include="AGENTS.md" .  # Check hierarchy
# Verify each parent reference resolves to a real file
```

### Phase 3: Claude Code Security Configuration

**Goal**: Create a project-level `.claude/settings.json` with precise Bash whitelist.

**Principles**:
1. `defaultMode: "acceptEdits"` -- file edits auto-approved, other ops prompt
2. `allow` list: only operations the project actually needs
3. `deny` list: only hard red lines (rm -rf, rm -r, sudo, chown, system file redirection)
4. Operations with legitimate but rare use cases should NOT be in deny -- they should just trigger a confirmation prompt
5. Keep it minimal: merge redundant rules (e.g., `Bash(git:*`)` covers all git operations)

**Allow list template** (adapt for each project):
```
Read, Write, Edit, Glob, Grep           ← Code operations
Bash(npm run:*, npm install:*, npx:*)   ← Build ecosystem
Bash(git:*)                              ← Version control
Bash(npx tsx:*, npx vitest:*, tsc:*, vite:*) ← Compile & test
Bash(ls:*, find:*, cat:*, head:*, wc:*, grep:*, sort:*) ← Read-only queries
Bash(date:*, echo:*, mkdir:*, cp:*, mv:*, rm:*, sleep:*) ← File ops
Bash(node:dist/src/main.js:*)            ← Run the built CLI
Bash(curl:*)                             ← HTTP debugging
Agent, WebSearch, WebFetch, LSP, Skill, TodoWrite, AskUserQuestion
```

**Deny list template** (hard red lines):
```
Bash(rm -rf:*), Bash(rm -r:*)   ← Recursive deletion
Bash(> /dev:*, > /etc:*)        ← System file redirection
Bash(sudo:*), Bash(chown:*)     ← Privilege escalation
```

**Pitfalls to avoid**:
- Don't add `chmod` to deny -- scripts may need `+x`
- Don't add `wget` to deny -- no one uses it, don't silently block it
- Don't restrict `curl` to localhost only -- debugging APIs needs external access
- Don't forget to update `.gitignore` to allow `.claude/settings.json`

**Verification**: Read the final file and confirm every entry has a clear justification.

### Phase 4: Build Verification

**Goal**: Confirm the project actually builds and runs.

1. Check Node version: `node --version`
2. Install dependencies: `npm install --ignore-scripts` (skip postinstall to avoid side effects)
3. Type check: `npx tsc --noEmit`
4. Build: `npm run build`
5. Run CLI: `node dist/src/main.js list` (or equivalent for non-Node projects)

**Verification**: All steps pass. Working tree stays clean after restoring side-effect files.

### Phase 5: Cleanup

**Goal**: Identify and remove redundant/stale content.

**What to look for**:
1. **Duplicate documentation directories** -- e.g., `docs/adapters-doc/` vs `docs/adapters/browser/` (check if content overlaps)
2. **Stale design docs** -- are `designs/` and `docs/superpowers/specs/` redundant? Don't delete, just note the relationship
3. **Empty or near-empty directories** -- only has 1-2 files that could live elsewhere
4. **Unused directory structure experiments** -- directories with only one file that don't match the project's established patterns

**Rules for cleanup**:
- If two files overlap on the same topic, merge and remove the redundant one
- If a directory was an early experiment that was abandoned, clean it up
- Don't delete unique content just because it's in an unusual location
- Every deletion must have a clear reason you can explain in the commit message

### Phase 6: Push to GitHub

**Goal**: Get everything committed and pushed.

1. Verify clean working tree: `git status --short`
2. Commit each logical change separately (docs, config, cleanup)
3. Use conventional commit format: `docs:`, `chore:`, `fix:`, `feat:`
4. Use `gh auth status` to check GitHub authentication
5. Push via `gh` credential helper: `git -c credential.helper='!gh auth git-credential' push origin main`
6. If pushing fails, try `gh` CLI directly. Don't keep retrying raw tokens -- GitHub deprecated password-in-URL auth.

**Branch strategy**:
- For forks: create a feature branch first, PR to main later
- Add `upstream` remote for forks: `git remote add upstream <original-repo>`
- `main` should stay clean for upstream syncs

## Project-Specific Adaptations for OpenCLI-Studio

This skill was extracted from onboarding the OpenCLI-Studio project (a fork of jackwener/OpenCLI).
Specific adaptations for this project:

- **Env vars to add to settings.json**: `OPENCLI_DAEMON_PORT`, `OPENCLI_VERBOSE`
- **Plugins to keep**: oh-my-claudecode, superpowers, typescript-lsp
- **Plugins to drop**: glm-plan-bug, glm-plan-usage (GLM-specific, not relevant)
- **Build command**: `npm run build` (includes tsc + studio build + manifest generation)
- **Run command**: `node dist/src/main.js list`
- **Key directories to AGENTS.md**: src/ (10 subdirs), studio/, extension/, clis/, docs/, skills/, scripts/

## Success Criteria

After completing all 6 phases:
- [ ] Can explain the project in one sentence
- [ ] Full tech stack identified
- [ ] 15-20 AGENTS.md files with valid parent references
- [ ] `.claude/settings.json` committed with precise allow/deny rules
- [ ] Project builds and CLI runs successfully
- [ ] Redundant documentation consolidated
- [ ] All commits pushed to GitHub
- [ ] Working tree clean

## Quality Gate

Before running this skill, confirm:
- "Is this a real codebase?" → Yes (not a template/hello-world)
- "Will AI agents work on this?" → Yes
- "Is the current state undocumented/under-documented?" → Yes
