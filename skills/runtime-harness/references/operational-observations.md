# Capabilities and typed discovery observations

Runtime Harness 1.2.0 extends snapshots additively. It reads 1.1.0 snapshots at the same
installation path and publishes new observations as 1.2.0. Refresh catalog/environment
state explicitly after upgrading or moving an installation; never migrate domain state.

## Capability registration

`publish-capability --input <JSON>` takes uri (`capability://<id>`), tool (`tool://<id>`),
proof (repo/skill/resource file URI), optional ttl_seconds (1..86400, default 3600).
The existing UTF-8 JSON proof must contain exactly:

```json
{"schema":"capability-observation/v1","capability_uri":"capability://python-json","tool_identity":"<current tool identity>","available":true,"features":["json"]}
```

This file is produced by an already-authorized caller after its own observation/probe;
the harness never executes a probe or authenticates the producer. Features are at most
32 unique lowercase labels. The tool and proof must exist and match; the stored record
pins tool identity, proof hash, features, timestamp and expiry. `resolve capability://...`
returns available only while the tool/proof identities and TTL remain current. It never
verifies arbitrary minimum version expressions or grants permission to run a command.

## Typed attempts

`observe-attempt --input <JSON>` takes target (tool/capability/resource URI), outcome,
strategy and optional duration_ms/ttl_seconds. Outcomes: available, missing, denied,
incompatible, transient, broken, stale. Strategies: path, explicit, registered-root.
Only measured duration or null is accepted; raw stderr, commands, credentials and prose
are not fields. Attempts bind current scope, target identity and search fingerprint.

TTL defaults/ceilings: available 3600s, missing 600s, denied 60s, incompatible 600s,
transient 30s, broken 120s, stale 1s. The log holds at most 512 immutable-snapshot records;
oldest observations roll out of the current projection, not out of canonical evidence.

`discovery-history --input <JSON>` takes target and optional budget_bytes (512..65536).
It returns only still-current observations, explicit omitted count and per-strategy
success counts, smoothed success rate `(successes+1)/(observations+2)` and median duration.
This is bounded descriptive strategy reuse, not machine learning or permission to bypass
denied outcomes. No strategy is executed. Changing PATH or target identity invalidates
old hints. Short transient expiry prevents permanent negative caching of temporary errors.

Read-only consumers inspect supplied observations; only execution/cache-authorized workers
publish. Runtime Harness still owns environment knowledge, not workflow status, action
cache, artifact lifecycle, test acceptance or cross-workspace operational memory.
