# CLI and Packaging Contract

Use for deterministic harness commands, host-neutral execution, exits, receipts, and packaging.

## Runtime convention

Use `<PYTHON>` for the available Python 3.10+ execution mechanism. Do not assume the executable name or shell. Bundled scripts use only the Python standard library.

Use `<skill-root>` for this harness package root and `<TARGET_SKILL_PATH>` for the target skill root. Resolve paths from the active environment; semantic behavior must not depend on a host installation directory.

## Commands

### `scripts/skill_harness_snapshot.py`

Capture before mutation:

```text
<PYTHON> <skill-root>/scripts/skill_harness_snapshot.py capture \
  --target <TARGET_SKILL_PATH> \
  --snapshot-dir <work-dir>/baseline-snapshot \
  --manifest <work-dir>/baseline-manifest.json
```

Verify the baseline copy remained unchanged:

```text
<PYTHON> <skill-root>/scripts/skill_harness_snapshot.py verify \
  --manifest <work-dir>/baseline-manifest.json \
  --snapshot-only \
  --output <report-dir>/baseline-verification.json
```

Exit `0` on pass, non-zero on failure. Capture fails closed for sensitive-looking files and unsafe symlinks.

### `scripts/skill_harness_inventory.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_inventory.py --target <TARGET_SKILL_PATH> --output <report-dir>/inventory.json
```

Deterministic structural inventory only; not behavioral evidence.

### `scripts/skill_harness_audit.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_audit.py \
  --target <TARGET_SKILL_PATH> \
  --output <report-dir>/harness-audit.md \
  --json-output <report-dir>/harness-audit.json
```

The main score is structural and can saturate. Use auxiliary portability/integrity controls plus target-specific metrics before claiming improvement.

### `scripts/skill_harness_portability.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_portability.py \
  --target <TARGET_SKILL_PATH> \
  --profile portable|openai|claude|copilot|cursor \
  --output <report-dir>/portability.json
```

Validates the open Agent Skills core, relative/resource safety, name/directory identity, optional compatibility metadata, and host-adapter isolation. Host-specific discovery notes are informational adapters, not portable semantics.

### `scripts/skill_harness_host_matrix.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_host_matrix.py \
  --target <TARGET_SKILL_PATH> \
  --profiles all \
  --strict \
  --output <report-dir>/host-matrix.json
```

Runs the existing portability validator for `portable`, `openai`, `claude`, `copilot`, and `cursor` without changing those profile semantics. `--profiles` may also be a comma-separated subset. Exit non-zero when any selected profile fails; with `--strict`, warnings also fail the matrix.

### `scripts/run_self_tests.py`

```text
<PYTHON> <skill-root>/scripts/run_self_tests.py \
  --output <report-dir>/self-tests.json
```

Runs bundled zero-argument functions whose names start with `test_` using only the Python standard library. It fails closed when the tests directory is missing, no matching test modules exist, no test functions are discovered, a module import fails, or any test fails. Use `--tests-dir <path>` only for explicit alternate test fixtures. This is the portable self-test command; pytest remains optional developer tooling rather than a runtime requirement.

### `scripts/skill_harness_validate.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_validate.py \
  --target <TARGET_SKILL_PATH> \
  --profile portable|openai|claude|copilot|cursor \
  --output <report-dir>/validation.json
```

Exit `0` for `accept` or `accept with risks`; non-zero for `reject`. A publish/package gate may still require `accept` only.

### `scripts/skill_harness_package.py`

```text
<PYTHON> <skill-root>/scripts/skill_harness_package.py \
  --target <TARGET_SKILL_PATH> \
  --output <artifact-dir>/skill.zip \
  --report <report-dir>/package-validation.json \
  --profile portable|openai|claude|copilot|cursor \
  --strict
```

Packaging semantics:

1. preflight authored and canonical package/report paths;
2. reject wrong extensions, in-target outputs, symlink cycles, and package/report aliases;
3. validate before mutation;
4. stage ZIP and receipt privately;
5. build a deterministic archive whose single root directory equals `SKILL.md:name`;
6. verify ZIP CRC and root shape;
7. hash the exact staged package;
8. atomically commit package + report while preserving previous outputs as backups;
9. restore last-good outputs on failure; preserve/report recovery paths if rollback is incomplete;
10. never overwrite a prior passing report merely to record a failed attempt.

Package receipts contain `source_tree_sha256`, `package_sha256`, byte/file counts, validation result, profile, and recovery information.

## Packaging exclusions

Exclude VCS metadata, caches, generated report/artifact/scratch/build directories, nested ZIPs, coverage outputs, and bytecode. Reject symlink entries in portable packages rather than depending on host-specific ZIP symlink behavior.

Do not include secrets, credentials, baseline snapshots, evaluator run outputs, benchmark reports, or unrelated generated evidence in the final skill archive.

## Final freeze

After all gates pass, freeze the candidate. Package only that exact tree. Compare the current target tree hash with the package receipt's `source_tree_sha256` before claiming the delivered ZIP corresponds to the final candidate.
