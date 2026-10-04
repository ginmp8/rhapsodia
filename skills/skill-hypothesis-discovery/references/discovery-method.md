# Discovery Method

Generate hypotheses from identified evidence, not open-ended mutation search. Acquire new external evidence only when a bounded source-resolvable gap materially blocks discovery and the active research policy allows it.

## Deterministic discovery pipeline

Use this order:

`resolve target -> establish baseline identity -> evidence-sufficiency gate -> optional bounded research -> freeze research artifact -> freeze discovery evidence -> classify signals -> classify backlog item kind -> causal/falsification gate -> dedupe -> conflicts/dependencies -> saturated-metric gate -> score -> deterministic rank -> bounded selection -> validate -> handoff`

The same target identity, frozen evidence/research identities, mode, research policy, and constraints should produce a materially equivalent backlog. Exact wording may vary where semantic judgment is irreducible; item class, evidence linkage, eligibility, priority inputs, ordering, and selection should not vary without a material reason.

## 1. Resolve baseline identity

Record the target name and strongest available stable identity:

1. immutable package/repository revision or content hash;
2. explicit version plus hash/manifest;
3. supplied artifact identity;
4. `unverified:<label>` only when exact identity cannot be obtained.

Do not mix findings from different target versions unless the comparison itself is evidence and each version is separately identified.

## 2. Evidence sufficiency and optional research

Before freezing the normal v2 evidence snapshot, classify the evidence state:

- `sufficient` — enough identified evidence exists to support or reject a causal/measurable hypothesis;
- `insufficient-source-resolvable` — a material question could be answered by bounded research;
- `insufficient-local` — target/repository/runtime evidence is missing and external research would not answer it;
- `unknown` — provenance or scope is too weak to decide.

Apply `research_policy`:

- `never`: do not acquire external evidence; unresolved material gaps remain `evidence-gap` / `gather-evidence`;
- `if-needed`: acquire bounded evidence only for `insufficient-source-resolvable` gaps when research capability exists;
- `required`: complete the bounded research phase before research-backed discovery; if unavailable/blocked, stop truthfully.

Load [research-grounding.md](research-grounding.md) only when this branch is active. Prefer local/package/repository evidence for facts about the target. External research is for external methods, literature, standards, current behavior, disputed claims, or domain knowledge that local inspection cannot establish.

Research must include deliberate contradiction/counterevidence search. Stop when additional searches no longer change a material finding or close a required field. Freeze the resulting research corpus/artifact before using it as discovery evidence.

## 3. Research trace and evidence roles

When research ran, normalize:

`source -> atomic finding -> evidence role -> hypothesis`

If a Research Traceability-compatible corpus already exists, preserve its source/finding identities instead of re-extracting the same material. Otherwise use the lightweight research artifact described in [research-grounding.md](research-grounding.md).

Keep roles separate:

- `discovery` — may support causal hypothesis generation;
- `contextual` — constrains scope/interpretation;
- `validation` — decides a candidate and must not be reused as discovery support for that same research-backed hypothesis;
- `regression-gate` — protects known behavior and is not causal discovery evidence.

Candidate-aware validation evidence may start a new hypothesis only after explicit re-baselining with a new evidence snapshot/hypothesis identity.

## 4. Snapshot discovery evidence

Create stable evidence ids (`E001`, `E002`, ...) and record source identity, evidence status, and concise claim. Prefer exact hashes/revisions when available. Sort evidence sources by id in machine-readable output; the v2 validator derives the snapshot digest from this set.

Evidence statuses:

- `measured` — executed evaluator/command/scenario result;
- `observed` — direct inspection of file/output;
- `derived` — deterministic calculation from evidence;
- `supplied` — user/caller result not independently rerun;
- `planned` — intended but not executed;
- `gap` — explicitly missing evidence;
- `unknown` — provenance/status cannot be established.

Never relabel `planned`, `gap`, or `unknown` as stronger evidence.

## 5. Classify signals

Classify evidence by area before creating candidates:

- `activation`: trigger/non-trigger failures or boundary gaps;
- `ambiguity`: unclear routing, overlap, or ask/proceed/handoff rules;
- `output`: unstable output contract or evidence labels;
- `architecture`: control-plane/resource/progressive-loading issues;
- `consistency`: contradictions across package resources;
- `documentation`: stale or unclear human guidance;
- `validation`: missing/failed validators, gates, holdout/evaluator independence, or regression checks;
- `security`: authority, unsafe mutation, secret/logging, or blocked-path issues;
- `packaging`: package scope, generated residue, symlink, archive, or identity issues;
- `token`: repeated or unnecessarily loaded instructions;
- `behavioral`: executed scenario failures, missing holdouts, or stochastic variance;
- `evidence`: provenance gaps, research gaps, evaluator absence, or saturated metrics.

## 6. Classify each backlog item before ranking

Use the taxonomy from [hypothesis-schema.md](hypothesis-schema.md):

- `testable-hypothesis` only when evidence and measurement path satisfy the minimum gate;
- `evidence-gap` when more evidence/evaluator/metric is needed;
- `recommendation` when useful output is guidance rather than an experiment;
- `unsupported-speculation` when the idea lacks evidence or measurable causal path.

Do not promote an item because it sounds plausible.

## 7. Causal and falsification gate

Every v2 testable hypothesis must make this chain explicit:

