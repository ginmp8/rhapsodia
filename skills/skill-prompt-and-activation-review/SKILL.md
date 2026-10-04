---
name: skill-prompt-and-activation-review
description: >-
  Review or rewrite existing skill/agent activation descriptions, reusable instructions, boundaries, handoffs, activation scenarios, and output/evidence contracts. Use for trigger/non-trigger, overlap, ambiguity, or prompt-routing review. Do not use for net-new prompt authoring, package-wide benchmark/hardening/harness work, or application-code implementation.
---

# Skill Prompt and Activation Review

## Purpose

Review prompt and activation surfaces for reusable Agent Skills, agents, chat modes, and instruction packages. Preserve linguistic judgment where it is useful while making routing boundaries, evidence identity, stochastic comparison, and claims reproducible.

This is a focused reviewer. It may propose or apply bounded rewrites inside the target prompt/activation surface and validate activation evidence. It does not own package-wide benchmark/harness infrastructure, hardening, consistency repair, repository implementation, deployment, or packaging.

## Required Inputs

Resolve the exact target surface, requested review action, allowed mutation scope, current ownership, and available evidence. When behavioral comparison is requested, also resolve invocation modes, evaluator visibility, competing catalog identity, routing environment, and trial policy. If target/ownership is materially ambiguous, stop that branch rather than inventing authority.

## Portable Core

Treat `SKILL.md` plus relative `references/`, `scripts/`, `evals/`, examples, and assets as the semantic core. Host-specific discovery paths, invocation syntax, metadata, and permissions are optional adapters.

`agents/openai.yaml` is an OpenAI adapter when present. Claude-, Copilot-, Cursor-, or other host extensions may be preserved as adapters, but correctness must not depend on them.

## Required Contracts

Load only what the active branch needs:

- [references/activation-contract.md](references/activation-contract.md) — canonical trigger/non-trigger, invocation, overlap, evidence, claim, anti-gaming, stop, and portability rules.
- [references/activation-review-rubric.md](references/activation-review-rubric.md) — evidence/severity criteria for discovery descriptions, boundaries, scenarios, and output contracts.
- [references/prompt-rewrite-patterns.md](references/prompt-rewrite-patterns.md) — minimal rewrite patterns and evidence requirements.
- [references/adversarial-scenarios.md](references/adversarial-scenarios.md) — scenario groups, realistic dimensions, near-miss negatives, and anti-gaming cases.
- [references/evaluation-protocol.md](references/evaluation-protocol.md) — frozen baseline/candidate protocol, metrics, freshness, and comparison gates.
- [references/routing-evidence-profile.md](references/routing-evidence-profile.md) — evidence v2, routing fingerprint, catalog identity, invocation modes, and repeated-trial shape.
- [references/evaluator-visibility.md](references/evaluator-visibility.md) — candidate-visible versus evaluator-only isolation/leakage rules.
- [evals/activation-scenarios.json](evals/activation-scenarios.json) — canonical candidate-visible suite v3; presence is not execution evidence and bundled cases are not blind holdouts.
- [examples/good-and-bad-descriptions.md](examples/good-and-bad-descriptions.md) — optional description calibration.
- [examples/prompt-review-cases.md](examples/prompt-review-cases.md) — optional finding/ownership calibration.
- [tests/test_activation_eval_tools.py](tests/test_activation_eval_tools.py) — deterministic regression coverage for suite, evidence, freeze, and comparison helpers.
- [assets/templates/review-report.md.template](assets/templates/review-report.md.template) — durable review report when useful.

## Modes

| Mode | Use when the user asks to... | Primary output |
|---|---|---|
| `activation-description-review` | review frontmatter/trigger text | evidence-backed findings and minimal rewrite |
| `instruction-clarity-review` | review reusable prompt/agent instructions | clarity findings and bounded edits |
| `boundary-review` | inspect scope, non-goals, handoffs, overlap, stop rules | ownership/boundary findings |
| `adversarial-review` | stress prompt/activation rules for bypasses/gaming | adversarial findings and scenarios |
| `output-contract-review` | inspect expected output/evidence wording | output-contract findings and corrected contract |
| `prompt-rewrite` | rewrite an existing prompt/activation surface | rewritten text plus evidence/rationale |
| `activation-scenarios` | create/revise activation test cases | versionable scenario records |
| `verification-report` | produce formal review evidence | report using the template |

