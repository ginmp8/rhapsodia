---
name: skill-change-gate
description: evaluate proposed or candidate changes to chatgpt, claude, codex, copilot, or compatible agent skill packages before acceptance. use when reviewing a diff, patch, before/after skill folder, benchmark candidate, manual edit, hardening patch, or skill-improver hypothesis to decide whether it introduces blocking regressions in activation, scope, safety, local references, validation, packaging, evidence discipline, or output contracts. do not use for broad skill repair loops, benchmark scoring, new skill creation, generic code review, or ordinary document editing unless the requested output is an accept/reject quality gate for a skill change.
---

# Skill Change Gate

## Mission

Decide whether a proposed change to an existing skill package can be accepted without quality regression. Act as a stateless gate: inspect evidence, classify regressions, and return `pass`, `pass-with-warnings`, `fail`, or `insufficient-evidence`. Do not mutate the target skill unless the user separately asks for an implementation pass.

Use this skill as the structural acceptance gate for `skill-improver`, manual skill patches, hardening candidates, cleanup candidates, and package updates. Keep measured improvement, benchmark scoring, and hypothesis selection owned by the caller.

## Scope

Use for:

- gating a candidate diff, patch summary, before/after folder pair, or changed skill package;
- deciding whether a `skill-improver` candidate may be accepted after benchmark evaluation;
- reviewing manual edits for regressions in activation, boundaries, references, validation, packaging, safety, or output contract;
- separating blocking regressions from material concerns, non-blocking trade-offs, and follow-up hypotheses;
- producing an auditable accept/reject decision that another workflow can consume.

Do not use for:

- creating a new skill package;
- running a broad repair loop or repeatedly fixing findings;
- claiming benchmark, precision, recall, robustness, or improvement scores without executed or supplied evidence;
- ordinary application-code review outside a skill package;
- editing evaluator fixtures, expected outputs, benchmark baselines, secrets, credentials, `.git`, generated evidence, old zips, or unrelated files.

## Required Inputs

Proceed with explicit assumptions when evidence is partial, but mark the gate `insufficient-evidence` when acceptance cannot be justified.

1. Target skill identity: folder, zip, root `SKILL.md`, inspected text, or package name.
2. Candidate evidence: diff, patch summary, changed files, before/after package, or declared hypothesis.
3. Caller context: manual patch, `skill-improver` candidate, hardening pass, cleanup pass, token-efficiency pass, or package update.
4. Acceptance policy: `strict`, `normal`, or `advisory`; default to `normal`, and use `strict` for automated or self-improvement loops.
5. Supporting evidence: validator output, benchmark report, scenario results, command logs, reviewer notes, or stated missing evidence.
6. Blocked paths and protected artifacts when known.

## Modes

| Mode | Use when | Primary decision |
|---|---|---|
| `candidate-gate` | a candidate change exists and must be accepted or rejected | pass/fail decision with regressions |
| `preflight-gate` | a workflow wants to know required evidence before patching | evidence checklist and blockers |
| `post-validation-gate` | validators or benchmark already ran and need structural interpretation | decision impact of supplied evidence |
| `advisory-review` | the user wants non-blocking quality feedback only | warnings and follow-up hypotheses |

Default to `candidate-gate` when a changed package, diff, or hypothesis is present.

## Resource Loading

Load only the branch needed:

- `references/gate-rubric.md` for gate areas, severity definitions, and decision rules.
- `references/integration-with-skill-improver.md` when the caller is `skill-improver` or another experiment loop.
- `scripts/static_change_gate.py` when filesystem access is available for a target folder and optional before/after comparison.
- `examples/usage-examples.md` for compact examples of pass, warning, fail, and insufficient-evidence outputs.
- `evals/activation-scenarios.json` for planned activation and non-activation coverage; treat as planned evidence unless executed.

## Workflow

1. **Resolve gate target.** Identify the target skill, candidate evidence, caller context, policy, and whether this is before/after, diff-only, or post-validation review.
2. **Check evidence sufficiency.** If no target content or candidate evidence is available, stop with `insufficient-evidence`. If only partial evidence exists, inspect what is available and state limits.
3. **Inventory touched surfaces.** Map changes to activation, `SKILL.md`, references, scripts, assets/templates, examples, evals, validators, packaging, blocked paths, and output contract.
4. **Run static helper when available.** For local folders, run `python scripts/static_change_gate.py --target <after> [--before <before>] --json <report>` and treat output as mechanical evidence, not the full gate decision.
5. **Classify findings.** Use the rubric to classify each issue as blocking regression, material concern, non-blocking trade-off, false positive, or follow-up hypothesis.
6. **Decide.** Fail when blocking regressions exist. Return pass-with-warnings when only material concerns or accepted trade-offs remain. Pass only when required evidence is sufficient and no blocking/material concern affects acceptance under the selected policy.
7. **Report for the caller.** State what the caller should do: accept candidate, reject/revert, repair before accept, gather evidence, or create a follow-up hypothesis.

## Decision Rules

- A better benchmark score does not override a blocking quality regression.
- A clean static report does not prove semantic safety; still review activation, authority, evidence, and output behavior.
- Missing evidence is not a pass. Use `insufficient-evidence` or `pass-with-warnings` only when the remaining uncertainty does not affect acceptance.
- In `strict` policy, unresolved material concerns fail the gate unless explicitly waived by the user.
- In `advisory` policy, warnings may be reported without blocking acceptance, but blocking regressions must still be visible.
- Do not convert quality feedback into edits. If edits are needed, return required fixes or hand off to an implementation workflow.

## Output Contract

Return this structure for every substantive gate:

```markdown
## Skill Change Gate Result

- target:
- mode:
- policy:
- status: pass | pass-with-warnings | fail | insufficient-evidence
- decision for caller: accept | reject | repair-before-accept | gather-evidence | advisory-only

### Evidence inspected
- target evidence:
- candidate evidence:
- commands/results:
- missing evidence:

### Findings
| severity | area | finding | decision impact |
|---|---|---|---|

### Accepted trade-offs and false positives
- 

### Required fixes before accept
- 

### Follow-up hypotheses
- 
```

Use concise entries. Do not invent command results or benchmark scores.

## Stop Conditions

Stop or return `insufficient-evidence` when:

- no target skill content is available;
- no candidate change, before/after comparison, or acceptance question is available;
- multiple root `SKILL.md` files exist and the intended target cannot be inferred;
- the request requires editing files but the current mode is gate-only;
- requested evidence depends on an unavailable benchmark, validator, or scenario run;
- the candidate touches blocked files, secrets, credentials, evaluator fixtures, expected outputs, benchmark baselines, generated evidence, `.git`, old zips, or unrelated paths;
- archive inspection would require unsafe extraction or path traversal handling outside the available tools.

## Integration Defaults

When called from or for `skill-improver`, use `strict` policy for `automated-loop` and `self-improvement`, and `normal` policy for `manual-patch`. Return a machine-readable decision section that can be copied into the `skill-improver` report.
