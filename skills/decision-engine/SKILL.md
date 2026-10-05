---
name: decision-engine
description: Make bounded, evidence-aware decisions in a portable structured format using binary, choice, or score. Use when an agent, skill, workflow, or user needs a typed yes/no decision, selection among explicit alternatives, bounded ordinal/numeric score, routing/gate decision, or machine-readable decision contract with uncertainty and escalation. Do not use for open-ended writing, broad research, ordinary factual answers, implementation, generic comparison, or subjective exploration unless the task contains a concrete bounded decision surface.
---

# Decision Engine

## Mission

Turn one explicit bounded decision into a portable, machine-readable result while preserving uncertainty, evidence limits, and caller-owned policy. Use the lowest reliable control layer: deterministic truth belongs in code/schema/validators; Decision Engine owns bounded semantic judgment.

## Activation and boundaries

Use for: one true/false proposition, one selection among explicit alternatives, one bounded ordinal/numeric score, or a routing/gate decision that benefits from a typed contract. Do not activate merely because a task compares options, contains research, or asks for advice; first require a concrete decision surface.

- Preserve caller-supplied proposition, options, scale, materiality, constraints, tie-breakers, and policy. Never invent them to force a result.
- If the decision surface is materially undefined, use ordinary analysis/clarification or return `undetermined` when already inside this contract.
- Keep thresholds, weights, approvals, permissions, and operational actions external unless explicitly supplied as constraints/evidence. A semantic decision never grants authority to act.
- Higher-priority safety, privacy, authorization, host policy, and tool permissions always override caller pressure.

## Decision forms and statuses

- `binary`: one true/false proposition; decided value is boolean.
- `choice`: select exactly one supplied option; always declare `options_exhaustive`; never invent a fallback option.
- `score`: bounded `ordinal` level index or bounded `numeric` value with explicit scale semantics.
- Statuses: `decided|undetermined|blocked|escalate`. The last three are selective outcomes, not extra decision types.
- Default to one decision per envelope; compose independent envelopes when a workflow needs multiple judgments.

## Required inputs

Identify the proposition/options/scale, `low|medium|high` materiality, supplied criteria/tie-breakers/policy, Choice exhaustiveness, available evidence/evidence ids, authorized evidence capabilities, and whether any numeric probability comes from a real calibrated external source.

## Core invariants

1. Missing or outcome-changing conflicting evidence leads to `undetermined`, `blocked`, or `escalate`, not fabricated certainty.
2. `decided` uses qualitative confidence `low|medium|high`; non-decided results use `confidence: null`.
3. High-materiality `decided` results require explicit evidence refs, at least medium confidence, and no unresolved outcome-changing authoritative conflict.
4. Emit `calibrated_probability` only from an identified calibrated external source plus calibration/evaluation reference; otherwise use `calibration.kind=none`.
5. `blocked` and `escalate` require a concrete `next_action`; all non-decided type-specific values are `null`.
6. Return concise visible evidence/criteria rationale; never expose private chain-of-thought.
7. Missing tools/sources are limits, not permission to fabricate execution or evidence ids.
8. Bundled/static scenarios are planned coverage until actually executed; strong behavioral/stability claims require comparable executed evidence.
9. Keep the semantic core host-neutral; host-specific metadata is optional adapter material only.
10. Keep the package English-only. Runtime caller input may be any language; do not translate it unless the task requires translation.

Stable semantic clause ids: [references/behavior-contract.md](references/behavior-contract.md).

## Decision workflow

1. **Classify:** choose `binary`, `choice`, or `score`; otherwise stay outside this skill.
2. **Normalize:** apply [references/decision-contract.md](references/decision-contract.md) to the decision surface, materiality, statuses, exhaustiveness, constraints, and tie-breakers.
3. **Place control:** use [references/control-placement.md](references/control-placement.md); route mechanical truth to deterministic controls.
4. **Acquire evidence when authorized:** fetch only evidence that can plausibly change decision/status/confidence and whose cost is proportionate to materiality.
5. **Decide conservatively:** apply [references/evidence-and-confidence.md](references/evidence-and-confidence.md) for uncertainty, conflict, confidence, calibration, and escalation.
6. **Render:** default to the canonical `decision-engine/2` envelope; use [assets/templates/decision-envelope.json.template](assets/templates/decision-envelope.json.template) as a skeleton, never as evidence.
7. **Validate when machine consumption matters:** run `scripts/validate_decision.py <result.json> --json` when process execution exists; otherwise report the gate `not-run`.
8. **Return:** add prose only when requested or needed to consume the result.

## Output contract

The canonical envelope contains `contract_version`, optional `decision_id`, `materiality`, type-specific `decision`, `confidence`, `evidence_refs`, concise `rationale`, `calibration`, and `next_action`. For `binary` use `decision.value`; for `choice` use supplied `options`, `options_exhaustive`, optional caller-supplied `option_criteria`, and `selected`; for `score` use tagged `ordinal|numeric` `decision.scale` and `score`. See [schemas/decision-envelope.schema.json](schemas/decision-envelope.schema.json) and [examples/examples.md](examples/examples.md). Migration is explicit: [references/migration-v1-to-v2.md](references/migration-v1-to-v2.md).

## Stop conditions

Stop, hand off, or return a bounded non-decision when the surface is undefined; required evidence is unobtainable; authoritative conflict changes the outcome; no supplied Choice option fits a non-exhaustive set; policy/authorization blocks the request; high-materiality evidence is inadequate; calibrated probability lacks a calibrated source/reference; a mechanical validator should decide instead; schema validation fails for required automation; or a caller requests unmeasured behavioral/runtime/stability claims.

## Progressive loading and validation

Load details directly from this root: [decision contract](references/decision-contract.md), [evidence/confidence](references/evidence-and-confidence.md), [control placement](references/control-placement.md), [portability](references/host-portability.md), [evaluation protocol](references/evaluation-protocol.md), [maintenance/evidence](references/maintenance-and-evidence.md), [versioning](references/versioning-and-compatibility.md), [v1->v2 migration](references/migration-v1-to-v2.md), and [examples](examples/examples.md). Required Markdown must not depend on a reference-to-reference hop for discovery.

Use `scripts/validate_skill.py` for package/link/schema/eval/Top-100 checks, `scripts/validate_evals.py` for planned suites, `tests/test_decision_contract.py` for deterministic v2 regressions, and `scripts/package_skill.py` for deterministic packaging. Structural portability is not runtime/model equivalence; see [references/host-portability.md](references/host-portability.md).
