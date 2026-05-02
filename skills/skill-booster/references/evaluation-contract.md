# Evaluation Contract

Use this contract before editing a target skill.

## Baseline Record

Record these fields:

```yaml
target: <path>
mode: <audit-only|plan-only|apply-optimization|validation-only|package>
evaluator: <command or specialist report>
evaluator_status: <executed|planned|blocked>
score: <number or null>
gates:
  - name: <gate>
    status: <pass|fail|planned|blocked>
blocked_paths:
  - .git
  - secrets
  - credentials
  - fixtures
  - expected_outputs
  - benchmark_baselines
  - generated_evidence
  - old_zips
```

## Evaluator Freeze Rules

After baseline, do not modify:

- scenario suite used for scoring;
- expected outputs;
- evaluator scripts;
- benchmark config;
- generated baseline report;
- fixture files;
- metric calculation logic.

If evaluator design itself is the requested task, run it as a separate planning phase and freeze the new evaluator before optimization begins.

## Metrics

Prefer multiple signals:

- structural validity;
- activation scenario coverage;
- output contract adherence;
- local link integrity;
- script smoke-test status;
- security finding count by severity;
- unresolved contradiction count;
- package validation status;
- token estimate before/after;
- benchmark maturity score.

Do not claim measured improvement unless before/after evidence exists.

## Hypothesis Record

Each patch batch needs:

```yaml
id: H1
statement: <if we change x, y should improve because z>
files: []
expected_effect: <metric or gate>
validation: <command or scenario>
status: <accepted|rejected|blocked|planned>
evidence: <score, gates, or rationale>
```

## Accept Criteria

Accept a patch only when:

- required gates pass;
- no frozen evaluator file changed;
- no blocked path changed;
- no critical regression appears in activation, safety, or output contract;
- score or auxiliary metric meets the stated threshold, when a metric was required.

Reject or revert when:

- gates fail;
- score worsens without explicit trade-off acceptance;
- token reduction removes safety, validation, triggers, exclusions, or output requirements;
- patch expands scope beyond target skill.

## Saturated Score Handling

If baseline already passes all primary gates, treat the primary score as a gate, not an improvement metric. Add an auxiliary non-saturated metric such as:

- fewer unresolved risks;
- fewer tokens with preserved semantic map;
- more complete scenario suite;
- fewer unreferenced resources;
- clearer output contract;
- safer script interface.
