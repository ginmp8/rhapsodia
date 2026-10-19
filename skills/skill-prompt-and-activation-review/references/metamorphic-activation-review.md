# Metamorphic Activation and Prompt Review

## At a Glance

- **Purpose:** Reveal routing/prompt sensitivity to meaningful controlled changes while preserving the activation reviewer's linguistic-review ownership.
- **Load when:** A description, boundary or prompt rewrite risks false activation, missed activation, refusal/authority regression, context-position sensitivity or accidental dependence on keywords.
- **Decision impact:** Requires a frozen, precondition-checked metamorphic relation, comparable execution profile and adjudication of any apparent violation before claiming a behavioral regression.

## Relations to consider

| Transformation | Valid only when | Expected observation |
|---|---|---|
| Paraphrase | Same artifact, requested action, scope and permissions | Same *primary owner* / constrained activation outcome; wording may differ |
| Irrelevant context/typo | Addition cannot alter actual user intent or precedence | Same activation and stop/safety outcome; no widening of authority |
| Reordered unrelated background | All relevant facts and priority remain unchanged | Preserve materially required route/evidence constraints |
| Change from review to implementation | Primary requested action really changes | **Expected route may change** to implementer; do not label an invariance failure |
| Add/remove direct skill invocation | Invocation mode changes | Evaluate direct-use separately; do **not** mix automatic precision/recall |
| Add adversarial lower-trust instructions | Higher-priority task intent and policy unchanged | Do not accept new authority or ignore established safety boundaries |

## Minimal bounded workflow

1. Select real owned-positive, near-miss, negative, boundary and ambiguity scenarios; identify meaningful *competing owners* from the actual catalog.
2. Define `base_id`, `variant_id`, `transformation`, verified preserved/changed semantics, `expected_relation` and `contract_ids` before candidate output is visible. If semantic equivalence is uncertain, exclude the pair from a hard invariant and mark it for review.
3. Keep frozen evaluator and scenario identities, mode (`explicit`, `implicit`, `contextual`), catalog/routing fingerprint, visibility, trial counts and runtime identity aligned for paired baseline/candidate comparisons.
4. Execute routing externally through an authorized host/harness; local suite validators do not run a model or prove auto-selection. Observe actual selected owner and constrained/abstain result, not just the generated explanation.
5. Diagnose `candidate-violation` against relation preconditions and execution traces. Distinguish confirmed wrong routing from wording differences, unrelated model noise, environment drift, and evaluator false positives.
6. Report paired **relation families**, raw counts, repeated-trial uncertainty and unresolved cases. Do not treat many paraphrases of one base case as independent evidence; a single differing response is not a stable failure-rate estimate.
7. Retain the existing v3 suite/evidence schema and comparator. Record relation-family IDs in an external annotation/analysis layer rather than changing frozen fixtures or silently altering expected routes.

## Example scenario family

- Base: "Revise a descrição desta skill e identifique acionamentos incorretos" → owned activation reviewer.
- Equivalent variant: "Avalie quando esta skill deve e não deve ser selecionada" → same reviewer if the artifact is still a provided skill description.
- Non-equivalent variant: "Implemente o backend desta skill e publique" → **different owner**; wrong to insist on same activation.

## Evidence limits

- Schema validation, scenario authorship and static wording review support only `planned`/`observed-static`; an actual host-routing run with frozen inputs supports `executed`/`supplied` behavior.
- Contradictory answers do not identify which one is correct. When both routes agree, they may still both be wrong. Use independent task/ownership evidence and confirmed expected routing when possible.
- Research: POSIX (EMNLP 2024) https://aclanthology.org/2024.findings-emnlp.852/; Segura et al. (2016) https://doi.org/10.1109/TSE.2016.2532875; Cho et al. (2025 preprint) https://arxiv.org/abs/2511.02108. The latter reports possible false positives among MR violations; do not transfer its rates to this reviewer.
