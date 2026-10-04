# Research Grounding

Use this reference only when identified evidence is materially insufficient, the user explicitly supplies/requests research, or `evidence-gap-review` needs to prioritize evidence collection. Research is an evidence-acquisition capability, not a mandatory dependency.

## Research policy

Resolve one policy before external acquisition:

- `never` — do not use external research; unresolved material gaps remain `evidence-gap` / `gather-evidence`.
- `if-needed` — default when a material source-resolvable gap blocks a causal/measurable hypothesis and research capability is available.
- `required` — use when the caller explicitly requires research before discovery; do not proceed to a research-backed handoff unless the bounded research phase completes.

`deep-discovery` is a discovery-depth mode, not a synonym for deep research. It means broader candidate generation followed by adversarial critique, counterexample search, consolidation, and deterministic final ranking. It must work serially; optional parallel/multi-agent execution may accelerate independent research or critique but cannot change semantics, evaluator identity, caps, or tie-breaks.

## Evidence sufficiency gate

Before freezing the normal v2 evidence snapshot, ask whether the missing information is material and source-resolvable.

Use local/package/repository evidence first for facts about the target. External research is appropriate for domain methods, current standards, external behavior, literature, best practices, or disputed/uncertain causal claims. Do not browse merely to restate facts already established by stronger local evidence.

If research is needed:

1. formulate bounded research questions tied to a specific evidence gap;
2. search primary/official sources first and add independent evidence when trade-offs or operational experience matter;
3. deliberately search for contradicting evidence and alternative explanations, not only support;
4. preserve version/date/jurisdiction qualifiers when they change meaning;
5. stop when additional searches no longer change a material finding or close a required field;
6. freeze the research corpus or the research artifact that interprets live sources before using it to justify a hypothesis.

If research cannot run, return a truthful evidence gap. Network availability is never a correctness prerequisite for the portable core.

## Source -> finding -> hypothesis

Do not feed raw citations directly into mutation ideas. Normalize one atomic finding per independently actionable claim:

`source -> finding -> discovery evidence -> hypothesis`

When an existing Research Traceability workspace is supplied, reuse its stable `S-*` / `F-*` identities and corpus identity instead of re-extracting the same research. This is interoperability, not a runtime dependency: another host may supply equivalent source/finding records directly.

Keep research completeness `corpus-bounded`. A validated trace proves that recorded findings were accounted for, not that all knowledge on the web was discovered.

## Discovery vs validation evidence

Research that inspired a hypothesis is discovery evidence. Evidence used to accept/reject the resulting candidate is validation evidence. Keep those roles explicit:

- `discovery` — may support the causal mechanism;
- `contextual` — may constrain scope or interpretation;
- `validation` — must not be reused as discovery support for the same research-backed hypothesis;
- `regression-gate` — protects already-proven behavior; it is not causal discovery evidence.

Do not present a post-result explanation as if it were an a-priori hypothesis. If candidate-aware evidence materially changes the mechanism, re-baseline and create a new discovery snapshot/hypothesis identity.

## Falsification contract

Before a research-backed hypothesis proceeds to the existing v2 handoff, record:

- supporting finding refs;
- counterevidence finding refs, which may be empty only after an explicit bounded search;
- credible alternative explanations, or an explicit statement that none were found after the bounded search;
- at least one falsification criterion: an observation that would weaken/reject the mechanism;
- a concise search summary describing the negative test/counterevidence attempt;
- a stable evaluator identity with exposure `held-out` or `independent`.

A shared/unknown deciding evaluator or `falsification.status != attempted` blocks research-backed v2 handoff. Do not weaken this rule to make a candidate testable.

## Research-discovery artifact

Use `assets/templates/research-discovery.json.template` and validate it with:

```text
<PYTHON> scripts/validate_research_discovery.py --input <RESEARCH.json> --json-output <RESULT.json>
```

The helper is standard-library-only. It deterministically:

- derives `research_corpus.corpus_id` from canonical source/finding records;
- checks source/finding referential integrity;
- checks evidence-role separation and rejects validation/regression leakage into discovery support;
- checks falsification and evaluator independence for research-backed handoff;
- ranks open evidence gaps.

After this artifact passes, translate only the supported hypotheses into the existing canonical `skill-opt.hypothesis-pool` v2 and validate that v2 backlog with `validate_hypothesis_backlog.py`. The research artifact enriches discovery; it does not replace or silently change the peer-facing v2 contract.

## Evidence-gap priority

For open gaps with 1..5 integer ratings:

```text
priority = information_value - ceil(collection_cost / 2)
```

Tie-break in this order:

1. higher priority;
2. higher information value;
3. lower collection cost;
4. lexical gap id.

`information_value` estimates how much resolving the gap could change eligibility, mechanism, evaluator, safety, or experiment choice. It is a bounded decision heuristic, not a Bayesian posterior or measured effect size.

## Anti-bias and anti-overfitting rules

Reject:

- research queries framed only to confirm a favored mutation;
- cherry-picked sources while credible conflicting evidence is hidden;
- candidate-aware validation evidence relabeled as discovery evidence;
- evaluator/holdout changes after seeing candidate results without explicit invalidation and re-baselining;
- novelty as a generic skill-improvement objective;
- mandatory multi-agent or vendor-specific research machinery when serial/capability-based execution is sufficient.
