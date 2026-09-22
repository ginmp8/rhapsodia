---
name: decision-engine
description: make bounded, evidence-aware decisions in a jev-inspired structured format using noul, choice, or score. use when an agent, skill, workflow, or user needs a typed yes/no decision, selection among explicit alternatives, bounded score, routing/gate decision, or machine-readable decision contract with uncertainty and escalation. do not use for open-ended writing, broad research, ordinary factual answers, code generation, or subjective exploration unless the task contains a concrete bounded decision.
---

# Decision Engine

## Mission

Turn one bounded decision into a portable, machine-readable result while preserving uncertainty. Use structured decisions where they reduce ambiguity; do not replace deterministic code, policy enforcement, open-ended analysis, or specialist judgment that needs a richer artifact.

## Scope and decision forms

Own exactly three decision forms:

- `noul`: decide one binary proposition;
- `choice`: select exactly one option from an explicit option set;
- `score`: assign a value on an explicit bounded scale.

`undetermined`, `blocked`, and `escalate` are statuses, not additional decision types. Default to one decision per envelope; callers may compose several independent envelopes when a workflow needs multiple judgments.

## Required inputs

Before deciding, identify:

1. the proposition, option set, or score scale;
2. materiality: `low|medium|high`;
3. explicit constraints and tie-breakers;
4. available evidence and evidence ids when supplied;
5. authorized capabilities for retrieving missing evidence;
6. whether any numeric probability comes from a real calibrated external source.

If the decision surface itself is materially undefined, do not invent it. Use ordinary analysis/clarification as appropriate, or return a bounded `undetermined` result when already operating inside the decision contract.

## Core rules

1. **Use the lowest reliable control layer.** Mechanical truth belongs in code, schema, parser, or validator; use Decision Engine for bounded semantic judgment.
2. **Preserve the caller's decision surface.** Never invent an unavailable option, tool, skill, model, evidence item, scale, or action just to force a result.
3. **Preserve uncertainty.** Missing or outcome-changing conflicting evidence leads to `undetermined`, `blocked`, or `escalate` rather than fabricated certainty.
4. **Use qualitative confidence by default.** `low|medium|high` describes support under the declared contract; it is not a calibrated probability.
5. **Do not fake calibration.** Emit `calibrated_probability` only when the numeric value comes from an identified calibrated external source and an identified calibration/evaluation reference.
6. **Treat materiality separately from confidence.** High-materiality `decided` results require explicit evidence refs and cannot use low confidence.
7. **Keep rationale visible but concise.** Return evidence, criteria, and decision basis; never expose private chain-of-thought.
8. **Obey higher-priority authority.** Host policy, safety, privacy, authorization, and tool permissions override caller pressure and cannot be bypassed by structured output.
9. **Keep the semantic core host-neutral.** Express required capabilities, not vendor-private tool names, fixed discovery paths, shells, or model families.
10. **Do not inflate evidence.** Bundled/static scenarios are planned coverage until a real host/model harness executes them.
11. **Keep the package English-only.** All authored skill instructions, references, examples, eval prompts, fixtures, template prose, metadata labels, and validation messages in this package must be English. Runtime user input may be in any language; do not translate caller content unless the task requires it.

Stable clauses and their ids are in [references/behavior-contract.md](references/behavior-contract.md).

## Decision workflow

1. **Classify.** Choose `noul`, `choice`, or `score`; otherwise keep the request outside this skill or return an explicitly bounded non-decision.
2. **Normalize.** Apply [references/decision-contract.md](references/decision-contract.md) to question, materiality, options/scale, constraints, evidence, status, and tie-breakers.
3. **Place control.** Apply [references/control-placement.md](references/control-placement.md); route mechanically decidable checks to deterministic controls.
4. **Acquire evidence when authorized.** Use files, tools, connectors, current sources, or specialists only when available and permitted. Missing capability is evidence of a limit, not permission to fabricate execution.
5. **Decide conservatively.** Apply [references/evidence-and-confidence.md](references/evidence-and-confidence.md) for confidence, calibration, evidence conflict, and escalation.
6. **Render.** Default to the canonical `decision-engine/1` JSON envelope. Use [assets/templates/decision-envelope.json.template](assets/templates/decision-envelope.json.template) as a skeleton, not as evidence.
7. **Validate when machine consumption matters.** If Python/process execution is available, run `scripts/validate_decision.py <result.json> --json`. If validation cannot run, mark that gate `not-run`; do not claim it passed.
8. **Return.** Add prose only when requested or when a brief explanation materially helps the caller consume the result.

