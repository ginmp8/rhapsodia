# Command contract

Resolve this package directory; `scripts/operational.py` is package-relative, not a
project requirement. Python 3.10+ standard library only. The repository additionally
ships `scripts/operational.py` as a convenience launcher. No peer package is imported.

One UTF-8 JSON request is read from `--input <FILE>` or stdin. Duplicate keys, nonfinite
numbers and input beyond 4 MiB are rejected. Responses are one JSON object; exit 0 is
success, 2 invalid input/limits, 3 unavailable data, 4 stale/conflicting state, 5 busy.
Explicit paths and requested data must already be authorized. No command executes a
project tool, restores build outputs, contacts a service, or invokes a model.

Use `describe` with `{"command":"pack"}` to load one exact request schema. Empty `{}`
returns only the command/mutation inventory. Schema and semantic validation are distinct;
Python validators enforce live hashes, filesystem and policy constraints.

| Command | Writes |
|---|---|
| `pack`, `pack-verify`, `pack-use`, `prefix`, `output-card`, `describe` | None |
| `query`, `action-key`, `action-lookup`, `usage`, `metric-summary`, `metrics-compare`, `delegate`, `retrieval`, `graph-export`, `federation-export` | None |
| `pack-save`, `index`, `action-store`, `metric-record`, `federation-import` | Disposable immutable objects only |
| `lease` | None for `check`; cooperative lease state for acquire/renew/release |

The working directory is selected by `--workspace <ROOT>`, not inferred from input paths.
Relative source paths cannot escape it or traverse symlinks/private components. The
explicit input file may be outside that workspace, but it does not authorize other reads.

Examples are real request formats, not executed evidence. Copy the selected request and
replace its paths/digests with actually observed values. Do not load every example.
[Example requests](../examples/requests.json) and [schemas](../contracts/commands.json)
are machine-readable. The package entrypoint links every required instruction directly.
