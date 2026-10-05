---
name: skill-prompt-and-activation-review
description: >-
  Review or rewrite an existing skill, agent, chat-mode, or reusable prompt activation surface: discovery descriptions, instructions, boundaries, handoffs, activation scenarios, and output/evidence contracts. Use when the primary artifact and action concern trigger/non-trigger behavior, overlap, ambiguity, prompt routing, or evidence wording. Do not use for net-new prompt authoring, package-wide benchmark/hardening/harness work, application-code implementation, deployment, or packaging.
---

# Skill Prompt and Activation Review

## Purpose and Scope

Review existing prompt and activation surfaces without expanding their ownership. Preserve linguistic judgment where useful while making routing boundaries, evidence identity, comparison rules, and claims reproducible.

This focused reviewer may propose or apply bounded rewrites only inside the supplied prompt/activation surface and may validate activation evidence. It does not own package-wide benchmark/harness infrastructure, hardening, consistency repair, repository implementation, deployment, or packaging.

## Activation and Routing Boundary

Use this skill when the **primary artifact + requested action** is one or more of:

- an existing Agent Skill/frontmatter discovery description, reusable agent/chat-mode instruction, or reusable prompt;
- activation, non-activation, boundary, handoff, overlap, ambiguity, or stop-condition language;
- activation scenario suites, near-miss negatives, adversarial cases, or prompt-routing evidence;
- output/evidence contracts tied directly to activation or prompt behavior.

Do **not** own net-new generic prompt authoring, generic copy editing, package-wide benchmark/maturity/harness work, package hardening/cleanup/consistency, application code, repository mutation outside prompt surfaces, deployment, packaging, or domain review where prompt/activation text is incidental. If a broader request contains one narrow prompt/activation subproblem, review only that surface and hand off the rest.

## Required Inputs

Resolve the exact target surface, requested review action, allowed mutation scope, current ownership, and available evidence. For behavioral comparison also resolve invocation mode, evaluator visibility, competing catalog identity, routing environment, and fixed trial policy. If target or ownership remains materially ambiguous, stop that branch rather than inventing authority.

## Mode Selection

| Mode | Use for | Primary output |
|---|---|---|
| `activation-description-review` | discovery/frontmatter trigger text | evidence-backed findings and minimal rewrite |
| `instruction-clarity-review` | reusable prompt/agent instructions | clarity findings and bounded edits |
| `boundary-review` | scope, non-goals, handoffs, overlap, stop rules | ownership/boundary findings |
| `adversarial-review` | bypass, gaming, or boundary-weakening attempts | adversarial findings and scenarios |
| `output-contract-review` | output/evidence wording | output-contract findings and corrected contract |
| `prompt-rewrite` | bounded rewrite of an existing surface | rewritten text plus evidence/rationale |
| `activation-scenarios` | versionable routing/activation scenarios | versionable scenario records |
| `verification-report` | formal evidence-backed review | formal review evidence |

Use one primary mode unless the request clearly spans multiple owned surfaces. Group material findings by TAX-001 defect code.

## Core Rules and Invariants

- Route by **artifact + action + ownership**, not keywords; preserve the target role, authority, safety rules, and supplied scope.
- Separate `explicit` direct invocation from `implicit`/`contextual` automatic routing; never count explicit cases in automatic precision/recall.
- Static breadth/omission is FP/FN **risk**; only frozen executed host-routing evidence can confirm a false positive/negative.
- Keep `alternative-owner` negatives separate from true `abstain` negatives.
- Before behavioral comparison, freeze suite/evaluator, catalog/routing fingerprint, evaluator visibility, and trial policy; paired arms must use identical material identities.
- Bundled activation scenarios are candidate-visible regression/calibration evidence, never a blind holdout. Blind holdouts stay external/evaluator-only.
- Use TAX-001 severity and EVD-001 traceability for material rewrites; reject ADV-001/GAME-001/STOP-001 weakening.
- Keep `planned`, `observed-static`, `supplied`, `executed`, `derived`, and `blocked` evidence distinct.
- Only comparable executed/supplied `host-routing` evidence supports measured activation behavior. Static checks support structural/static claims only.
- Reject activation gaming, evaluator weakening, expected-outcome edits made to pass, fabricated validation, or authority expansion.
- Keep host-specific metadata/invocation mechanisms as optional adapters; portable-core correctness must not depend on them.

## Workflow

1. Resolve the exact target, authority, writable scope, review mode, and whether work is static review or behavioral comparison.
2. Apply [`references/activation-contract.md`](references/activation-contract.md); preserve stronger target-specific policy.
3. Classify evaluation intent as explicit direct invocation, implicit auto-routing, contextual auto-routing, or no behavioral execution; explicit success is not discovery evidence.
4. Capture the original text/location before edits; for comparisons also capture exact suite/evaluator/catalog/routing/trial identities.
5. Classify defects with TAX-001, keeping static FP/FN risks distinct from executed routing defects.
6. Resolve overlap and negatives using OVL-001/NEG-001; prefer the narrow legitimate owner and split cleanly decomposable work.
7. Apply the smallest EVD-001-supported rewrite; do not broaden authority or optimize for trigger frequency.
8. When routing changes, cover positive, near-miss negative, abstention, ambiguous, boundary, adversarial, and regression cases.
9. Before behavioral execution, freeze evaluator/suite, visibility boundary, routing fingerprint, and fixed trial policy.
10. Validate suite/evidence arms, compare only materially identical identities, and keep single-run observations separate from repeatability evidence.
11. Report metrics by question: automatic precision/recall, explicit route accuracy, abstention, near-miss false activation, full-route regressions, and trigger rates.
12. Apply CLM-001/FRESH-001; host/model/catalog drift makes prior evidence historical/non-comparable until rerun or re-baselined.
13. Apply STOP-001 rather than weakening scope, evaluator integrity, evidence requirements, expected outcomes, or ownership.

