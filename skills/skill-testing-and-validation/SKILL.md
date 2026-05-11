---
name: skill-testing-and-validation
description: use when asked to create, improve, validate, run, lint, debug, or minimally fix tests, validators, build commands, test commands, lint commands, runners, benchmark tools, packaging checks, or small polyglot technical packages, especially reusable skill packages and their scripts. supports python, javascript/typescript, shell, and detectable multi-language projects. do not use for generic feature implementation, security review, documentation-only work, governance artifacts, or edits to fixtures, expected outputs, benchmark evidence, secrets, .git, or blocked files without explicit authorization.
---

# Skill Testing and Validation

## Mission

Operate as an evidence-first testing and validation workflow for skill packages, auxiliary scripts, validators, runners, linters, benchmark tools, packagers, and small multi-language technical projects. Prefer local, repeatable commands and minimal patches over broad rewrites.

This skill does not depend on MCP. Use the filesystem and available terminal/container tools directly. If commands cannot be executed, return a plan and limitations; do not claim validation.

## Core rules

- Establish a baseline before any fix: inspect files, identify commands, run the relevant failing command when possible, and preserve the original failure evidence.
- Never state that build, tests, lint, validators, or packaging passed unless command output or supplied evidence proves it.
- Classify failures before fixing: `build`, `test`, `lint`, `environment`, `configuration`, `packaging`, `validator`, or `unknown`.
- Apply the smallest safe patch that addresses the observed failure. Do not improve unrelated code opportunistically.
- Do not edit `.git`, secrets, credentials, locked paths, benchmark evidence, generated baseline reports, fixtures, golden files, snapshots, expected outputs, or user-declared read-only files unless the user explicitly authorizes that exact path category.
- Do not convert this workflow into generic feature implementation. Stay within tests, validation, command discovery, runners, linters, build/test plumbing, and failure repair.
- Keep measured evidence separate from recommendations and unexecuted plans.

## Mode router

Choose one primary mode, then stage supporting modes only when required by the user's request.

| Mode | Use for | Primary output |
|---|---|---|
| `research-testability` | Analyze structure, languages, test patterns, commands, risks, and gaps | Testability research with command candidates and priorities |
| `plan-tests` | Turn research into phased test/validator work | Phase plan with risks, gates, and priority |
| `generate-tests` | Generate tests, cases, scenario suites, or validator cases | Test/case artifacts or patch plan with assumptions |
| `implement-test-phase` | Implement one named phase from a plan | Minimal file changes plus build/test/lint evidence |
| `run-build` | Discover and execute build/compile command | Build status with command and output summary |
| `run-tests` | Discover and execute test/validator command | Test status with command and failure details |
| `run-lint` | Discover and execute lint/format check | Lint status with command, changed files, or failures |
| `fix-failures` | Repair build/test/lint/validator failures | Baseline, classification, patch, rerun evidence |
| `validation-report` | Summarize evidence after validation work | Command log, results, changed files, residual risk |

## Required inputs

Resolve or conservatively infer these before mutating files:

1. Target root and requested scope.
2. Primary mode from the mode router.
3. Writable paths and blocked paths.
4. Baseline evidence source: command output, supplied log, or static inspection when execution is unavailable.
5. Candidate build, test, lint, validation, and packaging commands.
6. Acceptance gates and final artifact expectation.

Use [`examples/prompt-scenarios.md`](examples/prompt-scenarios.md) for activation, non-activation, ambiguous, and failure examples when behavior is unclear. Use [`evals/activation-scenarios.json`](evals/activation-scenarios.json) as planned activation coverage; do not report scenario metrics unless those prompts were actually executed.

## Workflow

### 1. Resolve target and scope

Identify the target root, requested scope, writable paths, blocked paths, language/runtime hints, and final artifact expectation. If the user gave a specific phase, file, command, or package, restrict work to that scope.

### 2. Inspect before editing

