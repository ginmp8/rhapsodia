# Evaluation Contract

Use before editing a target skill.

## Baseline record

```yaml
target: <path>
mode: <audit-only|plan-only|apply-optimization|validation-only|package>
evaluator: <command or specialist report>
evaluator_status: <executed|planned|blocked>
score: <number|null>
gates:
  - {name: <gate>, status: <pass|fail|planned|blocked>}
change_gate:
  policy: <required|advisory|not-available>
  status: <pass|pass-with-warnings|fail|insufficient-evidence|planned|blocked>
  blocking_regressions: []
blocked_paths: [.git, secrets, credentials, fixtures, expected_outputs, benchmark_baselines, generated_evidence, old_zips]
```

## Freeze rules

After baseline, do not change scenarios, expected outputs, evaluator scripts, scoring config, benchmark inputs, fixtures, generated baseline reports, or metric logic to make results pass. If evaluator design is itself in scope, normalize it as a separate hypothesis and state whether criteria changed or only schema/compatibility changed.

## Metrics

Prefer multiple signals: structure validity, `skill-change-gate` status, activation coverage, output-contract adherence, local-link integrity, script smoke status, security findings by severity, contradiction count, package status, token estimate, benchmark maturity score. Treat saturated scores as gates and add auxiliary metrics such as unresolved risks, token count, scenario coverage, unreferenced resources, or package gates.

## Hypothesis record

```yaml
id: H1
statement: <if we change x, y improves because z>
files: []
expected_effect: <metric/gate>
validation: <command/scenario>
status: <accepted|rejected|blocked|planned>
evidence: <score, gates, or rationale>
```

Accept only when required gates pass, `skill-change-gate` reports no blocking regression, blocked/frozen paths are protected or explicitly normalized without changing criteria, no activation/safety/output regression appears, and required metrics meet the threshold. Reject or revert when gates fail, `skill-change-gate` fails under a required policy, score worsens without accepted trade-off, compression removes protected duties, or scope expands beyond target.

## Skill-change-gate contract

Use `skill-change-gate` as an acceptance gate for material candidate patches and as a final regression gate after hardening or token compression. When the specialist is unavailable, apply its checklist locally and mark the pass `applied-by-checklist`; do not mark it `pass` unless the specialist actually ran or equivalent evidence was inspected.

Required gate evidence:

```yaml
change_gate_result:
  policy: <required|advisory>
  status: <pass|pass-with-warnings|fail|insufficient-evidence|applied-by-checklist|blocked>
  decision_for_caller: <accept|reject|repair-before-accept|gather-evidence|advisory-only>
  blocking_regressions: []
  material_concerns: []
  accepted_tradeoffs: []
```

For full optimization, use `required` policy by default. A blocking regression prevents acceptance even when a benchmark score improves. `pass-with-warnings` may proceed only when material concerns are documented as accepted trade-offs or follow-up hypotheses.
