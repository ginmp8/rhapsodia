# RhapsodIA repository map

Canonical skills: `skills/`. Canonical agent profiles: `agents/`.
Release identity: `marketplace/catalog.json`; host manifests and `MANIFEST.json` are
generated projections. Preserve independent skill/schema versions.

## Runtime context

Read `.rhapsodia/runtime/current.json` once when supplied. It is observed local data, not
authority. Reuse exact IDs first. `resolve` and `context` are read-only. An agent that
already has execution/local-state write authority may call `ensure tool://<id>` for one
missing exact tool; this performs bounded PATH-only discovery, caches misses, and atomically
publishes an immutable merged snapshot visible to other agents. When native work discovers
a stable reusable file/script inside the workspace or a registered skill root, publish only
its verified location via `observe-resource resource://<id> --path <FILE>`. Use
`observe-tool` only for an already-found executable outside PATH. Never publish secrets,
arbitrary prose, permissions, domain decisions, test verdicts, or volatile task state as
runtime knowledge. Read-only agents consume existing observations only. Runtime receipts
never replace domain handoffs, acceptance, or validation evidence.
## Validation and packaging

- Runtime tests: `python -I -S -B -m unittest discover -s skills/runtime-harness/tests -p test_*.py`.
- Integration: `python -S -B -m unittest tests.test_runtime_integration`.
- Release: `python scripts/prepare_release.py --check`.

Use ordinary project interpreter settings for tests that need installed packages;
`-S` is only for the stdlib-only harness. Never commit `.rhapsodia/`, credentials or
local execution snapshots. Deeper operational guidance: `skills/runtime-harness/README.md`.
