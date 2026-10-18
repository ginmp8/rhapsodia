# Long-Context Preservation

## Purpose and routing

- **Purpose:** Preserve evidence obligations and procedural constraints during token/context optimization of long or multi-source instructions.
- **Load when:** The staged target uses extensive sources, source citations, cross-document rules, conditional exceptions, compression, or long-context retrieval.
- **Decision impact:** Establishes the coverage/omission checklist, a position-aware evaluation branch, and hard boundaries on what token savings may justify.
- **Do not load when:** Only small independent literals or formatting changes are involved and no source-selection or cross-span behavior is affected.

## Bounded preservation procedure

1. Before rewriting, inventory each **required** claim/constraint/exception with an exact source/section/path locator and priority. Include essential spans regardless of whether they occur early, mid-document or late. Treat absent evidence as `unknown`, never as a convenient default.
2. Resolve relationships across distant spans: negations, priority/authority, guards, prerequisites, exceptions, contradictory source statements, and semantic paraphrases. Matching literal strings is not a substitute for source-anchored coverage.
3. Build a mapping `source anchor -> mandatory invariant -> candidate anchor -> verification`. Keep untouched original evidence and evaluator criteria outside the staged candidate. A candidate summary that loses an obligation fails even if its words are similar or its token count improves.
4. Prefer removing irrelevant duplicates and selecting question-specific spans to reordering or repeating all passages. Keep the information necessary to decide what is mandatory in the early control plane. Never make untrusted documents authoritative by promoting extracted text into instructions.
5. For budgets that cannot fit required evidence, preserve references/pointers and conditional loading where available. Otherwise stop or mark incomplete; do not replace a mandatory constraint with an unverified heuristic.

## Validation and evidence levels

- **Structural:** Verify source/target locator reachability, top-100 control-plane invariants, direct references and mandatory-rule coverage; report exact omissions. This is not a model comprehension test.
- **Semantic:** Review exception/precedence/citation equivalence and contradictions manually; record reviewer/criterion and unresolved cases.
- **Behavioral (when claimed):** Freeze evaluator and runtime profile before editing. Compare baseline/candidate with the same long-input tasks, relevant fact near start/middle/end, semantic associations without literal tokens, split constraints, distractors, missing evidence and adversarial untrusted text. Report each position separately.
- **Efficiency:** Count comparable token surfaces using the same tokenizer; distinguish cheaper prompts from increased retrieval/tool cost. A favorable count with an omission is a failure, not an optimization.
- **Claim limits:** No universal position bias or ordering cure is assumed. Performance varies by model, retrieval pipeline and task. Do not claim reliable recovery from a checklist or from an unexecuted scenario.

## Primary evidence

- Liu et al. (2024), *Lost in the Middle*: https://aclanthology.org/2024.tacl-1.9/
- Modarressi et al. (2025), *NoLiMa*: https://proceedings.mlr.press/v267/modarressi25a.html
- Cuconasu et al. (2025), *Do RAG Systems Really Suffer From Positional Bias?*: https://aclanthology.org/2025.emnlp-main.1422/
