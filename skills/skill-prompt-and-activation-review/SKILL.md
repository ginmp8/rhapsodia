---
name: skill-prompt-and-activation-review
description: use when asked to review, improve, rewrite, validate statically, or stress-test existing prompt and activation surfaces such as skill frontmatter descriptions, trigger/non-trigger boundaries, handoffs, overlap rules, stop conditions, reusable agent instructions, activation scenarios, or output contracts. focus on precise routing, scope ownership, adversarial resistance, and evidence-aware claims. do not use for generic prompt creation, full benchmarking/harness execution, package-wide hardening or consistency repair, repository implementation, or unrelated writing/code review.
---

# Skill Prompt and Activation Review

## Purpose

Review prompt and activation surfaces for reusable Agent Skills, agents, chat modes, and instruction packages. Preserve the linguistic judgment needed for prompt review while making activation/boundary criteria, evidence identity, scenario comparison, and claims reproducible.

This skill is a focused reviewer. It may propose or apply bounded rewrites inside the target prompt/activation surface and may validate evidence contracts. It does not own full benchmark, harness execution infrastructure, package hardening, consistency repair, repository implementation, or deployment.

## Portable Core

Treat Agent Skills as the semantic core: `SKILL.md` plus relative `references/`, `scripts/`, `evals/`, examples, and assets. Host-specific discovery, invocation syntax, metadata, or tool permissions are optional adapters only.

`agents/openai.yaml` is an OpenAI adapter when present. Do not require it for semantic correctness, and do not make core routing depend on ChatGPT-, Claude-, Copilot-, Cursor-, or other proprietary invocation mechanisms.

## Required Contracts

Load only what the active branch needs:

- `references/activation-contract.md` — canonical trigger/non-trigger, ambiguity, boundary, overlap, FP/FN, evidence, claim, taxonomy, stop, and portability rules.
- `references/activation-review-rubric.md` — evidence and severity criteria for activation/boundary/output review.
- `references/prompt-rewrite-patterns.md` — minimal rewrite rules and evidence requirements.
- `references/adversarial-scenarios.md` — scenario design and evidence labels.
- `references/evaluation-protocol.md` — evaluator freeze, baseline/candidate pairing, self-generated candidate provenance, hidden-evaluator visibility, trace provenance, result schema, metrics eligibility, and claim gates.
- `references/evaluator-visibility.md` — candidate-visible vs evaluator-only boundaries, blind-evaluation leakage rules, and capability-based isolation guidance.
- `evals/activation-scenarios.json` — canonical host-neutral seed scenarios. Presence is not execution evidence.
- `assets/templates/review-report.md.template` — formal durable report when useful.

## Modes

| Mode | Use when the user asks to... | Primary output |
|---|---|---|
| `activation-description-review` | review frontmatter/trigger text | evidence-backed findings and minimal rewrite |
| `instruction-clarity-review` | review reusable prompt/agent instructions | clarity findings and bounded edits |
| `boundary-review` | inspect scope, non-goals, handoffs, overlap, stop rules | ownership/boundary findings |
| `adversarial-review` | stress prompt/activation rules for bypasses | adversarial findings and scenarios |
| `output-contract-review` | inspect expected output/evidence wording | output-contract findings and corrected contract |
| `prompt-rewrite` | rewrite an existing prompt/activation surface | rewritten text plus evidence/rationale |
| `activation-scenarios` | create/revise activation test cases | versionable scenario records |
| `verification-report` | produce formal review evidence | report using the template |

Use one primary mode unless the request clearly spans multiple review surfaces. Group findings by defect code rather than blending different risks.

## Workflow

1. **Resolve target and scope.** Identify the exact prompt/activation surface, allowed mutation scope, and whether the task is static review or evidence-backed comparison.
2. **Apply the activation contract.** Read `references/activation-contract.md`. Preserve ACT-001/NTR-001/BND-001/ROLE-001 semantics and any stronger target-specific policy.
3. **Select the smallest mode.** Do not escalate a local rewrite into package-wide review.
4. **Capture baseline evidence before edits.** Preserve original text/location. For before/after comparisons, record baseline identity and exact scenario/evaluator identity.
5. **Classify defects with TAX-001.** Distinguish static risks from confirmed executed FP/FN defects. Use the stable severity guidance from the rubric.
6. **Resolve overlap using OVL-001.** Route by artifact + action + ownership. Split mixed requests when appropriate; do not duplicate authority.
7. **Propose the smallest supported change.** Every changed activation/frontmatter surface must satisfy EVD-001: original evidence, criterion, defect/risk, minimal change, affected scenarios, and validation state.
8. **Build scenario coverage when routing/boundaries change.** Include positive (`activation`), negative (`non-activation`), ambiguous, boundary, adversarial, and holdout cases when stronger comparison evidence is intended.
9. **Freeze before behavioral comparison.** Follow `references/evaluation-protocol.md`. Baseline and candidate must use exactly the same frozen cases and evaluator. For self-generated candidates, also preserve controller/generation provenance and ensure both the authoring controller and evaluated candidate remain blind to evaluator-only holdouts when blind evaluation is claimed. When hidden graders/expected outcomes/holdouts are used, apply `references/evaluator-visibility.md` and keep evaluator-only assets outside candidate-visible inputs. If the evaluator changes or leaks into the candidate run, invalidate and restart the comparison.
10. **Validate without overclaiming.** Use bundled deterministic scripts for suite/evaluator/evidence integrity. They do not execute model activation. Treat trace identity as optional runtime provenance, not as proof by itself.
11. **Report claim strength truthfully.** Apply CLM-001. Separate proposed, observed-static, supplied, executed, and derived evidence.
12. **Stop on integrity/scope blockers.** Apply STOP-001 instead of weakening a boundary or evaluator.

