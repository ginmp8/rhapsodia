# Reproducibility by Design

Use this reference while designing or materially updating a skill. This is a lightweight architecture pass owned by Skill Creator Juiced. It does **not** mean `reproducibility-engineer` must be invoked.

## Goal

Give each skill only the reproducibility controls justified by its failure modes. Preserve model judgment where judgment is useful; move objective, fragile, repetitive, or safety-critical behavior to lower-variance mechanisms.

Prefer the lowest reliable control layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`

Do not add machinery merely because it is available.

## 1. Classify the skill's reproducibility ceiling

Classify the primary work before deciding controls:

| Class | Typical examples | Mechanical ceiling |
|---|---|---|
| `objective-artifact` | ZIP/package generation, structured files, diagrams, code generation with contracts | high |
| `tool-action` | mutate files, publish artifacts, call external systems | high for pre/postconditions and receipts |
| `research-analytic` | repository analysis, document evidence synthesis, benchmark interpretation | medium/high for provenance and output contracts; conclusions retain judgment |
| `constrained-subjective` | UX critique, writing, visual direction, ideation | low/medium; process and evidence can be bounded, quality still needs judgment |

Do not promise byte-identical output when the task is inherently subjective or stochastic.

## 2. Build a variability map

For material workflows, inspect variance across:

`activation -> input -> routing -> references -> decisions -> generation/action -> validation -> repair -> delivery`

Classify each material source:

- **mechanical**: deterministic parsing, normalization, conversion, packaging, hashing, path handling;
- **constrained heuristic**: defaults, ordering, mode selection, tie-breakers, bounded choices;
- **model judgment**: research conclusions, editorial quality, perceptual decisions;
- **external nondeterminism**: mutable files, moving branches, API versions, network data, runtime capabilities.

Only add a control when it removes a real failure mode or creates evidence needed for acceptance.

## 3. Choose controls proportionally

### Low-risk text or subjective skill

Usually enough:

- precise activation/boundaries;
- clear inputs/outputs;
- strong defaults and stop conditions;
- examples/rubric where they improve consistency;
- no artificial schemas or scripts for ordinary language judgment.

### Structured-output or objective-artifact skill

Consider:

- schema or typed intermediate representation;
- deterministic renderer/converter;
- independent validator;
- stable diagnostic codes;
- regression/edge fixtures;
- package/artifact identity hashes.

### Tool-action or mutating skill

Also consider:

- explicit preconditions and postconditions;
- idempotency/retry semantics where relevant;
- canonical path resolution before mutation;
- protection against input/output aliases;
- stage-before-commit behavior;
- last-good preservation;
- recovery paths when rollback is incomplete;
- durable machine-readable receipts.

### Research or repository-evidence skill

Also consider:

- exact source provenance;
- immutable snapshot of material files before analysis;
- immutable VCS object reads for pinned revisions when supported;
- separate source, evaluator, candidate, and artifact identities;
- explicit invalidation/re-baseline rules if source evidence changes.

## 4. Snapshot material evidence before analysis

When external files or repository content materially determine a candidate or acceptance decision, prefer:

`resolve -> capture exact bytes -> hash/provenance -> analyze snapshot -> verify identity before acceptance`

For a pinned VCS revision, prefer reading the immutable revision object rather than assuming the current working tree represents that revision. Local dirty files, moving branches, replacement refs, regenerated files, or symlink redirection must not silently redefine pinned evidence.

Do not require snapshots for incidental context that does not affect acceptance.

## 5. Design output paths before implementing writes

For skills that create or mutate files, define path rules before coding:

- validate the authored path;
- canonicalize/resolve the final destination;
- enforce required file type/extension before and after resolution;
- reject symbolic-link cycles;
- reject output aliases with inputs, protected files, evaluators, or sibling receipts;
- keep generated artifacts outside a frozen source tree when package identity matters.

Preflight failures should not modify existing bytes.

## 6. Treat delivery as a transaction when outputs belong together

When one logical action emits an artifact plus receipt/sidecars:

1. stage all candidate bytes privately;
2. validate the staged candidates;
3. calculate hashes from those exact staged bytes;
4. preserve existing targets;
5. commit all outputs;
6. remove backups only after all commits succeed;
7. rollback on failure;
8. preserve and report recovery files if rollback is incomplete.

Do not overwrite a last-known-good artifact merely to report a failed candidate.

## 7. Make receipts evidence, not decoration

When receipts materially improve traceability, prefer fields such as:

- `receipt_version`;
- `status`;
- `stage`;
- stable diagnostic `code` when useful;
- target/source identity;
- package/artifact hash;
- validation profile;
- executed gates;
- recovery paths;
- residual `not-run` gates.

A success receipt must describe the exact committed artifact. File receipts should be staged and committed atomically when they are part of the delivery transaction. Large stdout JSON should be fully flushed before process exit.

Do not force receipts on simple conversational skills that create no durable artifact or action.

## 8. Keep evaluator identity separate from candidate identity

When improvement is measured:

- freeze or otherwise protect evaluator rules before mutation;
- use the same evaluator for baseline and candidate arms;
- invalidate the experiment if evaluator evidence changes mid-comparison;
- keep source identity, evaluator identity, candidate identity, artifact identity, and receipt identity separate.

Do not edit tests/evaluators to bless a candidate.

## 9. Decide whether specialist reproducibility work is still needed

After applying this design pass, use `references/reproducibility-routing.md`.

Invoke `reproducibility-engineer` only when material gaps remain or the user explicitly requests deeper reproducibility engineering. Typical triggers:

- complex schemas/IR or validators are needed;
- an existing skill has uncontrolled semantic variance;
- evaluator freeze and before/after experiments matter;
- multiple output/recovery paths need hardening;
- repeated regressions justify a dedicated transformation pass;
- cross-agent consistency requires stronger contracts than the local design pass can provide.

For simple new skills, recording `not-applicable` after this pass is valid.

## 10. Creation-time acceptance checklist

Before declaring a skill design complete, answer:

1. What can vary materially?
2. Which variance is intentional model judgment?
3. Which objective variance can be moved to a lower control layer?
4. Does external evidence need an immutable snapshot/provenance record?
5. Does the skill mutate state or create durable artifacts?
6. If so, can outputs alias inputs/protected paths?
7. Does a failed write preserve the last-known-good state?
8. Do receipts materially improve auditability?
9. Are evaluators independent/protected when improvement is measured?
10. Is `reproducibility-engineer` still materially useful after these controls?

If a control has no identified failure mode or evidence purpose, omit it.
