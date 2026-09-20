---
name: skill-testing-and-validation
description: use when asked to create, improve, validate, run, lint, debug, or minimally fix tests, validators, build commands, test commands, lint commands, runners, benchmark tools, packaging checks, or small polyglot technical packages, especially reusable skill packages and their scripts. supports python, javascript/typescript, shell, and detectable multi-language projects. do not use for generic feature implementation, security review, documentation-only work, governance artifacts, or edits to fixtures, expected outputs, benchmark evidence, secrets, .git, or blocked files without explicit authorization.
---

# Skill Testing and Validation

## Mission

Operate as an evidence-first testing and validation workflow. Given the same target bytes, supported environment, scope, and evidence, converge on the same relevant commands, failure categories, gate states, and conclusion wherever objective mechanisms can decide them.

Remain a testing/validation skill. Do not become a generic implementation workflow: production behavior changes are out of scope unless they are strictly test/validator/build/lint plumbing required to restore an observed gate.

## Portable core and capabilities

The semantic core is host-neutral Agent Skills content. `agents/openai.yaml` is an optional OpenAI adapter, not a correctness dependency.

Before execution, detect capabilities rather than branching on host name:

- filesystem read;
- filesystem write for baseline/candidate evidence;
- command execution;
- Python 3.10+ for bundled deterministic helpers;
- required project runtimes/tools;
- artifact delivery when a ZIP/report is requested.

Load [`references/host-portability.md`](references/host-portability.md) when host/runtime assumptions affect execution. If a required capability is absent, mark the affected gate `blocked` or `not-run`; never infer a pass.

## Core invariants

- Preserve a baseline before every repair. No repair without baseline evidence.
- Never claim build, test, lint, validator, or packaging success without executed or supplied evidence.
- Preserve exact target-command exit codes in receipts; do not replace them with the runner's exit code.
- Classify failures only as: `build`, `test`, `lint`, `validator`, `environment`, `configuration`, `packaging`, or `unknown`.
- Gate states are only: `pass`, `fail`, `blocked`, or `not-run`.
- Protect `.git`, secrets, credentials, fixtures, snapshots, expected outputs, golden files, benchmark evidence, baseline evidence, and user-declared read-only paths unless the user explicitly authorizes the exact protected category/path.
- Repair from diagnostics, not taste. Apply the smallest supported patch and rerun the exact failing gate before adjacent gates.
- Do not weaken validators, tests, thresholds, fixtures, or expected outputs to manufacture a pass.
- Once the final applicable gates pass, freeze the candidate. Any later edit invalidates affected evidence and requires rerun.

## Mode router

Choose one primary mode.

| Mode | Use for | Primary output |
|---|---|---|
| `research-testability` | Inspect structure, runtimes, commands, risks, and gaps | Testability research plus deterministic command candidates |
| `plan-tests` | Turn research into bounded test/validator phases | Phase plan with gates and risks |
| `generate-tests` | Generate tests/cases/validator scenarios | Test artifacts or a patch plan |
| `implement-test-phase` | Implement one named test/validator phase | Minimal changes plus gate evidence |
| `run-build` | Select and execute build/compile gate | Build receipt |
| `run-tests` | Select and execute test gate | Test receipt |
| `run-lint` | Select and execute check-only lint gate | Lint receipt |
| `fix-failures` | Repair observed build/test/lint/validator/package failures | Baseline, diagnosis, minimal patch, same-gate rerun |
| `validation-report` | Summarize completed validation evidence | Deterministic gate/report summary |

## Input normalization

Before mutation, normalize and record:

1. one canonical target root;
2. mode;
3. requested scope and required gates;
4. writable paths and protected paths;
5. baseline source: executed command, supplied log, or static evidence;
6. explicit user-provided commands, if any;
7. final artifact/report expectation;
8. detected capabilities and environment fingerprint.

Use canonical resolved paths. If multiple target roots remain plausible and choosing one changes what is executed or mutated, stop as `blocked` rather than guessing.

## Deterministic workflow

### 1. Discover target and environment

Inspect package/project markers, existing tests/validators, scripts, CI/task files, and command documentation. For executable work, capture:

```text
<PYTHON> scripts/environment_fingerprint.py <TARGET> --format json
```

The fingerprint intentionally contains no timestamp. It records relevant platform, Python, tool availability, paths, and versions when obtainable.

### 2. Establish baseline before repair

Before any fix:

1. preserve the original target state or equivalent immutable snapshot when mutation is planned;
2. identify the narrowest relevant command;
3. execute it when safe/available, or preserve supplied failure evidence;
4. record command, canonical working directory, environment fingerprint, exit code, output evidence, gate state, and classification.

Static inspection alone may establish a non-executable baseline, but it cannot prove a runtime gate passed.

### 3. Discover and select commands deterministically

Use:

```text
<PYTHON> scripts/discover_commands.py <TARGET> --format json
```

Load [`references/command-selection.md`](references/command-selection.md) for precedence. The helper emits all candidates plus exactly one selected command per discoverable gate using fixed ranks and tie-breakers.

Precedence outside the helper is:

1. exact user-provided command;
2. command frozen in an approved research/plan artifact for this target;
3. helper-selected project command.

Never replace a higher-precedence command merely because a lower-precedence command is easier to pass.

### 4. Execute gates with receipts

For safe argv-based commands, use:

