# Safe Cleanup Rules

Use these rules before any cleanup, simplification, consolidation, or deletion.

## Non-negotiable safety rules

1. Classify before deleting.
2. Prefer integrating useful resources over removing them.
3. Preserve progressive-loading resources even when they are not imported by scripts.
4. Do not change domain behavior without direct evidence and validation.
5. Do not delete resources only because a shallow grep did not find a reference.
6. Validate after any applied cleanup.
7. When evidence is insufficient, recommend a plan instead of executing removal.

## Protected resources

Never edit, move, or delete these unless the user explicitly names the exact file and the purpose is not destructive:

- `.git/` and VCS metadata;
- secrets, credentials, keys, certificates, tokens, `.env` files, and private config;
- fixtures, golden files, expected outputs, snapshot baselines, benchmark reports, scenario results, and generated evidence;
- existing `*.zip`, `*.tar`, `*.tgz`, `*.7z`, and package archives;
- user-declared read-only files;
- unrelated repository files outside the target scope.

## Allowed cleanup classes

Removal can be considered only for:

- placeholder scaffold created by an initializer and not adapted;
- cache directories such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.coverage`, `dist/`, `build/`, and temporary working folders;
- generated artifacts accidentally left inside a package, such as local reports, inventories, or package zips;
- exact duplicate files or sections after references are updated;
- obsolete files proven by target documentation, replacement files, or validation evidence.

## Consolidation rules

Treat duplication as real only when the content serves the same mode, audience, and contract. Similar text may be intentional when it appears in different branches, e.g. a short control-plane rule in `SKILL.md` and a detailed reference rubric.

When consolidating:

1. Pick the clearest source of truth.
2. Preserve any unique constraints from the duplicated copies.
3. Update every local link, workflow reference, template instruction, and script path.
4. Leave a migration note only when external references may exist.
5. Re-run validation.

## Rollback minimum

For every mutation, record:

- files changed or removed;
- original path and replacement path, if moved;
- reason and evidence;
- validation command;
- simple rollback instruction, such as restore from backup, revert patch, or copy retained content back.
