---
name: skill-testing-and-validation
description: use when the primary task is to plan, generate, run, validate, diagnose, or minimally repair tests, validators, build/test/lint commands, gate runners, package checks, benchmark helpers, or small polyglot validation packages. use for evidence-backed gate execution and test-plumbing fixes; do not use as the primary workflow for generic feature implementation, generic bug diagnosis, security review, documentation/governance work, standalone oracle engineering, or edits to protected fixtures, expected outputs, benchmark evidence, secrets, .git, or other blocked paths without exact authorization.
---

# Skill Testing and Validation

## Purpose and activation boundary

Own evidence-first testing and validation. Given the same material target bytes, supported environment, scope, and evidence, converge on the same relevant commands, failure categories, gate states, reliability interpretation, and conclusion wherever objective mechanisms can decide them.

Use this skill when the requested outcome is a test/validator/build/lint/package gate, deterministic test planning/generation, failure classification, validation evidence, or a minimal repair to testing/validation plumbing.

Do not use it as the primary owner for production feature implementation, generic application debugging, security audits, documentation/governance work, or a standalone executable-oracle design task. It may route to advanced testing strategies, but it does not become a fuzzing, mutation, or oracle-design framework. Production behavior changes are out of scope unless strictly required test/validator/build/lint/packaging plumbing is the observed cause.

## Mode router

Choose one primary mode before acting.

| Mode | Use for | Primary output |
|---|---|---|
| `research-testability` | Inspect structure, commands, risks, oracle/reliability gaps, and strategy | Testability research + command candidates |
| `plan-tests` | Convert evidence into bounded test/validator phases | Phase plan with gates, oracle, reliability, risks |
| `generate-tests` | Generate tests/cases/validator scenarios | Test artifacts or patch plan with oracle provenance |
| `implement-test-phase` | Implement one named test/validator phase | Minimal changes + gate evidence |
| `run-build` | Execute the selected build/compile gate | Build receipt |
| `run-tests` | Execute the selected test gate | Test receipt; stability evidence when required |
| `run-lint` | Execute a check-only lint gate | Lint receipt |
| `fix-failures` | Repair observed build/test/lint/validator/package failures | Baseline, diagnosis, minimal patch, exact-gate rerun |
| `validation-report` | Summarize completed validation evidence | Deterministic validation report |

## Critical rules

- Preserve a baseline before every repair. No repair without baseline evidence.
- Never claim build, test, lint, validator, or packaging success without executed or supplied evidence.
- Gate states are only `pass`, `fail`, `blocked`, or `not-run`; failure categories are only `build`, `test`, `lint`, `validator`, `environment`, `configuration`, `packaging`, or `unknown`.
- Preserve the exact target-command exit code in receipts; never replace it with a runner exit code.
- Gate execution, reliability/stability, and test/oracle effectiveness are separate evidence dimensions; a green gate proves neither stability nor adequacy.
- Never retry until green. If reliability matters, preserve every attempt and assess stability with a declared bounded run count.
- Generated or changed semantic tests require explicit test intent and an adequate oracle source. Do not derive a bug-finding expected value only from a suspected faulty SUT.
- Coverage, mutation score, fuzz counts, and similar values are proxy metrics, not correctness proof.
- Protect `.git`, secrets, credentials, fixtures, snapshots, expected outputs, golden files, benchmark/baseline evidence, frozen evaluators, and user-declared read-only paths unless the exact category/path is authorized.
- Repair from diagnostics, not taste. Apply the smallest supported patch and rerun the exact failed gate before adjacent gates.
- Never weaken validators, tests, thresholds, fixtures, expected outputs, reliability requirements, or oracle quality to manufacture a pass.
- After final applicable gates pass, freeze the candidate. Any later material edit invalidates affected evidence and requires rerun.

## Quick-start workflow

1. Resolve one canonical target root, choose the mode, and record scope, required gates, writable/protected paths, baseline source, requested output, and available capabilities.
2. Discover commands deterministically. Precedence is: exact user command -> approved frozen plan command -> helper-selected project command; never command-shop for an easier pass. See [`references/command-selection.md`](references/command-selection.md).
3. Before repair, preserve original target state plus the narrowest relevant failing gate/receipt. Static inspection may establish context but cannot prove a runtime pass.
4. For test design/generation, state intent and oracle source first; map known requirements/contracts/invariants to tests. See [`references/test-effectiveness.md`](references/test-effectiveness.md) and, only when needed, [`references/advanced-test-strategies.md`](references/advanced-test-strategies.md).
5. Execute safe gates with machine-readable receipts. For skill packages, use the structural validator before packaging; a read-only gate that mutates material target bytes is not final acceptance evidence without explicit re-baselining.
6. When flakiness/nondeterminism is material, run bounded stability assessment and interpret it separately from the gate result. See [`references/test-reliability.md`](references/test-reliability.md).
7. Classify failure formally, patch only authorized testing/validation plumbing, verify protected paths, then rerun the exact same gate/argv and working directory first. See [`references/failure-classification.md`](references/failure-classification.md).
8. Compute final required-gate conclusion with fixed precedence: any `fail` -> fail; else any `blocked` -> blocked; else all required applicable gates pass and at least one ran -> pass; otherwise not-run. Apply reliability/oracle/effectiveness overlays separately, then freeze/package only the validated candidate.