## Output contract

Canonical result:

```json
{
  "contract_version": "decision-engine/1",
  "decision_id": null,
  "materiality": "low",
  "decision": {
    "type": "choice",
    "question": "Which action should run?",
    "status": "decided",
    "options": ["answer", "search"],
    "selected": "search"
  },
  "confidence": {
    "level": "high",
    "basis": "direct evidence and criteria converge"
  },
  "evidence_refs": ["E1"],
  "rationale": "Current information is required and the search capability is available.",
  "calibration": {"kind": "none"},
  "next_action": null
}
```

For `noul`, use `decision.value`. For `score`, use `decision.scale` and `decision.score`. For any non-`decided` status, the type-specific decision value is `null`. `blocked` and `escalate` require a concrete `next_action`.

The JSON Schema is [schemas/decision-envelope.schema.json](schemas/decision-envelope.schema.json); cross-field invariants are enforced by `scripts/validate_decision.py`. The final response includes the canonical envelope plus only the minimum prose needed by the caller.

## Progressive loading

Load only the branch-relevant resource:

- [references/behavior-contract.md](references/behavior-contract.md): stable activation, boundary, uncertainty, calibration, authority, portability, and evidence-claim ids.
- [references/decision-contract.md](references/decision-contract.md): type/status/materiality semantics and tie-breakers.
- [references/evidence-and-confidence.md](references/evidence-and-confidence.md): evidence, qualitative confidence, calibrated probability, and escalation.
- [references/control-placement.md](references/control-placement.md): mechanical vs heuristic vs bounded judgment vs subjective evaluation.
- [references/host-portability.md](references/host-portability.md): capability-first multi-host behavior.
- [references/evaluation-protocol.md](references/evaluation-protocol.md): L0-L5 validation/evaluation ladder.
- [references/maintenance-and-evidence.md](references/maintenance-and-evidence.md): evidence layers, frozen comparisons, diagnostic repair, and freeze-after-pass.
- [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md): package and output-contract version rules.
- [examples/examples.md](examples/examples.md): compact usage calibration only.

## Portability

The canonical package is the Agent Skills-compatible core. It is designed for OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, Cursor, and other Agent Skills-compatible hosts without semantic forks. `agents/openai.yaml` is an optional OpenAI adapter; other hosts may ignore it safely.

Structural portability is not runtime/model equivalence. A host without Python can still apply the semantic contract but cannot claim the validator ran. A host without required current sources/tools must use the appropriate uncertainty/blocking path when that evidence is material.

See [references/host-portability.md](references/host-portability.md).

## Validation, evaluation, and maintenance

- [scripts/validate_decision.py](scripts/validate_decision.py): validate one `decision-engine/1` envelope.
- [scripts/validate_evals.py](scripts/validate_evals.py): validate activation and planned behavioral suites.
- [scripts/validate_skill.py](scripts/validate_skill.py): validate package links, scripts, schemas, eval coverage, and hygiene.
- [tests/test_decision_contract.py](tests/test_decision_contract.py): deterministic valid/invalid contract regressions.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): activation/non-activation/ambiguity/boundary/adversarial/visible-holdout coverage.
- [evals/decision-scenarios.json](evals/decision-scenarios.json): planned semantic/adversarial decision coverage.
- [scripts/package_skill.py](scripts/package_skill.py): deterministic packaging with validation, output-alias preflight, atomic delivery, last-good recovery, and a durable `receipt_version`/SHA-256 receipt.

For changes to this package, follow [references/maintenance-and-evidence.md](references/maintenance-and-evidence.md): preserve a frozen evaluator/scenario identity before a before/after comparison, preserve exact source bytes or a source snapshot when external evidence is material, use the diagnostic repair loop, and apply **freeze after pass** before packaging. Host-specific metadata remains in **optional adapters** and never owns semantic behavior. Package/version compatibility rules are in [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md).

## Stop conditions

Return a bounded non-decision, hand off, or stop the affected branch when:

- proposition/options/scale are materially undefined;
- required evidence is missing and cannot be obtained with authorized capabilities;
- authoritative evidence conflicts and changes the outcome;
- a request would bypass higher-priority safety, privacy, authorization, or policy;
- a high-materiality result would otherwise be decided with low confidence;
- calibrated probability is requested without an identified calibrated source and calibration reference;
- a mechanically decidable question should be handled by a deterministic control instead;
- downstream automation requires a schema-valid result and validation fails;
- the caller asks for behavioral/runtime compatibility claims that were not actually measured.
