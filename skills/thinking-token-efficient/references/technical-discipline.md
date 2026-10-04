# Technical Discipline

## Operating principle

Keep technical assistance small, explicit, and verifiable. Token savings must come from fewer irrelevant branches and less recomputation, not from skipping inspection, evidence, or validation.

## Context selection

Load context in this order:

1. user-provided code, diff, log, file, or design text;
2. directly referenced files and nearby tests or callers;
3. project commands, configuration, and existing patterns;
4. official docs or current sources when version-specific behavior matters.

Avoid broad directory sweeps, unrelated modules, generated files, large logs, and lockfiles unless they prove a named hypothesis.

## Information-gain gate

Before another tool call, file read, branch, subagent, retry, or alternative implementation, identify the unmet obligation or decision it could change. Continue only when the expected information gain is material enough to justify the work.

A resolved branch stays closed unless new evidence, a failed acceptance check, or a changed constraint reopens it. Parallel work can reduce latency while increasing total compute; use it only for genuinely independent work whose results are all needed or whose isolation materially improves correctness.

## Smallest sufficient change

For code, config, ci, infrastructure, or technical examples:

- name the artifact and behavior to preserve;
- inspect before broad edits;
- avoid new abstractions, dependencies, rewrites, defensive configurability, and unrelated cleanup;
- preserve public APIs unless the user requested a change;
- mention unrelated issues separately instead of patching them opportunistically.

## Validation labels

Use precise evidence labels in final answers when relevant:

- `executed`: command or check ran in this session;
- `inspected`: artifact was read;
- `static reasoning`: conclusion follows from visible content only;
- `not executed`: check was not run; name the best check when useful;
- `unverified`: no reliable evidence supports the claim.

## Failure handling

If a command, search, file read, or validator fails, preserve the failure as evidence. Do not replace it with a weaker passing check without stating what the weaker check proves and does not prove.

A failure, contradiction, or changed dependency may justify higher reasoning effort. Do not compensate by merely expanding prose or repeatedly retrying the same unsupported approach.
