# Autoresearch Adaptation

## Mapping

- autoresearch training file -> target skill files;
- fixed experiment budget -> fixed iteration/time/token budget;
- validation metric -> skill benchmark, activation, conformance, robustness, or other declared metric;
- keep/discard experiment -> accept/revert candidate;
- program instructions -> `skill-improver` workflow plus configured agent-adapter prompt;
- overnight autonomous run -> bounded CI/container/host run with logs, stop condition, source/evaluator freeze, and rollback.

## Principles

1. **Single objective**: choose one primary non-saturated metric; secondary gates may block but must not hide the optimization target.
2. **Minimal mutation**: target skill folder only; evaluator files, secrets, generated evidence, and unrelated content are read-only.
3. **Comparable trials**: use the same frozen evaluator and source identities before/after each hypothesis.
4. **Patch accountability**: every iteration has one named hypothesis, bounded diff, evaluator evidence, structural gate result, and accept/reject reason.
5. **Falsification**: rejected hypotheses are evidence; log them and avoid equivalent retries.
6. **Causal repair**: repair one diagnosed cause at a time and stop after two non-improving rounds on the same objective error set.
7. **Final freeze**: package only the exact candidate that passed final validation.

## Host neutrality

The semantic loop is host-neutral. `scripts/skill_improver_loop.py` ships a Codex adapter for backward compatibility and a generic command adapter for other agent CLIs. Host-specific adapters are execution details, not part of the acceptance contract.

## Skill-specific risk

Skill packages can overfit small eval suites or benchmark wording. Counter with activation, negative, ambiguous, edge, regression/holdout, static structure, packaging, change-gate, and qualitative-review checks. Treat saturated structural scores as gates.

## Acceptance policy

Accept only when the predeclared metric/hardening objective passes; evaluator/source identities remain frozen; mandatory gates pass; only allowed paths changed; structural regression gate allows acceptance; safety/ownership boundaries remain intact; tests/evidence are not weakened; and the record explains the causal reason for acceptance.
