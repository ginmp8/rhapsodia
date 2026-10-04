# Rhapsodia Workspace

Rhapsodia Workspace is an optional, read-only projection layer for artifacts owned by RhapsodIA producers. It discovers producer-published `.artifact.json` sidecars, validates their metadata, builds derived catalogs, and renders a self-contained offline HTML view.

Workspace never becomes the source of truth for governance, planning, or execution. Nomia owns product and delivery governance, Mago owns technical planning, and Magia owns implementation and execution evidence. Their artifacts remain independently usable when Workspace is absent.

## Ownership model

| Component | Owns | Workspace behavior |
|---|---|---|
| Nomia | Product and delivery governance | Reads published metadata only |
| Mago | Technical planning | Reads published metadata only |
| Magia | Execution and validation evidence | Reads published metadata only |
| Rhapsodia Workspace | Derived catalogs and offline views | May rebuild or replace only its derived outputs |

Workspace does not create missing domain artifacts, move canonical files, change status or priority, execute referenced content, or infer completion from file existence.

## Data flow

1. A producer writes its canonical artifact in its own source tree.
2. The producer publishes an adjacent `.artifact.json` sidecar using the shared artifact envelope contract.
3. Workspace discovers and validates the sidecars without importing producer implementation code.
4. Workspace builds a stable, non-authoritative catalog.
5. Optional projections and the offline HTML view are generated under `.rhapsodia/`.

Derived outputs are disposable. Deleting `.rhapsodia/` does not change producer state.

## Commands

Use Python 3.11 or later:

```bash
python skills/rhapsodia-workspace/scripts/workspace.py discover --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py validate --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py index --repo-root /path/to/project
python skills/rhapsodia-workspace/scripts/workspace.py project --repo-root /path/to/project --view portfolio
python skills/rhapsodia-workspace/scripts/workspace.py render --repo-root /path/to/project
```

Generated outputs are written only below `.rhapsodia/catalog` and `.rhapsodia/views`. See [`skills/rhapsodia-workspace/references/commands.md`](../../skills/rhapsodia-workspace/references/commands.md) for command details and source-root selection.

## Offline viewer

The rendered HTML supports:

- portfolio, timeline, relationship, and per-skill views;
- local search and producer/lifecycle filtering;
- source hash and relationship inspection;
- light and dark themes;
- JSON snapshot export and explicit snapshot import.

Snapshot import validates the embedded metadata contract before replacing the currently loaded snapshot. An imported snapshot is still derived data: it is not authenticated filesystem evidence and does not prove that its source files remain current.

The synthetic [`demo.html`](demo.html) is provided only to demonstrate the interface. It does not represent real repository state.

## Validation

Workspace package validation and tests are part of the repository and should be version-controlled. Generated validation evidence is not source material and should be written outside the repository or to the ignored root `validation/` directory.

Core checks:

```bash
python -B -m pytest -q -p no:cacheprovider skills/rhapsodia-workspace/tests
python -B skills/rhapsodia-workspace/scripts/validate_skill_package.py --target skills/rhapsodia-workspace
python -B skills/rhapsodia-workspace/scripts/validate_native_contracts.py
```

Optional browser regression checks require Playwright and Chromium:

```bash
python -B skills/rhapsodia-workspace/tests/browser_workspace_checks.py --output-dir /outside/repo/browser-results
```

The metadata parity checker compares the Python artifact validator with the JavaScript import validator embedded in the viewer and requires Node.js:

```bash
python -B skills/rhapsodia-workspace/tests/differential_viewer.py \
  skills/rhapsodia-workspace \
  /outside/repo/metadata-parity.json
```

Keep generated reports, screenshots, receipts, hashes, and other run-specific evidence out of the source tree. Release-specific evidence may be attached separately to a GitHub Release when preservation is useful.

## Safety and freshness

Workspace rejects malformed metadata, duplicate identities, dependency cycles, unsafe paths, source/output overlap, and source drift during a run. A failed refresh preserves the last valid derived output rather than replacing it with partial data.

A last-good view can become stale after a failed refresh. Treat its source fingerprint and diagnostics as part of the view's freshness state; do not interpret an old projection as current runtime truth.

Private artifact metadata remains local unless all included records authorize the selected destination.

## Legacy Board migration

Workspace does not migrate legacy Board content. Migration is owned by each producer and is copy-only: recognized files are copied into the producer's native artifact tree while originals remain unchanged. Workspace can index the resulting sidecars after producer validation.

See [`skills/rhapsodia-workspace/references/migration-boundary.md`](../../skills/rhapsodia-workspace/references/migration-boundary.md) and [`skills/mago/references/ecosystem-migration.md`](../../skills/mago/references/ecosystem-migration.md) for the migration boundaries.

## Detailed contracts

The skill package is the normative source for implementation-level contracts:

- [`SKILL.md`](../../skills/rhapsodia-workspace/SKILL.md)
- [`artifact-contract.md`](../../skills/rhapsodia-workspace/references/artifact-contract.md)
- [`privacy-and-safety.md`](../../skills/rhapsodia-workspace/references/privacy-and-safety.md)
- [`packaging.md`](../../skills/rhapsodia-workspace/references/packaging.md)
