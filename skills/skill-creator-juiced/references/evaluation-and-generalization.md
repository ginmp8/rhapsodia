# Evaluation and Generalization

Use this reference when creating or improving a skill that needs behavioral evidence, iterative refinement, activation tuning, or protection against overfitting.

## 1. Enter at the current lifecycle state

Do not restart the workflow mechanically. Classify the target first:

- `raw-idea`: intent exists but workflow/output are not yet defined;
- `requirements-known`: concrete inputs, outputs, boundaries, and examples are already available;
- `draft`: a candidate package exists but has not been evaluated;
- `existing-skill`: an installed or supplied skill is the current baseline;
- `candidate-under-evaluation`: a modified version already exists and needs evidence;
- `validated-candidate`: required gates already passed and only packaging/delivery remains.

Start at the earliest unresolved stage. Do not repeat intake, research, or drafting that the current conversation or target package already settled.

## 2. Harvest context before asking questions

Before asking the user for information, extract what is already known from the current conversation and supplied artifacts:

- concrete user prompts and near-miss prompts;
- corrections and rejected approaches;
- workflow order and tools already selected;
- expected inputs and output formats;
- examples of good/bad results;
- constraints, safety boundaries, portability targets, and dependencies;
- terminology and owner boundaries.

Ask only for missing facts that materially change semantics, authority, safety, or acceptance. Never make the user restate information already established.

## 3. Select the correct baseline

Use the comparator that answers the actual question:

- **net-new skill**: compare the candidate with `without-skill` when execution infrastructure makes that comparison meaningful;
- **existing skill**: compare the candidate with an immutable snapshot of the prior skill;
- **portability-only change**: compare semantic behavior against the prior skill and validate host-neutral structure separately;
- **subjective skill**: use the prior version or blind qualitative comparison when objective assertions cannot represent quality.

Run equivalent prompts, files, environment assumptions, and evaluators across comparison arms. If a valid baseline cannot be executed, mark behavioral comparison `not-run` and do not claim measured improvement.

## 4. Build a small realistic seed set, then expand

Start with a small set of realistic prompts that cover the core behavior. Prefer real user phrasing over synthetic keyword tests. After the first candidate stabilizes, expand with held-out scenarios that were not used to shape the change.

Cover applicable classes:

- expected/common path;
- edge conditions;
- invalid or incomplete input;
- adjacent-domain near miss;
- ambiguous ownership;
- adversarial/boundary pressure;
- portability/runtime degradation;
- regression from previously supported behavior.

Do not call a set "held out" if it influenced the candidate before final evaluation.

## 5. Separate objective and subjective evaluation

Use the strongest valid evaluator for each property:

- deterministic file/content rules -> scripts, schemas, parsers, exact assertions;
- structured semantic rules -> independent validator or rubric with evidence;
- research/analytic quality -> source/evidence traceability plus bounded rubric;
- writing, design, taste, or perceptual quality -> blind or human/image-capable review when practical.

Do not manufacture numeric assertions for qualities that cannot be meaningfully reduced to them. Keep structural, behavioral, runtime, and perceptual evidence separate.

## 6. Generalize from failures; do not patch examples

Treat an eval failure as evidence of a missing general rule, not as permission to hard-code the example.

Before accepting a change, ask:

1. What class of failure does this represent?
2. Does the proposed change solve that class without keying on the exact prompt, filename, wording, or fixture?
3. Could the change harm adjacent valid cases?
4. Does a held-out case exercise the generalized rule?

Reject or reformulate changes that merely memorize the observed eval. Reproducibility must not become deterministic overfitting.

## 7. Inspect process, not only final output

When execution traces or transcripts are available, inspect them for:

- repeated dead-end reasoning;
- redundant tool calls;
- repeated rediscovery of the same rules;
- unnecessary context loading;
- inconsistent routing;
- repeated helper generation;
- hidden dependence on host-specific behavior.

A final output can pass while the workflow remains expensive, fragile, or non-portable. Use process evidence to improve the skill only when it exposes a generalizable issue.

## 8. Promote repeated work into reusable resources

If multiple independent runs repeat the same work, classify it before changing the package:

| Repetition | Preferred home |
|---|---|
| deterministic transformation or validation | `scripts/` |
| stable domain knowledge, schema, policy, or lookup guidance | `references/` |
| output skeleton reused verbatim or filled in | `assets/` |
| bounded model judgment or decision heuristic | `SKILL.md` or focused reference |

Do not extract a resource after one incidental repetition. Promote it when repetition is material and the reusable resource reduces cost, variance, or error.

## 9. Activation evaluation uses difficult boundaries

When activation quality matters, evaluate the description against realistic prompts including:

- explicit should-trigger cases;
- implicit should-trigger cases that do not name the skill;
- competing-skill cases where this skill should own the work;
- lexical near-misses that share keywords but should not trigger;
- adjacent-domain negatives;
- ambiguous cases;
- adversarial attempts to broaden ownership.

Prefer held-out evaluation for final activation claims. If activation is stochastic, repeat scenarios enough to distinguish a stable improvement from one lucky run. Do not optimize description wording against the final holdout set.

## 10. Treat efficiency as supporting evidence

When available, record token/context use, duration, tool-call count, or repeated work as supporting metrics. These do not override correctness or quality. A faster candidate that loses semantic coverage is a regression.

## 11. Human feedback is evidence, not an instruction to overfit

Use user feedback to identify the underlying quality gap. Preserve specific feedback as evidence, then convert it into the smallest generalizable rule or resource change. For subjective outputs, user or independent reviewer preference can be primary perceptual evidence, but it must remain separate from mechanical pass/fail claims.

## 12. Stop conditions

Stop the iteration branch when:

- two consecutive repair rounds do not improve the best objective diagnostic or reviewer outcome;
- the only remaining improvements depend on inventing domain facts;
- passing requires weakening a validator, evaluator, safety boundary, or semantic contract;
- the change is becoming eval-specific rather than generalizable;
- the user-requested quality is inherently subjective and the required perceptual reviewer is unavailable;
- the candidate is already validated and further cosmetic edits would invalidate the frozen state without material benefit.
