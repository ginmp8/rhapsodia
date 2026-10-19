# Metamorphic Variance in Agent Skills

## At a Glance

- **Purpose:** Diagnose controllable semantic variance with related-input tests when no single deterministic model output exists.
- **Load when:** A target skill varies under paraphrase, irrelevant detail, input location, tool-result order, or otherwise equivalent contexts; or when cross-agent consistency is an explicit optimization goal.
- **Decision impact:** Separates valid invariance from intended behavior changes, requires frozen evidence and repeated trials for reliability claims, and prevents false deterministic promises.

## When this is the right probe

This skill owns **reducing controllable variance** for exactly one existing skill, not MT harness construction. Use existing `skill-harness` when scenario execution infrastructure is required. Use `skill-benchmark` when the goal is solely a score/report. Do not add scripts/dependencies to the target simply to standardize subjective prose.

## Procedure

1. State the target's reproducibility ceiling (objective-artifact/tool-action/research-analytic/constrained-subjective) and the observable semantic contract: allowed actions, required gates, authority, source/evidence identity, output obligations, stops, and relevant user intent.
2. Freeze evaluation assets before changing the skill. Define each family as `(base input, transformed input, precondition, expected relation, outcome oracle, evaluator identity, model/host/runtime/corpus identity, trial budget)`.
3. Separate **invariance** (paraphrase preserving intent, genuinely irrelevant noise, moved-but-not-changed evidence) from **expected change** (negation, altered authorization, new task scope or resource availability). Do not require a constant answer across the second class.
4. Run both before/after arms using comparable material environments. Track exact runs, abstentions, inconsistent routes, changed evidence requirements, constraint losses, and stop-condition breaches; do not penalize surface wording variations.
5. If a relation fails, first challenge its premise and evaluator. A semantic difference in the input may legitimately change output. Classify `candidate-violation`, `confirmed-defect`, `inconclusive`, or `invalid-relation`; confirm defects with independent oracles/reviews when needed.
6. Group correlated variants by base case and MR; use replication and uncertainty for stochastic reliability claims. One observation can expose a bug but cannot establish an overall failure probability.
7. Apply a targeted control at the lowest reliable layer without expanding skill scope. Rerun original tests, adjacent negative/boundary scenarios, and previously frozen relation families. Keep unaffected baseline/holdout bytes immutable.

## Examples of semantic relations

- Rephrase "inspecione a skill sem alterar arquivos" → authority remains read-only; output format may vary.
- Move a mandatory safety rule from the middle to the end without removing it → a correct response must continue respecting the rule **if** the context is fully supplied and precedence unaltered. Failure may reveal retrieval instability, not why it occurred.
- Change "auditar" to "implementar" → expected tool/owner behavior **changes**; not a valid invariance pair.
- Change host from Cursor to a platform without code execution → the honest result becomes `not-run/blocked`; claiming identical execution would be wrong.

## Evidence and limitations

Do not present static schema checks as observed behavioral variance reduction or guarantee bitwise determinism from an LLM. Pin model/provider/host/tool/config/environment versions for causal comparisons; when these change, rebase or report `not-comparable`. Mask protected evaluator-only cases from the authoring agent; candidate-visible scenarios are not blind holdouts.

Research: Segura et al. (2016) https://doi.org/10.1109/TSE.2016.2532875; Chatterjee et al. (2024) https://aclanthology.org/2024.findings-emnlp.852/; Cho et al. (2025, preprint) https://arxiv.org/abs/2511.02108. Metamorphic failures may include oracle false positives, so adjudication is necessary.
