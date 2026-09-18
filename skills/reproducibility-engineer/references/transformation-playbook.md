# Transformation Playbook

## Contents

- Core principle
- Patterns 1-16
- Transformation priority
- Anti-patterns

## Principle

Convert quality from an aspiration into contracts that fail loudly. Prefer mechanisms that reduce degrees of freedom without deleting useful adaptability.

## Pattern 1: Router before execution

Replace vague all-purpose behavior with a small mode/type router. Select the representation by the user's question, not by the easiest renderer or example.

Good controls:
- explicit mode enum;
- default mode only when ambiguity is harmless;
- guide/diagnostic command for ambiguous cases;
- non-activation boundaries.

## Pattern 2: Typed IR between intent and artifact

Use a typed intermediate representation when the model currently writes fragile final artifacts directly.

Pipeline:

`intent -> typed JSON/YAML/AST -> validator/compiler -> artifact`

Use IR when it removes repeated syntax/layout/mechanical choices. Do not invent IR for simple prose outputs.

## Pattern 3: Strong defaults and bounded overrides

Start from automatic/default behavior. Allow manual overrides only when a diagnostic proves the default cannot satisfy the contract.

Examples:
- automatic routing before manual coordinates;
- default theme before custom styling;
- canonical ordering before user-controlled sorting;
- one supported override per diagnosed repair.

## Pattern 4: Semantic data cannot be deleted to fix presentation

If a label, field, citation, safety check, or protocol carries meaning, preserve it. Repair presentation/geometry/spacing first. Removal is allowed only when the information is genuinely redundant under an explicit rule.

## Pattern 5: Independent validator

The generator must not be the only judge of its own output. Add an independent validator for objective properties.

Validator diagnostics should contain:

- stable `code`;
- exact `subject`;
- measured or observed `evidence`;
- `supported_fixes` when the repair space is bounded;
- severity/gate effect.

## Pattern 6: Repair by one causal change

Use:

`diagnostic -> smallest supported change -> same validator -> adjacent validators`

Avoid broad cleanup while a specific gate is failing. Stop after two consecutive non-improving rounds on the same objective error set unless new evidence changes the hypothesis.

## Pattern 7: Freeze after pass

A final pass freezes the candidate. Any later edit invalidates the relevant evidence and requires revalidation. This prevents untested "last polish" changes.

## Pattern 8: Atomic delivery

For file/artifact skills:

1. render/write a private candidate;
2. validate/check that candidate;
3. compute identity/receipt where useful;
4. atomically replace the output only on success;
5. preserve the last-good artifact on failure.

Never test a stale last-good artifact as if it were the failed candidate.

## Pattern 9: Separate evidence layers

Never collapse these claims:

- structure/package valid;
- semantic/behavioral eval passed;
- real runtime/browser/tool behavior passed;
- subjective/perceptual quality approved.

Each requires its own evidence source.

## Pattern 10: Version the contract

If schema/layout/output semantics change incompatibly:
- add explicit version identity;
- define migration or preserve legacy behavior intentionally;
- reject unsupported old forms explicitly;
- do not silently reinterpret old artifacts.

## Pattern 11: Progressive loading

Keep `SKILL.md` as the control plane. Move branch-specific rules, schemas, long rubrics, examples, and implementation details to one-level references loaded only when needed.

This reduces context dilution and accidental rule mixing.

## Pattern 12: Regression from every meaningful failure

When a defect is confirmed and generalizable, convert it into one of:
- deterministic validator rule;
- regression fixture;
- golden scenario;
- activation/non-activation example;
- explicit stop condition.

A repeated bug that never becomes a gate is likely to recur.

## Pattern 13: Snapshot evidence before analysis

When external files or repository content materially determine a change or acceptance decision, capture the exact bytes first and analyze the snapshot. Record provenance separately from the live source.

For pinned VCS evidence, prefer immutable object reads tied to the recorded revision. Dirty working files, moving branches, local replacement refs, or regenerated files must not silently redefine the evidence.

## Pattern 14: Canonical output preflight

Validate paths before writing anything. Check both authored and resolved destinations, including symbolic links. Reject outputs that alias inputs, evaluators, protected paths, or sibling receipts. Enforce required output types/extensions both before and after canonicalization.

Preflight failures must preserve all existing bytes.

## Pattern 15: Recovery-aware multi-output commit

Treat an artifact plus receipts/sidecars as one logical transaction:

`stage all -> validate all -> preserve previous targets -> commit all -> clean backups`

If commit fails, restore the last-good targets. If rollback is incomplete, preserve backup and failed-candidate paths and report them explicitly. Recovery evidence is more important than cosmetic cleanup.

## Pattern 16: Durable stage-aware receipts

Receipts are evidence. They must be complete, parseable, and emitted only for the exact bytes they describe. Prefer stable stage/code/subject/evidence fields, atomic file replacement, and flushed output. A large or piped receipt must not be truncated by an early process exit.

## Transformation priority

Apply in this order unless evidence demands otherwise:

1. semantic correctness and safety;
2. activation/routing;
3. input/output contracts;
4. mechanical determinism;
5. validators and diagnostics;
6. evaluation/regression;
7. repair loop;
8. source/evidence integrity;
9. output-path and delivery integrity;
10. recovery and durable receipts;
11. context/token efficiency;
12. cosmetic polish.

## Anti-patterns

Reject these pseudo-improvements:

- adding more MUST statements when a script/schema can enforce the rule;
- lowering a threshold or deleting a test to get green;
- changing eval prompts after seeing candidate results;
- copying example facts into new outputs;
- adding manual coordinates/options before automatic defaults fail;
- claiming measured improvement from static inspection;
- using hidden overflow/clipping or omitted content to make visual checks pass;
- adding validators that only check the same code path that generated the artifact;
- rereading a mutable live source after a frozen comparison already depends on earlier bytes;
- accepting output paths that can alias inputs or receipts through symbolic links;
- deleting backups after an incomplete rollback;
- emitting a success receipt before the described artifact is durably committed;
- expanding `SKILL.md` until all branches are always in context.
