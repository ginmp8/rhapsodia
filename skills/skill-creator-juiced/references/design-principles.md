# Design Principles

Use this reference when deciding package structure and control depth.

## 1. Start from real work and existing context

Build from concrete prompts, corrections, artifacts, repository evidence, schemas, runbooks, failures, and existing contracts. Harvest what the current conversation already established before asking the user to restate it. Keep an instruction only when it changes likely behavior.

## 2. Enter at the current lifecycle state

A raw idea, a complete requirements set, an unevaluated draft, an existing production skill, a candidate under evaluation, and a validated candidate do not need the same workflow. Start at the earliest unresolved stage instead of replaying intake and design mechanically.

## 3. Cohesion beats size

A healthy skill has one coherent operational responsibility, shared vocabulary, related inputs/outputs, compatible evidence, and a common validation lifecycle. Size alone is not a reason to split.

Use modes for variants of one role. Use a router for separate specialist roles. Extract a mode when activation, ownership, tools, evidence, or validation lifecycle materially diverge.

## 4. Portable core before host adapters

When multi-host support is required, design the Agent Skills-compatible core first. Host install paths, UI metadata, tool aliases, and vendor-only optimizations are adapters.

Do not duplicate the semantic skill for ChatGPT, Claude, Copilot, or Cursor when the workflow is identical. A host fork is justified only when the host changes behavior, authority, evidence, or validation enough to require a separate lifecycle.

## 5. Progressive loading

`SKILL.md` is a control plane, not a knowledge dump. Keep mission, scope, defaults, workflow, resource map, evidence rules, stop conditions, and output contract there.

Put branch-specific detail in `references/`. Use relative paths from the skill root. Use scripts for deterministic operations and assets for output resources.

## 6. Activation quality

The description is the primary discovery surface. State what the skill does and when to use it with common user language. Include important adjacent exclusions without turning the description into a catalog.

When optimizing activation, test realistic explicit positives, implicit positives, competing-skill cases, lexical near-misses, adjacent-domain negatives, ambiguous cases, and adversarial boundary pressure. Prefer held-out cases for final claims; do not tune against the holdout set.

## 7. Match control strength to variability

Prefer the lowest reliable control layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`.

Move only objective or repetitive behavior downward. Preserve bounded model judgment for research, editorial, perceptual, and ambiguous tasks where code would create false certainty.

## 8. Evaluate against the right comparator

For a net-new skill, the useful behavioral question is usually whether it adds value over `without-skill`. For an existing skill, compare against an immutable prior version. For subjective work, use independent or blind qualitative comparison when mechanical assertions cannot represent quality.

If the correct comparator cannot run, do not substitute a weaker comparison and call it measured improvement.

## 9. Generalize; do not memorize evals

An eval failure identifies a class of missing behavior. Fix the class, not the exact prompt. Reject changes keyed to observed wording, filenames, fixtures, or examples unless those values are part of the actual domain contract.

Use held-out scenarios to check that a candidate improved the rule rather than memorized the training examples. Reproducibility is not an excuse for deterministic overfitting.

## 10. Promote repeated work deliberately

Repeated deterministic transformations or validations belong in `scripts/`; stable knowledge and schemas belong in `references/`; reusable output skeletons belong in `assets/`; bounded judgment remains in instructions or focused rubrics.

Promote repeated work only when several runs demonstrate that the shared resource will reduce variance, cost, or error. Do not extract abstractions after one incidental repetition.

## 11. Output consistency

If structure matters, define a contract or template. If machine consumption matters, prefer a schema and validator. If style matters, add examples or a rubric. If safety/correctness matters, add gates and explicit stop conditions.

Prefer strong defaults over large menus. Define tie-breakers where equivalent choices would otherwise create material drift.

## 12. Evidence discipline

Treat static checks, behavioral scenarios, runtime execution, perceptual review, and efficiency metrics as different evidence classes. Never infer one from another.

Planned eval files are not executed evidence. A generated score is not a benchmark unless the underlying scenarios actually ran under a declared evaluator. Token/time/tool-call reductions are supporting evidence and never override correctness.

## 13. Explain why, constrain where necessary

Prefer concise rationale that helps a capable model generalize the rule. Use strong normative language for genuine invariants, safety boundaries, frozen evidence, authority limits, or exact output contracts. Avoid arbitrary `ALWAYS`/`NEVER` rules that exist only to force one example.

## 14. Lack of surprise

A skill's behavior, authority, external calls, data handling, and outputs should be consistent with what its activation description and documented capability imply. Do not hide side effects or expand tool authority beyond the user's reasonable expectation.

## 15. Backward compatibility

For existing skills, preserve the name, activation ownership, user-visible behavior, and validated interfaces unless the requested change requires a migration. Do not create a second skill solely to avoid updating a compatible existing one.

## 16. Simplicity under gates

Reproducibility mechanisms are justified only when they eliminate observed variability or create useful evidence. Prefer the smallest mechanism that closes the gap. Avoid ornamental schemas, scripts, agents, or validators.

## 17. Reproducibility by design, not by retrofit

During creation or material redesign, classify the skill's reproducibility ceiling and map material variance before deciding resources. A simple text skill may need only activation, defaults, and a rubric; an objective-artifact or tool-action skill may justify schemas, deterministic helpers, validators, immutable evidence, canonical output preflight, last-good preservation, recovery, and receipts.

Read `reproducibility-by-design.md` for the proportional control checklist. Apply the local design pass even when `reproducibility-engineer` is `not-applicable`; invoke the specialist only when material gaps remain or the user requires deeper reproducibility engineering.

For evidence-driven skills, keep source, evaluator, candidate, artifact, and receipt identities separate. For mutating skills, validate resolved output destinations before writes and preserve recovery evidence when rollback is incomplete.