## Deterministic Helpers

Use Python 3.10+ when execution is available. Resolve the Python executable from host capabilities instead of assuming a product-specific command.

Validate a scenario suite:

```text
<PYTHON> scripts/validate_activation_suite.py evals/activation-scenarios.json --json <OUT>
```

Freeze evaluator assets before baseline execution:

```text
<PYTHON> scripts/freeze_activation_evaluator.py freeze \
  --root . \
  --path evals/activation-scenarios.json \
  --path references/activation-contract.md \
  --path references/activation-review-rubric.md \
  --path references/evaluation-protocol.md \
  --out <EVALUATOR_MANIFEST>
```

Verify they did not change:

```text
<PYTHON> scripts/freeze_activation_evaluator.py verify \
  --root . \
  --manifest <EVALUATOR_MANIFEST> \
  --json <OUT>
```

Compare paired evidence only after both arms use the same frozen suite/evaluator:

```text
<PYTHON> scripts/compare_activation_evidence.py \
  --suite <FROZEN_SUITE> \
  --baseline <BASELINE_RESULTS> \
  --candidate <CANDIDATE_RESULTS> \
  --json <OUT>
```

If host-routing execution is unavailable, mark behavioral evidence `blocked` or `not-run`. Do not simulate precision/recall from static review.

## Review Criteria

Use these criteria across modes:

- **Trigger fit:** artifact + requested action satisfy ACT-001.
- **Non-trigger resistance:** adjacent ownership in NTR-001 remains excluded.
- **Ambiguity control:** AMB-001 cases are clarified or conservatively bounded, not forced into a metric.
- **Overlap control:** OVL-001 resolves ownership consistently.
- **Role preservation:** ROLE-001 remains intact.
- **Boundary integrity:** BND-001 prevents silent mutation expansion.
- **Evidence integrity:** EVD-001 connects each material change to evidence and scenario coverage. Hidden-evaluator claims also require leakage-free candidate/evaluator visibility separation.
- **Claim integrity:** CLM-001 prevents unexecuted metrics/improvement claims.
- **Adversarial resilience:** ADV-001/STOP-001 resist scope/evaluator weakening.
- **Output auditability:** findings use stable taxonomy, severity, evidence status, and limitations.

## Evidence and Claims

Never treat these as equivalent:

- a scenario was authored;
- a scenario was statically reviewed;
- a user supplied a result;
- a scenario was actually executed in a host/harness;
- a derived metric was computed from valid paired execution evidence.

Do not claim activation precision, activation recall, behavioral improvement, or regression reduction unless the evidence protocol's executed-host-routing gate is satisfied.

When only static evidence exists, use `proposed improvement`, `structurally hardened`, or `observed static improvement` as appropriate.

## Handoffs

Hand off the out-of-scope portion when the request primarily needs:

- generic prompt authoring from scratch;
- full package benchmark/scorecard;
- repeated scenario execution or harness infrastructure;
- package-wide hardening or consistency repair;
- technical implementation, repository mutation, deployment, or packaging.

Use capability roles rather than depending on specific host invocation names. If no suitable workflow exists, state the unsupported portion instead of expanding this skill's authority.

## Output Contract

For ordinary reviews, provide:

1. **Mode and target surface**.
2. **Verdict**: `pass`, `needs-changes`, or `blocking`.
3. **Findings** using TAX-001 defect codes, stable severity, evidence/location, contract clause, and rationale.
4. **Recommended rewrite** only for affected text.
5. **Scenarios** with group, expected route, and evidence status when routing/boundaries are relevant.
6. **Evidence identities** for baseline/candidate/suite/evaluator when a comparison is attempted, plus controller/generation provenance when the candidate is self-generated.
7. **Validation status** separated into static, supplied, executed, derived, or blocked.
8. **Regressions and metrics** only when actually measurable under the evaluation protocol.
9. **Gates and residual risks**.

Use `assets/templates/review-report.md.template` for formal reports.

## Stop Conditions

Stop the affected branch and report the blocker when:

- the target surface or ownership cannot be identified;
- a requested rewrite would change authority, safety, or mutation scope beyond the supplied intent;
- the user requests behavioral metrics but no valid same-suite/same-evaluator execution evidence can be obtained;
- evaluator/scenario evidence changes after baseline freeze;
- baseline and candidate case identities differ;
- an out-of-scope implementation/package mutation is required to complete the request;
- overlapping ownership contracts cannot be resolved from available evidence;
- passing would require editing expected outcomes, weakening a boundary, fabricating validation, or lowering an evidence gate.

## Final Checklist

Before finalizing:

- target role and scope are preserved;
- trigger and non-trigger boundaries are explicit;
- overlap and ambiguous cases follow the contract;
- FP/FN labels distinguish risk from executed confirmation;
- frontmatter/description changes have EVD-001 evidence;
- scenario suite/evaluator identity is frozen before any behavioral comparison;
- hidden evaluator/holdout assets are excluded from candidate-visible inputs when blind evaluation is claimed;
- baseline and candidate use exactly the same cases and materially equivalent host configuration;
- defect taxonomy and severity are stable;
- host-specific mechanisms remain adapters, not semantic dependencies;
- validation claims match evidence actually obtained;
- no edit occurred after the final validated candidate freeze.
