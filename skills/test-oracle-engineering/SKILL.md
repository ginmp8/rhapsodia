---
name: test-oracle-engineering
description: "Design, author, execute, and review bounded executable test oracles that prove or falsify a concrete behavior claim against a specific candidate. Use when a workflow needs objective proof stronger than model self-assessment: integration/public-stack behavior, authorization boundaries, API/event contracts, data or migration invariants, concurrency/idempotency/retry behavior, CLI behavior, or other executable acceptance checks. Do not use for general implementation, broad test-suite maintenance, subjective review, or fixing the production candidate that failed the oracle."
---

# Test Oracle Engineering

## Mission

Turn one concrete claim into an executable, falsifiable proof contract and evidence receipt. Keep **producer**, **oracle**, **candidate**, and **verifier** identities separate so a passing statement is backed by environment evidence rather than model confidence.

A test oracle answers: **what observation would prove or reject this exact claim for this exact candidate?**

## Ownership boundary

Own:

- claim normalization into observable setup/input/action/expected/failure semantics;
- selection of the highest practical proof layer;
- bounded verification-only test/fixture authoring when authorized;
- execution of the selected oracle when the runtime is available;
- `test-oracle-spec/v1` and `test-oracle-proof/v1` validation;
- evidence identity, negative/adversarial boundaries, and proof freshness.

Do not own:

- production implementation or repair;
- requirements, acceptance-criteria, or architecture changes;
- broad test-suite refactors unrelated to the claim;
- changing expected results after observing the candidate;
- subjective visual/editorial approval;
- declaring a workflow checkpoint promoted; the caller owns promotion.

## Modes

| Mode | Use when | Mutation |
|---|---|---|
| `oracle-design` | define the falsifiable claim and proof layer | none |
| `oracle-authoring` | add a bounded test/fixture needed to execute the oracle | verification scope only |
| `oracle-execution` | run the frozen oracle against one candidate | evidence only |
| `proof-review` | validate/interpret supplied proof receipts | none |

Select the smallest mode that answers the request. Authoring and execution may be combined only when the write scope is explicit and the candidate production surface remains read-only to this skill.

## Core invariants

1. One oracle proves or rejects one bounded claim. Split materially different claims.
2. Freeze claim semantics before inspecting candidate-specific results when feasible.
3. Prefer the highest practical public/observable layer that can falsify the claim; do not accept an internal mock when the real boundary is material.
4. A test that never exercises the claimed behavior is not proof even if it passes.
5. Negative, cross-identity, retry, concurrency, or invalid-input cases are required when the claim depends on those boundaries.
6. The verifier may author verification artifacts but must not edit production implementation to make the oracle pass.
7. Do not weaken fixtures, expected outputs, assertions, thresholds, or acceptance criteria after failure.
8. Bind every result to exact oracle-spec and candidate identities. Candidate mutation invalidates prior proof unless the proof is demonstrably unaffected.
9. Preserve exact commands, environment identity, exit status, and evidence refs when execution occurs.
10. `planned`, `static`, or model-only review is never reported as executed proof.
11. Retry/repair attempts are finite. Repeating the same oracle without changed candidate/evidence is not progress.
12. Missing runtime, source truth, authority, or proof layer yields `blocked`/`not-run`, not invented success.

## Proof-layer selection

Choose the narrowest layer that still observes the real contract:

1. existing focused test already exercising the contract;
2. integration/public-stack test at the API/service/process boundary;
3. contract/event/data invariant test against the real serializer/storage boundary;
4. component/unit test only when the claim is genuinely local;
5. static validation only when the property itself is static.

Examples and edge guidance live in [references/oracle-patterns.md](references/oracle-patterns.md). The canonical spec/receipt semantics are defined in [references/oracle-contract.md](references/oracle-contract.md).

## Oracle contract

Use [schemas/oracle-spec.schema.json](schemas/oracle-spec.schema.json) and [assets/templates/oracle-spec.json.template](assets/templates/oracle-spec.json.template). A material oracle records:

- claim and claim type;
- source/reference and candidate identities;
- target and verification write scopes;
- setup, input, action, expected observation, and failure signal;
- proof layer and runtime requirements;
- evaluator identity and bounded attempts;
- protected evidence/paths.

Production write scope is intentionally absent: this skill cannot repair the candidate.

## Workflow

1. **Resolve one claim.** Trace it to source requirements, current contracts, existing tests, or supplied evidence. If intent is ambiguous, return `blocked` rather than inventing behavior.
2. **Choose a proof layer.** Prefer existing executable evidence before generating new tests.
3. **Design the oracle.** Define setup/input/action/expected/failure semantics and negative boundaries. Produce `test-oracle-spec/v1` for material proof.
4. **Validate the spec.** Run the bundled validator before authoring/execution when Python 3 is available.
5. **Author only if necessary.** Modify only explicit verification/test scope. Do not alter production code, frozen expected outputs, or acceptance criteria.
6. **Execute against one candidate.** Preserve candidate/environment/oracle identities and exact command evidence.
7. **Classify truthfully.** `proven`, `rejected`, `inconclusive`, `blocked`, or `not-run`. A command that did not execute cannot yield `proven`.
8. **Emit proof receipt.** Use `test-oracle-proof/v1`; validate it mechanically.
9. **Return, do not repair.** The caller/producer decides whether to repair, replan, or stop. A repaired candidate requires affected proof to rerun.

## Deterministic validation

```text
<PYTHON> scripts/validate_oracle_artifact.py <SPEC_OR_RECEIPT.json> --json <REPORT.json>
```

The validator is standard-library only. It validates the machine contract and proof truthfulness rules; it does not execute user/project tests itself.

## Portability

The semantic core is Agent Skills-compatible and uses capabilities, not vendor-private tool names. Load [references/host-portability.md](references/host-portability.md) when runtime availability differs across OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, Cursor, Visual Studio, or another host.

Required capabilities depend on mode:

- design/review: repository/file read;
- authoring: scoped verification-file write;
- execution: bounded command/process execution;
- artifact delivery: optional.

A host lacking authoring or execution can still design an oracle, but those gates remain `not-run`.

## Stop conditions

Stop with `blocked`, `inconclusive`, or `not-run` when:

- the claim/source of truth is unresolved;
- proving the claim would require changing production behavior;
- the only route to pass is weakening the oracle or protected evidence;
- required credentials/runtime/environment are unavailable or unsafe to use;
- a destructive/production action would be required without explicit authority;
- candidate identity changed and cannot be re-established;
- the proof layer does not exercise the claimed boundary;
- the retry/attempt budget is exhausted.

## Output contract

Return, as applicable:

1. claim, source identity, candidate identity, and selected proof layer;
2. validated oracle spec identity;
3. verification artifacts created, if any;
4. exact command/environment evidence when executed;
5. proof verdict: `proven | rejected | inconclusive | blocked | not-run`;
6. validated proof receipt identity when produced;
7. evidence gaps and what changed evidence would require a rerun;
8. explicit confirmation that production implementation and acceptance criteria were not modified.
