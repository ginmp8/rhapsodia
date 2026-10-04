# Testability strategy

Use for `research-testability`, `plan-tests`, `generate-tests`, and `implement-test-phase`.

## Research order

1. Package role, requested scope, and known behavioral requirements/contracts/invariants.
2. Canonical target root and subprojects.
3. Language/runtime markers.
4. Existing tests, validators, runners, packagers, evals, benchmarks, and known oracle sources.
5. Command sources and deterministic precedence.
6. Environment/tool availability and version identity.
7. Side effects and reliability risks: network, time/timezone, locale, randomness/hash seed, ordering, concurrency, caches, credentials, generated outputs, and mutable fixtures.
8. Behavioral gaps: required behaviors/failure classes not mapped to tests.
9. Structural/proxy gaps such as line/branch coverage or mutation signals, labeled as proxies rather than correctness evidence.
10. Known failure evidence and whether the goal is characterization, bug finding, contract, property, security, or compatibility testing.

Run `scripts/discover_commands.py` when executable command discovery matters. Record all candidates and the selected candidate rather than only a prose recommendation.

Load:

- [`test-effectiveness.md`](test-effectiveness.md) for test intent, oracle provenance, behavioral coverage, and proxy interpretation;
- [`test-reliability.md`](test-reliability.md) when stability/nondeterminism is material;
- [`advanced-test-strategies.md`](advanced-test-strategies.md) only when example-based tests are insufficient.

## Priority

- **P0**: command discovery/runner correctness, package/delivery integrity, protected evidence, baseline/rerun integrity, invalid or circular oracles, known flakiness that can invalidate acceptance.
- **P1**: parsing/classification logic, schema validation, negative cases, receipt/identity generation, behavioral requirement mapping.
- **P2**: regression/edge cases, CLI error behavior, and bounded advanced strategies where problem shape justifies them.
- **P3**: broad low-risk coverage expansion and proxy-metric improvement after behavior/oracle coverage is understood.

## Phase contract

Each implementation phase must state:

- objective and bounded file set;
- protected paths;
- baseline command/evidence;
- exact required gate(s);
- selected command and working directory;
- test intent and oracle source when tests are generated/changed;
- behavioral requirements/invariants/failure classes covered;
- reliability/stability requirement and rationale when material;
- proxy metrics, if any, explicitly labeled as proxy evidence;
- expected failure/success states;
- rollback/stop condition.

After mutation, rerun the exact failed gate before adjacent gates.

## Test generation

- Match existing framework/style when it is clearly established.
- Prefer deterministic unit tests for pure parsing/classification.
- Use temporary directories for filesystem behavior.
- Do not write real fixtures, snapshots, golden files, expected outputs, or benchmark evidence without exact authorization.
- Include happy, empty, malformed, boundary, failure, and repeated-run cases where relevant.
- Validator tests must include rejected inputs and must not weaken the validator.
- Runner tests must verify exact exit-code preservation, target identity behavior, and `pass|fail|blocked|not-run` states.
- Command-discovery tests must include multi-runtime and ambiguity/tie-break cases.
- Repair tests should prove the same gate/command is rerun after a correction.
- For bug finding, do not copy expected output exclusively from a SUT that may contain the bug.
- Use property/stateful, metamorphic/differential, fuzz, contract, or mutation approaches only when the problem shape and available capability justify them; never auto-install them.

## Reliability rule

Do not run repeated attempts merely to search for green. When stability matters, declare an attempt budget and use `scripts/assess_stability.py`. Keep stability separate from the gate's four-state result.

## Effectiveness and proxy rule

A suite may pass and be stable while missing required behavior. Map known requirements/contracts/invariants to tests before making effectiveness claims. Coverage/mutation can supplement that evidence but never replace it.

## Evidence rule

Generated-but-unexecuted tests are `planned`, not passing evidence. An implemented phase is not complete until applicable target-owned build/test/lint/validator gates have executable evidence or are explicitly `blocked`/`not-run`. Structural, reliability, oracle/effectiveness, and proxy evidence remain distinct.
