# Testability strategy

Use this reference for `research-testability`, `plan-tests`, `generate-tests`, and `implement-test-phase`.

## Research checklist

Inspect the target in this order:

1. **Package role**: skill package, script bundle, CLI tool, validator, runner, benchmark helper, library, or application fragment.
2. **Language markers**: package.json, pyproject.toml, pytest.ini, *.sln, *.csproj, go.mod, Cargo.toml, pom.xml, build.gradle, Makefile, deno.json.
3. **Existing tests and validators**: tests/, test/, spec/, __tests__/, `evals/`, `validators/`, `benchmarks/`, `scripts/validate*`, `scripts/*test*`.
4. **Command sources**: README, Makefile, package scripts, CI workflows, pyproject tool sections, comments in validators, task files.
5. **Testability risks**: side effects, filesystem writes, network calls, nondeterminism, time dependence, environment variables, credentials, generated outputs, language/runtime mismatch.
6. **Coverage gaps**: important files without direct tests, validators without negative cases, scripts without argument error tests, packagers without exclusion tests, linter/build commands not exercised.

## Priority model

Rank work by risk and leverage:

- **P0**: packaging, validators, build/test/lint runners, command discovery, failure-prone scripts, safety-critical exclusions.
- **P1**: core parsing/classification logic, test-generation helpers, schema validators, report generators.
- **P2**: edge-case expansions, regression tests for known failures, usability tests for CLI errors.
- **P3**: broad coverage expansion with low defect risk.

## Phase design

A good phase is independently valuable and verifiable. Keep phases small enough that a failed build or test can be attributed to a limited patch.

Recommended phase shape:

- objective;
- files to inspect;
- files to create or modify;
- scenarios and expected assertions;
- build/test/lint gates;
- risks and rollback notes.

## Test/case generation rules

- Match existing framework, naming, fixtures, assertion style, and directory conventions.
- Prefer deterministic unit tests for pure parsing/validation code.
- Use temporary directories for filesystem behavior; do not write into real fixtures or benchmark evidence.
- Cover happy path, empty input, malformed input, boundary conditions, and representative error paths.
- For scripts, include CLI argument validation and non-zero exit behavior where practical.
- For validators, include both accepted and rejected cases. Do not weaken the validator or expected output to make tests pass.
- For skill packages, validate frontmatter, referenced local files, absence of placeholders, scenario schemas, executable script syntax, and package exclusions.

## Generated tests versus implemented tests

When asked to generate tests without applying them, return proposed file paths and test content or case tables. When asked to implement, write files only inside allowed scope and run gates afterward.
