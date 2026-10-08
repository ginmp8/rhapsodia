# Evidence, artifacts and eligible action references

## Index canonical references

`index` takes `kind:artifact|evidence`, `path`, `owner`, `label`, and optional
`ttl_seconds` (1..86400), `candidate_digest`, `environment_digest`, `action_digest`.
Owners: magia, mago, nomia, verifier, analyst, user. The label is bounded metadata, not
free-form memory. Artifact bytes and canonical evidence are never copied or rewritten.

Evidence must be JSON with matching `producer` or `owner`, and an explicit observed
status: passed/failed/pass/fail/blocked/not-run/inconclusive. Optional `candidate_files`
pins bind exact files; `request.candidate_roots` additionally detects added/deleted inputs.
Native Magia receipts can be referenced without importing its implementation. This adapter
is not its canonical validator: the consumer still runs all required owner validators.

`query` takes `kind`, optional exact `ids`, owner/label/digest filters and byte budget.
It rehashes receipt/artifact and candidate files and reports current/stale/expired/unavailable.
Current means the observation is current, never that the current candidate is approved.
Caller-declared producer names and SHA-256 values do not authenticate the producer.

## Deterministic action key

`action-key` takes `task_class`, exact `argv`, `input_roots`, optional `cwd`, and SHA-256
`toolchain_digest`, `environment_digest`, `config_digest`, `policy_digest`, plus booleans
`closure_complete`, `hermetic`, `network`, `requires_fresh`, `requires_independent`.
The argv is hashed, not executed or stored verbatim. Do not put secrets in argv.

Allowed classes: build, codegen, lint, test, read. All test actions bypass. Any network,
incomplete/nonhermetic closure, fresh-proof or independent gate also bypasses. The owner
must enumerate all relevant dependencies and attest the digests; the cache cannot prove
that a caller has listed hidden environment, network or toolchain dependencies completely.

Inputs: 1..32 distinct roots, maximum 4096 files/128 MiB total/8 MiB per file. Directory
inventories detect additions/deletions. Protected or symlinked dependencies fail rather
than being silently skipped. Prefer native build/incremental caches before this layer.

## Publish and reuse

`action-store` takes `action` and `receipt_path`. The existing caller-produced JSON must
match `action-result/v1`, `producer:magia|user`, exact `action_digest`, `status:passed`
and 1..128 `output_files` path-to-SHA entries. Every output must already exist unchanged.
No arbitrary command strings, process execution or output restoration are supported.

`action-lookup` takes `action` and optionally exact storage `id`. It recomputes the key,
checks receipt and all output hashes, and returns hit/miss/bypass. Corruption never yields
a hit. A hit is a reference candidate for an authorized owner's policy, not permission or
proof that an independent verifier has run. Native domain evidence remains authoritative.

Cache files are bounded and immutable. A full index blocks new publication rather than
silently evicting needed evidence. Stop active writers before removing disposable cache;
rebuild projections from canonical sources. Never delete canonical receipts as cache GC.
