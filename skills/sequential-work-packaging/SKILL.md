---
name: sequential-work-packaging
description: Create, refine, decompose, audit, order, or normalize canonical sequential work packages using cycle_version, stable spec_id and feature identities, deterministic validation, guarded writes, recovery, and machine-readable receipts. Use for planning-first work packaging and MAGO-compatible planning handoffs; do not use for implementation execution.
---

# Sequential Work Packaging

Create and maintain planning-first work packages under one canonical convention. Preserve `cycle_version` as the macro container, `spec_id` as the stable execution identity, `feature_key` as the stable functional identity, and `feature_version` as semantic technical evolution.

## Authority boundary

This skill owns planning package structure, ordering, identity validation, planning-mode behavior, transition validation, and safe writes of the canonical artifacts. It does not own implementation, delivery governance, deployment, or MAGIA execution evidence. Current MAGO boards use a different canonical registry/identity model: compatibility is adapter-only, MAGO remains authoritative, and this skill must not rewrite a MAGO BOARD_ROOT into the specNNN convention.

## Canonical structure

```text
<cycle_version>/
  spec-catalog.yaml
  specs/
    specNNN/
      manifest.yaml
      prd.md
      tasks.md
      notes.md
      validation.md
```

Only these names are canonical. Legacy names are input aliases, never authoritative outputs.

## Mode selection

Select exactly one primary mode unless the caller explicitly requests a combined pass. Apply this precedence:

1. explicit `order|define|refine|decompose|audit|normalize`;
2. explicit MAGO alias using `references/mago-adaptation.md`;
3. legacy-to-canonical conversion -> `normalize`;
4. read-only conformance/review -> `audit`;
5. catalog sequence/dependency maintenance -> `order`;
6. creation or full definition of exactly one cataloged spec -> `define`;
7. minimal revision of one existing spec -> `refine`;
8. split broad remaining work inside one existing spec -> `decompose`.

If more than one mode remains equally valid, do not mutate. Return `MODE_AMBIGUOUS` and use read-only `audit` behavior until intent is resolved.


## Output contract

For mutation modes, return canonical artifacts plus a machine-readable validation report and change receipt when execution capability exists. For `audit`, return diagnostics/remediation only and do not write. Report structural evidence, behavioral evidence, runtime evidence, and perceptual evidence separately; this skill normally has no perceptual gate. Never present an unexecuted scenario as behavioral evidence.

## Stop conditions

Fail closed and stop mutation on ambiguous mode, unresolved identity/version classification, source/output alias, protected path, active transaction lock, unresolved recovery state, hash/snapshot precondition mismatch, duplicate canonical identity, dependency cycle, frozen evaluator drift, or validator failure.

## Evidence and freeze discipline

Snapshot exact source bytes or equivalent hashes before comparison when source state materially determines the change. The packaged regression scenarios and acceptance contract are a frozen evaluator set; verify `evals/frozen-manifest.json` before final acceptance. Freeze after pass: once the candidate passes final validation, do not edit it afterward without restarting the affected validation gates.

## Run protocol

1. Resolve the authored cycle/spec paths to canonical paths before reading or writing. Reject path escape, symlink escape, input/output aliasing, protected paths, receipt paths inside the canonical cycle, and duplicate output targets.
2. Inventory the current cycle and selected spec. Record hashes for every file that may be updated. Unknown files are evidence: preserve them unless the caller explicitly owns and authorizes their change.
3. Read `spec-catalog.yaml` whenever the cycle exists. For `define`, `refine`, or `decompose`, read the complete selected canonical spec package before planning changes.
4. Normalize identity inputs using `references/reproducibility-contract.md`. Never derive identity from prose when the catalog already defines it.
5. Apply the selected mode reference. Preserve existing stable ids and done history. Existing `order` values may change only when the operation explicitly records `allow_order_change: true` in `order` mode.
6. Build candidate files outside the live targets. Do not mutate source files while deciding the change.
7. Commit only through an exclusive, hash-guarded transaction or an equivalent host mechanism. The transaction must lock the cycle, reject unresolved recovery state, snapshot the exact before-tree, stage all candidate bytes, validate the full candidate and transition invariants before live mutation, re-check the snapshot immediately before commit, preserve last-good bytes, and commit atomically. `scripts/apply_transaction.py` is the portable reference implementation.
8. Re-run structural and transition validation on the committed bytes and verify the committed tree hash equals the prevalidated candidate tree hash. A failed postcondition must restore the last-known-good targets or preserve explicit recovery evidence.
9. Emit the durable receipt outside the canonical cycle tree. The receipt must bind before, candidate, and committed hashes to the same transaction identity.
10. Freeze the accepted state: any later content change invalidates its validation evidence and requires revalidation.

## Identity and creation/update rules

