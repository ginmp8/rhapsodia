# Autoresearch Adaptation

## Mapping

- autoresearch training file -> target skill files
- fixed 8-minute budget -> fixed iteration/time/token budget
- `val_bpb` or validation metric -> skill benchmark, eval, activation, or conformance score
- keep/discard experiment -> accept/revert patch
- program instructions -> `skill-improver` workflow plus Codex prompt
- overnight autonomous run -> bounded CI/container run with logs and rollback

## Principles

1. Single objective: choose one primary metric; secondary gates may block but must not hide the optimization target.
2. Minimal mutation: target skill folder only; evaluator files, secrets, and unrelated repo content are read-only.
3. Comparable trials: same evaluation command before/after each hypothesis; do not change prompts, scoring, or fixtures mid-run unless objective is eval design.
4. Patch accountability: every iteration needs small diff, named hypothesis, eval results, and accept/reject decision.
5. Falsification: rejected hypotheses are evidence; log them and avoid equivalent retries.

## Skill-specific risk

Skill packages are discrete and can overfit small eval suites. Counter with activation, negative, ambiguous, edge, static-structure, packaging, and qualitative-review checks. Edge cases include missing files, invalid paths, conflicting goals, and unsafe requests.

## Acceptance policy

Accept a candidate only when: primary score improves by at least `min_delta`; all mandatory gates pass; only allowed paths changed; safety/ownership boundaries remain intact; tests are not removed or trivialized; and the report explains why the patch improved the metric.
