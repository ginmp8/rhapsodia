# RhapsodIA

A curated collection of agent skills, evaluation harnesses, benchmarks, and delivery workflows.

## Purpose

RhapsodIA organizes reusable skills, prompts, validation utilities, benchmarks, and delivery workflows for agent-assisted work.

The repository is intended to make skill creation, review, hardening, testing, packaging, and execution workflows easier to reuse, inspect, and evolve.

## Repository structure

```text
skills/
  <skill-name>/
    SKILL.md          # Main skill instructions and activation contract
    agents/           # Optional agent metadata
    references/       # Supporting documentation and reusable guidance
    scripts/          # Optional validation, packaging, or helper scripts
    assets/           # Optional templates or reusable assets
    evals/            # Optional scenarios, checks, or evaluation inputs
```

Each skill should be treated as an independent package. Start with the skill's `SKILL.md` and inspect supporting files only when needed.

## Usage

Browse the `skills/` directory and open the relevant `SKILL.md` for the task you want to perform.

Typical workflows include:

- creating or improving skills;
- reviewing skill architecture and activation rules;
- validating skill packages;
- hardening skills, prompts, scripts, and references;
- benchmarking or evaluating reusable agent workflows;
- organizing delivery, planning, and execution workflows.

When a skill includes scripts, read the local instructions before running them. Some scripts are intended for validation, packaging, inventory, or report generation and may have package-specific assumptions.

## Validation

Validation is handled per skill. Check each skill package for available scripts, references, or evaluation files before making changes.

Common validation-related locations include:

```text
skills/<skill-name>/scripts/
skills/<skill-name>/evals/
skills/<skill-name>/references/
```

Do not assume that one validation command applies to every skill package.

## Third-party and adapted content

Some packages may include copied, adapted, derived, or inspired third-party material. When present, original license notices and attribution notes must be preserved in the relevant files or directories.

Known third-party or adapted content:

- `skills/skill-creator/` includes OpenAI `skill-creator` content with its original Apache License 2.0 notice preserved in `skills/skill-creator/LICENSE.txt`.
- `skills/streamlit/` is an original RhapsodIA skill built from and cross-referencing the official Streamlit documentation and Streamlit project sources. The official upstream repositories `streamlit/docs` and `streamlit/streamlit` are licensed under Apache License 2.0; see `skills/streamlit/references/source-and-license.md` for source and attribution notes.
- `skills/context-architect/` is inspired by GitHub's `awesome-copilot` Context Architect agent. The upstream source is licensed under the MIT License, Copyright GitHub, Inc.; see `skills/context-architect/references/upstream-source.md` for source and adaptation notes.
- `skills/skill-creator-juiced/` is an original RhapsodIA orchestration skill conceptually related to `skills/skill-creator/`; see `skills/skill-creator-juiced/references/source-and-license.md` for attribution and update rules.
- `skills/karpathy-guidelines/` is an original RhapsodIA skill inspired by public software-engineering guidance; see `skills/karpathy-guidelines/references/source-and-license.md` for source and update rules.
- Some skills may include upstream or adaptation notes in their own `references/` files.

Third-party content is not relicensed by this repository unless its original license allows it.

## License

Copyright 2026 ginmp8

Unless otherwise stated, this repository is licensed under the [Apache License 2.0](LICENSE).

The Apache License 2.0 applies to prompts, skills, scripts, examples, templates, and documentation created specifically for this repository.

If this repository includes copied or adapted third-party content, its original license notices are preserved and that content is not relicensed unless the original license allows it.
