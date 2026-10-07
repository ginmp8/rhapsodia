# Evaluation and Generalization

## At a Glance

- **Purpose:** Define lifecycle-aware evaluation, baseline choice, realistic scenarios, evaluator separation, and anti-overfitting rules for skill creation/redesign.
- **Load when:** Designing evaluation, diagnosing failed cases, choosing a comparator, or deciding whether a repair generalizes beyond visible examples.
- **Decision impact:** Determines the correct baseline and lifecycle entry point, separates objective/subjective evidence, requires difficult activation boundaries, and prevents eval-specific fixes from being reported as general improvement.

## Contents

- 1. Enter at the current lifecycle state
- 2. Harvest context before asking questions
- 3. Select the correct baseline
- 4. Build a small realistic seed set, then expand
- 5. Separate objective and subjective evaluation
- 6. Generalize from failures; do not patch examples
- 7. Inspect process, not only final output
- 8. Promote repeated work into reusable resources
- 9. Activation evaluation uses difficult boundaries
- 10. Treat efficiency as supporting evidence
- 11. Human feedback is evidence, not an instruction to overfit
- 12. Stop conditions


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

Define the first small set of realistic prompts before substantial candidate authoring whenever behavior can be exercised. Prefer real user phrasing over synthetic keyword tests. Use the seed set to expose baseline gaps and justify the minimum candidate; after the first candidate stabilizes, expand with held-out scenarios that were not used to shape the change. A substantial instruction/resource without a requirement, invariant, observed gap, or regression rationale is a candidate for removal.

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

### LLM-judge calibration

When an LLM evaluator materially decides acceptance, use an explicit evidence-bound rubric and calibrate against a bounded gold/human-labeled set when practical. Prefer pass/fail or pairwise comparison to arbitrary granular scoring when possible. Reverse/randomize pair order when position bias can matter, check whether verbosity/style is being rewarded independently of quality, and treat unstable calibration as an evaluator limitation rather than a candidate defect.

### Model capability calibration

When instruction sufficiency or constraint level may materially depend on model capability, evaluate representative capability tiers actually in scope rather than assuming one model generalizes to all. Use a small set such as `constrained`, `balanced`, and `high-capability` only when the deployment surface materially spans those tiers.

- Keep prompts, files, acceptance criteria, and evaluator rules equivalent across tiers.
- Check constrained models for under-guidance, missed sequencing, and ambiguous branching.
- Check high-capability models for over-prescription, unnecessary steps, and instructions that suppress useful judgment.
- Record exact model/provider/version when known as runtime evidence, but keep vendor/model names out of the portable semantic contract unless they are an explicit target requirement.
- If relevant model runtime access is unavailable, mark the calibration `not-run`; do not infer cross-model compatibility from structural portability.
- Do not require multi-model execution when model capability is immaterial to the changed behavior.

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

- skill/resource selection;
- tool selection and argument correctness;
- tool-result interpretation;
- handoff/delegation correctness;
- retry and stop behavior;
- repeated dead-end reasoning or redundant tool calls;
- unnecessary context loading or repeated helper generation;
- authority escalation beyond the declared budget;
- hidden dependence on host-specific behavior.

A final output can pass while the workflow remains expensive, fragile, over-authorized, or non-portable. Treat unnecessary privileged calls, repeated repair loops, ignored stop conditions, or unsafe interpretation of lower-trust content as process regressions even when the final answer is acceptable. Use process evidence to improve the skill only when it exposes a generalizable issue.

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

Prefer held-out evaluation for final activation claims. If activation is stochastic, repeat scenarios enough to distinguish a stable improvement from one lucky run. Do not optimize description wording against the final holdout set. When deployment exposes many skills, add increasing catalog pressure (`isolated -> nearest competitors -> representative catalog -> large/saturation catalog` when relevant) and track wrong-skill/no-skill/competitor-steal behavior where observable. Do not rewrite one description to compensate for a failure proven to be catalog-level saturation.

## 10. Treat efficiency as supporting evidence

When available, record token/context use, duration, tool-call count, or repeated work as supporting metrics. These do not override correctness or quality. A faster candidate that loses semantic coverage is a regression.

## 11. Human feedback is evidence, not an instruction to overfit

Use user feedback to identify the underlying quality gap. Preserve specific feedback as evidence, then convert it into the smallest generalizable rule or resource change. For subjective outputs, user or independent reviewer preference can be primary perceptual evidence, but it must remain separate from mechanical pass/fail claims.

Maintain a field-evidence loop when real usage is available: `traces/corrections/incidents -> failure clusters -> durable eval cases -> candidate change -> regression suite`. Distinguish recurring real-world failures, historical regressions, synthetic/adversarial cases, and one-off preferences; promote recurring classes into evals before persistent skill instructions whenever practical.

## 12. Stop conditions

Stop the iteration branch when:

- two consecutive repair rounds do not improve the best objective diagnostic or reviewer outcome;
- the only remaining improvements depend on inventing domain facts;
- passing requires weakening a validator, evaluator, safety boundary, or semantic contract;
- the change is becoming eval-specific rather than generalizable;
- the user-requested quality is inherently subjective and the required perceptual reviewer is unavailable;
- the candidate is already validated and further cosmetic edits would invalidate the frozen state without material benefit.
