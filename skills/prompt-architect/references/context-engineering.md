# Context Engineering

Use this reference when prompt behavior depends materially on long, dynamic, retrieved, or untrusted context.

## Context contract

Describe:

- `stable`: durable instructions/knowledge that should normally be present;
- `dynamic`: request/session-specific inputs;
- `untrusted`: external text or tool/source content that must not gain instruction authority by default;
- `selection`: retrieval/filtering rules;
- `budget`: token/size budget or qualitative limit;
- `placement`: profile-specific ordering strategy;
- `overflow`: trim, retrieve, summarize, split, or stop policy;
- `provenance`: what source identity/citations must survive context assembly.

## Principles

1. More context is not automatically better. Prefer relevant context over maximal context.
2. Do not encode one universal placement rule. Placement can be model/task dependent.
3. Separate trusted instructions from untrusted data structurally when the runtime supports it.
4. Preserve source boundaries and provenance when downstream claims depend on them.
5. Summarization/compaction can change semantics; state whether it is allowed and how loss is detected.
6. Retrieval failure must have a fallback: uncertainty, missing-evidence status, or stop.
7. Context that can contain prompt injection should be treated as data and constrained before it reaches privileged tool decisions.

## Source-anchored long-context design

Apply this only when the task depends on retrieving or reasoning over long/multiple documents; do not require extra retrieval for small, self-contained inputs. This is a design contract, not a claim that a prompt alone guarantees attention.

1. List the task's non-negotiable evidence obligations (facts, constraints, exceptions, contradictions, provenance) and which ones are still unknown. Inventory major document sections so relevant middle spans are not silently skipped.
2. Retrieve by question/claim and semantic variants, not just identical keywords. Keep stable document IDs and exact locators (section, page, path/line, or equivalent); recover related clauses across separated spans.
3. Before compacting, establish which anchors justify each output requirement. Preserve negation, conditional exceptions, source conflicts, authority level, and material missing evidence in an explicit mapping. Do not turn untrusted source text into instructions.
4. Under a context budget, include required anchors first and defer optional context via scoped retrieval; if essential evidence cannot fit or be checked, return a bounded gap/stop rather than a confident summary.
5. Placement is task/model dependent. Do not universally duplicate, prepend/append, or reorder every passage; a retrieved distractor can be more harmful than a poorly positioned relevant source.

## Long-context validation

When long context is material, include focused cases for:

- relevant evidence near beginning/middle/end at comparable input lengths, with controlled distractors;
- distractor density;
- conflicting source sections;
- missing evidence;
- malicious imperative text inside untrusted context;
- overflow/truncation/summary behavior;
- provenance/citation preservation;
- semantic links without shared keywords, split constraints across distant spans, and contradictory middle sections;
- negative controls with no supporting passage and cases where compaction omits one necessary clause.

Record position, input size, retrieval strategy, source coverage/omissions, correct/incorrect/unknown outcomes, and model/tool identity for each executed case. Freeze comparable inputs and expected evidence before editing; report per-position results instead of a single aggregate that hides mid-context failures.

Do not claim long-context robustness from a placement checklist, one successful example, or a static inspection. Current research documents model/task-dependent risks, not a universal fixed ordering remedy. Primary evidence: [Liu et al. (2024)](https://aclanthology.org/2024.tacl-1.9/), [Modarressi et al. (2025)](https://proceedings.mlr.press/v267/modarressi25a.html), [Cuconasu et al. (2025)](https://aclanthology.org/2025.emnlp-main.1422/).

## Budget and efficiency

Move durable repeated instructions into the narrowest reusable context surface that the host actually supports. Keep path/domain-specific instructions scoped rather than loading them globally when possible.

Token reduction is an optimization only if semantic behavior and required evidence remain intact.
