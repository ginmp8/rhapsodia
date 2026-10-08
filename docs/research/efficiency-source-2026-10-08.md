# Technical research: Token and latency efficiency in RhapsodIA

**Research date:** 2026-10-08\
**Artifact examined:** `rhapsodia-feature-runtime-harness.zip`\
**ZIP SHA-256:** `47c340cfacebc47b1e91f820ef775112264bf1a6fbc0dc8a09f7ee12602e13f2`\
**Scope:** Static analysis of version 0.7.0 and research into 11 opportunities, using 19 distinct sources. No changes were made to the ZIP or the original repository. No real agents were run against paid APIs; token and latency reduction estimates are hypotheses, not measurements.

## Executive summary

**Recommendation:** Do not build a second global memory or centralize everything in `runtime/current.json`. Preserve the Runtime Harness as the source of technical knowledge about the environment; connect agents to evidence already produced by Magia/Verifier, adding **disposable context projections**, **read-only evidence indexes**, and **comparative measurement of end-to-end execution**. Reuse of execution results comes later, with policies by task class. Local Graph Engine v3 remains an optional index/projection, not a new owner of operational truth.

Prioritize avoiding *context reload*, *duplicate research*, *duplicate delegation*, *redundant tool calls*, and *replay of huge outputs* before trying to store every `dotnet test` result. Token savings and latency gains do not always coincide.

### Findings verified in code

| Component | Evidence in ZIP | Implication |
|---|---|---|
| Runtime Harness 1.1.0 | On-demand discovery, positive/negative observations, immutable snapshots, scope identity, stale checks, bounded queries and ETags, hash-linked handoffs | Do not reimplement tool-path, resource, and snapshot caching |
| Supervisor | Prevents materially identical work/delegation; limits read fan-out; requires a single canonical writer; limits reentry/delegation | Improve the decision of *when* to delegate, not create another supervisor |
| Magia and Verifier | Magia maintains execution evidence and selects validations; Verifier provides a separate check under existing rules | Reuse should *point* to receipts, without issuing its own verdicts |
| Local Graph Engine v3 | SQLite evidenced by sources, byte-budgeted contexts, caller-held receipt reuse, and a derived graph | Reuse it for complex dependency searches; never send the full graph by default |
| Runtime benchmark | Measures local startup/query time and bytes; sets `billed_tokens: None` | Does not prove prompt savings, billing savings, or total agent time |
| MCP Runtime | One read-only `runtime_query`, protocol versions 2025-11-25/2025-06-18, handshake, and results in `content` + `structuredContent` | Test 2026-07-28 compatibility and whether duplication reaches the LLM before changing anything |

## Prioritized roadmap

Qualitative impact assumes tasks that actually repeat context/operations. **These are not measured gains.**

| Order | Improvement | Tokens | Time | Cost/risk | Owner |
|---|---|---|---|---|---|
| P0 | **Instrumentation and paired benchmarking**, with cost by phase/host/agent | Identifies waste | Locates bottlenecks | Low-medium | Host adapters, Skill Token Efficient |
| P0 | **Minimal context pack per work unit**, just-in-time selection, focused files/symbols | High potential | Medium-high | Medium (omissions) | Supervisor composes; sources remain canonical |
| P0 | **Cost- and critical-path-aware delegation policy**, single-agent fast path | High potential | High for suitable tasks | Medium (quality) | Supervisor / adaptive-workflow-orchestration |
| P0 | **Prefix stability and native prompt caching** when exposed by the host | May reduce billed cost, not necessarily logical tokens | Potentially lower TTFT | Low-medium | Host adapter |
| P1 | **Operational Evidence Index**, a read-only bridge to existing evidence | High for repeated work | Medium-high | Medium-high (trust/freshness) | Receipt owner = Magia/Verifier; derived index |
| P1 | **Incremental reference handoffs**, with immutable parent and full fallback | Medium in long workflows | Medium | Medium | Runtime Harness transport; workflow remains external |
| P1 | **Progressive, selective search**, reusing Local Graph v3 only when worthwhile | High in complex repositories | Varies | Low-medium | Mago/Magia + optional Local Graph |
| P1 | **Catalog of derived artifacts with SHA**, without duplicating payloads in chat | Medium-high in workflows with large artifacts | Medium | Medium | Canonical producers + index |
| P2 | **Deterministic action cache** for repeatable build/codegen/lint | Medium | High for expensive tasks | High (incorrect key) | Authorized worker, no new test authority |
| P2 | **Capabilities and typed failures**, compatibility-oriented discovery | Medium | Medium | Medium | Runtime Harness |
| P2 | **MCP 2026-07-28 compatibility / cacheable lists** | Varies by catalog | Varies | Medium (older clients) | Transport adapter |
| P3 | **Cross-workspace memory/federation; general leases** | Conditional | Conditional | High (authorization, consistency) | Only when a demonstrated need exists |

