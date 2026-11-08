# Public Source Attribution Audit

Date: 2026-09-22

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

The repository includes OpenAI `skill-creator` content and preserves its original Apache License 2.0 notice at `licenses/third-party/archify-apache-2.0.txt`; `licenses/skill-assets.json` restores the historical `LICENSE.txt` name for standalone packaging. The README already lists this package under known third-party or adapted content.

### `skills/streamlit/`

Status: already covered.

The package is documented as an original RhapsodIA skill built from and cross-referencing official Streamlit documentation and source repositories. The local source note remains in `skills/streamlit/references/source-and-license.md`.

### `skills/context-architect/`

Status: covered by PR #8.

The repository already contained `skills/context-architect/references/upstream-source.md`, which records that the skill is inspired by GitHub's `awesome-copilot` Context Architect agent and notes the upstream MIT License and GitHub, Inc. copyright.

PR #8 added the missing root README entry.

### `skills/decision-engine/`

Status: newly documented.

The package is an original RhapsodIA implementation conceptually inspired by JEV's structured decision approach. The repository currently records no copied JEV text, code, templates, or other license-bearing material in the package. The package is therefore documented as conceptual inspiration rather than as an official JEV implementation or a runtime-compatible derivative.

This audit records the attribution boundary: any future change that copies or closely adapts JEV material must identify the exact source URL or repository, version or commit, copyright holder, license, and affected files before distribution.

### `skills/skill-creator-juiced/`

Status: covered by PR #8.

The package is original RhapsodIA work, conceptually related to `skills/skill-creator/`. PR #8 added `skills/skill-creator-juiced/references/source-and-license.md` and a root README entry.

### `skills/karpathy-guidelines/`

Status: covered by PR #8.

The package is original RhapsodIA work inspired by public software-engineering guidance commonly associated with Andrej Karpathy-style coding discipline: small changes, explicit assumptions, verification, and resistance to unnecessary abstraction. It does not copy upstream text verbatim. Future edits that copy or closely adapt public posts, talks, repositories, or documentation must record the source, license, and affected files in `README.md` and this audit.

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

The current root README attribution entries are:

- `skills/skill-creator/`
- `skills/streamlit/`
- `skills/context-architect/`
- `skills/skill-creator-juiced/`
- `skills/karpathy-guidelines/`
- `skills/decision-engine/`

The public review found common names and category-level overlaps, but no additional strong evidence of copied or closely adapted third-party skill content. The decision-engine entry records conceptual JEV inspiration without asserting third-party license rights or runtime compatibility.

## Follow-up policy

Add or update an attribution note in the root README, this audit, or relevant package metadata when future changes do any of the following:

1. copy upstream text, examples, scripts, or templates;
2. closely adapt upstream structure, workflow, or section wording;
3. preserve a public skill name because the package is intentionally based on that public skill;
4. rely on a specific upstream project as source truth rather than generic public domain knowledge;
5. distribute a skill package independently where attribution would otherwise be lost.

Do not add source or license references to operational `SKILL.md` files unless the information changes how the skill executes. Keep license and attribution metadata in `README.md`, local `references/source-and-license.md`, local `references/upstream-source.md`, `LICENSE.txt`, `NOTICE`, or this audit document.

## Archify suite added in RhapsodIA 0.15.0

Three independently versioned packages are derived from the upstream Archify project (tt-a1i/archify), using `ginmp8/archify` commit `a4065941f12be7967436261d9934784e381d423c` as the immutable integration reference:

- `skills/archify/`: Archify 3.2.0 runtime, schemas, examples, frontend assets and adapted Agent Skills discovery/reference guidance. This is upstream-derived code, not original RhapsodIA authorship.
- `skills/archify-review/`: versioned portable rewrite of upstream Value/Cost/Impact reviewer and review references, with current-branch and evidence-readiness controls.
- `skills/archify-tuning/`: portable methodology extracted from upstream internal experiment guidance; upstream repo-local experimental scripts are not included.

Each package preserves original author attribution and records changes in `SOURCE.md` and `CHANGELOG.md`, with each package's original `NOTICE` preserved centrally under `licenses/notices/`. Archify preserves the Cocoon AI lineage, Apache-2.0 license, historical MIT grant and third-party notices in the central license registry; standalone packaging restores the historical filenames. This inclusion does not confer rights in brand marks or imply upstream approval. In particular, some embedded brand artwork has non-commercial or share-alike conditions independent of the software license; redistributors should consult the bundled notices for intended use.

## 2026-11-08: RhapsodIA 0.17.0 Matt Pocock adaptations

The following seven new skill packages are independently maintained adaptations of [Matt Pocock's Skills](https://github.com/mattpocock/skills), from the user-owned fork [ginmp8/mattpocock-skills](https://github.com/ginmp8/mattpocock-skills) pinned to commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`: `grilling`, `grill-me`, `grill-with-docs`, `domain-modeling`, `wayfinder`, `retro`, and `code-review`.

Each directory preserves the exact original file and Git blob in `SOURCE.md`. The complete unchanged MIT notice (Copyright (c) 2026 Matt Pocock) is consolidated once in `licenses/third-party/mattpocock-skills-MIT.txt`; standalone skill export restores `LICENSE-MIT` into the resulting ZIP. RhapsodIA modifies the language for host portability, finite questioning, source/evidence discipline and non-conflicting Nomia/Mago/Magia ownership. The surrounding project retains its separate Apache-2.0 license. The fork is an attribution source, not evidence of upstream endorsement. These are not presented as official Matt Pocock releases.

The seven SVG icons added during the 0.17.0 compatibility hardening are original RhapsodIA adaptation assets and are **not copied from** the upstream Matt Pocock repository. They remain distinct from the MIT-attributed workflow text and do not imply upstream endorsement.

## 2026-11-08 — Catalog-wide license relocation

All **76** installed RhapsodIA skill roots were inventoried. The 22 remaining license/NOTICE/OFL files in established skills were moved without modifying the original Git blob bytes and recorded in `licenses/skill-assets.json`. Identical texts are deduplicated; package-specific NOTICE content and vendor texts remain distinct. The seven previously centralized Matt Pocock MIT notices are also included in the catalog. The repository and portable plugin retain the full notice corpus; standalone skill ZIP exports restore the original path and exact bytes. `skills/archify/renderers/shared/software-notices.mjs` remains executable code (not a license text), and Streamlit's source-and-license reference remains skill-operational guidance. The 0.15.0 release notes remain a historical account of that earlier package layout.
