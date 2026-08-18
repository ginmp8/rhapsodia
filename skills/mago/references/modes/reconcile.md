# Reconcile Mode

Use `reconcile` only as a read-only lifecycle stage after Mago planning and when current Magia evidence is supplied. It does not edit the canonical plan or Magia evidence.

## Inputs

- resolved Mago board/spec package and feature version;
- selected Magia evidence with provenance;
- stable requirement, acceptance, decision, task, and validation identifiers when available;
- explicit evidence statuses; unknown and not-run remain distinct from pass.

## Workflow

1. Validate Mago package identity and read canonical intent.
2. Read Magia-owned evidence without mutation.
3. Normalize only the fields needed for comparison into external envelopes.
4. Run `scripts/reconcile_planning.py` or perform the same classifications from `references/interoperability-and-reconciliation.md`.
5. Produce `planning-reconciliation.md` outside the canonical package unless a caller-owned report location is explicitly defined.
6. Recommend, but do not perform, a separate Mago revision when intended planning must change.

## Calibration fixture

Use `examples/golden/reconciliation/plan.json.fixture` and `examples/golden/reconciliation/magia-evidence.json.fixture` only to smoke-test the bundled reconciliation script. They are examples, not runtime evidence or canonical artifacts.

## Gate

The report must declare `authoritative: false`, preserve Magia provenance and evidence status, contain all outcome headings, avoid runtime claims authored by Mago, and never overwrite source evidence.