Use one primary mode unless the request clearly spans multiple surfaces. Group findings by TAX-001 defect code.

## Workflow

1. **Resolve target and scope.** Identify the exact prompt/activation surface, authority, writable scope, and whether work is static review or behavioral comparison.
2. **Apply the activation contract.** Read `references/activation-contract.md`; preserve target-specific policy when it is stronger.
3. **Select the smallest mode.** Do not escalate a local rewrite into package-wide work.
4. **Classify evaluation intent.** Distinguish explicit direct invocation, implicit auto-routing, contextual auto-routing, or no behavioral execution. Never treat explicit invocation as automatic-discovery evidence.
5. **Capture baseline before edits.** Preserve original text/location and, for comparisons, exact suite/evaluator/catalog/routing/trial identities.
6. **Classify defects with TAX-001.** Keep static FP/FN risks separate from executed FP/FN defects.
7. **Resolve overlap with OVL-001/NEG-001.** Route by artifact + action + ownership; distinguish alternative-owner negatives from true abstention.
8. **Apply the smallest supported change.** Satisfy EVD-001 for every activation/frontmatter rewrite. Reject GAME-001 activation gaming.
9. **Build scenario coverage when routing changes.** Include positive, near-miss negative, abstention, ambiguous, boundary, adversarial, and candidate-visible regression cases with realistic dimensions. True blind holdouts stay external/evaluator-only.
10. **Freeze before behavioral comparison.** Follow `references/evaluation-protocol.md`: freeze evaluator/suite, routing fingerprint (including catalog identity), visibility boundary, and fixed trial policy before baseline execution.
11. **Validate evidence before comparing.** Validate suite and each evidence arm; compare only identical suite/evaluator/routing/trial identities. Repeated trials support bounded repeatability evidence; one run remains a single observation.
12. **Report metrics by question.** Keep automatic precision/recall, explicit route accuracy, abstention accuracy, near-miss false activation rate, full-route regressions, and trigger rates separate.
13. **Gate claims and freshness.** Apply CLM-001/FRESH-001. Material host/model/catalog drift makes prior runs historical/non-comparable until rerun or re-baselined.
14. **Stop on integrity/scope blockers.** Apply STOP-001 instead of weakening authority, evaluator, evidence, or expected outcomes.

## Deterministic Helpers

Use Python 3.10+ when command execution is available. Resolve the Python launcher from capabilities rather than assuming a product-specific command.

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

## Review and Evidence Rules

- Route by artifact + action + ownership under ACT-001/NTR-001/OVL-001; preserve ROLE-001/BND-001.
- Keep explicit invocation out of auto-routing precision/recall under INV-001.
- Preserve catalog/routing identity under CAT-001/RTE-001 and repeated-trial semantics under STO-001.
- Separate alternative-owner and abstention negatives under NEG-001.
- Use TAX-001 severity and EVD-001 traceability for every material rewrite; reject ADV-001/GAME-001/STOP-001 weakening.
- Keep `planned`, `observed-static`, `supplied`, `executed`, `derived`, and `blocked` evidence distinct.
- Only comparable executed/supplied host-routing evidence supports measured activation behavior. Static checks support structural/static claims only.

## Handoffs

Hand off the out-of-scope portion when the primary request needs:

- generic prompt authoring from scratch;
- full package benchmark/scorecard or repeated-run harness infrastructure;
- package-wide hardening/consistency/cleanup;
- technical implementation, repository mutation outside prompt surfaces, deployment, or packaging.

Use capability roles rather than hard-coding neighboring skill names into the portable core.

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
