# Oracle Contract

## `test-oracle-spec/v1`

The spec freezes one desired/claimed observable behavior before execution.

Required semantic fields:

- `oracle_id`, `claim`, `claim_type`;
- `source_identity`, `candidate_identity` (`unbound` is allowed only before a candidate exists);
- `target_scope`, `verification_write_scope`, `protected_paths`;
- `observable.setup`, `.input`, `.action`, `.expected`, `.failure_signal`;
- `execution.layer`, `.mode`, `.requirements`, optional `.working_directory` and `.command_argv`;
- `evaluator_identity`, `max_attempts`.

A spec never grants production write authority.

## `test-oracle-proof/v1`

A proof receipt binds a frozen oracle to one candidate and execution attempt.

- `verdict=proven` requires `execution_state=pass` and executed command evidence.
- `verdict=rejected` requires `execution_state=fail` and executed command evidence.
- `inconclusive`, `blocked`, and `not-run` cannot be promoted into proof.
- `production_mutation_performed` and `criteria_changed` must always be `false`.

The receipt validates evidence shape and identity. It does not independently prove that the underlying test was well designed; that is the oracle-design responsibility.
