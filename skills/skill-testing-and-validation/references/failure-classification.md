# Failure classification

Use this reference when a command fails or when the user supplies logs.

## Categories

### `build`

Compile, type-check, import, bundling, or syntax failures before test assertions run.

Signals:

- C#: `CS0246`, `CS0103`, `CS1061`, `MSB`, `NETSDK`;
- TypeScript: `TS2304`, `TS2322`, `TS2339`, `tsc` errors;
- Python: `SyntaxError`, import failure during collection, `py_compile` failure;
- Go/Rust/Java compile errors;
- bundler/transpiler failures.

Repair pattern: fix missing imports, names, signatures, syntax, type mismatches, or project references. Rerun build before tests.

### `test`

The project builds, but assertions, setup, fixtures, or test runtime fail.

Signals: assertion diffs, expected/actual mismatch, failed test names, stack traces inside test execution, non-zero test summary.

Repair pattern: determine whether code, test, or fixture is wrong. Do not edit expected outputs, golden files, snapshots, or fixtures unless explicitly authorized. Prefer correcting generated tests that misunderstood existing behavior.

### `lint`

Formatting, style, static analysis, or quality gate failures.

Signals: ESLint, Prettier, Ruff, Black, dotnet format, gofmt, rustfmt, shellcheck, markdownlint, yamllint.

Repair pattern: run check-only first when validating. Apply format/fix only when asked to fix. Avoid broad formatting of unrelated files.

### `environment`

The command cannot run because the runtime, dependency, binary, network, permission, or file system capability is unavailable.

Signals: `command not found`, missing interpreter, missing package manager, permission denied, read-only filesystem, network/DNS failure, timeout, out-of-memory, unavailable service.

Repair pattern: report the missing environment and provide exact setup or alternate static validation. Do not claim project failure.

### `configuration`

The project command or settings are wrong or incomplete.

Signals: missing config files, incompatible versions, invalid paths, malformed JSON/YAML/TOML, missing env var, unresolved workspace references, invalid package script.

Repair pattern: fix config only when within scope and not secret-dependent. Otherwise report required configuration.

### `validator`

A custom validation script fails because artifact structure, schema, local links, placeholders, or package hygiene violate the validator contract.

Repair pattern: fix the artifact unless the validator is clearly wrong. Do not weaken validators to pass.

### `packaging`

Archive creation or package validation fails.

Signals: missing entrypoint, wrong zip structure, oversized archive, forbidden files included, invalid frontmatter, package validator failure.

Repair pattern: fix structure or exclusions, then rebuild and validate archive.

### `unknown`

Insufficient evidence to classify. Request or run a narrower command if possible.

## Root-cause discipline

Always separate:

- observed failure text;
- classification;
- probable root cause;
- patch hypothesis;
- validation command.

Do not collapse environment/configuration failures into code failures. Do not change tests to match broken behavior without explicit product evidence.
