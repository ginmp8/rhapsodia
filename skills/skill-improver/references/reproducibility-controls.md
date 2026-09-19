# Reproducibility Controls

Use this reference when candidate acceptance depends on trustworthy source bytes, bounded repair, final freezing, or safe artifact delivery.

## Control hierarchy

Prefer the lowest reliable control layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form instruction`

Do not move inherently subjective judgment into code just to appear deterministic.

## 1. Source snapshot before analysis

When external files, benchmark inputs, repository content, or prior reports materially affect a hypothesis or acceptance decision:

1. resolve the source identity;
2. capture the exact bytes before analysis;
3. hash and record provenance;
4. analyze the snapshot, not a moving live source;
5. verify the live identity before final acceptance.

Use:

```text
<PYTHON> scripts/evidence_snapshot.py capture \
  --root <SOURCE_ROOT> \
  --path <RELATIVE_PATH> \
  --snapshot-dir <WORK>/source-bytes \
  --manifest <WORK>/source-manifest.json

<PYTHON> scripts/evidence_snapshot.py verify \
  --manifest <WORK>/source-manifest.json
```

Repeat `--path` for multiple sources. If verification fails, invalidate the comparison or deliberately create a new baseline. Do not mix candidate evidence from different source versions.

For pinned VCS evidence, prefer immutable revision-object reads when the host supports them. Record the repository/revision/path identity rather than assuming the working tree represents that revision.

## 2. Frozen evaluator

Freeze all material evaluator inputs before candidate mutation:

- evaluator command/version;
- scoring configuration and thresholds;
- scenarios, expected outputs, golden data, grader prompts;
- benchmark result files reused as fixtures;
- shared dependencies that can change evaluator behavior.

A candidate never earns acceptance by modifying these inputs. If an evaluator is wrong, invalidate the experiment, repair/freeze the evaluator separately, then restart baseline comparison.

## 3. Diagnostic-driven repair loop

Use:

`diagnostic -> one causal subject -> smallest supported fix -> same gate -> adjacent gates`

Prefer diagnostics with stable `code`, exact `subject`, observed `evidence`, severity, and bounded `supported_fixes`.

Stop the current repair branch after two consecutive rounds that do not reduce the same objective error set unless new evidence changes the hypothesis. Do not random-search wording or broad cleanup while a specific gate is failing.

## 4. Saturated metrics

A saturated metric is a gate, not an optimization target. Add a non-saturated auxiliary metric before claiming improvement, for example:

- ambiguous activation robustness;
- holdout pass rate;
- repair rounds;
- manual rework;
- runtime failures;
- token/context cost;
- portability/capability coverage.

Static `100/100` does not prove behavioral improvement.

## 5. Freeze after pass

Once the final candidate passes applicable validation:

1. compute and record the exact candidate identity;
2. mark it frozen;
3. do not apply cleanup, formatting, or documentation edits afterward without rerunning affected validation.

Use tree hashing when a single artifact hash is not enough:

```text
<PYTHON> scripts/evidence_snapshot.py hash-tree \
  --root <TARGET_SKILL_PATH>
```

The final package must be built from the same frozen candidate bytes.

## 6. Canonical output preflight

Before writing package/report/receipt outputs, validate both the authored path and canonical resolved destination.

Reject when:

- an output aliases the target, an input, evaluator, protected file, or sibling receipt;
- a relative destination escapes the allowed output root after resolution;
- symlink resolution changes the required output type/extension;
- multiple outputs resolve to the same file.

Preflight failures must leave existing bytes untouched.

## 7. Recovery-aware delivery

Treat an artifact and its optional receipt as one logical transaction:

`stage -> validate -> hash -> preserve last-good -> commit -> verify -> clean backups`

If commit fails:

1. restore the previous last-good outputs where possible;
2. preserve failed-candidate/backups when rollback is incomplete;
3. report recovery paths explicitly;
4. never emit a success receipt for bytes that were not committed.

`scripts/package_skill.py` implements this policy for package ZIPs and optional receipt sidecars. It also runs the target validator against a private copy so validator side effects such as caches cannot mutate the frozen candidate.

## 8. Durable receipt

A receipt should be parseable and tied to exact committed bytes. Prefer:

```json
{
  "receipt_version": 1,
  "status": "pass",
  "stage": "package",
  "target": "...",
  "artifact": {
    "path": "...",
    "sha256": "...",
    "size": 123
  },
  "checks": [],
  "validator": {},
  "recovery": []
}
```

Write sidecar receipts atomically. Flush stdout before successful exit. Failure receipts must not claim artifact commitment.

## 9. Evidence layers

Keep these claims separate:

- **structural evidence**: static package and validator evidence;
- **behavioral evidence**: executed prompts/scenarios/evaluators;
- **runtime evidence**: actual tool/application/browser behavior;
- **perceptual evidence**: independent subjective review.

When execution infrastructure is missing, label the result `structurally hardened` or `validation-ready`, not `behaviorally improved`.

## 10. Version and compatibility

When changing persistent schemas, output contracts, CLI flags, or host adapters:

- preserve existing behavior by default where practical;
- add explicit migration/version identity for incompatible changes;
- keep deprecated aliases long enough to avoid silent breakage;
- reject unsupported old forms explicitly rather than silently reinterpreting them.
