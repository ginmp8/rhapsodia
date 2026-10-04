---
name: test-oracle-engineering
description: "Design, author, execute, and review bounded executable test oracles that prove or falsify one concrete behavior claim against one candidate. Use when a workflow needs evidence stronger than model self-assessment: public-stack/integration behavior, authorization boundaries, API/event contracts, data or migration invariants, concurrency/idempotency/retry semantics, CLI behavior, security findings, property/metamorphic/differential checks, or proof-receipt review. Do not use for production implementation/repair, broad test-suite maintenance, requirements changes, subjective visual/editorial approval, or checkpoint promotion."
---

# Test Oracle Engineering

## Mission

Turn one concrete claim into a falsifiable oracle contract and evidence receipt. Keep **producer**, **oracle**, **candidate**, and **verifier** identities separate so a proof claim is backed by observable evidence rather than model confidence.

A test oracle answers: **what observation would prove or reject this exact claim for this exact candidate, and what observations would remain inconclusive?**

## Ownership boundary

Own:

- claim normalization into setup/input/action/expected/failure semantics;
- selection of the highest practical proof layer and oracle strategy;
- bounded verification-only test/fixture authoring when authorized;
- execution of the selected oracle when runtime capability exists;
- canonical `test-oracle-spec/v2` and `test-oracle-proof/v2` validation;
- review compatibility for v1 artifacts;
- strict spec/candidate/proof cross-verification;
- evidence identity, nondeterminism controls, negative/adversarial boundaries, and proof freshness.

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
| `oracle-design` | define the falsifiable claim, strategy, and proof layer | none |
| `oracle-authoring` | add a bounded test/fixture needed to execute the oracle | verification scope only |
| `oracle-execution` | run the frozen v2 oracle against one candidate | evidence only |
| `proof-review` | validate/interpret supplied spec/proof receipts | none |

Select the smallest mode that answers the request. Authoring and execution may be combined only when write scope is explicit and the candidate production surface remains read-only to this skill.

## Core invariants

1. One oracle proves or rejects one bounded claim. Split materially different claims.
2. Freeze claim semantics, strategy, evaluator, expected/failure signals, and material nondeterminism controls before candidate-specific results when feasible.
3. Prefer the highest practical public/observable layer that can falsify the claim; do not accept an internal mock when the real boundary is material.
4. Strategy is distinct from claim type. A property, metamorphic, differential, model-based, or statistical oracle may apply to the same claim type.
5. A test that executes the claimed path but cannot observe the relevant fault is not proof. Coverage alone is not oracle strength.
6. Negative, cross-identity, retry, concurrency, or invalid-input cases are required when the claim depends on those boundaries.
7. The verifier may author verification artifacts but must not edit production implementation to make the oracle pass.
8. Do not weaken fixtures, expected outputs, assertions, thresholds, statistical rules, or acceptance criteria after failure.
9. New material proofs use v2 and bind exact spec, candidate, evaluator, command, attempts, environment evidence, and observed outcome. Candidate/spec drift invalidates affected proof.
10. `harness-error`, `environment-error`, `timeout`, `cancelled`, and `unstable-observation` never directly prove or reject the behavioral claim.
11. Retry/repair attempts are finite. Repeating unchanged evidence until green is not progress; conflicting semantic outcomes are instability evidence.
12. `planned`, static-only, v1 review, or model-only assessment is never reported as strict executed proof.
13. Missing runtime, source truth, authority, identity, or adequate proof layer yields `blocked`, `inconclusive`, or `not-run`, not invented success.

## Proof-layer selection

Choose the narrowest layer that still observes the real contract:

1. existing focused test already exercising and observing the claim;
2. integration/public-stack test at the API/service/process boundary;
3. contract/event/data invariant test against the real serializer/storage boundary;
4. component/unit test only when the claim is genuinely local;
5. static validation only when the property itself is static.

Use [references/oracle-patterns.md](references/oracle-patterns.md) for domain patterns. Load [references/oracle-strategies.md](references/oracle-strategies.md) when the oracle is property/model/metamorphic/differential/statistical/implicit or when direct expected output is weak.

## Canonical contracts

Use [schemas/oracle-spec.schema.json](schemas/oracle-spec.schema.json), [schemas/proof-receipt.schema.json](schemas/proof-receipt.schema.json), and the templates in `assets/templates/`.

A v2 spec records:

