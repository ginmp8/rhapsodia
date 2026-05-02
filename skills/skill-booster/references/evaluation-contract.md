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
blocked_paths: [.git, secrets, credentials, fixtures, expected_outputs, benchmark_baselines, generated_evidence, old_zips]
```

## Freeze rules

After baseline, do not change scenarios, expected outputs, evaluator scripts, scoring config, benchmark inputs, fixtures, generated baseline reports, or metric logic to make results pass. If evaluator design is itself in scope, normalize it as a separate hypothesis and state whether criteria changed or only schema/compatibility changed.

## Metrics

Prefer multiple signals: structure validity, activation coverage, output-contract adherence, local-link integrity, script smoke status, security findings by severity, contradiction count, package status, token estimate, benchmark maturity score. Treat saturated scores as gates and add auxiliary metrics such as unresolved risks, token count, scenario coverage, unreferenced resources, or package gates.

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

Accept only when required gates pass, blocked/frozen paths are protected or explicitly normalized without changing criteria, no activation/safety/output regression appears, and required metrics meet the threshold. Reject or revert when gates fail, score worsens without accepted trade-off, compression removes protected duties, or scope expands beyond target.
