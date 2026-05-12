# Public Source Attribution Audit

Date: 2026-05-12

## Purpose

Record the public-source attribution review for RhapsodIA skills after the root README attribution update in PR #8.

This document is repository metadata. It is intentionally not referenced from operational `SKILL.md` files because it does not affect skill execution and should not add runtime context cost.

## Scope

Reviewed the repository attribution posture for public-source similarity and missing source notes across RhapsodIA skill packages, with emphasis on:

- copied, adapted, derived, or inspired third-party skill packages;
- public skills with exact or near-exact names;
- public registries that mirror or index `SKILL.md` packages;
- upstream notes already present inside this repository.

This audit is not a legal opinion and does not prove absence of every possible similar private or unpublished source. It records evidence found in accessible public sources and repository files.

## Public sources checked

The review included searches and spot checks across public repositories and skill registries, including:

- OpenAI `skills` repository: `https://github.com/openai/skills`
- Anthropic `skills` repository: `https://github.com/anthropics/skills`
- Anthropic `claude-plugins-official` skill creator plugin: `https://github.com/anthropics/claude-plugins-official`
- GitHub `awesome-copilot`: `https://github.com/github/awesome-copilot`
- `awesome-copilot` website and listing guidance: `https://awesome-copilot.github.com`
- Agent Skills registry examples: `https://agent-skills.md`
- SkillsMP: `https://skillsmp.com`
- SkillMD and related public skill indexes: `https://skillmd.io`, `https://skillmd.ai`
- Elite AI Tools skill listings: `https://eliteai.tools/agent-skills`
- ExplainX skill listings: `https://explainx.ai/skills`
- Learn Skills listings: `https://learn-skills.dev`
- Paperclip skill listings: `https://papercliporg.com/skills`
- Smithery skill listings: `https://smithery.ai/skills`
- Agent Layer skill specification notes: `https://agent-layer.dev/skill-design/`
- OpenCrabs skill system documentation: `https://docs.opencrabs.com/features/skills.html`

## Search patterns used

Representative searches included exact skill names and category searches such as:

- `skill-creator SKILL.md`
- `skill-improver SKILL.md`
- `prompt-architect SKILL.md`
- `agent-design SKILL.md`
- `secure-code-review SKILL.md`
- `security-and-governance-review SKILL.md`
- `skill-hardening SKILL.md`
- `skill-benchmark SKILL.md`
- `benchmark-skills SKILL.md`
- `skill-harness SKILL.md`
- `skill-consistency-repair SKILL.md`
- `skill-package-architecture-review SKILL.md`
- `skill-prompt-and-activation-review SKILL.md`
- `context-architect awesome-copilot`

## Confirmed attribution cases

### `skills/skill-creator/`

Status: already covered.

The repository includes OpenAI `skill-creator` content and preserves the Apache License 2.0 notice in `skills/skill-creator/LICENSE.txt`. The README already lists this package under known third-party or adapted content.

### `skills/streamlit/`

Status: already covered.

The package is documented as an original RhapsodIA skill built from and cross-referencing official Streamlit documentation and source repositories. The local source note remains in `skills/streamlit/references/source-and-license.md`.

### `skills/context-architect/`

Status: covered by PR #8.

The repository already contained `skills/context-architect/references/upstream-source.md`, which records that the skill is inspired by GitHub's `awesome-copilot` Context Architect agent and notes the upstream MIT License and GitHub, Inc. copyright.

PR #8 added the missing root README entry.

### `skills/skill-creator-juiced/`

Status: covered by PR #8.

The package is original RhapsodIA work, conceptually related to `skills/skill-creator/`. PR #8 added `skills/skill-creator-juiced/references/source-and-license.md` and a root README entry.

### `skills/karpathy-guidelines/`

Status: covered by PR #8.

The package is original RhapsodIA work inspired by public software-engineering guidance commonly associated with Andrej Karpathy-style coding discipline. PR #8 added `skills/karpathy-guidelines/references/source-and-license.md` and a root README entry.

## Public similarity observations that do not require new attribution

### `prompt-architect`

Public sources include multiple `prompt-architect` skills, especially framework-heavy prompt-engineering packages that use named frameworks such as CO-STAR, RISEN, RISE, RTF, Chain of Thought, or Chain of Density.

RhapsodIA's `skills/prompt-architect/` uses a different structure: source-grounded prompt design, prompt tester validation, source integration, quality rubric, and reusable prompt assets. The name overlaps, but the inspected structure and workflow do not show evidence of copied or closely adapted upstream text requiring attribution.

Decision: no new attribution required.

### `skill-improver`

Public sources include Trail of Bits `skill-improver`, described as iteratively refining Claude Code skills through automated review-fix cycles with a `skill-reviewer` agent.

RhapsodIA's `skills/skill-improver/` is materially different in mechanism and scope: frozen evaluators, baseline/final metric contract, hypothesis discovery, change gates, rollback, auxiliary metrics, and package evidence. The public package is a relevant concept collision, but no copied or closely adapted text was identified from the public snippets reviewed.

Decision: no new attribution required.

### `secure-code-review` and broader code-review skills

Public registries include `secure-code-review` and `software-code-review` skills with generic security/code-review checklists.

RhapsodIA has `skills/secure-code-review/`, `skills/security-and-governance-review/`, and `skills/karpathy-guidelines/` with more specific boundaries around secret handling, security/governance review, and disciplined implementation. The overlap is category-level and naming-level, not evidence of copied or adapted source material.

Decision: no new attribution required.

### `skill-benchmark`, `benchmark-skills`, and evaluation skills

Public sources include `benchmark-skills`, model benchmarking skills, and evaluation framework skills. These use common benchmark/eval vocabulary.

RhapsodIA's benchmark-related packages are specific to reusable skill-package maturity, reports, gates, and evidence. The overlap is generic domain terminology.

Decision: no new attribution required.

### `agent-design` and agent design skills

Public sources include `agentic-design`, `agent-designer`, and generic AI-agent development skills.

RhapsodIA's `skills/agent-design/` focuses on Skill-vs-Agent separation, authority boundaries, routing, handoff contracts, repository agent structure, and validation plans. The overlap is generic domain terminology.

Decision: no new attribution required.

### `skill-harness`

Public sources include browser harnesses, long-running harness kits, and test-driven agent harness skills.

RhapsodIA's `skills/skill-harness/` is a skill-package harness/evidence workflow, not a browser harness or generic TDD agent-team harness. The overlap is name/category-level only.

Decision: no new attribution required.

## Decision summary

No additional root README attribution entries are required beyond the cases already documented by PR #8:

- `skills/skill-creator/`
- `skills/streamlit/`
- `skills/context-architect/`
- `skills/skill-creator-juiced/`
- `skills/karpathy-guidelines/`

The public review found common names and category-level overlaps, but no additional strong evidence of copied or closely adapted third-party skill content.

## Follow-up policy

Add or update a local source note when future changes do any of the following:

1. copy upstream text, examples, scripts, or templates;
2. closely adapt upstream structure, workflow, or section wording;
3. preserve a public skill name because the package is intentionally based on that public skill;
4. rely on a specific upstream project as source truth rather than generic public domain knowledge;
5. distribute a skill package independently where attribution would otherwise be lost.

Do not add source or license references to operational `SKILL.md` files unless the information changes how the skill executes. Keep license and attribution metadata in `README.md`, local `references/source-and-license.md`, local `references/upstream-source.md`, `LICENSE.txt`, `NOTICE`, or this audit document.
