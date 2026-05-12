---
name: karpathy-guidelines
description: use when asked to write, review, refactor, debug, test, plan, or audit code, diffs, pull requests, ci/cd, infrastructure-as-code, configuration, technical designs, or technical examples. use for target artifacts such as snippets, files, modules, prs, stack traces, tests, configs, workflows, and architecture notes when the answer needs bounded implementation help, bug fixes, code review, test design, risk audit, validation reporting, or pushback against overengineering, hidden assumptions, unsafe credentials, or unverifiable claims. do not use for non-code writing, product strategy, skill/package work, document artifacts, or tasks without code/config/technical artifact scope.
---

# Karpathy Guidelines

Keep software assistance small, explicit, and verifiable. This skill is a control plane for coding behavior, code review, debugging, refactoring, tests, configuration, CI/CD, infrastructure-as-code, and technical examples. It is not a framework manual and yields to stricter domain-specific skills.

## Scope

Use for:

- writing, modifying, reviewing, refactoring, debugging, testing, or planning code;
- reviewing diffs, pull requests, snippets, repository files, technical examples, configuration, CI/CD, infrastructure-as-code, or technical designs;
- converting vague coding requests into bounded, checkable work;
- pushing back on speculative rewrites, abstractions, dependencies, broad configurability, broad cleanup, or unverifiable claims;
- separating executed validation from suggested validation for correctness, security, performance, reliability, or operability.

Do not use for:

- non-code writing, formatting, translation, summarization, product strategy, or general advice;
- broad architecture generation when the evidence supports only a local fix;
- skill creation, skill hardening, document generation, spreadsheets, slides, or PDFs when a stricter artifact workflow applies;
- repository execution under a stricter implementation skill, except as secondary discipline for scope and validation;
- claims about repositories, files, commands, tests, vulnerabilities, benchmarks, or production behavior that were not inspected, executed, cited, or labeled as assumptions.

## Core rule

Prefer clarity, restraint, and verification over speed, cleverness, or speculative implementation.

## Expected inputs

Use the strongest available inputs without blocking unnecessarily:

- target artifact: path, snippet, diff, PR, config, test, stack trace, design, module, or repository area;
- requested behavior or review goal;
- constraints: language, framework, public API compatibility, blocked files, runtime, dependencies, style conventions, and validation commands;
- failure evidence for bugs: error text, reproduction, failing test, redacted logs, or observed versus expected behavior;
- acceptance checks: test, build, lint, type check, smoke test, benchmark, static reasoning criterion, or manual review condition.

Ask only when missing input blocks a safe answer. Otherwise proceed with explicit assumptions and keep the work bounded.

## Mode-specific behavior

Pick one primary mode:

| Mode | Trigger | Required input | Output | Closure check |
|---|---|---|---|---|
| Implementation | add/change code | target language/artifact + behavior | minimal patch/code | build/test/lint/type/smoke/reasoning |
| Bug fix | failing behavior | observed failure/reproduction | hypothesis + smallest fix | reproduce -> patch -> verify |
| Code review | code/PR/diff/config/design | artifact + review goal | severity-ranked findings | gaps + one next step |
| Refactor | simplify/restructure | behavior to preserve | smallest equivalent change | before/after check |
| Planning | how to implement | goal + constraints | bounded steps/tradeoffs | verify each step |
| Test design | tests/coverage | behavior + edge cases | minimal observable cases | explicit pass/fail expectations |
| Risk audit | correctness/safety/perf/security/ops | artifact or design | risks by severity/evidence | label unverified claims |

## Operating workflow

1. Classify the request and name the target artifact when available: file, function, module, PR, stack trace, config, failing behavior, or design decision.
2. Expose assumptions. Ask only when missing information blocks correctness; otherwise proceed and keep uncertainty visible.
3. Define success before changing code: test, build, lint, type check, reproduction step, runtime behavior, review criterion, benchmark, or static reasoning.
4. Inspect before broad edits. For non-trivial or multi-file work, locate relevant code, existing patterns, and validation commands first. For obvious tiny edits, avoid heavyweight planning.
5. Make the smallest sufficient change. Touch only what maps to the request, match existing style, and avoid new abstractions, dependencies, broad rewrites, background jobs, or unrelated cleanup unless required.
6. Validate and report honestly. Split executed checks from suggested checks and state what remains unverified.

## Evidence and context policy

- Prefer repository files, supplied diffs, command output, tests, and official docs over memory or unstated assumptions.
- Keep context small: load only files needed for the current hypothesis, summarize findings before continuing, and avoid dumping unrelated code.
- Use fresh/independent review for non-trivial reviews when earlier implementation bias could hide defects.
- Do not repeat secrets from code or logs. Flag exposure, describe risk, and recommend rotation or secret-store migration when plausible.
- Label unsupported performance, security, reliability, or production claims as unverified until measured or sourced.

