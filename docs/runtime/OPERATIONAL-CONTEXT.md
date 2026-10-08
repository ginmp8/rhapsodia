# Operational context architecture

## Ownership

The Supervisor routes and composes; domain owners retain authority. Runtime Harness owns
observations about the environment. Operational Context owns only disposable local
representations used to retrieve work context efficiently. Neither helper becomes a
workflow engine, approval service, authentication layer, model router or execution daemon.

```text
Supervisor --native delegation--> Nomia / Mago / Magia / Verifier
    |                                   | canonical records and proof
    +--> Operational Context -----------+ read references, never promote results
    |       packs / indexes / usage / policy / conservative result lookup
    +--> Runtime Harness
    |       tools / resources / observed capabilities / immutable handoffs
    +--> optional Local Graph v3 projection
```

## Physical data and lifecycle

| Surface | Meaning | Authority |
|---|---|---|
| `.rhapsodia/runtime/current.json` and snapshots | Existing pointer/catalog mechanism | Environment observations only |
| `.rhapsodia/cache/operational-context/` | Hash-addressed finite objects, cooperative leases | Disposable derived data |
| Domain artifact roots | Approved plans, decisions, implementation/evidence records | Existing producer owners |
| Local Graph | Optional relationships extracted from pinned data | Projection, not canonical truth |

Read commands create no cache directories. Publication uses short exclusive local locks,
immutable objects and atomic files. It is not a multi-user or hostile-filesystem security
boundary. Missing/invalid data causes an explicit error or miss, never a fabricated pass.
No external database is introduced merely to index a small local workload.

## Context before delegation

Start with an exact source reference, diff or known symbol; expand only for unresolved
relationships. Preserve required contracts in every task pack. If a budget cannot contain
them, fail explicitly instead of truncating. Optional omissions are visible; inline content
requires approval. A line slice pins the entire file so edits outside the slice still
invalidate its context. `pack-use` rechecks live pins, not only the stored object hash.

Static prefixes exclude the dynamic tail from their content identity. Native provider
caching remains conditional on host/model support. Full log text stays in a selected file;
output cards carry observed status, hash, location and explicit omission metadata.

## Evidence reuse without false approval

Artifact/evidence indices reference existing source receipts; they do not sign them or
create a new test result. Producer labels and hashes are checked for consistency, not
identity/authenticity. Candidate additions, deletions and edits invalidate declared input
inventories. Missing or expired records remain missing/expired.

An action key covers task class, exact argv digest, cwd, declared input inventory, workspace,
toolchain, environment, configuration and policy. Action results only qualify when the
caller explicitly declares complete hermetic inputs and no network side effects. Lookups
recheck source receipts and existing outputs. They never run a command, restore files,
cache tests or waive fresh/independent proof. Existing build-system incremental behavior
remains the first choice; this layer locates equivalent completed work conservatively.

## Delegation and measurement

Use one canonical worker per owner phase. Unknown overhead/costs select serial processing.
Only independent same-owner readers qualify for bounded cost-justified fan-out; writers,
verifiers and dependencies remain ordered. The helper returns a suggestion, not tool calls.

Record actual reported input/output/cache counters or null. OpenAI cache reads are already
included in its input total; Anthropic totals require all relevant categories. Paired
comparisons bind scenario, host, model, configuration, input, evaluator, sample, phase and
cache state. Quality failures cannot be traded away for a faster result. Samples produce
descriptive statistics, not a confidence interval or proof of general speedup.

## Optional sharing

Capability records require a current tool and a matching existing proof file. Typed
failures expire according to outcome; local strategy statistics are hints, not learned
global policy. No capability grants permission to execute its tool.

A runtime delta is useful only with an acknowledged exact parent and a smaller payload.
Otherwise send the full handoff. Reconstruction verifies immutable identity but does not
mark live pins current; consumers resume through normal runtime/domain validation.

Federation is explicit path-free pointer exchange with a selected-source allowlist and a
short expiry. Imported data is quarantined and never consulted by local action-cache hits.
Cooperative leases fence holder/nonce/generation changes and refuse takeover of live leases;
all participants must use the same logical key. They do not detect overlapping paths or
stop a stale external writer by themselves. Graph exports include observed edges only.

## Adoption and acceptance

Start with reference packs and measurement, then opt into evidence lookup and deltas where
there is actual repetition. Keep cross-workspace exchange and leases off ordinary paths.
Use the [migration guide](MIGRATION-0.8.0.md), [research accounting](../research/efficiency-0.8.0.md)
and [release evidence](../releases/validation-0.8.0.json). Real host/model benchmarks remain
required before publishing token or workflow-speed claims.
