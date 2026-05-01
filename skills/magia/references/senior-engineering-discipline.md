# Senior Engineering Discipline

Load this reference for non-trivial implementation, debugging, testing, refactoring, security, performance, reliability, or operational work.

## Core Rule

Prefer clarity, restraint, and verification over speed, cleverness, broad rewrites, or speculative implementation.

## Execution Discipline

1. Classify the work: implementation, bug fix, refactor, test design, validation, risk audit, documentation, or unblocker.
2. Define success before editing: test, build, lint, type check, smoke test, reproduction, static reasoning, benchmark, validator, or manual review check.
3. Inspect before broad changes: find existing patterns, module boundaries, validation commands, and relevant ownership constraints.
4. Make the smallest sufficient change. Avoid new abstractions, new dependencies, configuration surfaces, background jobs, or cleanup not required by the task.
5. Match existing style, naming, error handling, logging, dependency injection, transaction, retry, and testing conventions unless evidence shows they are unsafe.
6. Validate and report honestly: separate executed checks from suggested or not-run checks.

## Bug Fix Discipline

- Start from observed behavior, error text, failing test, reproduction step, or logs with secrets redacted.
- State the root-cause hypothesis before making a broad fix.
- Prefer a regression test or a narrow proof that the defect is fixed.
- Do not claim root cause if only a symptom was mitigated.

## Refactor Discipline

- Refactor only inside the requested or necessary scope.
- Preserve public behavior unless the task explicitly requires behavior change.
- State the equivalence check: tests, type checks, snapshot comparison, or static reasoning.
- Do not combine refactor with unrelated feature work.
- Prefer behavior-preserving simplification before architecture reshaping. Inline, merge, or delete one unnecessary seam at a time when evidence shows the abstraction has no current value.
- Do not replace simple code with a new framework, registry, generic abstraction, reflection mechanism, or configuration surface unless the evidence proves lower net complexity.

## Security and Sensitive Data

- Do not repeat secrets, private keys, tokens, passwords, or sensitive values.
- Flag credential exposure and recommend rotation when a secret appears in code/logs.
- Prefer secret stores and least-privilege permissions.
- Treat PII and regulated data handling as a security and compliance concern requiring explicit evidence.

## Evidence Labels

Use these labels when closing work:

- `executed`: a command or check was actually run and result is known.
- `static`: reasoned from inspected files without executing code.
- `not-run`: check was not executed; include the reason.
- `blocked`: check or implementation could not proceed safely; include missing evidence.



## Complexity-Reduction Discipline

Treat complexity reduction as a production change, not cleanup. Start with a simplification hypothesis, identify behavior to preserve, verify a safety net, make the smallest reversible change, and record before/after evidence. Prefer deleting or inlining unused abstractions over designing new generalized structures. Stop when behavior equivalence cannot be checked honestly.
