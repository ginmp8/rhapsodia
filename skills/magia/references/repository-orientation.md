# Repository Orientation

Load for brownfield, unfamiliar, multi-module, or validator-discovery work before selecting files to change. Orientation is read-only evidence collection, not planning authority or implementation approval.

## Objectives

Identify enough current repository context to choose the smallest safe execution scope:

- languages, build systems, package managers, and entry-point signals;
- modules and source/test layout;
- likely validators and test runners already present;
- API, event, schema, file-format, migration, and persistence contract signals;
- Mago planning and nomia governance markers as read-only context;
- generated, vendor, cache, and build paths that should not be treated as source;
- missing evidence that blocks a safe proving check.

## Deterministic Projection

Use:

```text
python scripts/inspect_repository_context.py --root <repository-root> --format json
```

Use `--format markdown` for a human-readable view and `--output <path>` only when a durable, explicitly requested projection is useful. The script:

- scans file paths and limited safe metadata;
- does not run build, test, package-manager, network, or repository commands;
- does not read secret values;
- skips common generated, dependency, and VCS directories;
- emits suggested command families only from detected files;
- keeps every list sorted for reproducible output.

The projection is non-authoritative. Verify relevant files and command semantics before mutation or execution.

## Orientation-to-Execution Gate

Before editing, confirm:

1. the target module and consumer surface are identified;
2. existing conventions are known or explicitly unknown;
3. the narrowest proving check is available or its absence is recorded;
4. public contracts, persistence, security, and cross-repository effects are classified;
5. allowed writes and blocked paths are explicit;
6. any planning or governance conflict is handed off rather than silently resolved.

Do not expand scope merely because the repository contains adjacent modules or cleanup opportunities.
