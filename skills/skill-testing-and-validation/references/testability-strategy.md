# Testability strategy

Use for `research-testability`, `plan-tests`, `generate-tests`, and `implement-test-phase`.

## Research order

1. Package role and requested scope.
2. Canonical target root and subprojects.
3. Language/runtime markers.
4. Existing tests, validators, runners, packagers, evals, and benchmarks.
5. Command sources and deterministic precedence.
6. Environment/tool availability and version identity.
7. Side effects, network/time/randomness, credentials, generated outputs, and mutable fixtures.
8. Coverage gaps and known failure evidence.

Run `scripts/discover_commands.py` when executable command discovery matters. Record all candidates and the selected candidate rather than only a prose recommendation.

## Priority

- **P0**: command discovery/runner correctness, validators, packagers, protected evidence, baseline/rerun integrity.
- **P1**: parsing/classification logic, schema validation, negative cases, receipt generation.
- **P2**: regression/edge cases and CLI error behavior.
- **P3**: broad low-risk coverage expansion.

## Phase contract

Each implementation phase must state:

- objective and bounded file set;
- protected paths;
- baseline command/evidence;
- exact required gate(s);
- selected command and working directory;
- expected failure/success states;
- rollback/stop condition.

After mutation, rerun the exact failed gate before adjacent gates.

## Test generation

- Match existing framework/style when it is clearly established.
- Prefer deterministic unit tests for pure parsing/classification.
- Use temporary directories for filesystem behavior.
- Do not write real fixtures, snapshots, golden files, expected outputs, or benchmark evidence.
- Include happy, empty, malformed, boundary, failure, and repeated-run cases where relevant.
- Validator tests must include rejected inputs and must not weaken the validator.
- Runner tests must verify exact exit-code preservation and `pass|fail|blocked|not-run` states.
- Command-discovery tests must include multi-runtime and ambiguity/tie-break cases.
- Repair tests should prove the same gate/command is rerun after a correction.

## Evidence rule

Generated-but-unexecuted tests are `planned`, not passing evidence. An implemented phase is not complete until applicable target-owned build/test/lint/validator gates have executable evidence or are explicitly `blocked`/`not-run`.
