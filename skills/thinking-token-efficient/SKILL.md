---
name: thinking-token-efficient
description: use when a complex chat task needs compact private reasoning, tool planning, code or artifact analysis, multi-step synthesis, or validation with less unnecessary reasoning work. do not use for simple answers, ordinary rewriting or translation, visible prose compression, image generation, raw chain-of-thought disclosure, or shortcuts that reduce correctness, evidence, citations, validation, safety, or required detail.
---
# thinking-token-efficient

## Mission

Reduce unnecessary private reasoning work without weakening correctness, safety, evidence, citations, validation, or output. Optimize the reasoning path, not visible prose. Hidden reasoning-token savings require host telemetry.

## Inputs

Keep only load-bearing inputs: goal/output, hard constraints, evidence/citation duties, sources/tools, stakes, and validation requirements. Budgets or levels never waive hard obligations.

## Core rules

- **Quality first.** Compress only when semantic obligations remain equivalent.
- **Compact, not cryptic.** No novelty dialects, gibberish, arbitrary language switching, or illegible shorthand.
- **Do not reveal hidden chain of thought.** Give concise rationale, evidence, assumptions, and validation status instead.
- Remove filler, restatement, resolved branches, speculative options, and redundant checks; never remove a necessary check.
- Preserve `evidence/citation/source/path/line`, exact commands, versions, numeric limits, and artifact identity when material.
- Distinguish executed and not-executed validation; planned checks are not evidence.

## Compression ladder

1. `readable` - ambiguity, high stakes, citations, code, security, failures, or destructive actions.
2. `dense` - compact notes after facts, constraints, and checks are stable.
3. `max-safe` - tiny private ledger only for low-risk substeps with stable success criteria.

Never use `max-safe` for safety, legal, medical, financial, security, identity, citations, code correctness, destructive actions, or current external facts.

## Private reasoning workflow

1. Classify stakes, evidence, tools, and validation burden.
2. Freeze obligations; choose the least verbose safe level.
3. Load only context that can change the decision; prefer supplied artifacts, connected sources, official/current evidence, and exact command output.
4. Execute the shortest valid path; drop resolved branches.
5. Check contradictions, evidence/citations, unsupported claims, validation honesty, safety, and required detail.

Use a private ledger only if useful: `goal`, `facts`, `unknowns`, `path`, `checks`, `answer`.

## Resource loading

Load only the needed branch:

- `references/compression-protocol.md`, `references/semantic-safety.md`, `references/technical-discipline.md`, `references/validation-gates.md` - runtime rules.
- `references/measurement-and-preservation.md` and `contracts/semantic-contract.json` - package measurement/preservation.
- `examples/activation-scenarios.md` and `evals/activation-scenarios.json` - planned cases; metrics require execution.
- `assets/templates/private-ledger.md.template` - optional ledger template; never final-answer content.
- `scripts/validate_skill.py`, `scripts/token_audit.py`, `scripts/compare_candidate.py` - maintenance helpers.

## Output contract

Visible answers remain normal. Include only applicable answer/recommendation, material assumptions, evidence/citations or inspected paths, executed and not-executed validation, and risks/next step. Never print private ledgers, hidden chain of thought, scratchpad fragments, or internal compression markers.

## Claim rules

Static token audits prove only package/control-plane footprint. Claim hidden reasoning-token reduction only from host telemetry; claim behavioral equivalence/improvement only from executed paired scenarios using the same frozen evaluator. Planned evals are not measured evidence.

## Stop conditions

Stop or expand reasoning when compression would drop safety, evidence, citations, validation, compatibility, or output duties; uncertainty is material; authoritative lookup is required; file/command/test claims lack evidence; or the user requests raw chain of thought or obfuscated thinking.

## Package maintenance

Preserve an immutable baseline and frozen evaluator; use the same tokenization method before/after; run protected-literal and semantic-invariant checks plus `python -S scripts/validate_skill.py <skill-folder>` and package validation; keep rollback/last-known-good evidence; freeze the final candidate after its last pass; package only those exact bytes with a hash receipt. Revalidate after any later edit.