## Suggested minimal architecture

```text
                      RhapsodIA Supervisor
                       |             |
              asks context        delegates native
                       |             |
            [Context Composer]  Nomia / Mago / Magia / Verifier
                 |   |   |                  |
          read-only views                 writes OWN evidence
                 |   |   |                  |
                 |   |   +------> [Evidence Reference Index]
                 |   |                      (derived/read-only)
                 |   +-----> Runtime Harness (tool/resource/env facts)
                 +---------> Local Graph v3 (optional query projection)

     Source files + domain records + approved test receipts = authority
     Context packs + reference index + action cache + graph = disposable aids
```

Keep `runtime/current.json` only as the existing pointer/manifest; do not put workflow state in it. Logically separate environment information, operational references, and governance state, **without declaring three new competing authorities**.

Suggested disposable on-disk layout, only if an implementation is authorized:

```text
.rhapsodia/
  runtime/                        # existing: identity/snapshots/observations
  cache/                          # new, derived, can be deleted in its entirety
    context-packs/
    evidence-index/
    action-objects/
  # Nomia/Mago/Magia remain owners of their canonical records
```

The minimal backend can be local JSON/SQLite, with no always-on service. The choice should depend on actual concurrency, cardinality, and read patterns; Local Graph v3 already has SQLite and APIs, so there is no initial justification for another graph engine. SQLite WAL imposes filesystem constraints and is not suitable for a shared database placed directly on a network drive.

## Four incremental contracts

### A. Task context pack (`task-context/v1`)

A **small, derived** package delivered to the agent:

```json
{
  "schema": "task-context/v1",
  "work_unit_id": "unit-42",
  "goal": "validate a scoped code change",
  "source_scope": {"repo": "repo-id", "commit": "sha", "dirty_tree_sha256": "sha256"},
  "required_contract_refs": ["resource://approved-spec"],
  "relevant_evidence": [
    {"uri": "resource://path#L20-L50", "sha256": "...", "trust": "repo-source"}
  ],
  "known_blockers": [],
  "max_payload_bytes": 8192,
  "incomplete": false
}
```

*Illustrative example, not the current schema.* The first package says what to query; details come later by reference. The byte limit is not a token limit. Do not omit mandatory contracts and gates to fit the budget—setting `incomplete: true` and resolving the gap is preferable to false certainty.

### B. Evidence reference index (`execution-evidence-index/v1`)

```json
{
  "schema": "execution-evidence-index/v1",
  "reference": "execution://sha256:...",
  "producer": {"owner": "magia", "receipt_uri": "resource://..."},
  "subject": {"candidate_digest": "...", "workspace_scope": "..."},
  "action_digest": "...",
  "environment_digest": "...",
  "gate": "unit-tests",
  "observed_status": "passed",
  "freshness": "current",
  "reuse_policy": "reference-only",
  "verified_at": "2026-10-08T00:00:00Z"
}
```

The index does **not** execute, sign, change state, or replace a canonical receipt. An observed status is not equivalent to current approval. The consumer must validate the scope, SHA, and independent-evidence requirement.

