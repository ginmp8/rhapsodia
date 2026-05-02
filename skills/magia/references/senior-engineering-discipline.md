# Senior Engineering Discipline

Load for non-trivial implementation, debugging, testing, refactor, security, performance, reliability, or operations.

## Core Rule

Prefer clarity, restraint, and verification over speed, cleverness, broad rewrites, or speculative implementation.

## Execution Discipline

1. Classify work: implementation, bug fix, refactor, test design, validation, risk audit, documentation, unblocker.
2. Define success before editing: test, build, lint, type check, smoke, reproduction, static reasoning, benchmark, validator, or manual review.
3. Inspect patterns, module boundaries, validation commands, and ownership constraints before broad change.
4. Make the smallest sufficient change; avoid unnecessary abstractions, dependencies, config surfaces, background jobs, and cleanup.
5. Match existing style, naming, errors, logging, DI, transactions, retries, and tests unless unsafe.
6. Report honestly: separate executed, static, not-run, and blocked evidence.

## Bug Fix

Start from observed behavior, error text, failing test, reproduction, or redacted code/logs. State root-cause hypothesis before broad fixes. Prefer regression proof. Do not claim root cause when only a symptom was mitigated.

## Refactor

Stay in requested/necessary scope. Preserve public behavior unless explicitly changed. State equivalence check: tests, type checks, snapshot comparison, or static reasoning. Do not mix unrelated feature work. Prefer behavior-preserving simplification before architecture reshaping. Inline, merge, or delete one unnecessary seam at a time when evidence shows no current value. Do not replace simple code with a framework, registry, generic abstraction, reflection, or config surface unless evidence proves lower net complexity.

## Security and Sensitive Data

Do not repeat secrets, private keys, tokens, passwords, or sensitive values. Flag credential exposure and recommend rotation. Prefer secret stores and least privilege. Treat PII and regulated data as security/compliance concerns requiring evidence.

## Evidence Labels

- `executed`: command/check actually ran and result is known.
- `static`: reasoned from inspected files without running code.
- `not-run`: skipped check with reason.
- `blocked`: work/check could not proceed safely; include missing evidence.

## Complexity Reduction

Treat complexity reduction as production change, not cleanup: hypothesis, behavior to preserve, safety net, smallest reversible change, before/after evidence. Prefer deletion/inlining over new generalized structures. Stop when behavior equivalence cannot be checked honestly.