## Direct resource map

Load only the branch that changes the decision; all required Markdown is directly reachable from this file.

- [`references/acceptance-criteria.md`](references/acceptance-criteria.md): hard completion gates, overall conclusion, skill-package gates, proxy/evidence labels.
- [`references/command-selection.md`](references/command-selection.md): command precedence, tie-breaks, working directory, multi-runtime behavior, safe execution.
- [`references/failure-classification.md`](references/failure-classification.md): allowed failure categories, precedence, gate-state mapping, diagnostic repair.
- [`references/testability-strategy.md`](references/testability-strategy.md): research/plan/generation phase contract and priorities.
- [`references/test-effectiveness.md`](references/test-effectiveness.md): test intent, oracle provenance, behavioral coverage, proxy limits.
- [`references/test-reliability.md`](references/test-reliability.md): hermeticity, flakiness, bounded repetition, stability interpretation.
- [`references/advanced-test-strategies.md`](references/advanced-test-strategies.md): conditional property/stateful, metamorphic/differential, fuzz, contract, mutation routing.
- [`references/host-portability.md`](references/host-portability.md): capability-based cross-host behavior and degraded mode.
- [`examples/prompt-scenarios.md`](examples/prompt-scenarios.md): activation, ambiguity, anti-cheating, reliability/oracle, and delivery-boundary examples.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned activation/non-activation coverage only; never treat it as executed evidence unless a harness actually runs it.

## Stop or block early

Stop or return a bounded partial result when target identity is ambiguous; repair lacks preservable baseline evidence; execution needs missing credentials, destructive actions, unapproved dependency installation, or unavailable runtime/network; required repair touches protected evidence without exact authorization; the fix requires production behavior changes outside testing/validation plumbing; test generation would invent domain facts or use a circular faulty-SUT oracle; passing requires weakening evidence/thresholds/reliability/oracle quality; or two consecutive repair rounds fail to improve the same objective diagnostic set.

## Input normalization and portable capabilities

Before mutation, normalize and record: canonical target root; mode; requested scope and gates; writable/protected paths; baseline source; explicit user commands; final artifact/report expectation; detected capabilities/environment fingerprint; test intent/oracle/contracts when semantic tests are material; reliability requirement; and requested proxy metrics with their limited interpretation.

The semantic core is host-neutral Agent Skills content. Detect filesystem read/write, command execution, Python 3.10+ for bundled helpers, required project runtimes/tools, optional advanced-test capabilities only when selected by problem shape, and artifact delivery when requested. Load [`references/host-portability.md`](references/host-portability.md) when runtime/host assumptions affect execution. Missing required capability means `blocked` or `not-run`, never inferred pass or silent substitute installation.

Use canonical resolved paths. If multiple target roots remain plausible and choosing one changes what is executed or mutated, stop as `blocked` rather than guessing.

## Deterministic workflow

### 1. Discover target and environment

Inspect package/project markers, existing tests/validators, scripts, CI/task files, command documentation, behavioral contracts, and relevant sources of nondeterminism. For executable work, capture:

```text
<PYTHON> scripts/environment_fingerprint.py <TARGET> --format json
```

The fingerprint intentionally contains no timestamp and never dumps arbitrary environment variables. It records relevant platform/Python/tool identity plus a safe execution-context subset such as locale, timezone, Python hash seed, and CI presence when available.

### 2. Establish baseline before repair

Before any fix:

1. preserve the original target state or equivalent immutable snapshot when mutation is planned;
2. identify the narrowest relevant command;
3. execute it when safe/available, or preserve supplied failure evidence;
4. record command, canonical working directory, environment fingerprint, material target identity, exit code, output evidence, gate state, and classification.

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

### 4. Design tests against intent and oracle evidence

For `research-testability`, `plan-tests`, `generate-tests`, and implementation phases, load [`references/test-effectiveness.md`](references/test-effectiveness.md).

Before generated tests become acceptance evidence:

- state the test intent;
- identify the oracle source independently enough for that intent;
- map known requirements/contracts/invariants/failure classes to tests where source truth exists;
- keep coverage/mutation and similar values labeled as proxy metrics;
- if ordinary example tests are insufficient, route through [`references/advanced-test-strategies.md`](references/advanced-test-strategies.md) by problem shape and available capability.

Do not invent domain facts or expected outcomes to fill a test suite.

### 5. Execute gates with receipts

For Agent Skills packages, the canonical structural validator is `scripts/validate_skill_package.py`. It validates the root `SKILL.md`, parses YAML frontmatter with a real YAML parser when available and a conservative portable fallback otherwise, and rejects malformed frontmatter before package promotion. `discover_commands.py` selects this validator as the default `validator` gate whenever a root `SKILL.md` is present.

For safe argv-based commands, use:

```text
<PYTHON> scripts/run_gate.py --target <TARGET> --gate <build|test|lint|validator|packaging> --execute --format json
```

