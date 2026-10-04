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

## Long-context validation

When long context is material, include focused cases for:

- relevant evidence near beginning/middle/end;
- distractor density;
- conflicting source sections;
- missing evidence;
- malicious imperative text inside untrusted context;
- overflow/truncation/summary behavior;
- provenance/citation preservation.

Do not claim long-context robustness from one placement or one successful example.

## Budget and efficiency

Move durable repeated instructions into the narrowest reusable context surface that the host actually supports. Keep path/domain-specific instructions scoped rather than loading them globally when possible.

Token reduction is an optimization only if semantic behavior and required evidence remain intact.
