---
name: thinking-token-efficient
description: use when a complex chat task needs adaptive private reasoning effort, token-efficient tool planning, code or artifact analysis, multi-step synthesis, evidence work, or validation without unnecessary reasoning. do not use for simple direct answers, ordinary rewriting or translation, visible prose compression, image generation, raw chain-of-thought disclosure, or shortcuts that reduce correctness, evidence, citations, validation, safety, compatibility, or required detail.
---
# thinking-token-efficient

## Mission

Reduce unnecessary private reasoning work without weakening correctness, safety, evidence, citations, validation, compatibility, or output. Optimize effort, context, branching, and stopping—not visible prose. Hidden reasoning-token savings require host telemetry.

## Hard rules

- **Quality first.** Freeze goal, constraints, evidence/citation duties, safety, compatibility, output, and validation obligations before optimizing; efficiency never waives them.
- **Do not reveal hidden chain of thought.** Give concise rationale, evidence, assumptions, and validation status instead.
- Preserve `evidence/citation/source/path/line`, exact commands, versions, numeric limits, artifact identity, and freshness when material.
- Distinguish executed and not-executed validation; planned checks are not evidence.
- Continue a tool, branch, subagent, or reconsideration only when plausible new information can change the decision or satisfy an unmet material obligation.

## Two independent controls

**Reasoning effort:** `direct → light → standard → deep`. Choose the minimum safe level from difficulty, uncertainty, stakes, evidence/tool burden, failures, and validation needs. Escalate when these increase; never lower effort merely to hit a token target. See `references/adaptive-effort-policy.md`.

**Compression ladder:** `readable → dense → max-safe`. This controls private representation, not reasoning effort. Effort and representation are orthogonal. Never use `max-safe` for safety, legal, medical, financial, security, identity, citations, code correctness, destructive actions, or current external facts. See `references/compression-protocol.md` and `references/semantic-safety.md`.

## Runtime workflow

1. Classify difficulty, stakes, uncertainty, evidence/tool needs, and validation burden; freeze hard obligations.
2. Resolve relevant host capabilities without assuming a vendor. Use `references/host-capabilities.md` for effort controls, telemetry, opaque reasoning-state continuity, truncation, caching, or lazy tool loading.
3. Choose the minimum safe effort and representation independently.
4. Load only context that can change the decision; prefer supplied artifacts, connected sources, official/current evidence, and exact command output.
5. Execute the shortest valid path. Keep resolved branches closed unless new evidence reopens them. Reuse opaque host reasoning state when safely supported; otherwise carry only a compact semantic checkpoint (`facts`, `unknowns`, `decision`, `checks`).
6. After each material result, run the **sufficiency gate** in `references/stopping-and-escalation.md`. Stop when obligations are satisfied and further expected information gain is negligible; continue or escalate for unresolved evidence, contradictions, validation, safety, or completion.
7. Final-check citations/evidence, unsupported claims, validation honesty, truncation/completion, safety, compatibility, and required detail.

Treat hard token/context/output limits as infrastructure or safety bounds, not the primary efficiency policy. If a hard limit yields incomplete, truncated, or empty output, report failure/limitation rather than an efficiency success.

## Resource loading

Load only what the active branch needs:

- `references/adaptive-effort-policy.md`, `references/stopping-and-escalation.md`, `references/host-capabilities.md` — effort, stopping, portability/state.
- `references/compression-protocol.md`, `references/semantic-safety.md`, `references/technical-discipline.md`, `references/validation-gates.md` — runtime discipline.
- `references/measurement-and-preservation.md`, `contracts/semantic-contract.json` — measurement/claims/preservation.
- `evals/activation-scenarios.json`, `examples/activation-scenarios.md` — planned cases; planned evals are not measured evidence.
- `assets/templates/private-ledger.md.template` — optional private ledger template; never final-answer content.
- `scripts/validate_skill.py`, `scripts/token_audit.py`, `scripts/compare_candidate.py` — maintenance helpers.

## Output contract and claims

Visible answers remain normal: include only applicable answer/recommendation, material assumptions, evidence/citations or inspected paths, executed and not-executed validation, and risks/next step. Never print private ledgers, hidden chain of thought, scratchpad fragments, or internal effort/compression markers.

Static token audits prove only package/control-plane footprint. Claim hidden reasoning-token reduction only from host telemetry; claim behavioral equivalence/improvement only from comparable executed paired scenarios using the same frozen evaluator. When available, report efficiency as a vector: quality, reasoning/input/output/cache tokens, tool/model calls, latency, cost, and completion/truncation status.

## Stop conditions

Stop or expand reasoning when lower effort/compression would drop safety, evidence, citations, validation, compatibility, or required output; when authoritative evidence is missing; when a required result is truncated/incomplete; or when raw chain of thought is requested. Stop further exploration when obligations are satisfied and new work cannot plausibly change the decision.

## Package maintenance

Preserve an immutable baseline and frozen evaluator; compare with the same tokenization method; run protected-literal/semantic checks, `python -S scripts/validate_skill.py <skill-folder>`, portability/package validation, and affected tests; freeze after the last pass and package only those exact bytes with a hash receipt. Revalidate after any later edit.
