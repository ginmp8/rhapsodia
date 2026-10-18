# Causal-Flow Investigation (Read-Only Reasoning)

**Purpose:** Test the mechanistic completeness of an existing source or behavior trace without claiming execution evidence that the corpus cannot provide.
**Load when:** Asked how/why a behavior arises, whether a state is reachable, whether a guard can be bypassed, or whether a component/feature trace describes every relevant alternative.
**Decision impact:** Require a bounded path/state hypothesis, evidence-specific classification, explicit counterpaths, and a scoped verdict; preserve the six Reverse Engineering modes and all authorization gates.

## Inputs and scope

- Form one answerable question with entry state, target state/effect, execution boundary, version/revision and inspected artifact identity.
- Use existing Discover/Investigate for static evidence, Characterize for trusted observations, Verify for finite original/candidate comparisons, or Diagnose for actual differential mismatches. This playbook is **not** a seventh mode.
- Name included parsers, sources, route registrations, configuration and skipped/unknown constructs. A lexical call or inferred receiver is a candidate, not a definite call; source matches cannot establish complete runtime coverage.

## Build the mechanism model

Trace `input/event -> guard/authorization/config -> call/state transition -> write/publish/return -> downstream effect`. For each material edge record:

| Field | Required distinction |
|---|---|
| Edge and precondition | What must hold for it to be taken, including feature flags / runtime dispatch |
| Source evidence | Exact artifact path/member/offset/symbol, revision and parser/tool identity |
| Evidence class | `declared`, `lexical_candidate`, `decoded_call_site`, `claimed_semantic_resolution`, `runtime_observed`, `inferred`, `unknown` |
| Assertion | What the evidence supports; do not confuse declared registration with observed activation |
| Closure | Which competing writers/callers/events were checked and which remain unexplored |

Prefer a compact branch/state table to a long list of components. Explain missing intermediate steps rather than bridging them with invented calls. Preserve static/runtime/proxy/reflection/distributed boundaries.

## Challenge the explanation

1. Generate at least one concrete **counterpath** when material: another endpoint/handler, configuration branch, asynchronous consumer, retry/duplicate, alternate state writer, partial failure, or concurrency ordering.
2. State an observation that would distinguish the proposed path from its alternative (e.g. source guard, executed trace under controlled input, existing finite test); do not assert the counterpath exists without evidence.
3. Search only within the authorized bounded corpus and permitted read-only capabilities. Do not execute unknown targets or infer external effects from a static source graph.
4. For `always/never/no other path/all writers`, require an explicit closed-world justification: enumerated entrypoints, writers, dynamic hooks, configuration variants and recognized parser coverage. Otherwise conclude `not established within available evidence`.
5. Separate `static possible`, `observed finite execution`, `unconfirmed plausible`, and `unknown`. An example trace cannot prove a universal safety invariant; negative test results cannot exhaust undiscovered paths.

## Output

Start with the scoped answer; follow with (1) mechanism and guard chain, (2) strongest evidence for each consequential edge, (3) supported alternatives/possible counterexamples, (4) missing evidence and a falsifying next check, (5) exact execution/permission limitations. If tools cannot validate an edge, use a bounded partial answer rather than fabrication.

## Research transfer boundary

Cognitive research on explanatory-depth illusions (Rozenblit & Keil, 2002, https://doi.org/10.1207/s15516709cog2605_1) supports skepticism about familiarity-based understanding. Sillito et al. (2008, https://doi.org/10.1109/TSE.2008.26) examined developer questions during change tasks. The mechanistic challenge above is an **engineering design inference**, not an experimentally proven improvement in reverse-engineering-agent accuracy. Treat evaluation on representative repository tasks as a separate obligation.
