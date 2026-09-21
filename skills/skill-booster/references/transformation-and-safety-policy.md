# Transformation and Safety Policy

## Allowed scope

Default writable scope is the target skill folder only. Common allowed files: `SKILL.md`, Markdown under `references/`, deterministic scripts, templates used by the workflow, examples/evals when evaluator design or compatibility is explicitly in scope, and optional host adapters such as `agents/openai.yaml` only when relevant. Portable-core behavior must never depend on a host adapter.

## Blocked paths

Do not edit or package `.git/`, secrets, credentials, keys, private certs, generated reports, baseline evidence, old `skill.zip`, caches, bytecode, fixtures, expected outputs after freeze, unrelated repository files, or user-declared read-only files.

## Transformation discipline

Use one bounded change or inseparable batch at a time. Safe examples: refine activation, add output contract, repair local links, add deterministic validator/packager, improve script diagnostics, move branch detail to references, compress after validation. Unsafe examples: edit expected outputs to pass, remove safety/validation for tokens, delete unknown resources without classification, package reports/credentials, or claim benchmark improvement without evidence.

When `reproducibility-engineer` runs in `audit-only`, it does not own target changes; route findings through selection. When it runs in `apply`, it owns only the explicitly selected reproducibility batch. Do not let `skill-improver` independently change the same batch.

Use the strategy gate before editing. A known repair should normally use direct repair, not experimental or evolutionary machinery. Search-specific concepts must not become prerequisites for canonical target changes.

## Rollback, freeze, and boundaries

Preserve enough state to revert, record changed files, reject failed gates, and keep rejected notes. When optimization depends on external files or repository evidence, snapshot/pin the exact source bytes before analysis and verify their identity before acceptance. Use connectors/source truth when optimization depends on repository or Drive facts; otherwise mark assumptions or stop. After final acceptance, freeze the candidate. Any later target edit invalidates the freeze and requires affected validation plus a new manifest.

## Delivery integrity

Package from the verified frozen candidate only. Canonicalize package and receipt paths first; reject aliases, outputs inside the target, invalid resolved filenames/extensions, and symbolic-link cycles before editing output artifacts. Build and test temporary outputs first, calculate candidate/package hashes, then commit archive and success receipt as one recovery-aware transaction. A failed attempt must preserve the previous `skill.zip` and previous successful receipt. If rollback is incomplete, preserve and report recovery paths instead of deleting evidence.

## Security floor

Every optimized skill preserves secret boundaries, scoped filesystem writes, no fabricated validation/benchmark claims, no unsafe shell guidance, explicit package exclusions, and stop conditions for missing evidence. Third-party/downloaded skills are `external-untrusted-skill` until the external intake passes; do not execute their scripts, installers, hooks, binaries, or package-manager commands during quarantine.

## Cross-host safety

Do not pre-approve shell/process execution in portable frontmatter. Permission models differ by host; leave tool authorization to the host/user. Keep validators offline and standard-library-only. Do not hard-code vendor-private tool calls, `/home/...` sandbox paths, or platform-specific skill installation paths in core instructions.