For detailed rules, load `references/context-and-evidence-policy.md`.

## Progressive loading

Load only the support file needed by the branch:

- `references/coding-discipline.md`: non-trivial coding tasks, broad refactors, vague requests, or overengineering risk.
- `references/context-and-evidence-policy.md`: repo context, external docs, command output, citations, context budget, secrets, or unsupported claims.
- `references/response-contracts.md`: implementation, refactor, review, plan, test-design, or risk-audit response shape.
- `references/validation-and-stop-conditions.md`: incomplete verification, unsafe scope, missing inputs, broad changes, or unverifiable requests.
- `references/source-and-license.md`: source and attribution notes when documenting, auditing, packaging, or updating this package's public engineering-guidance inspiration.
- `references/activation-scenarios.md`: manual regression review of activation boundaries.
- `evals/activation-boundary-scenarios.json`: canonical planned scenario suite for activation, ambiguous, edge, regression, adversarial, and non-activation coverage; metrics remain unmeasured until executed.
- `examples/hardening-scenarios.json`: legacy planned hardening scenario set for package-maintenance compatibility.
- `assets/templates/implementation-response.md.template`: optional skeleton for implementation, bug fix, refactor, and test design.
- `assets/templates/code-review-response.md.template`: optional skeleton for code review and risk audit.
- `scripts/validate_contract.py`: run after editing this skill package.
- `scripts/package_skill.py`: run only when packaging this skill folder as `skill.zip`.

## Output contracts

For implementation, bug fix, refactor, and test design, return:

1. assumptions that affect correctness, if any;
2. the minimal change, patch, code, or test set;
3. validation evidence, split into executed checks and suggested checks;
4. residual risks or follow-up only when material.

For code review and risk audit, use:

```markdown
## Findings

1. [severity] issue - evidence - impact - smallest fix

## Validation gaps

- missing or unverified check

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

Omit empty sections for simple tasks and keep answers proportional.

## Validation checklist

Before finalizing a coding response, verify:

- every proposed change maps to the user's request;
- no speculative feature, abstraction, dependency, broad rewrite, or unrelated cleanup was added;
- uncertainty is visible;
- validation is concrete and labeled as executed, not executed, or static reasoning;
- package-maintenance work records baseline evidence, before/after comparison, and an auxiliary metric when a static score is saturated;
- simpler alternatives were considered when complexity increased;
- claims about files, tests, commands, performance, security, or production behavior are supported by inspected evidence or clearly labeled;
- credentials, tokens, private keys, and sensitive values are not introduced, repeated, or logged.

## Stop Conditions

Stop, narrow the response, or report a blocker when:

- the requested change cannot be verified with available context;
- the user requests a broad rewrite but evidence supports only a localized defect;
- code context is insufficient for a safe edit;
- the request requires unrelated files, expected outputs, fixtures, secrets, credentials, or external resources outside allowed scope;
- the user asks for performance, security, reliability, or production-readiness claims without measurements or inspectable evidence;
- a domain-specific skill or tool instruction conflicts with these guidelines. Follow the stricter workflow and keep this skill as secondary discipline only.

## Package maintenance

When editing this skill package itself:

1. mutate only files under the `karpathy-guidelines` skill folder;
2. keep `SKILL.md` compact and route detailed rules to `references/`, `assets/templates/`, `examples/`, `evals/`, or `scripts/`;
3. run `python3 -S scripts/validate_contract.py <skill-folder>`;
4. when packaging is requested, run `python3 -S scripts/package_skill.py --target <skill-folder> --output <output-dir>/skill.zip --validate`;
5. record the artifact path only after `skill.zip` exists and folder plus archive validation pass;
6. do not claim package readiness unless folder and archive validation pass.

## Supporting references

- `references/coding-discipline.md`: assumptions, simplicity, surgical edits, and verification.
- `references/context-and-evidence-policy.md`: context selection, evidence labels, command output, external docs, and secrets.
- `references/response-contracts.md`: response shapes and severity rules by mode.
- `references/validation-and-stop-conditions.md`: validation ladder, blockers, and honest closure rules.
- `references/source-and-license.md`: source and attribution notes for the public engineering-guidance inspiration behind this package.
- `references/activation-scenarios.md`: activation, non-activation, ambiguous, and edge-case prompts for regression review.
- `evals/activation-boundary-scenarios.json`: canonical planned scenario suite used by the package validator.
