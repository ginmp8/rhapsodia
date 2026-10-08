# Research-to-implementation accounting: 0.8.0

The bounded source is the prior 2026-10-08 research report plus the explicitly verified
MCP/current-provider documentation cited by the target skills. This is not a new universal
literature review. [The preserved report](efficiency-source-2026-10-08.md) is evidence, not
runtime instructions; its proposals become requirements only through the mapping below.

| Research area | 0.8.0 implementation | Deliberate bound |
|---|---|---|
| Minimum context / prefix / large outputs | `pack*`, `prefix`, `output-card`, `describe` | Required evidence cannot be dropped; provider control remains external |
| Shared artifacts and evidence | `index`, `query` | Disposable references, no approval authority |
| Repeated deterministic work | `action-*` | Complete hermetic inputs attested; no tests, execution or restore |
| Actual usage and comparable experiments | `usage`, `metric-*`, `metrics-compare` | Unknown stays null; no model benchmark fabricated |
| Cost-aware delegation / selective retrieval | `delegate`, `retrieval`, agent guidance | No new orchestrator or parallel canonical writers |
| Capabilities / failures | Runtime publication and typed observations | Exact tool/proof pins; no probes during lookup |
| Handoff deltas | Runtime full/delta transport | Exact parent acknowledgement and full fallback |
| Modern MCP | 2026-07-28 read-only stdio profile | Legacy clients retained; real IDE validation not claimed |
| Graph / federation | Data-only graph patches and quarantined pointer exchange | No mandatory graph or automatic cross-workspace trust |
| Leases / discovery learning | Cooperative nonce/generation leases; scoped statistics | No OS writer enforcement or learned autonomous policy |
| Integration and release | Seven profiles, 53-skill catalog, synchronized 0.8.0 manifests | Unrelated skills and domain authority preserved |

## Artifact selection and creation workflow

Operational Context is one reusable on-demand capability with modes, not a new always-on
agent. Runtime Harness remains the environment owner. The initial plan and frozen seed
checks preceded substantial implementation. The seed ran red without the feature, then
green. Supplementary tests cover generalized failure modes, not only seed examples.

Skill Creator Juiced gates validate the new package's compact control surface, one-hop
references, scripts, optional OpenAI metadata and six semantic/seven distribution profiles.
Local imports identified as possible external dependencies by heuristic scanners are
resolved to bundled `oc_core` modules; isolated `-I -S` tests demonstrate no third-party
package requirement. Static module-orphan hints are likewise checked against real imports.
These findings are documented, not silenced by changing the gate.

Research Traceability records are separate per skill:
[Operational Context](operational-context-traceability.json) and
[Runtime Harness](runtime-harness-traceability.json). Findings outside an individual owner
are explicitly routed rather than silently omitted. Structural accounting does not prove
semantic completeness, independent model evaluation or measured performance.

## Preserved constraints

Do not add a second workflow engine, duplicate canonical records, centralize work state in
`current.json`, treat SHA as authentication, skip mandatory test gates, share private paths
or extrapolate tokens from bytes. Do not require Orca, an external runtime, a paid API or a
particular IDE for core behavior. Optional host support must degrade explicitly.

## Evidence limits

Native model/IDE evaluations, paired paid-token benchmarks and Windows/macOS execution
were not available in this run. The configured CI matrix is a future execution surface,
not completed evidence. Release claims distinguish structural, local behavior and runtime
checks from those unexecuted layers. See [validation](../releases/validation-0.8.0.json).
