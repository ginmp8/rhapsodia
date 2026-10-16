# Shared-memory purpose: bounded research and design decisions

Reviewed 2026-10-16. This note records selected primary-document observations, not a fresh
benchmark or an audit of the external implementations. The upstream pages are mutable;
section locators and the access date identify what was reviewed. This note's content hash
pins our curated corpus, not an upstream commit or the entirety of any website.

## Source observations

| ID | Primary source and locator | Bounded observation |
|---|---|---|
| S-001 | [Graphify](https://github.com/Graphify-Labs/graphify), README: introductory model, See it in action, What it does | Its graph links code and other project artifacts, distinguishes extracted/inferred relations and retains source references, reducing repeated navigation through individual files. |
| S-002 | [Cartograph](https://github.com/onixhdz/cartograph), README: Quick Start | Symbol context includes callers, callees and relationships; impact queries and separate text/meaning retrieval motivate locating relevant structure before making blind changes. |
| S-003 | [Trail-Code](https://github.com/trailhq/Trail-Code), README: How it works, Part 1: The graft map, Part 2: Learnings | Distinguishes source-derived code maps from decisions and experience retained across sessions. Content-hash freshness and incremental refresh support reuse without treating old summaries as current source. The former trailhq/Graft URL redirects here. |
| S-004 | [AEndrix03/Graft concepts](https://github.com/AEndrix03/Graft/blob/master/docs/concepts.md), Memory node, Profile, Semantic cache | Focused titles, explanatory context, isolated scopes and stale/superseded states support selective retrieval of prior learning rather than indiscriminate context. This is a separate project from Trail-Code. |

These are authors' descriptions of intent and mechanics. They do not establish independent
performance, completeness or host reliability. No external code, prompts or algorithms are
incorporated here. Rhapsodia's permission, privacy, scope and source-authority rules prevail.

## Findings and dispositions

| Finding | Disposition | Rhapsodia application |
|---|---|---|
| F-001: Source maps reduce repeated navigation (S-001/S-002) | Implement | Explain graph-first compact context and exact-source follow-through, not blind replacement of source reads. |
| F-002: Structural maps and accumulated experience solve different problems (S-003) | Implement | Separate definitions/dependencies from decisions, remedies and failed attempts; keep environment locations in Harness. |
| F-003: Specific retrievable notes are more useful than undifferentiated transcripts (S-004) | Implement | One reusable question per stable record, source/evidence status, applicability, deduplication and explicit no-new-learning outcomes. |
| F-004: Mutable source and environment evidence requires freshness handling (S-001/S-003/S-004) | Implement | Reuse unchanged lookups; refresh affected scope, preserve history and learned experience that cannot be reconstructed from code. |
| F-005: Some upstream integrations use hooks or additional services (S-001/S-003) | Not applicable | Do not silently add dependencies, watchers, hooks, provider calls or external orchestration to clarify this release's instructions. |
| F-006: Upstream efficiency/accuracy numbers might transfer (S-001/S-003) | Uncertain | Exclude borrowed percentages. Measure actual useful reuse and quality; no Rhapsodia speedup or token claim follows from these descriptions. |

Mandatory bootstrap, explicit independent current-user opt-outs, private-maintenance scope,
no credentials, source/live authority and independent proof are requirements of this release's
accepted brief and existing contracts, not permissions inferred from external projects.

## Implementation and evaluation

Every agent's first-load block explains purpose, selective retrieval, cumulative learning and
quality-preserving completion. Runtime/graph skill roots and managed host guidance use the same
principles. The direct learning guide maps these principles to existing CLI records only.

Additive static mutation tests reject missing purpose, source authority, no-new-learning policy
or quantity-based success. Existing CLI suites cover warm/cold state, opt-outs, freshness,
privacy and concurrency. Planned model scenarios are labeled `planned`; static checks are not
proof that a model understood the purpose or that an editor enforced it. Native model sessions
and comparative token/latency benchmarks are not run in this clarification.

The [graph-skill trace](shared-memory-purpose-traceability.json) links this bounded corpus to
its owning skill's requirements, changes and evaluations. Cross-agent consumers remain under
the agent contract rather than becoming new responsibilities of Local Graph Engine.
