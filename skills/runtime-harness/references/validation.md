# Validation and performance evidence

## Executable checks

```text
<PYTHON> -I -S -B -m unittest discover -s tests -p test_*.py -v
```

The suite covers bootstrap, lazy arbitrary-tool discovery, negative-cache invalidation,
explicit tool publication, reusable resource publication, cross-process reuse, immutable
merge behavior, handoff pinning, traversal/symlink/hardlink guards, virtualenv identity,
MCP read-only behavior, bounded outputs and host adapters. Platform-specific tests skip
with a reason when the required shell is unavailable; a skip is not native-host proof.

Repository integration tests validate release inclusion/exclusion and agent guidance.
Cross-platform CI is a future/external verification mechanism unless its run evidence is
attached to the exact candidate.

## Performance boundary

`benchmark` measures local cold bootstrap, warm reuse and selected query timing. It does
not measure model startup, IDE startup, billed tokens or full task latency.

The important behavioral properties are separately tested:

- bootstrap does not scan a fixed tool catalog;
- read-only `resolve/context` perform no discovery;
- `ensure` discovers only requested tool IDs;
- later processes reuse published observations;
- repeated missing-tool lookup reuses a negative cache until TTL/search-space change;
- context output stays byte-bounded.

For real benefit claims, run paired native agent tasks with frozen correctness gates and
measure time/tool calls/tokens to first productive action plus complete task latency.

The 1.2.0 suite also exercises observed capability/proof invalidation, bounded typed
attempts, full/delta round trips and modern stateless stdio alongside legacy regression.
No local pass certifies native IDE integration or paid-model token efficiency.