```text
<PYTHON> scripts/run_gate.py --target <TARGET> --gate <build|test|lint|validator|packaging> --execute --format json
```

For an explicit command, pass a JSON argv array with `--argv-json`. Without `--execute`, the runner must return `not-run` and must not execute the command.

Every receipt must contain at least:

- `receipt_version`;
- target and canonical working directory;
- gate;
- relevant environment fingerprint;
- exact argv/display command and source;
- gate state;
- failure classification when applicable;
- exact target-command exit code, or `null` when no process started;
- bounded stdout/stderr evidence and hashes.

Machine-readable receipt shape is authoritative over prose summary.

### 5. Classify failures formally

Use [`references/failure-classification.md`](references/failure-classification.md) and, when useful:

```text
<PYTHON> scripts/classify_failure.py --gate <GATE> --exit-code <CODE> --format json < log.txt
```

Precedence is fixed: environment evidence overrides configuration; configuration overrides gate classification; otherwise an explicit gate classifies opaque non-zero failures; without gate context, fixed pattern priority is used. `unknown` means evidence is insufficient, not permission to guess.

### 6. Repair minimally and protect evidence

For `fix-failures` or implementation phases:

1. identify one causal diagnostic/root-cause hypothesis;
2. identify the smallest candidate file set;
3. reject protected evidence mutations unless specifically authorized;
4. patch only test/validator/build/lint/packaging plumbing needed for the observed failure;
5. do not change unrelated production behavior.

Before accepting a repair against a preserved baseline, use when applicable:

```text
<PYTHON> scripts/validate_protected_paths.py --baseline <BASELINE> --candidate <CANDIDATE> --format json
```

If two consecutive repair rounds do not improve the same objective failure set, stop that repair branch and report the unresolved diagnostic.

### 7. Rerun the exact failed gate

After repair, rerun the same gate with the same selected command/argv and canonical working directory first. Only after that gate passes may adjacent gates run.

Do not substitute a different command to convert a failure into a pass unless the original selection was proven invalid by higher-precedence evidence; record that as a configuration/command-selection correction.

### 8. Validate idempotency where relevant

Read-only validators should produce the same machine-readable result for the same target bytes and environment. Run deterministic validators twice when idempotency is part of acceptance. Volatile timestamps or random IDs are forbidden in validator evidence unless explicitly excluded by a normalization contract.

### 9. Compute final gate conclusion

For required gates only, use fixed precedence:

1. any `fail` -> overall `fail`;
2. otherwise any `blocked` -> overall `blocked`;
3. otherwise at least one required `pass` and all other required gates `pass` -> overall `pass`;
4. otherwise -> overall `not-run`.

Optional gates may be reported `not-run` without downgrading an otherwise passing required set.

### 10. Freeze and report

After the last applicable pass:

- do not make cleanup/cosmetic edits;
- if any file changes, rerun affected gates;
- preserve receipts and exact command evidence;
- package only the frozen candidate when packaging is requested.

For skill packaging, use [`scripts/package_skill.py`](scripts/package_skill.py) only after required validation passes. It stages the archive before atomic replacement and emits its SHA-256 receipt.

## Progressive references

- [`references/command-selection.md`](references/command-selection.md): precedence, ranks, tie-breakers, canonical working directory.
- [`references/failure-classification.md`](references/failure-classification.md): formal categories and state mapping.
- [`references/acceptance-criteria.md`](references/acceptance-criteria.md): hard gates and final acceptance.
- [`references/testability-strategy.md`](references/testability-strategy.md): research/plan/test-generation guidance.
- [`references/host-portability.md`](references/host-portability.md): capability-based cross-host behavior.
- [`examples/prompt-scenarios.md`](examples/prompt-scenarios.md): activation and boundary examples.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned prompt coverage only; never report it as executed behavioral evidence unless a harness actually runs it.

## Integration surface

`contracts/integration-manifest.json` declares `skill-opt.validation-gate-receipt` v1. `scripts/run_gate.py` receipts are therefore a public machine-readable surface when consumed by an orchestrator. Any incompatible receipt change requires a version bump and integration impact analysis; local validator success alone is insufficient for an ecosystem-safe claim.

## Output contract

Every validation response/report must identify, when applicable:

1. mode, target, scope, and protected paths;
2. baseline identity/evidence before fixes;
3. environment fingerprint relevant to executed gates;
4. discovered candidates and selected commands;
5. exact commands, working directories, exit codes, and states;
6. failure classification plus root-cause hypothesis;
7. files changed;
8. same-gate rerun evidence;
9. adjacent/final gates;
10. overall state using the fixed conclusion rule;
11. not-run/blocked items and residual risk;
12. which evidence is executed, supplied, static, or planned.

Use [`assets/templates/validation-report.md.template`](assets/templates/validation-report.md.template) for durable reports.

## Stop conditions

Stop as `blocked` or return a bounded partial result when:

- target identity is ambiguous;
- repair is requested but no baseline evidence can be preserved;
- a required command needs missing credentials, destructive actions, unapproved dependency installation, or unavailable runtime/network;
- the only repair requires modifying protected evidence without exact authorization;
- the fix requires production behavior changes outside testing/validation plumbing;
- the selected gate cannot be reproduced and no supplied failure evidence exists;
- generated tests require inventing domain facts absent from source/tests/docs/user evidence;
- the only way to pass is weakening a validator, test, threshold, or expected result;
- two consecutive repair rounds fail to improve the same objective diagnostic set.
