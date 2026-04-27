---
name: karpathy-guidelines
description: use when asked to write, review, refactor, debug, test, plan, or audit code, diffs, pull requests, ci/cd, infrastructure-as-code, configuration, technical designs, or examples. use for target artifacts such as snippets, files, modules, prs, stack traces, tests, configs, workflows, and architecture notes when the output needs bounded implementation help, bug fixes, code review, test design, risk audit, validation reporting, or pushback against overengineering, hidden assumptions, unsafe credentials, or unverifiable claims. do not use for non-code writing, product strategy, skill/package work, document artifacts, or tasks without code/config/technical artifact scope.
---

# Karpathy Guidelines

Use this skill to keep software assistance small, explicit, and verifiable. It is a control plane for coding behavior, code review, debugging, refactoring, tests, configuration, CI, infrastructure-as-code, and technical examples. It is not a framework manual and should not override a stricter domain-specific skill.

## Scope

Use for:

- writing, modifying, reviewing, refactoring, debugging, testing, or planning code;
- reviewing diffs, pull requests, snippets, repository files, technical examples, configuration, CI/CD, infrastructure-as-code, or technical design;
- converting vague coding requests into bounded, checkable work;
- pushing back on speculative rewrites, abstractions, dependencies, configurability, broad cleanup, or unverifiable claims;
- separating executed validation from suggested validation when answering about code correctness, security, performance, reliability, or operability.

Do not use for:

- non-code writing, formatting, translation, summarization, product strategy, or general advice;
- broad architecture generation when the user asked for a local fix;
- skill creation, skill hardening, document generation, spreadsheets, slides, or PDFs when a stricter artifact workflow applies;
- repository implementation under a stricter repository execution skill, except as a secondary discipline for scope and validation;
- making claims about repositories, files, commands, tests, vulnerabilities, benchmarks, or production behavior that were not inspected, executed, cited, or explicitly labeled as assumptions.

## Core rule

Prefer clarity, restraint, and verification over speed, cleverness, or speculative implementation.

## Expected inputs

Use the strongest available inputs without blocking unnecessarily:

- target artifact: file path, snippet, diff, PR, config, test, stack trace, design, module name, or repository area;
- desired behavior or review goal;
- constraints: language, framework, public API compatibility, blocked files, runtime environment, dependencies, style conventions, and validation commands;
- failure evidence for bug fixes: error text, reproduction step, failing test, logs with secrets redacted, or observed vs expected behavior;
- acceptance checks: test, build, lint, type check, smoke test, benchmark, static reasoning criterion, or manual review condition.

Ask a follow-up only when the missing input blocks a safe answer. Otherwise proceed with explicit assumptions and keep the patch, plan, or review bounded.

## Mode-specific behavior

| Mode | Trigger | Required inputs | Primary output | Closure check |
|---|---|---|---|---|
| Implementation | User asks to add or change code | target language, artifact, requested behavior | minimal patch or code with assumptions | executed or proposed build, test, lint, type, smoke, or reasoning check |
| Bug fix | User reports failing behavior | observed failure, reproduction signal, relevant artifact | reproduction hypothesis, smallest fix, regression check | reproduce -> patch -> verify when feasible |
| Code review | User asks to review code, PR, diff, config, or design | reviewed artifact and review goal | prioritized findings with severity, evidence, impact, and smallest fix | missing checks and one concrete next step |
| Refactor | User asks to simplify or restructure | behavior to preserve and target scope | smallest behavior-preserving refactor | before/after equivalence check |
| Planning | User asks how to implement | goal, constraints, stack, target scope | bounded plan with checks and tradeoffs | each step has a verification criterion |
| Test design | User asks for tests or coverage | target behavior, edge cases, test framework if known | minimal test set focused on observable behavior | failing/passing expectations are explicit |
| Risk audit | User asks about correctness, safety, performance, security, or operability | artifact or design under audit | risks ranked by severity and evidence | unverified risks are labeled |

## Operating workflow

1. **Classify the request.** Pick one primary mode from the table. Name the target artifact when available: file, function, module, PR, stack, config, failing behavior, or design decision.
2. **Expose assumptions.** Ask only when missing information blocks correctness. Otherwise proceed with explicit assumptions and keep uncertainty visible.
3. **Define success before changing code.** Convert the ask into observable checks: test, build, lint, type check, reproduction step, runtime behavior, review criterion, benchmark, or static reasoning.
4. **Inspect before broad edits.** For non-trivial or multi-file work, first locate relevant code, existing patterns, and validation commands; for tiny edits where the diff is obvious, skip heavyweight planning.
5. **Make the smallest sufficient change.** Touch only what maps directly to the request. Match existing style. Avoid new abstractions, dependencies, broad rewrites, background jobs, or unrelated cleanup unless required.
6. **Validate and report honestly.** Separate executed checks from suggested checks. State exactly what remains unverified and why.

## Evidence and context policy

