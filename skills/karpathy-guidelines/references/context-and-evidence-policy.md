# Context and Evidence Policy

Use this reference when correctness depends on repository context, command output, external documentation, history, citations, context budget, secrets, or unsupported claims.

## Context selection

Load context in this order unless the active hypothesis requires otherwise:

1. user-provided code, diff, error, stack trace, or design text;
2. directly referenced files or modules;
3. nearby tests, callers, configuration, and existing project patterns;
4. documented repository validation/build/task commands;
5. official external documentation when behavior is version-specific;
6. repository history only when current artifacts do not explain a material constraint being changed or removed.

Do not read broad trees, unrelated modules, generated outputs, lockfiles, large logs, or history without a stated reason.

## Repository-native tooling

Prefer execution paths in this order:

1. an exact user-provided command that is safe and in scope;
2. repository-documented or CI/task-runner commands;
3. existing project scripts/tools that test the same behavior;
4. ecosystem-standard tooling appropriate to the stack;
5. a one-off mechanism only when the existing paths are unavailable or inadequate and that limitation is explicit.

Do not invent a custom validator, build path, or temporary script merely because it is convenient to the agent. A stronger evidence-backed reason may override this order.

## History as conditional evidence

Use version-control history/blame when an apparently redundant or strange behavior is about to be removed or simplified and callers/tests/config/docs do not explain why it exists. Prefer the smallest relevant path/commit range. History can explain intent; it does not override current executable contracts or tests.

Do not require history for obvious local fixes or when the current code and tests already establish the constraint.

## Evidence labels

Use these labels when reporting closure:

- **Executed**: a check was run in the current session and the result is known.
- **Inspected**: a file, diff, configuration, or source was actually read.
- **Static reasoning**: the conclusion follows from visible artifacts without runtime proof.
- **Not executed**: a useful check was not run; state why or name it when material.
- **Unverified**: no reliable evidence in the current context supports the claim.

Never convert a suggested check into executed evidence. Never say tests passed unless the command actually completed successfully.

## Context efficiency

For quick local edits, load only the target artifact and directly relevant evidence. For non-trivial changes, use a bounded explore -> hypothesis -> change -> validate loop. Stop when the requested behavior is satisfied instead of expanding into opportunistic cleanup.

If two or more failed approaches accumulate, reset around the latest evidence rather than continuing from stale assumptions.

## External sources

Use official documentation, release notes, specifications, repositories, or other primary sources when behavior can vary by version. Cite or name the source when it materially changes the patch, command, or risk assessment. Avoid importing generic best-practice prose that does not affect the concrete task.

## Secrets and sensitive output

When code, logs, environment files, or configuration contain credentials, tokens, private keys, connection strings, or other secrets:

- do not quote the sensitive value;
- state the exposure without reproducing it;
- recommend rotation when exposure plausibly reached a shared channel, repository, log, artifact, or model context;
- use the repository's approved secret/environment mechanism;
- do not add examples that hardcode sensitive values.
