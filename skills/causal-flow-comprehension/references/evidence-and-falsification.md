# Evidence and Falsification

## At a Glance
- **Purpose:** Bound truth claims in flow explanations and distinguish verification from persuasive narratives.
- **Load when:** Source signals conflict, a negative or exhaustive claim is requested, tests/trace are available, or a source-backed assertion affects decisions.
- **Decision impact:** Controls admissible evidence, scoped universality, counterexample quality, failure disposition and reproducibility limits.

## Claim classes and required support

| Status | Admissible basis | Required qualification |
|---|---|---|
| `static-observed` | Exact code/config/test-definition locator and revision | Describes what source defines, *not* proof of runtime execution |
| `runtime-observed` | Executed test log or trace, environment/input and revision | Only establishes observed conditions; log presence is not complete tracing |
| `inferred` | Explicit cited premises and inference boundary | Could be overturned by unseen route/config/runtime |
| `hypothesis` | Plausible, falsifiable mechanism | Name competing explanation and discriminating check |
| `unknown` | Missing/unavailable/conflicted input | Name smallest source, permission, or experiment to resolve |

Do not promote an inference into an observation because it is plausible. Don't assign numeric confidence without a calibrated, task-appropriate empirical model. Keep what a user says the system does separate from source facts: a user report is evidence of a report, not automatic evidence of execution.

## Provenance and invalidation

Every nontrivial assertion links to a bounded locator such as `path/to/file.cs:120-141 @ commit`, `config:key @ revision`, `trace-id @ timestamp/environment`, or `test-name @ executed build`. If line markers unavailable, use a stable symbol plus version and mark precision. Capture actual revision/branch and working-tree condition if available; a file path without snapshot identity may become stale. Keep evidence source IDs and claim IDs separate. Avoid reading or publishing secrets; mask values but preserve control semantics.

When a source revision, runtime configuration, binding, or test environment changes, invalidate only affected claims and dependent transitions. If exact evidence snapshot is unavailable, say provenance is best effort. Persist evidence in an authorized destination only; read-only analysis by default.

## Challenge before acceptance

1. Restate the proposed mechanism in one falsifiable sentence (what action, preconditions and effects?).
2. Generate a distinct alternative explanation that would predict a different result under a specific condition, not merely a paraphrase.
3. Seek a counterpath: bypassed guard, alternate writer/entrypoint, feature flag, polymorphic dispatch, duplicate/out-of-order event, partial failure, race or external state mutation, **only where relevant**.
4. Choose a discriminating check: source traversal, targeted existing test, trace replay, config comparison or controlled experiment with explicit safety/permission boundaries.
5. Record result: `supported-within-scope`, `contradicted`, `insufficient-evidence` or `not-run`; update only conclusions justified by the outcome.

## Universal and negative claims

"Never", "always", "no possible path" and "the only writer" demand a closed-world model: finite source/version/runtime boundary, a complete enumeration of relevant dispatch/writers and substantiated assumptions about dynamic/external behavior. Absent that, report `not established within inspected scope`. A failed text search is never proof of absence. Static analysis may overapproximate; testing finite inputs cannot prove an unbounded negative. State the proof obligation that remains.

## Evidence layering

- **Static:** grounded at-source structure, not complete behavioral proof.
- **Behavioral:** concrete executions under recorded setup, not a universal guarantee.
- **Semantic review:** checks whether citations, inference steps and counterexamples are meaningful; mechanical validators cannot establish source truth.
- **Host/runtime:** tool availability and environment can change what can be checked; label `not-run` when absent.

Do not convert a valid JSON schema, polished prose, passing documentation lint, or successful illustrative fixture into proof of target-system runtime behavior.
