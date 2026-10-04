# Maintenance and Evidence

## Evidence layers

Keep claims separate:

- **structural**: package shape, links, schema syntax, portability checks, tree/archive hashes;
- **deterministic**: decision validator, eval validator, regression fixtures, packaging checks;
- **semantic review**: evidence-backed judgment about whether instructions/requirements preserve intended meaning;
- **behavioral**: actual model/host executions on frozen scenarios;
- **runtime**: actual tool/connector/process behavior on a named host/environment.

A pass in one layer does not imply another.

## Research-backed change traceability

When external research materially changes behavior, keep the traceability workspace outside the target package and preserve this chain with stable ids:

`source -> atomic finding -> disposition -> requirement -> target change -> evaluation`

Rules:

1. freeze the interpreted research corpus or source snapshot before deriving requirements;
2. account for every material finding, including rejected/not-applicable/conflicting findings;
3. require every substantive change to trace backward to at least one accepted requirement;
4. define evaluation intent before candidate mutation when feasible;
5. verify the links semantically, not only structurally;
6. claim corpus-bounded coverage, never universal research completeness.

The Decision Engine package must not require a specific traceability product or host at runtime.

## Comparison discipline

For changes to this skill:

1. freeze baseline bytes and evaluator/scenario identities before mutation;
2. apply one bounded repair/optimization batch at a time;
3. run the narrowest affected gate first;
4. compare baseline and candidate with the same evaluator where a behavioral delta is claimed;
5. keep bundled scenarios candidate-visible and never call them a hidden holdout;
6. use repeated trials plus material environment identity when stochastic stability/reliability is part of the claim;
7. after the last required pass, freeze the candidate and make no further semantic edit without revalidation.

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

Rich provenance belongs in caller-owned evidence records. Keep the runtime envelope compact by storing stable `evidence_refs` rather than copying full provenance graphs into every result.

## Delivery integrity

For distributable archives, preflight canonical output paths, reject aliases with target/protected inputs, stage and validate before commit, preserve the last-good archive/receipt during replacement, and emit a durable receipt tied to the exact committed bytes. If delivery or rollback fails, preserve the recovery path/evidence instead of deleting it.
