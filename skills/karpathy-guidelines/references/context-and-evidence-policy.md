# Context and Evidence Policy

Use this reference when correctness depends on repository context, command output, external documentation, citations, context budget, secrets, or unsupported claims.

## Context selection

Load context in this order:

1. user-provided code, diff, error, stack trace, or design text;
2. directly referenced files or modules;
3. nearby tests, callers, configuration, and existing project patterns;
4. documented validation commands such as test, build, lint, type check, or smoke scripts;
5. official external documentation only when the task depends on API, framework, or tool behavior that could be version-specific.

Do not read broad directory trees, unrelated modules, generated outputs, lockfiles, or large logs unless they are necessary to test a stated hypothesis.

## Evidence labels

Use these labels when reporting closure:

- **Executed**: the check was run in the current session and the result is known.
- **Inspected**: the file, diff, or configuration was read but no executable check was run.
- **Static reasoning**: the conclusion follows from visible code or configuration, with no runtime proof.
- **Not executed**: the check was not run; include the most useful command or observation when concise.
- **Unverified**: there is no reliable evidence for the claim in the current context.

Never convert a suggested check into evidence. Never say tests passed unless the test command actually ran and completed successfully.

## Context efficiency

For quick local edits, avoid long plans and load only the target artifact. For non-trivial changes, use a short explore -> plan -> change -> validate loop:

1. inspect the smallest set of files that can explain the behavior;
2. summarize the current hypothesis;
3. apply a bounded change or provide a bounded plan;
4. run or name the strongest feasible validation check;
5. stop when the user request is satisfied instead of expanding into opportunistic cleanup.

If two or more failed approaches have accumulated, reset the plan around the latest evidence rather than continuing with stale assumptions.

## External sources

Use official documentation, release notes, or primary sources when behavior may be version-specific. Cite or name the source in the answer when it materially affects a recommendation. Avoid importing generic best-practice prose unless it changes the concrete patch, validation command, or risk assessment.

## Secrets and sensitive output

When a snippet, log, environment file, or configuration includes a credential, token, private key, connection string, or other secret:

- do not quote the secret value;
- state the exposure without reproducing it;
- recommend rotation when exposure plausibly reached a shared channel, model context, log, repository, or artifact;
- propose secret-store or environment-based handling consistent with the visible stack;
- avoid adding examples that hardcode sensitive values.
