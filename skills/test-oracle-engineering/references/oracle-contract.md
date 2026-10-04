# Oracle Contract

## Canonical contracts

New material proofs use `test-oracle-spec/v2` and `test-oracle-proof/v2`. Version 1 artifacts remain readable for compatibility and historical review, but v1 cannot establish strict cross-artifact proof binding and must not be emitted for new proof work.

## `test-oracle-spec/v2`

The spec freezes one bounded claim before execution.

Required surfaces:

- claim identity: `oracle_id`, `claim`, `claim_type`;
- provenance: typed `source_identity`, `candidate_identity`, `evaluator_identity`;
- authority: `target_scope`, `verification_write_scope`, `protected_paths`;
- oracle semantics: `oracle_strategy`, `oracle_origin`, `quality`;
- observation: setup, input, action, expected observation, claim-level failure signal;
- execution: proof layer, mode, requirements, exact argv, optional working directory;
- nondeterminism controls: mode, repetitions, seed/order/clock/scheduler policies, and a statistical rule when applicable;
- finite `max_attempts`.

Identity strings are explicit schemes such as `sha256:<digest>`, `vcs:<revision>`, `version:<id>`, or `declared:<stable-label>`. `candidate_identity=unbound` is allowed only while designing the oracle. Bind it before execution proof.

### Strategy-specific minimums

- `property` / `invariant`: provide `property`.
- `metamorphic`: provide the frozen `relation` between source and follow-up observations.
- `differential`: provide at least two `references` and a `decision_rule`; disagreement alone does not identify which implementation is correct.
- `model-based`: provide `model_identity`.
- `statistical`: provide `decision_rule`, use `nondeterminism.mode=probabilistic`, and predeclare `statistical_rule`.

Read [oracle-strategies.md](oracle-strategies.md) when a direct expected-value oracle is not the best strategy.

## `test-oracle-proof/v2`

A proof receipt records an execution outcome; it becomes strict proof only after cross-verification against the frozen v2 spec and candidate identity.

Important fields:

- exact `oracle_spec_identity=sha256:<canonical-json-digest>`;
- bound candidate, verifier, and environment identities;
- current attempt plus ordered attempt summary;
- `execution_state` separately from `outcome_kind`;
- explicit observation booleans and evidence refs;
- exact command argv and exit code;
- immutable `production_mutation_performed=false` and `criteria_changed=false`.

### Verdict matrix

| Verdict | Required semantics |
|---|---|
| `proven` | `pass` + `expected-observation` + expected observed + failure not observed |
| `rejected` | `fail` + `oracle-rejection` + frozen failure signal observed + expected not observed |
| `inconclusive` | execution occurred but evidence cannot safely prove or reject the claim |
| `blocked` | required runtime/authority/environment prevented proof execution |
| `not-run` | no execution occurred |

`harness-error`, `environment-error`, `timeout`, `cancelled`, or `unstable-observation` can never directly produce `proven` or `rejected`.

## Strict proof verification

Standalone schema validation is necessary but insufficient. For v2 execution proof run:

```text
<PYTHON> scripts/verify_oracle_proof.py \
  --spec <SPEC.json> \
  --proof <PROOF.json> \
  --candidate-identity <FROZEN_CANDIDATE_ID> \
  --json <REPORT.json>
```

When exact candidate bytes are available as a directory, use `--candidate-root <PATH>` instead. The verifier computes a deterministic tree digest, checks spec/proof/candidate identity correspondence, command drift, attempt/repetition limits, and contradictory semantic outcomes.

See [proof-integrity.md](proof-integrity.md) for the proof boundary and limitations.

## Version 1 compatibility

`test-oracle-spec/v1` and `test-oracle-proof/v1` are accepted by `validate_oracle_artifact.py` for read/review compatibility. They remain weaker because they do not encode strategy, nondeterminism, typed outcomes, observation evidence, or strict spec/candidate cross-verification. Do not upgrade a v1 receipt into a v2 proof claim without re-executing or re-establishing the missing evidence.
