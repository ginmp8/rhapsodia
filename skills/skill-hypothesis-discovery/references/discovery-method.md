# Discovery Method

Generate hypotheses from frozen evidence, not from open-ended mutation search.

## Deterministic discovery pipeline

Use this order:

`resolve target -> establish baseline identity -> snapshot evidence -> classify signals -> classify backlog item kind -> apply minimum-evidence gate -> dedupe -> declare conflicts/dependencies -> score -> deterministic rank -> bounded selection -> stop/handoff`

The same target identity, evidence snapshot, mode, and constraints should produce a materially equivalent backlog. Exact wording can vary where semantic interpretation is irreducible; item class, evidence linkage, eligibility, priority inputs, ordering, and selection should not vary without a material reason.

## 1. Resolve baseline identity

Record the target name and the strongest available stable identity before discovery:

1. immutable package/repository revision or content hash;
2. explicit version plus hash/manifest;
3. supplied artifact identity;
4. `unverified:<label>` only when exact identity cannot be obtained.

Do not mix findings from different target versions into one backlog unless the comparison itself is the evidence and each version is identified separately.

## 2. Snapshot evidence

Create stable evidence ids (`E001`, `E002`, ...) and record source identity, evidence status, and a concise claim. Prefer exact hashes/revisions when available. Sort evidence sources by id in machine-readable output; the v2 validator derives the snapshot digest from this set.

Evidence statuses:

- `measured` — executed evaluator/command/scenario result;
- `observed` — direct inspection of file/output;
- `derived` — deterministic calculation from evidence;
- `supplied` — result supplied by the user/caller but not independently rerun;
- `planned` — intended but not executed;
- `gap` — explicitly missing evidence;
- `unknown` — provenance/status cannot be established.

Never relabel `planned`, `gap`, or `unknown` as stronger evidence.

## 3. Classify signals

Classify evidence by area before creating any candidate:

- `activation`: trigger/non-trigger failures or boundary gaps;
- `ambiguity`: unclear routing, overlap, or ask/proceed/handoff rules;
- `output`: unstable output contract or evidence labels;
- `architecture`: control-plane/resource/progressive-loading issues;
- `consistency`: contradictions across package resources;
- `documentation`: stale or unclear human guidance;
- `validation`: missing/failed validators, gates, or regression checks;
- `security`: authority, unsafe mutation, secret/logging, or blocked-path issues;
- `packaging`: package scope, generated residue, symlink, archive, or identity issues;
- `token`: repeated or unnecessarily loaded instructions;
- `behavioral`: executed scenario failures, missing holdouts, or stochastic variance;
- `evidence`: provenance gaps, evaluator absence, or saturated metrics.

## 4. Classify the backlog item before ranking

Use the taxonomy from `hypothesis-schema.md`:

- `testable-hypothesis` only when the evidence and measurement path satisfy the minimum gate;
- `evidence-gap` when more evidence/evaluator/metric is needed;
- `recommendation` when the useful output is guidance rather than an experiment;
- `unsupported-speculation` when the idea lacks evidence or a measurable causal path.

Do not promote an item merely because it sounds reasonable.

## 5. Generate the causal relation

Every testable hypothesis must make this chain explicit:

`hypothesis -> evidence_refs -> mechanism -> expected_effect -> evaluator -> acceptance_criteria`

If any link is missing, downgrade the item before ranking:

- missing evidence -> `evidence-gap` or `unsupported-speculation`;
- missing mechanism -> reject as unsupported speculation;
- missing measurable effect -> evidence gap or reject;
- missing evaluator -> `gather-evidence` / `defer`, never `test-now`;
- missing acceptance criteria -> not testable.

## 6. Deduplicate and resolve conflicts

Before scoring:

1. derive the canonical `dedupe_key` from bounded semantic keys;
2. merge exact duplicates into one item and union their evidence refs;
3. review semantic near-duplicates and keep only the broader or better-supported item when they test the same mechanism/effect;
4. declare `conflicts_with` for mutually exclusive changes;
5. declare `depends_on` for prerequisite evidence/changes;
6. never select conflicting items together.

If duplicate candidates have materially different evidence or acceptance criteria, consolidate them rather than arbitrarily choosing one.

## 7. Saturated metrics

If the primary metric is saturated:

1. keep it as a regression gate;
2. do not rank hypotheses by tiny/noisy changes in that metric;
3. identify an auxiliary non-saturated metric tied to an observed variance source (for example holdout failures, ambiguous activation, repair rounds, unsupported-claim count, token cost, runtime/package failures, or manual rework);
4. if no meaningful auxiliary metric exists, return `evidence-gap` or `no-mutation-recommended`.

## 8. Score and rank

Use the formula and tie-breakers in `hypothesis-schema.md`. Scores help order already-eligible candidates; they do not convert weak evidence into a valid hypothesis.

Blocking correctness/safety/validation/package issues are ranked before non-blocking opportunities through `gate_effect`, but still require evidence and an evaluator.

## 9. Bounded selection

Respect mode limits. Final output is intentionally small; broad ideation is an internal temporary step, not a deliverable.

For `backlog-discovery` or `deep-discovery`:

- final items must fit the mode cap;
- select at most three ready hypotheses;
- `next_hypothesis_id` identifies exactly one first experiment;
- `skill-improver` tests one bounded hypothesis at a time.

For `evidence-gap-review`, select no mutation hypothesis.

## 10. Stop conditions

Stop generation and return evidence collection or no mutation when:

- target identity cannot be established well enough to know what was analyzed;
- evidence cannot support a causal/measurable hypothesis;
- every candidate is duplicate, blocked, conflicted, or depends on unavailable evidence;
- the evaluator needed for the next experiment does not exist and cannot be defined independently;
- the only relevant primary metric is saturated and no useful auxiliary metric exists;
- expected effects are not observable enough to write acceptance criteria;
- the requested number of hypotheses exceeds the mode cap and additional items would only add weak variants;
- further candidates require random search or speculative rewrites.

## Anti-random-search rules

Reject:

- random renames, moves, or rewrites without evidence;
- generic "clean up/refactor" hypotheses with no causal mechanism;
- mutations whose evaluator would be authored only after seeing candidate results;
- changing fixtures, thresholds, weights, baselines, or evidence to make a hypothesis pass;
- deleting resources because their names imply they are obsolete without tracing consumers;
- token optimization before activation/safety/validation contracts are stable;
- broad multi-file rewrites when one bounded experiment answers the question;
- claims of measured improvement from planned, inferred, or static evidence.