## Direct Resource Map

Load only the branch that changes the decision; required Markdown is directly reachable from this file.

- **Normative routing rules:** [`references/activation-contract.md`](references/activation-contract.md).
- **Static review/severity/evidence rubric:** [`references/activation-review-rubric.md`](references/activation-review-rubric.md).
- **Bounded rewrite patterns:** [`references/prompt-rewrite-patterns.md`](references/prompt-rewrite-patterns.md).
- **Adversarial and scenario design:** [`references/adversarial-scenarios.md`](references/adversarial-scenarios.md) and [`evals/activation-scenarios.json`](evals/activation-scenarios.json).
- **Behavioral comparison only:** [`references/evaluation-protocol.md`](references/evaluation-protocol.md), [`references/routing-evidence-profile.md`](references/routing-evidence-profile.md), and [`references/evaluator-visibility.md`](references/evaluator-visibility.md).
- **Optional calibration/reporting:** [`examples/good-and-bad-descriptions.md`](examples/good-and-bad-descriptions.md), [`examples/prompt-review-cases.md`](examples/prompt-review-cases.md), and [`assets/templates/review-report.md.template`](assets/templates/review-report.md.template).
- **Deterministic regression coverage:** [`tests/test_activation_eval_tools.py`](tests/test_activation_eval_tools.py).

## Portable Core

Treat `SKILL.md` plus relative `references/`, `scripts/`, `evals/`, examples, and assets as the semantic core. `agents/openai.yaml` and equivalent host-specific discovery paths, invocation syntax, metadata, or permissions are adapters only and must not be required for correctness.

## Deterministic Helpers

Use Python 3.10+ when command execution is available. Resolve the launcher from capabilities rather than assuming a host-specific command.

Validate suite v3:

```text
<PYTHON> scripts/validate_activation_suite.py evals/activation-scenarios.json --json <OUT>
```

Freeze evaluator assets before baseline execution:

```text
<PYTHON> scripts/freeze_activation_evaluator.py freeze --root . \
  --path evals/activation-scenarios.json \
  --path references/activation-contract.md \
  --path references/activation-review-rubric.md \
  --path references/evaluation-protocol.md \
  --path references/routing-evidence-profile.md \
  --out <EVALUATOR_MANIFEST>
```

Verify the evaluator did not change:

```text
<PYTHON> scripts/freeze_activation_evaluator.py verify --root . --manifest <EVALUATOR_MANIFEST> --json <OUT>
```

Validate each evidence arm:

```text
<PYTHON> scripts/validate_activation_evidence.py --input <RESULTS> --suite <FROZEN_SUITE> --json <OUT>
```

Compare paired evidence only after all identity gates pass:

```text
<PYTHON> scripts/compare_activation_evidence.py --suite <FROZEN_SUITE> --baseline <BASELINE_RESULTS> --candidate <CANDIDATE_RESULTS> --json <OUT>
```

These helpers validate evidence/contracts; they do not execute model routing. If host-routing execution is unavailable, mark behavioral evidence `blocked` or `not-run`.

## Output Contract

For ordinary reviews, report:

1. mode and target surface;
2. verdict: `pass`, `needs-changes`, or `blocking`;
3. TAX-001 findings with severity, evidence/location, contract clause, rationale, and validation state;
4. recommended rewrite only for affected text;
5. scenarios with group, invocation mode, negative kind/neighbor owner when applicable, expected route, and evidence status;
6. evidence identities for baseline/candidate/suite/evaluator/routing fingerprint/trial policy when comparison is attempted;
7. validation state separated into static, supplied, executed, derived, or blocked;
8. automatic routing metrics separated from explicit direct-use, abstention, near-miss, and route-regression metrics;
9. gates, freshness/comparability state, residual risks, and not-run evidence.

Use `assets/templates/review-report.md.template` for formal reports.

## Stop Conditions

Stop the affected branch when:

- target surface or ownership cannot be identified;
- a rewrite would expand authority/safety/mutation scope beyond supplied intent;
- requested behavioral metrics lack comparable host-routing evidence;
- evaluator/suite changes after freeze;
- routing fingerprint or trial policy differs between paired arms;
- evaluator-only material leaked to candidate/controller in a claimed blind run;
- baseline/candidate case identities differ;
- completing the task requires out-of-scope implementation/package mutation;
- passing requires editing expected outcomes, weakening a boundary, activation gaming, fabricating validation, or lowering an evidence gate.

## Final Checklist

Before finalizing, confirm: activation/non-activation/ambiguity/overlap remain explicit; description stays concise/discriminative; explicit invocation is separated from auto-routing; catalog/routing/trial identities support any behavioral comparison; blind holdouts are external; evidence freshness is truthful; host-specific mechanisms remain adapters; validation claims match actual evidence; and no edit occurred after the final validated freeze.