- `cycle_version` must be a quoted semantic container string such as `"01.00.00"`; it is not an execution id.
- `spec_id` is stable once created. New ids use `specNNN`. If the caller does not provide one, derive the next id only from the locked catalog as `max(existing numeric id)+1`; never fill a gap implicitly and never derive it from `feature_key`.
- `order` is sortable state, not identity. Preserve existing order. Appending defaults to `max(order)+10`. An insertion may use an unused integer between explicit anchors. If no free integer exists, block with `ORDER_REBALANCE_REQUIRED`; do not silently renumber.
- `feature_key` is lowercase kebab-case and may recur across specs as the same capability evolves.
- `(feature_key, feature_version)` is a unique functional release identity inside one cycle. Duplicate ownership blocks.
- Repeated `feature_key` entries must increase `feature_version`, execute later, and depend on the immediately preceding spec for that feature.
- Version classification remains semantic judgment; once classified, mapping is deterministic: new capability `v0.1.0`, compatible improvement minor, correction patch, breaking change major. If evidence cannot distinguish the class, block with `FEATURE_VERSION_UNRESOLVED` rather than guessing.
- New actionable tasks must carry an explicit stable `Task ID: taskNNN`. Existing explicit task ids never change. Legacy `Task N` labels may remain for compatibility, but refinement must not renumber them merely to modernize formatting.

## Create versus update

- `order`: may create or update only the catalog unless a combined pass was explicitly requested.
- `define`: may create the canonical spec folder only after its catalog identity exists; on an existing spec it may complete or revise the definition without changing stable identity.
- `refine`: requires an existing canonical spec; update only material future planning gaps and preserve correct history.
- `decompose`: requires an existing canonical spec; preserve the initiative boundary and stable task identities while splitting remaining work.
- `audit`: read-only.
- `normalize`: reads legacy/mixed inputs and writes canonical outputs to a non-aliasing destination. Never delete the legacy source or unknown files by default.

Every update requires an `expected_before_sha256` precondition for each target or the explicit sentinel `ABSENT` for a new file. If the current bytes differ, block rather than overwrite.

## Conflicts and dependencies

Fail closed on:

- duplicate `spec_id`;
- duplicate `order`;
- duplicate `(feature_key, feature_version)`;
- manifest/catalog identity mismatch;
- missing spec/feature/task dependency;
- self-dependency or dependency cycle;
- dependency ordered at or after its dependent spec/task;
- stable id removal or unauthorized renumbering;
- partially applied update whose preconditions no longer match.

Cancelled specs keep their ids. Do not recycle them.

## Protected and unknown paths

Never mutate `.git`, secrets, `.env`, private keys, evaluator/baseline evidence, or paths outside the resolved cycle root. Unknown files inside a cycle/spec are preserved and reported as `UNKNOWN_FILE_PRESERVED`; lack of recognition is never deletion authority.

## Idempotency and recovery

A repeated run with equivalent normalized input must preserve the same identities, ordering decisions, material structure, and semantic transaction identity. Absolute staging-source paths are not part of transaction identity; target paths, preconditions, candidate hashes, mode, and authorization are. If candidate bytes already equal target bytes, return `no_change` and do not rewrite them.

Only one compliant mutation transaction may operate on a cycle at a time. An active lock or preserved recovery workspace blocks a new mutation until the prior state is resolved. Transaction workspaces must live outside the canonical cycle tree so validation hashes describe only canonical/unknown cycle evidence, not temporary backup files.

For multi-file updates use:

`lock -> preflight -> exact before snapshot -> stage -> candidate validate -> transition validate -> precommit recheck -> preserve last-good -> commit -> post-validate -> exact candidate/committed hash check -> receipt`

On failure after any commit, restore all prior target bytes and verify the restoration. If rollback is incomplete, keep recovery material and report exact recovery paths. Do not emit success before committed bytes and postconditions are verified.

## Machine-readable validation

When Python 3.10+ execution is available:

```text
<PYTHON> scripts/validate_sequential.py --cycle-root <cycle> --mode <mode> [--spec-id <specNNN>] --json <validation.json>
<PYTHON> scripts/validate_transition.py --before <before-snapshot> --after <candidate-snapshot> --mode <mode> --json <transition.json>
<PYTHON> scripts/apply_transaction.py --plan <operation-plan.json> --receipt <change-receipt.json>
<PYTHON> scripts/verify_evals.py
<PYTHON> scripts/package_skill.py --target <skill-root> --output <skill.zip> --receipt <package-receipt.json>
```

Diagnostics use stable `code + subject + evidence + severity + supported_fixes`. A missing execution capability is `not-run`, not a pass.

## Mandatory postconditions

Before handoff:

- canonical paths and required artifacts validate;
- catalog and manifest identities agree;
- dependencies are acyclic and ordered;
- stable task ids are unique and dependency-safe;
- unknown files were preserved unless explicitly authorized;
- changed targets match candidate hashes;
- the committed tree hash equals the exact prevalidated candidate tree hash;
- transition invariants pass both before commit and on committed bytes;
- no protected or aliased path was written;
- receipt is outside the canonical cycle tree, parseable, and tied to before/candidate/committed hashes;
- no unresolved transaction/recovery workspace remains after success;
- final state is frozen after its last successful validation.

## References

Read only what the active mode needs:

- `references/convention.md` — full canonical convention and ownership precedence;
- `references/reproducibility-contract.md` — normalization, deterministic identity/order, protected paths, transaction, recovery, receipts, legacy and partial-update rules;
- `references/templates.md` — canonical templates;
- `references/order-mode.md`;
- `references/define-mode.md`;
- `references/refine-mode.md`;
- `references/decompose-mode.md`;
- `references/mago-adaptation.md`.

Host-specific metadata such as `agents/openai.yaml` is optional. The semantic workflow and scripts are host-neutral Agent Skills core.
