# Mutation and Safety Policy

## Allowed scope

Default writable scope is the target skill folder only. Common allowed files: `SKILL.md`, `agents/openai.yaml`, Markdown files under `references/`, deterministic scripts, templates used by the workflow, examples/evals only when benchmark/evaluator design or compatibility is explicitly in scope.

## Blocked paths

Do not edit or package `.git/`, secrets, credentials, keys, private certs, generated reports, baseline evidence, old `skill.zip`, caches, bytecode, fixtures, expected outputs after freeze, unrelated repository files, or user-declared read-only files.

## Patch discipline

Use one bounded hypothesis per batch. Safe examples: refine activation, add output contract, repair local links, add deterministic validator/packager, improve script errors, move branch detail to references, compress after validation. Unsafe examples: edit expected outputs to pass, remove safety/validation for tokens, delete unknown resources without classification, package reports/credentials, or claim benchmark improvement without evidence.

## Rollback and boundaries

Preserve enough state to revert, record changed files, reject failed gates, and keep rejected notes. Use connectors/source truth when optimization depends on repository or Drive facts; otherwise mark assumptions or stop.

## Security floor

Every optimized skill preserves secret boundaries, scoped filesystem writes, no fabricated validation/benchmark claims, no unsafe shell guidance, explicit package exclusions, and stop conditions for missing evidence.
