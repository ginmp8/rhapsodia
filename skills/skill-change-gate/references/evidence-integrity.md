# Evidence Integrity and Recovery Gate

## Purpose

Prevent a candidate from passing because the gate inspected different bytes, mutable evidence, unsafe outputs, or incomplete receipts. These checks complement semantic review; they do not replace it.

## Evidence identities

Keep these identities separate when they exist:

- before/baseline skill tree;
- after/candidate skill tree;
- frozen evaluator or protected evidence;
- benchmark/scenario input set;
- packaged/delivered artifact;
- persisted receipt/report.

A hash for one layer does not prove another layer is identical.

## Before and candidate tree identity

For local folders, the static helper emits deterministic tree hashes and change sets. Capture the baseline hash before mutation when the workflow needs strict before/after identity.

Example:

```text
<PYTHON> scripts/static_change_gate.py --target <BEFORE> --profile portable > <WORK>/before.json
```

Record `target_tree_sha256`. At acceptance time, provide the expected identities:

```text
<PYTHON> scripts/static_change_gate.py \
  --target <AFTER> \
  --before <BEFORE> \
  --expected-before-sha256 <BASELINE_HASH> \
  --expected-target-sha256 <FROZEN_CANDIDATE_HASH>
```

An expected hash mismatch is blocking. Do not silently recompute the expectation after seeing the mismatch.

## Frozen evaluator and protected paths

If benchmark/eval fixtures determine acceptance, freeze them before candidate mutation. They may live inside or outside the skill.

For paths inside the skill, pass each protected path/pattern to the static helper:

```text
--protected-path evals/** \
--protected-path tests/golden/** \
--protected-path references/acceptance-policy.md
```

A protected path that is added, removed, or modified is blocking in a measured experiment unless the experiment is explicitly invalidated and restarted with a new baseline.

For evaluators outside the skill, inspect the caller's freeze manifest or equivalent evidence. If identity cannot be verified and acceptance depends on it, return `insufficient-evidence`.

## Artifact and receipt correspondence

When packaging/delivery is part of acceptance, verify that the delivered artifact was built from the frozen candidate rather than merely trusting a successful package command.

The static helper accepts a JSON artifact receipt with a successful status and one of these candidate identity fields:

- `source_tree_sha256`;
- `candidate_tree_sha256`;
- `target_tree_sha256`.

Example:

```text
--artifact-receipt <WORK>/package-receipt.json
```

A receipt whose candidate identity differs from the current frozen candidate is blocking. A receipt without any candidate identity is material evidence weakness and fails under strict policy.

## Output-path safety

A gate must not mutate the package it is inspecting merely by writing its own report.

The bundled helper therefore requires `--json` to resolve outside both before and target roots. Resolve symlinks before deciding whether a path is outside. Report writes are staged in the destination directory and atomically replaced to avoid partial JSON.

For candidate skills that themselves produce files, review whether they:

- canonicalize output paths before mutation;
- reject aliases with inputs, evaluators, protected files, or sibling receipts;
- re-check required output type after symlink resolution;
- preserve previous valid outputs on validation/preflight failure.

A candidate that can overwrite its own inputs/protected evidence through path aliasing introduces a blocking regression.

## Recovery behavior

When a candidate performs multi-output or destructive delivery, acceptance should require a defined last-good strategy.

Preferred sequence:

`stage -> validate -> preserve previous targets -> commit all -> clean backups`

If commit or rollback fails, recovery files and exact target mappings should remain available. Deleting recovery evidence merely to leave a clean directory is a regression when recovery is part of the workflow contract.

## Durable receipts

Treat receipts as evidence. They should be:

- versioned when consumed by automation;
- stage-aware (`preflight`, `validation`, `commit`, `rollback`, etc.);
- complete and parseable;
- written/flushed before process exit;
- tied to the exact bytes they describe;
- explicit about missing evidence and recovery paths.

Do not accept `{"status":"pass"}` as sufficient proof of artifact correspondence when the caller depends on candidate identity, packaging identity, or frozen evaluator identity.

## Gate implications

Blocking by default:

- expected before/candidate identity mismatch;
- protected evaluator/fixture mutation in a frozen experiment;
- artifact receipt points to different candidate bytes;
- output can alias protected/input paths in a way that risks mutation;
- failed delivery destroys the last-good artifact where preservation is part of the contract;
- a failed rollback loses the remaining recovery evidence.

Material by default:

- successful artifact receipt lacks candidate identity;
- current host cannot mechanically verify an otherwise supplied identity but semantic evidence remains usable;
- recovery or receipt details are underspecified without a demonstrated destructive failure mode.