- typed source/candidate/evaluator identities;
- claim and claim type;
- oracle strategy, origin/independent validation, assumptions/blind spots, and optional strength assessment;
- observable setup/input/action/expected/failure signal;
- exact proof layer, argv, requirements, scopes, and protected evidence;
- deterministic/controlled/probabilistic execution controls and finite attempts.

Read [references/oracle-contract.md](references/oracle-contract.md) for exact semantics. Version 1 remains read/review compatible but is not canonical for new proof work.

## Workflow

1. **Resolve one claim.** Trace it to source requirements, current contracts, existing tests, or supplied evidence. If intent is unresolved, return `blocked` rather than inventing behavior.
2. **Choose proof layer and oracle strategy.** Prefer existing executable evidence before generating new tests. Record assumptions, blind spots, and strength needs proportionally to risk.
3. **Design the v2 oracle.** Define setup/input/action/expected/failure semantics plus strategy-specific fields and nondeterminism controls. If generated/LLM-assisted/inferred, record an independent validation path.
4. **Validate the spec.** Run the standalone validator before authoring/execution when Python 3 is available.
5. **Author only if necessary.** Modify only explicit verification/test scope. Do not alter production code, frozen expected outputs, evaluator criteria, or statistical thresholds.
6. **Execute against one bound candidate.** Preserve candidate/environment/verifier identities, exact argv, attempts, observation evidence, and failure class.
7. **Classify outcome before verdict.** Distinguish expected observation, oracle rejection, harness/environment failure, timeout/cancellation, and instability. Load [references/nondeterminism.md](references/nondeterminism.md) when repetitions or runtime variance matter.
8. **Emit v2 proof receipt.** Validate standalone shape and truthfulness rules.
9. **Cross-verify strict proof.** Run `verify_oracle_proof.py` against the frozen spec plus candidate identity/tree. Only a passing cross-verification may support strict `proven`/`rejected` language.
10. **Return, do not repair.** The caller/producer decides whether to repair, replan, or stop. A repaired candidate requires affected proof to rerun.

For concurrency/distributed claims whose correctness depends on interleavings or histories, load [references/concurrency-distributed.md](references/concurrency-distributed.md) before finalizing the oracle.

## Deterministic validation

Standalone validation:

```text
<PYTHON> scripts/validate_oracle_artifact.py <SPEC_OR_PROOF.json> --json <REPORT.json>
```

Strict v2 cross-verification:

```text
<PYTHON> scripts/verify_oracle_proof.py \
  --spec <SPEC.json> \
  --proof <PROOF.json> \
  --candidate-identity <FROZEN_ID> \
  --json <REPORT.json>
```

Use `--candidate-root <PATH>` instead of `--candidate-identity` when exact local candidate bytes should define identity. Both scripts are Python-standard-library only. The strict verifier proves contract/identity correspondence; it does not replace semantic review of oracle adequacy or arbitrary statistical calculations. See [references/proof-integrity.md](references/proof-integrity.md).

## Portability

The semantic core is Agent Skills-compatible and capability-based. Load [references/host-portability.md](references/host-portability.md) when runtime availability differs across OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, Cursor, Visual Studio, or another host.

Required capabilities depend on mode:

- design/review: repository/file read;
- authoring: scoped verification-file write;
- execution: bounded command/process execution;
- strict local proof: candidate identity/hash capability;
- artifact delivery: optional.

A host lacking execution can still design/review an oracle, but runtime gates remain `not-run`.

## Stop conditions

Stop with `blocked`, `inconclusive`, or `not-run` when:

- the claim/source of truth is unresolved;
- proving the claim would require changing production behavior;
- the only route to pass is weakening the oracle, protected evidence, or statistical rule;
- required credentials/runtime/environment are unavailable or unsafe;
- a destructive/production action would be required without explicit authority;
- candidate/spec/evaluator identity changed and cannot be re-established;
- the proof layer or oracle strategy does not exercise the claimed boundary;
- deterministic/controlled repetitions produce contradictory semantic outcomes;
- the retry/attempt budget is exhausted.

## Output contract

Return, as applicable:

1. claim, source identity, candidate identity, proof layer, and oracle strategy;
2. validated v2 spec identity, assumptions, and material blind spots;
3. verification artifacts created, if any;
4. exact command/environment/attempt evidence when executed;
5. execution outcome kind separately from proof verdict;
6. proof verdict: `proven | rejected | inconclusive | blocked | not-run`;
7. strict proof-verifier result/identity when `proven` or `rejected` is claimed;
8. evidence gaps and what changed evidence requires a rerun;
9. explicit confirmation that production implementation and acceptance criteria were not modified.