For an explicit command, pass a JSON argv array with `--argv-json`. Without `--execute`, the runner must return `not-run` and must not execute the command.

The public receipt contract remains `receipt_version: 1`. Additive evidence includes material target identity before/after execution and whether a read-only gate mutated material target bytes.

Every receipt must contain at least:

- `receipt_version`;
- target and canonical working directory;
- material target identity before/after execution;
- gate;
- relevant environment fingerprint;
- exact argv/display command and source;
- gate state;
- failure classification when applicable;
- exact target-command exit code, or `null` when no process started;
- bounded stdout/stderr evidence and hashes.

Machine-readable receipt shape is authoritative over prose summary. A read-only gate that changes material target bytes cannot be used as final acceptance evidence without an explicit mutation/re-baseline decision.

### 6. Assess stability only when material

Load [`references/test-reliability.md`](references/test-reliability.md) when flakiness or nondeterminism is material. Stability is orthogonal to the four gate states and does not create a new failure category.

Use an explicit bounded attempt count:

```text
<PYTHON> scripts/assess_stability.py --target <TARGET> --gate <GATE> --runs <N> --execute --receipt <RECEIPT.json>
```

Do not stop after the first successful retry. When reliability is a required acceptance condition, `unstable` fails that condition, `inconclusive` blocks it, and `not-assessed` leaves it not-run.

### 7. Classify failures formally

Use [`references/failure-classification.md`](references/failure-classification.md) and, when useful:

```text
<PYTHON> scripts/classify_failure.py --gate <GATE> --exit-code <CODE> --format json < log.txt
```

Precedence is fixed: environment evidence overrides configuration; configuration overrides gate classification; otherwise an explicit gate classifies opaque non-zero failures; without gate context, fixed pattern priority is used. `unknown` means evidence is insufficient, not permission to guess.

### 8. Repair minimally and protect evidence

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

### 9. Rerun the exact failed gate

After repair, rerun the same gate with the same selected command/argv and canonical working directory first. Only after that gate passes may adjacent gates run.

Do not substitute a different command to convert a failure into a pass unless the original selection was proven invalid by higher-precedence evidence; record that as a configuration/command-selection correction.

### 10. Validate idempotency and required reliability

Read-only validators should produce the same machine-readable result for the same material target bytes and comparable environment. Run deterministic validators twice when idempotency is part of acceptance. Volatile timestamps or random IDs are forbidden in validator evidence unless explicitly excluded by a normalization contract.

If reliability is a declared hard condition, evaluate its stability receipt separately from the single-run gate receipt using [`references/test-reliability.md`](references/test-reliability.md).

### 11. Compute final conclusion

For required gate states only, use fixed precedence:

1. any `fail` -> overall `fail`;
2. otherwise any `blocked` -> overall `blocked`;
3. otherwise at least one required `pass` and all other required gates `pass` -> overall `pass`;
4. otherwise -> overall `not-run`.

Optional gates may be `not-run` without downgrading an otherwise passing required set. Required reliability/oracle/effectiveness conditions remain separate acceptance overlays; do not rewrite the four-state gate taxonomy to encode them.

### 12. Freeze and report

After the last applicable pass:

- do not make cleanup/cosmetic edits;
- if any material file changes, rerun affected gates;
- preserve receipts, exact command evidence, identities, and stability evidence when used;
- package only the frozen candidate when packaging is requested.

For skill packaging, use [`scripts/package_skill.py`](scripts/package_skill.py) only after required validation passes. Package and report outputs must remain outside the validated target tree and must not alias one another. The packager stages the archive before atomic replacement and emits its SHA-256 receipt.

## Integration surface

`contracts/integration-manifest.json` declares `skill-opt.validation-gate-receipt` v1. `scripts/run_gate.py` receipts are therefore a public machine-readable surface when consumed by an orchestrator. New identity/context fields are additive and keep v1 consumers valid. Any incompatible receipt change requires a version bump and integration impact analysis; local validator success alone is insufficient for an ecosystem-safe claim.

## Output contract

Every validation response/report must identify, when applicable:

1. mode, target, scope, and protected paths;
2. baseline identity/evidence before fixes;
3. environment fingerprint relevant to executed gates;
4. discovered candidates and selected commands;
5. exact commands, working directories, exit codes, and states;
6. failure classification plus root-cause hypothesis;
7. test intent, oracle source, and behavioral coverage when generated/assessed tests are material;
8. reliability requirement and stability evidence when material;
9. proxy metrics separately from correctness evidence;
10. files changed;
11. same-gate rerun evidence;
12. adjacent/final gates;
13. overall gate state using the fixed conclusion rule plus separate acceptance overlays;
14. not-run/blocked items and residual risk;
15. which evidence is executed, supplied, static, planned, or blocked.

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
- bug-finding tests require an oracle that can only be copied from a suspected faulty SUT;
- the only way to pass is weakening a validator, test, threshold, expected result, reliability requirement, or oracle;
- two consecutive repair rounds fail to improve the same objective diagnostic set.
