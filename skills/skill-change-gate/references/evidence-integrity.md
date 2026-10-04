# Evidence Integrity and Recovery Gate

## Purpose

Prevent acceptance because the gate inspected different bytes, stale/contaminated evidence, unsafe outputs, or incomplete receipts. These checks complement semantic review; they do not replace it.

## Keep evidence identities separate

Record separately when material:

- baseline and direct-parent tree;
- candidate tree;
- source snapshot;
- evaluator/scenario set;
- policy and verifier implementation;
- destination/current state;
- packaged/delivered artifact;
- persisted receipt/report.

One hash does not prove another layer is identical.

## Candidate and baseline identity

For local folders, `scripts/static_change_gate.py` emits deterministic tree hashes. Capture baseline identity before mutation and candidate identity before acceptance. Expected mismatch is blocking; never refresh the expectation after seeing the mismatch merely to pass.

## Decision evidence binding

When evidence influences acceptance, prefer Gate Context v1 from `references/decision-evidence-contract.md`. Every deciding evidence record should identify the exact candidate it describes and its producer. Candidate-mismatched evidence is blocking even when the result itself says `pass`.

Under strict measured acceptance, preserve stable policy/verifier identities when those rules can change. A policy mode label alone is not exact decision provenance.

## Frozen evaluator and protected paths

Freeze evaluator/scenario/fixture inputs before candidate mutation when they decide acceptance. For in-package paths, pass protected patterns to the static helper. For external evaluators, inspect a freeze manifest or equivalent identity evidence.

Mutation of protected evaluator evidence invalidates the measured experiment unless explicitly restarted.

### Visibility is independent from bytes

A byte-identical evaluator can still cease to be a valid holdout when candidate construction or selection repeatedly observes its private content/results. Record evaluator role and exposure in Gate Context. If holdout evidence is required and contaminated, gather fresh independent evidence or narrow the claim.

## Caller-declared stochastic evidence contract

The gate does not choose trial counts or statistical thresholds. It verifies the supplied contract: required/completed trials, holdout requirement, and independent replication requirement. Missing required trials/replication means insufficient acceptance evidence.

## Freshness and destination state

When promotion depends on a parent/destination state, bind the decision to that state. If expected and observed destination identities differ before promotion, the prior decision is stale. Revalidate; do not reinterpret stale evidence as a current pass or a candidate defect.

## Artifact and receipt correspondence

When packaging/delivery is in scope, verify that the delivered artifact was built from the frozen candidate. `scripts/static_change_gate.py --artifact-receipt ...` accepts a successful receipt containing candidate/source/target tree identity. Candidate mismatch is blocking; missing identity is material evidence weakness and fails under strict policy.

## Output-path safety

Gate reports must not mutate the package they identify. Keep reports and run-specific Gate Context outside baseline/candidate roots. Resolve/canonicalize paths before writes and reject aliases with inputs, evaluators, protected files, or sibling receipts.

For candidate skills that produce files, review canonicalization, symlink handling, last-good preservation, and alias rejection.

## Recovery behavior

For multi-output/destructive delivery prefer:

`stage -> validate -> preserve previous targets -> commit all -> clean backups`

If commit/rollback fails, preserve recovery files and exact target mappings. Do not delete recovery evidence merely to leave a clean directory.

## Durable receipts

Receipts should be versioned when automated consumers exist, stage-aware, parseable, complete, flushed before exit, and tied to the exact bytes they describe. A bare `{ "status": "pass" }` is insufficient when candidate or artifact correspondence matters.

## Gate implications

Blocking by default:

- expected baseline/candidate identity mismatch;
- candidate-mismatched deciding evidence;
- protected evaluator mutation;
- contaminated required holdout;
- stale required destination identity for promotion;
- artifact/promotion receipt points to different candidate bytes;
- output can alias protected/input paths;
- failed delivery destroys last-good state or recovery evidence.

Material by default:

- successful receipt lacks candidate identity;
- an otherwise supplied external identity cannot be mechanically verified;
- recovery/receipt details are underspecified without a demonstrated destructive failure mode.
