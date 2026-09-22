# Maintenance and Evidence

## Evidence layers

Keep claims separate:

- **structural**: package shape, links, schema syntax, portability checks, tree/archive hashes;
- **deterministic**: decision validator, eval validator, regression fixtures, packaging checks;
- **behavioral**: actual model/host executions on frozen scenarios;
- **runtime**: actual tool/connector/process behavior on a named host/environment;
- **qualitative**: bounded reviewer judgment that cannot be reduced to a mechanical gate.

A pass in one layer does not imply another.

## Comparison discipline

For changes to this skill:

1. freeze the baseline bytes and the evaluator/scenario identities before mutation;
2. apply one bounded repair/optimization batch at a time;
3. run the narrowest affected gate first;
4. compare baseline and candidate with the same evaluator where a delta is claimed;
5. keep bundled scenarios candidate-visible and never call them a hidden holdout;
6. after the last required pass, freeze the candidate and make no further semantic edit without revalidation.

## Diagnostic repair loop

When a gate fails:

1. identify the exact diagnostic and affected contract clause;
2. change the smallest causal surface;
3. rerun that same gate;
4. only then run adjacent regression gates;
5. stop a repair branch after two consecutive non-improving rounds unless new evidence appears.

Never weaken the contract, safety boundary, evaluator, fixture expectation, or threshold merely to get green output.

## Source and capability discipline

If current/external evidence materially affects a decision, preserve its source/version identity when the surrounding workflow can do so. Missing network, files, tools, connectors, subprocess execution, or specialist invocation reduces the available evidence; it never authorizes fabricated execution.

## Delivery integrity

For distributable archives, preflight canonical output paths, reject aliases with target/protected inputs, stage and validate before commit, preserve the last-good archive/receipt during replacement, and emit a durable receipt tied to the exact committed bytes. If delivery or rollback fails, preserve the recovery path/evidence instead of deleting it.
