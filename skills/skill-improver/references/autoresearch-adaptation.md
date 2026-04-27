# Autoresearch Adaptation for Skill Improvement

## Core mapping

| Autoresearch concept | Skill-improver equivalent |
|---|---|
| Autoresearch training file edited by the agent | target skill files edited by the agent |
| fixed 8-minute training budget | fixed iteration, time, or token budget |
| validation metric such as val_bpb | skill benchmark score, eval score, activation accuracy, or conformance score |
| keep or discard experiment | accept patch or revert patch |
| Autoresearch program instructions | skill-improver workflow plus Codex prompt |
| overnight autonomous run | bounded CI/container run with logs and rollback |

## Design principles

1. Single objective per run.
   Pick one primary metric, such as benchmark score or activation recall. Secondary gates can block acceptance, but they should not obscure the optimization target.

2. Minimal mutation scope.
   Limit the agent to the target skill folder. For safety, treat evaluator files, secrets, and unrelated repository content as read-only.

3. Comparable trials.
   Use the same evaluation command before and after a hypothesis. Do not change prompts, scoring rules, or test fixtures mid-run unless the experiment is explicitly about eval design.

4. Patch-level accountability.
   Each iteration should produce a small diff, a named hypothesis, eval results, and an accept/reject decision.

5. Progress through falsification.
   A rejected hypothesis is useful evidence. Log it and avoid repeating equivalent changes.

## Difference from model research

Skill improvement is more discrete than neural network training. A skill can appear to improve through overfitting to a small eval suite. Counter this by using:

- activation prompts that should trigger the skill,
- negative prompts that should not trigger the skill,
- ambiguous prompts with expected decision rules,
- edge cases involving missing files, invalid paths, conflicting goals, and unsafe requests,
- static structure checks,
- packaging validation,
- qualitative review.

## Recommended acceptance policy

Accept a candidate patch only when all are true:

1. The primary score improves by at least `min_delta`.
2. All mandatory gates pass.
3. The patch modifies only allowed paths.
4. The patch does not weaken safety or ownership boundaries.
5. The patch does not remove or trivialize tests.
6. The report explains the mechanism of improvement.