- Prefer repository files, supplied diffs, command output, tests, and official docs over memory or unstated assumptions.
- Keep context small: load only files needed for the current hypothesis, summarize findings before continuing, and avoid dumping unrelated code into the answer.
- Treat fresh sessions, independent review, or separate checks as useful for non-trivial reviews when bias from earlier implementation could hide defects.
- Do not repeat secrets from code or logs. Flag the exposure, describe the risk, and recommend rotation or secret-store migration when plausible.
- Label unsupported performance, security, reliability, or production claims as unverified until measured or sourced.

For detailed rules, load `references/context-and-evidence-policy.md`.

## Progressive loading

Load supporting files only when the branch needs them:

- `references/coding-discipline.md`: use for non-trivial coding tasks, broad refactors, vague requests, or overengineering risk.
- `references/context-and-evidence-policy.md`: use when repo context, external docs, command output, citations, context budget, secrets, or unsupported claims affect correctness.
- `references/response-contracts.md`: use when shaping implementation, refactor, review, plan, test-design, or risk-audit responses.
- `references/validation-and-stop-conditions.md`: use when verification is incomplete, scope is unsafe, inputs are missing, or the user asks for a broad or unverifiable change.
- `references/activation-scenarios.md`: use for manual regression review of activation boundaries.
- `evals/activation-boundary-scenarios.json`: use as the canonical planned scenario suite for activation, ambiguous, edge, regression, adversarial, and non-activation coverage; metrics remain unmeasured until executed.
- `examples/hardening-scenarios.json`: use as the legacy planned hardening scenario set for package maintenance compatibility.
- `assets/templates/implementation-response.md.template`: optional skeleton for implementation, bug fix, refactor, and test-design responses.
- `assets/templates/code-review-response.md.template`: optional skeleton for code review and risk-audit responses.
- `scripts/validate_contract.py`: run after editing this skill package.
- `scripts/package_skill.py`: run only when packaging this skill folder as `skill.zip`.

## Output contracts

For implementation, bug fix, refactor, and test-design answers, return in order:

1. assumptions that affect correctness, if any;
2. the minimal change, patch, code, or test set;
3. validation evidence, clearly split into executed checks and suggested checks;
4. residual risks or follow-up only when material.

For code review and risk-audit answers, use prioritized findings:

```markdown
## Findings

1. [severity] issue - evidence - impact - smallest fix

## Validation gaps

- check that is missing or could not be verified

## Suggested next step

- one concrete action
```

For non-trivial plans, use:

```markdown
## Assumptions

- ...

## Plan

1. step -> verify: check
2. step -> verify: check
3. step -> verify: check

## Risks

- ...
```

Omit empty sections for simple tasks. Keep the response proportional to the user's request.

## Validation checklist

Before finalizing a coding response, verify:

- every proposed change maps to the user's request;
- no speculative feature, abstraction, dependency, broad rewrite, or unrelated cleanup was added;
- uncertainty is visible instead of hidden;
- validation is concrete and labeled as executed, not executed, or static reasoning;
- package-maintenance work records baseline evidence, before/after comparison, and an auxiliary metric when a static score is saturated;
- simpler alternatives were considered when complexity increased;
- claims about files, tests, commands, performance, security, or production behavior are supported by inspected evidence or clearly labeled;
- credentials, tokens, private keys, and sensitive values are not introduced, repeated, or logged.

## Stop Conditions

Stop, narrow the response, or report a blocker when:

- the requested change cannot be verified with the available context;
- the user asks for a broad rewrite but only a localized defect is evidenced;
- the available code is insufficient to make a safe edit;
- the request requires editing unrelated files, expected outputs, fixtures, secrets, credentials, or external resources outside the allowed scope;
- the user asks for performance, security, reliability, or production-readiness claims without measurements or inspectable evidence;
- a domain-specific skill or tool instruction conflicts with these guidelines. Follow the stricter workflow and keep these rules as style constraints only.

## Package maintenance

When editing this skill package itself:

1. mutate only files under the `karpathy-guidelines` skill folder;
2. keep this `SKILL.md` compact and route detailed rules to `references/`, `assets/templates/`, `examples/`, `evals/`, or `scripts/`;
3. run `python3 -S scripts/validate_contract.py <skill-folder>`;
4. when packaging is requested, run `python3 -S scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`;
5. record the final artifact path only after `skill.zip` exists and folder plus archive validation pass;
6. do not claim package readiness unless folder and archive validation pass.

## Supporting references

- `references/coding-discipline.md`: detailed heuristics for assumptions, simplicity, surgical edits, and verification.
- `references/context-and-evidence-policy.md`: rules for context selection, evidence labels, command output, external docs, and secrets.
- `references/response-contracts.md`: response shapes and severity rules by mode.
- `references/validation-and-stop-conditions.md`: validation ladder, blockers, and honest closure rules.
- `references/activation-scenarios.md`: activation, non-activation, ambiguous, and edge-case prompts for regression review.
- `evals/activation-boundary-scenarios.json`: canonical planned scenario suite used by the package validator.
