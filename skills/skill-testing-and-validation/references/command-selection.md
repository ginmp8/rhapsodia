# Deterministic command selection

Use this reference for `run-build`, `run-tests`, `run-lint`, `implement-test-phase`, and `fix-failures`.

## Canonical working directory

Default to the resolved target root. Use a subdirectory only when a higher-precedence command source explicitly belongs to that subproject. Record the canonical directory in every receipt.

## Precedence

Use the first available source:

1. exact user-provided command;
2. command frozen in an approved research/plan artifact for the same target/scope;
3. repository-level orchestrator target (`Makefile`/equivalent exact gate);
4. exact package-declared script (`build`, `test`, `lint`);
5. named package alternate (`compile`, `test:ci`, `format:check`, etc.);
6. runtime-standard command inferred from project markers;
7. conservative static/syntax fallback.

The bundled `discover_commands.py` implements filesystem-discoverable levels 3-7 with numeric ranks. It emits all candidates, their ranks, runtime availability, and one `selected` candidate per gate.

## Tie-breakers

When candidates share the same rank and confidence, sort by:

1. normalized source string;
2. normalized command string.

Report the competing candidates under `ambiguities`; do not choose by filesystem enumeration order, model preference, or whichever tool happens to be installed.

Runtime availability is evidence about executability, not a precedence override. A missing high-precedence tool produces an environment-blocked gate unless higher-precedence project evidence proves that command is invalid for the target.

## Gate-specific rules

### Build

Prefer declared orchestration/package scripts, then standard runtime build/type-check commands. For Python script bundles without a project build, `py_compile` is a syntax/build fallback, not semantic validation.

### Test

Prefer declared test commands. Use framework-standard commands only when markers support them. Do not auto-install a missing framework.

### Lint

Prefer check-only commands. Mutating format/fix commands are repair actions and require explicit intent.

### Validator

Prefer project-declared validators and package-integrity validators. A custom validator failure is not a test failure merely because it is implemented in a test framework.

### Packaging

Packaging is mutating output. Require an explicit output path when the command needs one. Do not select a placeholder command for execution.

## Multi-runtime projects

Discover candidates for every detected runtime. Selection remains global per requested gate using the same precedence/rank rules. If the user scopes a specific subproject/runtime, rerun discovery at that canonical scoped root rather than manually ignoring higher-ranked candidates.

## Safe execution

- Do not install dependencies or update lockfiles unless authorized.
- Do not deploy, publish, upload, delete, migrate, or mutate production state.
- Prefer argv execution over shell strings/pipelines.
- Preserve the exact selected command in the baseline and rerun receipt.
- A different post-fix command is a command-selection change and must be justified separately.
