# Measurement and bounded strategy advice

## Provider usage

`usage` takes `provider:generic|openai|anthropic` and `usage` object. OpenAI input/prompt
counts include cached input; the cached subset is not added again. Anthropic logical
input is noncached input plus cache reads plus cache creation, only when all three are
reported. Generic input is explicitly inclusive. Missing fields remain null, never zero.
Normalized usage is idempotent and can be replayed from recorded events.

`billed_tokens` stays null: provider prices, cache writes and discounts are not equivalent
to a universal token counter. `cost_usd` may only be an actually measured/attributed amount;
this package contains no price table or provider SDK. No raw prompt or tool log is stored.

## Events and experiments

`metric-record` requires run_id, event_id, scenario_id, host, model, config_digest,
input_digest, evaluator_digest, cache_state, sample, phase, arm, duration_ms, quality_pass,
provider, usage. Digests are SHA-256. Arm is baseline/candidate; cache state is cold/warm/
unspecified. Optional counters: context_bytes, tool_calls, agent_spawns, cache_hit,
ttft_ms, cost_usd. Timings must be monotonic measured durations or null; quality must be
an observed boolean. IDs must be non-sensitive opaque labels, not prompts or user names.

`metric-summary` optionally filters run_id. It rejects conflicting records with one event
ID. It never adds overlapping durations as end-to-end wall time. Select non-overlapping
leaf usage events when totals are needed; the caller is responsible for event granularity.

`metrics-compare` takes baseline and candidate event arrays, matched on scenario, host,
model, configuration, inputs, evaluator, cache state, sample and phase. Missing/duplicate
pairs fail rather than being silently dropped. Report P50/P95, sample size, paired mean
delta, usage completeness and quality. Mixed strata cannot support the combined gain flag.

The descriptive gain flag requires at least two complete timed pairs in one stratum,
preserved quality, lower mean latency, non-worse P95, and lower reported input tokens.
It is not a confidence interval, causal result, noninferiority proof or population claim.
Retain scenario coverage and balanced cold/warm repetitions; no real model savings may
be claimed from byte counters, synthetic usage fixtures or local CLI timings alone.

## Delegation and retrieval

`delegate` takes 1..4 units (id/effect and optional owner/independent/depends_on/estimated_ms),
optional host_parallel, spawn_ms, synthesis_ms, max_parallel (1..4), remaining_delegations
(0..24), required_verifier and token_budget/estimated_tokens. Default single or sequential.
Read-only fanout requires same owner, established independence, host support, available
budgets, known estimates and expected parallel time at most 90% of serial time. That 10%
margin is a conservative policy, not an experimentally established optimal threshold.

No writer or verifier runs in parallel on the same phase. This helper is advisory; it
cannot invoke agents, approve topology, bypass required verification, or create a second
workflow owner. Missing estimates favor the simpler path. Preserve native model/effort
selection when a host does not expose controls; never silently downgrade required rigor.

`retrieval` takes has_exact_refs, relationship_question, repeated_query, graph_available
booleans. Exact references win; bounded text/symbol search is the fallback. Budgeted graph
retrieval is optional for repeated relationship questions, never a full-graph default.
