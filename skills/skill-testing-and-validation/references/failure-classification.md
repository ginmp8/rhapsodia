# Formal failure classification

Failure category and gate state are separate dimensions.

## Allowed categories

- `build`: compile, type-check, import, bundling, or syntax failure before test assertions.
- `test`: an executed test gate failed assertions/setup/runtime behavior.
- `lint`: lint, formatting-check, or static-quality gate failure.
- `validator`: custom validator/schema/integrity contract failure.
- `environment`: required executable/runtime/dependency/network/permission/capability unavailable.
- `configuration`: malformed/missing non-secret project configuration, invalid paths, workspace/config mismatch.
- `packaging`: archive creation/shape/size/package-validation failure.
- `unknown`: insufficient evidence.

## Fixed precedence

When classifying non-zero command evidence:

1. environment signatures;
2. configuration signatures;
3. explicit gate context (`build`, `test`, `lint`, `validator`, `packaging`);
4. without gate context: packaging, validator, build, lint, test pattern priority;
5. `unknown`.

This prevents an absent test runner from being mislabeled as a test defect and prevents opaque test failures from drifting into `unknown` when the executed gate is known.

Use `scripts/classify_failure.py` for stable codes/evidence. Its machine-readable output includes `classification_version`, `category`, `code`, `gate`, `exit_code`, `evidence`, and a bounded summary.

## Gate states

- `pass`: the required command executed and exited successfully, or equivalent supplied evidence explicitly proves success.
- `fail`: the command executed and returned an in-scope failure.
- `blocked`: the gate could not meaningfully execute because of environment/authorization/capability/input constraints.
- `not-run`: intentionally not executed by scope, no applicable command exists, or execution was not requested.

A non-zero target command classified `environment` is normally `blocked`; other non-zero executed gates are normally `fail`. Preserve the original target exit code even when the wrapper returns its own process status.

## Diagnostic-driven repair

For every unresolved failure keep these distinct:

1. observed evidence;
2. formal category/code;
3. probable root cause;
4. smallest repair hypothesis;
5. exact rerun command.

Do not change fixtures, snapshots, golden files, expected outputs, benchmark evidence, or validator thresholds to fit broken behavior.