### C. Delta handoff (`runtime-handoff-delta/v1`)

A `parent_handoff_sha256` plus `added_refs`, `removed_refs`, `changed_fields`, and the hash of the effective view. Send the delta only if the recipient already has the exact parent; otherwise, resend the full snapshot. Limit chain length and compact only with authorization from the same owner, without modifying the existing `handoff/v1` agent-control or domain handoffs.

### D. Action key (deterministic tasks only)

```text
key = SHA256(
   task_class + normalized_command + declared_input_closure +
   workspace/dirty_state + toolchain_versions + relevant_env +
   config_digest + execution_policy_version
)
```

The key must change whenever any relevant input changes. If dependencies/inputs cannot be enumerated, set `cache_eligible=false`. Test receipts may be found, but the executing agent must still meet gates that require fresh execution. Preserve the native `dotnet build`/MSBuild cache before developing a second build cache.

## Execution rules for optimizing actual cost

**Task intake:** The Supervisor makes a low-cost choice among `single`, `sequential`, and `read-only-fanout`. A trivial action does not create subagents; fan-out depends on independence and expected benefit relative to startup cost, context tokens, and synthesis. Do not relax writer exclusivity or Verifier gates.

**Discovery:** Start with `git diff`, text search, cited symbols, and available receipts. Expand only when dependencies or ambiguity arise. Use Local Graph v3 for repeated relationship queries, not for every simple change.

**Observations:** Group deterministic commands with short, structured outputs; do not dump full logs into the prompt. Persist the full log as an artifact; send the agent the status, path, summary, and reference. Avoid silent data loss: truncated output must indicate how to retrieve the full output.

**Instructions and tool catalogs:** Measure the actual cost of prompts and tool schemas for each host; do not assume all 52 skills in the ZIP are loaded in full. In static inspection, the `rhapsodia-supervisor.agent.md` profile is 22,292 bytes; that size **does not prove** its token consumption by the model. Optimize with progressive blocks, short activation descriptions, critical rules in the core, and on-demand references, verifying that the host actually injects the blocks. Reduce redundancy without moving ownership/gates or harming prefix caching.

**Model/provider:** If the host exposes model routing and effort, maintain a policy by task type and escalate in case of failure/risk. Do not create an SDK/provider dependency in the portable core. Preserve stable prefixes and measure `cached_tokens`, `cache_write_tokens`, spend, and time-to-first-token according to host capabilities.

**Failures:** Use distinct semantics for `missing`, `denied`, `incompatible`, `transient`, `broken`, and `stale`; use specific TTLs and scopes; do not apply permanent negative caching to transient errors. Only already-authorized workers may perform executable probes. Resolving a capability does not grant permission.

**MCP:** The 2026-07-28 protocol implemented caching hints `ttlMs/cacheScope` and handshake/stateless-core changes. The current Runtime speaks earlier versions; add a negotiated adapter and per-host tests instead of switching abruptly. The same response in `content` and `structuredContent` duplicates transport bytes, but may or may not duplicate the tokens actually seen by the model: measure in the client before optimizing.

## Quantitative evaluation criteria

**No gains were measured in this work.** The first change should be instrumentation, with collection permitted by the host and privacy by default:

| Metric | How to obtain it | Use |
|---|---|---|
| Input tokens, cache reads/writes, output tokens | Usage reported by the provider, when available | Identify total versus billed tokens |
| Total cost | Explicit, dated model/pricing table + usage | Verify financial savings |
| Wall time P50/P95; TTFT | Monotonic traces by phase/tool/agent | Verify actual speed |
| Agent spawns, redundant calls, repeated searches | Structured events and fingerprints | Verify orchestration waste |
| Context bytes and unique source refs | Local meter + hashes | Compare without claiming equivalence to tokens |
| Valid cache hit/miss/stale/unsafe | Identity tests and audit | Verify correctness and cache poisoning |
| Completion rate / acceptance gates / retries | Objective oracles and occasional human review | Ensure efficiency does not compromise results |

