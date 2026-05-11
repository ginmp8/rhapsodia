---
name: sequential-work-packaging
description: enforce a planning-first convention for sequential work packaging and adapt mago-style planning modes to the canonical cycle_version/spec_id/feature_key/feature_version model. use when chatgpt needs to order work, define a spec package, refine an existing spec package, decompose broad remaining work, audit planning artifacts, or normalize legacy planning requests into spec-catalog.yaml plus specs/specnnn/manifest.yaml, prd.md, tasks.md, notes.md, and validation.md.
---

# sequential-work-packaging

## Overview
Use this skill to create, revise, audit, or normalize planning artifacts under the canonical sequential work packaging convention. Treat `cycle_version` as the macro container, `spec_id` as the stable execution identifier, `feature_key` as the stable functional identity, and `feature_version` as semantic technical evolution.

This skill also adapts MAGO-style planning requests into the canonical structure. When a request refers to `mago-define`, `mago-refine`, or `mago-decompose`, keep the planning intent of that mode but operate only on the canonical artifact set and directory layout.

## Mode selection
Choose exactly one primary mode for each run unless the caller explicitly asks for a combined pass.

- `order`: maintain or extend `spec-catalog.yaml`
- `define`: create or revise one execution-ready spec package
- `refine`: minimally update one existing spec package while preserving correct history
- `decompose`: split broad remaining work inside one existing spec package into smaller dependency-safe tasks
- `audit`: inspect existing artifacts for convention violations and produce corrections or a remediation plan
- `normalize`: convert legacy or mixed planning input into the canonical structure without preserving legacy filenames as authoritative artifacts

If a prompt mentions MAGO naming directly, map it as follows:

- `mago-define` -> `order` or `define`, depending on whether the request is catalog ordering or per-spec definition
- `mago-refine` -> `refine`
- `mago-decompose` -> `decompose`

## Canonical structure
Always treat this structure as authoritative:

```text
<cycle_version>/
  spec-catalog.yaml
  specs/
    specNNN/
      manifest.yaml
      prd.md
      tasks.md
      notes.md
      validation.md
```

Never treat any legacy structure as canonical. In particular, do not write or preserve as source-of-truth:

- `docs/current`
- `MANIFESTO.yaml`
- `PRD.md`
- `TASKS.md`
- `VALIDATION.md`
- `NOTES.md`
- `FEATURE_ORDER.yaml`

If a request or legacy prompt references these names, reinterpret them into the canonical equivalents:

- `MANIFESTO.yaml` -> `manifest.yaml`
- `PRD.md` -> `prd.md`
- `TASKS.md` -> `tasks.md`
- `VALIDATION.md` -> `validation.md`
- `NOTES.md` -> `notes.md`
- `FEATURE_ORDER.yaml` or equivalent ordering file -> `spec-catalog.yaml`
- `DOCS_ROOT = docs/current` -> `<cycle_version>/specs/<spec_id>/`

## Core workflow
1. Determine the primary mode.
2. Identify the active `cycle_version`.
3. Determine whether the request targets the catalog or exactly one `spec_id`.
4. Read only the minimum necessary artifacts:
   - always the active `spec-catalog.yaml` when a cycle already exists
   - the selected spec package when the mode is `define`, `refine`, or `decompose`
   - directly relevant discovery evidence, code, tests, contracts, schemas, or docs needed for safe planning
5. Apply the mode rules from the matching reference file:
   - `references/order-mode.md`
   - `references/define-mode.md`
   - `references/refine-mode.md`
   - `references/decompose-mode.md`
6. Run the mandatory final review.
7. Return only canonical artifacts and canonical terminology.

## Non-negotiable rules
- create or update `spec-catalog.yaml` before introducing a new spec
- keep `spec_id` stable once created
- do not use `feature_key` as the execution identifier
- keep `depends_on_features`, `depends_on_specs`, and task-level `Dependencies` separate
- keep lowercase everywhere for directory names, file names, ids, enum values, and yaml keys
- use `order` as an integer and usually increment by 10
- preserve truthful content and done history during refinement
- prefer decomposition over broad umbrella tasks
- keep acceptance criteria and validation concrete and testable
- finish every spec pass with a final review over manifest, prd, validation, notes, and architecture impact when relevant

## Identity and versioning
Use these rules consistently:

- new capability -> new `feature_key`
- compatible improvement -> same `feature_key`, increment minor version
- correction -> same `feature_key`, increment patch version
- conceptual redesign or materially different capability -> new `feature_key`
- first functional implementation -> `v0.1.0`
- first stable production release -> `v1.0.0`
- breaking change -> increment major version

Use semantic versioning for feature evolution only. Never use it to define execution order.

## Reasoning guidance
Every actionable task in `tasks.md` must declare one of:

- `low`
- `medium`
- `high`
- `xhigh`

Default to `low` or `medium`. Use `high` only for durable architectural or contract trade-offs. Use `xhigh` only for truth-critical or recovery-critical planning boundaries.

## Operating style
- stay planning-only unless the caller explicitly requests implementation
- make explicit assumptions when needed, but keep them bounded and visible
- preserve internal consistency across all artifacts
- normalize legacy requests into canonical artifacts rather than mixing systems
- when adapting MAGO prompts, preserve their planning intent but not their legacy filesystem or artifact casing
- if ordering, do not create spec folders
- if defining, refining, or decomposing, work on exactly one spec package unless the caller explicitly requests multiple specs

## References
Use these bundled references as the source of truth for mode behavior and templates:

- `references/convention.md`
- `references/templates.md`
- `references/order-mode.md`
- `references/define-mode.md`
- `references/refine-mode.md`
- `references/decompose-mode.md`
- `references/mago-adaptation.md`
