# Reproducibility Contract

## Variability map

Treat material variance by class:

| Surface | Variance | Preferred control |
|---|---|---|
| IDs, schema, references, coverage metrics | mechanical | script/schema |
| mode defaults, ordering, tie-breaks | constrained heuristic | explicit ordered rules |
| finding relevance, derivation, semantic satisfaction | model judgment | evidence + rubric + independent review |
| web/source/runtime changes | external nondeterminism | pin/snapshot/version/record identity |

Prefer the lowest reliable control layer. Do not compile legitimate semantic judgment into fake deterministic rules.

## Evidence identities

Keep research, target baseline, evaluator set, candidate, package, and receipt identities separate.

When exact external file/repository bytes determine a decision, preserve the exact source bytes in a source snapshot before analysis:
- snapshot before analysis;
- analyze the snapshot rather than a moving source;
- verify the snapshot before final acceptance.

When web evidence is material but cannot be byte-snapshotted, preserve the research artifact that contains the cited claim and record source freshness/version metadata.

## Baseline vs candidate evidence

For `improve` and `refresh`, use paired baseline vs candidate execution when claiming behavioral improvement. Keep prompts, files, evaluator logic, expected outcomes, and material runtime identity equivalent across arms. Static validation can prove repair closure or structural hardening, but not measured behavioral improvement.

## Evaluator freeze

Derive evaluations from requirements before candidate mutation when feasible. Freeze evaluator assets by hash. Do not change expected outcomes after seeing candidate failure without explicitly invalidating and re-baselining the comparison.

## Repair discipline

Repair one causal issue at a time. Rerun the narrowest failing gate first. Stop a repair branch after two non-improving rounds unless new evidence changes the hypothesis.

Do not weaken a gate, delete semantic content, hide unsupported findings, or change the oracle to force green.

## Final freeze

A passing candidate is immutable. Any later edit invalidates affected validation evidence.

## Delivery integrity

For packaging:
- canonicalize output and receipt paths before writes;
- reject paths inside the target and package/receipt aliases;
- stage the archive privately;
- validate the staged archive;
- compute SHA-256 identities;
- atomically commit package and receipt;
- emit a durable receipt; make it stage-aware and include receipt version, commit stage, source-tree hash, package hash, and recovery state;
- preserve the previous output if commit fails;
- retain recovery paths if rollback is incomplete.

## Evidence layers

Report separately:
- structural evidence;
- semantic-review evidence;
- behavioral/scenario evidence;
- runtime evidence;
- package/integrity evidence.

A pass in one layer never implies another.

## Conditional advanced evidence profiles

Do not add advanced reproducibility machinery by default. Mark these profiles `not-applicable` unless the claim actually depends on them:

- **Environment/provenance profile:** require when provider, model, tool versions, dependencies, cache, locale, time, or concurrency can materially affect a paired comparison.
- **Stochastic evaluation profile:** require repeated trials only for strong reliability or improvement claims about stochastic model/agent behavior.
- **Execution-lineage profile:** require when a multi-stage replay/invalidation claim depends on plan identity, node dependencies, and canonical outputs. Ordinary traceability edges alone do not require a full execution-lineage system.

Skipping an irrelevant profile is preferable to ornamental complexity.