**Recommended experiment protocol:** 20 representative work units (short, medium, long; code, validation, research; cold/warm; changed inputs; transient error; different environment), with each variant run using the same model, host, configuration, and criteria, multiple repetitions, and balanced ordering. Phases: (1) baseline, (2) context packs, (3) delegation policy, (4) evidence index, (5) deltas/caches. Report intervals/samples and do not infer causality from a single run.

**Proposed acceptance gates** (targets for testing, not facts): zero incorrect reuses in negative cases; no mandatory gate omitted; no authorization deviation; evidence coverage preserved; measurable token/cost reduction in at least one scenario class without worsening P95 latency for affected scenarios; correct fallback with empty, corrupted, expired caches and modified sources.

## Suggested implementation sequence

| Increment | Small deliverable | Mandatory acceptance |
|---|---|---|
| 0 | Portable metrics contract + opt-in adapters | Present and missing data represented correctly; no secret collection |
| 1 | Read-only `task-context/v1` + feature flag + fallback | Baseline/variant pairing, instruction/source completeness; no regression |
| 2 | Fan-out decision policy accounting for overhead and critical path | No parallel writers; quality preserved; cost and latency measured |
| 3 | `execution-evidence-index/v1` pointing to Magia receipts | SHA/scope/producer/time; stale evidence does not become approval |
| 4 | Delta handoff with identical round-trip and fallback | Tests for missing parent, changed hash, chain limit |
| 5 | Action cache only for a proven hermetic class | Changes to every known dependency invalidate; outputs verified |
| 6 | `capability://` and MCP updated according to support matrix | No-op on hosts without the capability; no read-only execution |
| 7 | Cross-workspace federation, only when justified by observed benefit | Privacy, isolation, authentication, provenance, and invalidation |

## Anti-patterns to avoid

- Having agents call an LLM to summarize every short output: this can cost more tokens than reading the original output.
- Forcing Local Graph for every query: indexing and projection can cost more than `grep`.
- Centralizing all agents' knowledge in `current.json`: state, concurrency, and invalidation become a single point of contention.
- Treating `SHA-256` as producer identity/authenticity or as authorization.
- Caching `dotnet test` without complete inputs, external factors, runner version, and an explicit evidence policy.
- Confusing **byte** reduction with **token** reduction, or confusing prompt caching with not sending logical tokens.
- Expanding subagents by default: fan-out can greatly increase total consumption, and implementation tasks often have sequential dependencies.
- Sharing memory across users/repositories without isolation and controls for the trustworthiness of retrieved content.

## Selected sources

- Anthropic — Effective Context Engineering for AI Agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic — Effective Harnesses for Long-Running Agents: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic — How We Built Our Multi-Agent Research System: https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic — Code Execution with MCP: https://www.anthropic.com/engineering/code-execution-with-mcp
- OpenAI — Prompt Caching: https://developers.openai.com/api/docs/guides/prompt-caching
- OpenAI — Compaction: https://developers.openai.com/api/docs/guides/compaction
- Model Context Protocol — 2026-07-28 release: https://blog.modelcontextprotocol.io/posts/2026-07-28/
- Bazel — Remote Caching: https://bazel.build/remote/caching
- Gradle — Build Cache Concepts: https://docs.gradle.org/current/userguide/build_cache_concepts.html
- Microsoft — MSBuild Incremental Builds: https://learn.microsoft.com/pt-br/visualstudio/msbuild/incremental-builds?view=visualstudio
- OpenTelemetry — GenAI Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- OWASP — Memory Is a Feature. It Is Also an Attack Surface (2026): https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/
- SQLite — WAL: https://sqlite.org/wal.html

The research JSON files in the `results/` folder detail 11 strategies and additional sources with provenance. This document is an engineering synthesis and proposal, **not a delivered implementation or a benchmark run with agents**.