For `research-testability`, `plan-tests`, `generate-tests`, `implement-test-phase`, and `fix-failures`, inspect the target before writing files:

- project markers: `SKILL.md`, package.json, pyproject.toml, pytest.ini, tox.ini, Makefile, *.sln, *.csproj, go.mod, Cargo.toml, pom.xml, build.gradle, deno.json, bun.lockb;
- source and tests: tests/, test/, spec/, __tests__/, *.test.*, *.spec.*, *_test.go, test_*.py, *_test.py;
- validators and runners: files under `scripts/`, `bin/`, `tools/`, `evals/`, `benchmarks/`, `validators/`;
- existing command documentation in `README*`, Makefile, package scripts, CI workflows, and skill references.

Use [`scripts/discover_commands.py`](scripts/discover_commands.py) when command discovery needs to be repeatable or reported as JSON.

### 3. Establish baseline evidence

Before applying fixes, run the narrowest relevant command that reproduces the issue. If no command exists, record that the baseline is static inspection only.

Capture:

- exact command;
- working directory;
- exit status;
- relevant stdout/stderr excerpt;
- timestamp if available;
- failure classification.

Use [`scripts/classify_failure.py`](scripts/classify_failure.py) when failure output is long or ambiguous.

### 4. Plan or generate tests

For test generation, follow a research-plan-implement sequence:

1. research structure, commands, existing patterns, testability, and gaps;
2. plan phases by priority, dependency order, complexity, and risk;
3. generate or implement one phase at a time;
4. run build/test/lint gates after each implemented phase when possible.

Load [`references/testability-strategy.md`](references/testability-strategy.md) and [`references/acceptance-criteria.md`](references/acceptance-criteria.md) for detailed planning rules. Use [`assets/templates/testability-research.md.template`](assets/templates/testability-research.md.template) and [`assets/templates/test-plan.md.template`](assets/templates/test-plan.md.template) only when a durable artifact is useful.

### 5. Run commands safely

Prefer project-declared commands over guessed commands. Prefer scoped commands over whole-repository commands when the user requested a narrow scope. Do not install dependencies, alter lockfiles, or run destructive scripts unless explicitly authorized.

Load [`references/command-selection.md`](references/command-selection.md) for command priority, language heuristics, and safe fallbacks.

### 6. Fix failures minimally

For `fix-failures`:

1. baseline the failure;
2. classify it using [`references/failure-classification.md`](references/failure-classification.md);
3. identify the smallest target file set;
4. patch only files needed to address the observed failure;
5. rerun the same command;
6. optionally run adjacent gates, such as lint after test changes or tests after build repair;
7. report accepted, partial, or blocked status.

If a failure indicates missing dependencies, unavailable runtime, permission denial, network restriction, incompatible toolchain, or missing secret/configuration, report `environment` or `configuration` and avoid fabricating a code fix.

### 7. Report evidence

When the requested deliverable is a packaged skill archive, use [`scripts/package_skill.py`](scripts/package_skill.py) only after validation gates pass.


For `validation-report`, use [`assets/templates/validation-report.md.template`](assets/templates/validation-report.md.template) as the default shape. Always include command outcomes and clearly identify not-run gates.

## Output contract

Every final response for validation work must include applicable sections:

1. Mode and target path.
2. Scope and blocked paths protected.
3. Baseline evidence before fixes.
4. Commands executed with pass/fail/not-run status.
5. Failure classification and root cause hypothesis.
6. Files created or changed.
7. Validation after changes.
8. Remaining risks and limitations.
9. Next recommended action, if any.

## Stop conditions

Stop and report a blocker when:

- target root cannot be identified;
- the requested repair requires editing blocked paths without explicit authorization;
- command execution requires missing credentials, destructive operations, network access, or dependency installation not authorized by the user;
- validation cannot be reproduced and no failure evidence is supplied;
- the fix would require changing production behavior outside test/validator/build/lint plumbing;
- generated tests would require inventing domain facts not present in source, existing tests, docs, or user-provided evidence.
