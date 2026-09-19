# Repair Workflow

Use for `apply-repair`, `validation-only`, and `package` stages. Run commands from this skill root and resolve `<PYTHON>` to an available Python 3.10+ runtime.

## 1. Normalize target and work paths

- Resolve exactly one target root containing `SKILL.md`.
- Put work evidence outside the target package.
- Record mode, writable scope, protected paths, runtime/capabilities, and canonical target path.
- Block outputs that alias the target, protected evidence, evaluator manifests, or sibling outputs.

## 2. Preserve baseline / last-known-good

Before any repair:

```text
<PYTHON> scripts/inventory_skill.py --target <TARGET> --output <WORK>/inventory-before.json
<PYTHON> scripts/consistency_audit.py --target <TARGET> --json-output <WORK>/audit-before.json --markdown-output <WORK>/audit-before.md
<PYTHON> scripts/validate_consistency_report.py <WORK>/audit-before.json
```

Preserve a full baseline copy, clean VCS revision, or equivalent last-known-good outside the mutation scope. The baseline inventory fingerprint and file hashes are the identity proof. Never overwrite baseline evidence during the run.

## 3. Freeze evaluators before candidate acceptance

Freeze only evaluator assets that will decide acceptance:

```text
<PYTHON> scripts/freeze_evaluators.py freeze --root <TARGET> --path evals --out <WORK>/evaluator-manifest.json
```

If evaluator design itself must change, treat that as a separate phase: invalidate the old experiment, update/review evaluator inputs, freeze a new manifest, then restart candidate comparison. Never edit a frozen evaluator to make a candidate pass.

## 4. Trace and classify

Use inventory `resource_trace` plus semantic review. Before removal, cover imports, links, references, consumers, tests, validators, examples, packaging, migration paths, and handoffs. Apply `references/consistency-taxonomy.md` and `references/authority-and-conflict-resolution.md`.

## 5. Create one bounded repair hypothesis

Record: finding id; diagnosis; evidence; authority owner; files allowed to change; protected files; expected effect; risk; rollback source; same-gate command; adjacent gates.

Repair rules:

- smallest coherent patch tied directly to the diagnosis;
- no cleanup-only edits in the same repair;
- no deletion from "unused" inference alone;
- do not weaken validators, safety, evidence, or acceptance thresholds;
- keep semantic judgment bounded by rubric/evidence;
- if two consecutive repairs do not improve the same objective diagnostic, stop that branch.

## 6. Rerun narrow gate, then adjacent gates

After each meaningful patch, run the narrowest causal validator first. Only after it passes, run adjacent validators. Keep rejected hypotheses in evidence rather than random-searching.

## 7. Final validation and freeze

Run at minimum:

```text
<PYTHON> scripts/inventory_skill.py --target <TARGET> --output <WORK>/inventory-after.json
<PYTHON> scripts/consistency_audit.py --target <TARGET> --json-output <WORK>/audit-after.json --markdown-output <WORK>/audit-after.md
<PYTHON> scripts/validate_consistency_report.py <WORK>/audit-after.json
<PYTHON> scripts/freeze_evaluators.py verify --root <TARGET> --manifest <WORK>/evaluator-manifest.json
```

Also run target-owned validators/tests and any independent package validator available in the host. Repeat inventory once and require the same `inventory_fingerprint` when no files changed between scans.

A passing candidate is frozen. Any edit after this point invalidates relevant evidence and requires revalidation.

## 8. Receipt and package

Create a receipt outside the target:

```text
<PYTHON> scripts/create_consistency_receipt.py --target <TARGET> --baseline-inventory <WORK>/inventory-before.json --final-report <WORK>/audit-after.json --evaluator-manifest <WORK>/evaluator-manifest.json --mode <MODE> --status pass --out <WORK>/consistency-receipt.json
```

For packaging:

```text
<PYTHON> scripts/package_target_skill.py --target <TARGET> --output <OUTPUT>/skill.zip --validate --receipt <OUTPUT>/package-receipt.json
```

Packaging stages and validates the new archive before commit, preserves the previous validated output as last-known-good when present, and reports recovery evidence if commit/rollback fails.