`hypothesis -> evidence_refs -> mechanism -> expected_effect -> evaluator -> acceptance_criteria`

If any link is missing, downgrade before ranking:

- missing evidence -> `evidence-gap` or `unsupported-speculation`;
- missing mechanism -> reject as unsupported speculation;
- missing measurable effect -> evidence gap or reject;
- missing evaluator -> `gather-evidence` / `defer`, never `test-now`;
- missing acceptance criteria -> not testable.

When external research materially informed the hypothesis, also require before v2 handoff:

`supporting findings -> counterevidence attempt -> alternative explanations -> falsification criteria -> independent/held-out evaluator identity`

Validate that stage with `validate_research_discovery.py`. A research-backed candidate with confirmation-only search, `falsification.status != attempted`, or evaluator exposure `shared|unknown` cannot proceed to the v2 handoff.

## 8. Deep-discovery semantics

`deep-discovery` broadens internal candidate consideration but does not change final caps. Use:

`generate -> adversarial critique -> counterexample search -> revise/consolidate -> dedupe -> deterministic rank`

Optional fan-out/multi-agent execution may parallelize independent generation, critique, or research when a host supports it. Serial execution is always valid and must produce the same semantic gates, caps, and ranking inputs. Do not make agent count, vendor API, or orchestration topology part of correctness.

## 9. Deduplicate and resolve conflicts

Before scoring:

1. derive canonical `dedupe_key` from bounded semantic keys;
2. merge exact duplicates and union evidence refs;
3. review semantic near-duplicates and keep only the broader/better-supported item when they test the same mechanism/effect;
4. declare symmetric `conflicts_with` for mutually exclusive changes;
5. declare `depends_on` for prerequisites;
6. never select conflicting items together.

If duplicates have materially different evidence or acceptance criteria, consolidate them rather than arbitrarily choosing one.

## 10. Saturated metrics

If the primary metric is saturated:

1. keep it as a regression gate;
2. do not rank hypotheses by tiny/noisy changes in that metric;
3. identify an active auxiliary metric tied to observed variance (for example holdout failures, ambiguous activation, repair rounds, unsupported-claim count, token cost, runtime/package failures, or manual rework);
4. if no useful auxiliary metric exists, return `evidence-gap` or `no-mutation-recommended`.

Do not use novelty as an auxiliary optimization metric merely to create room for change.

## 11. Evidence-gap priority

When research/evidence collection has multiple open gaps, use the bounded heuristic from [research-grounding.md](research-grounding.md):

`information_value - ceil(collection_cost / 2)`

Tie-break by higher information value, lower collection cost, then lexical id. This orders evidence collection only; it does not convert a gap into a testable mutation hypothesis.

## 12. Score and rank v2 hypotheses

Use the formula and tie-breakers in [hypothesis-schema.md](hypothesis-schema.md). Scores order already-eligible candidates; they do not convert weak evidence into a valid hypothesis.

Blocking correctness/safety/validation/package issues rank before non-blocking opportunities through `gate_effect`, but still require evidence and evaluator.

## 13. Bounded selection

Respect mode limits. Final output is intentionally small; broad ideation is temporary internal work.

For `backlog-discovery` or `deep-discovery`:

- final items fit the mode cap;
- select at most three ready hypotheses;
- `next_hypothesis_id` identifies exactly one first experiment;
- downstream improvement tests one bounded hypothesis at a time unless an inseparable dependency is explicitly recorded.

For `evidence-gap-review`, select no mutation hypothesis.

## 14. Validate and hand off

When research ran, validate the research artifact first:

```text
<PYTHON> scripts/validate_research_discovery.py --input <RESEARCH.json> --json-output <RESULT.json>
```

Then translate supported candidates into the existing v2 backlog and validate:

```text
<PYTHON> scripts/validate_hypothesis_backlog.py --input <BACKLOG.json> --json-output <RESULT.json>
```

The additive research artifact must not redefine the peer-facing `skill-opt.hypothesis-pool` v2 contract.

## Stop conditions

Stop and return evidence collection/no mutation when:

- target identity cannot be established well enough;
- required research cannot complete or source identity is too weak for a material claim;
- evidence cannot support a causal/measurable hypothesis;
- research-backed falsification cannot be attempted;
- the deciding evaluator cannot be frozen independently;
- every candidate is duplicate, blocked, conflicted, or depends on unavailable evidence;
- the only relevant primary metric is saturated and no useful auxiliary exists;
- expected effects are not observable enough for acceptance criteria;
- further candidates require random search, confirmation-only research, novelty chasing, or speculative rewrites.

## Anti-random-search and anti-overfitting rules

Reject:

- random renames, moves, or rewrites without evidence;
- generic "clean up/refactor" hypotheses with no causal mechanism;
- research queries framed only to support a favored mutation;
- hiding credible conflicting sources or alternative explanations;
- mutations whose evaluator would be authored only after seeing candidate results;
- changing fixtures, thresholds, weights, baselines, holdouts, or evidence to make a hypothesis pass;
- candidate-aware validation evidence relabeled as discovery evidence;
- deleting resources because their names imply obsolescence without tracing consumers;
- token optimization before activation/safety/validation contracts are stable;
- broad multi-file rewrites when one bounded experiment answers the question;
- novelty as a generic ranking bonus;
- claims of measured improvement from planned, inferred, or static evidence.
