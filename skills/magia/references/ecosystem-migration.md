# Artifact-native migration: 1.10.1 to 2.0.0

This is a coordinated major release for Mago, Magia and Nomia. Install the exact 2.0.0 set together. Keep the v3 domain handoff protocol; do not silently accept old release identities. Historical routing/cross-skill evaluator files remain byte-identical and pinned by SHA-256.

## Active paths and ownership

New work uses producer roots docs/product, docs/specs and docs/implementation with stable work_item_id. Mago creates its local planning-identity.json; Magia retains that spec_id only as a semantic link. Workers return validated artifact_actions. Workspace indexes adjacent descriptors and writes only regenerable .rhapsodia/catalog and .rhapsodia/views data. Workspace is not required to plan, govern, execute or validate.

## Existing Board data

Existing Board data is supported only when legacy-board is explicitly selected. Each producer runs its own migrate_artifacts.py plan, inspects recognized/omitted files, then apply with the unchanged hash-bound plan. Only recognized owned files are copied. Original Board files remain untouched. Unknown/foreign files are reported, not silently assigned. The copied sources and sidecars are usable by the new catalog immediately; no blanket state or completion inference is made. Reconcile and republish domain content through its owning skill when moving an active work item to native execution.

Interrupted migration uses recovery-plan and explicit --journal-sha256 recover. Recovery rolls back only unchanged files created by that operation, or finalizes an already committed receipt. Never run compatibility and native execution concurrently on the same work item.

## Rollback

Restore the exact prior three-package set and use the untouched original Board. Preserve native source/sidecar files as separate evidence; do not overwrite or delete them during rollback. Delete only generated catalog/views when rebuilding the presentation. Restore a whole validated set, never mixed versions. A failed migration does not permit automatic governance or planning changes.

## Packaging transition

Explicit trusted validation is separate from data-only packaging. Run the repository validate_and_attest.py with --trust-target-code to create external executed evidence, then package_skill.py --validation-evidence. Editing any packaged byte requires new validation. Receipts are integrity records, not cryptographic authorization credentials.

## Earlier release history (legacy compatibility only)

## Historical transition: 1.10.0 -> 1.10.1

The following retained notes document the previous release transition, not instructions to select the current release.

This is a coordinated exact-version patch release. Nomia, Mago, and Magia remain separately installable and independently executable; no package imports or reads a peer package at runtime.

## Compatibility

- Handoff schema remains `3.0.0`; payload directions and authority do not change.
- Priority schema remains `2.0.0`; `business_priority` remains Nomia-owned and `technical_criticality`/`execution_sequence` remain Mago-owned.
- Existing valid v3 handoff envelopes remain semantically valid after their `ecosystem_release`/`source_version` are produced by the 1.10.1 package set.
- Routing, ownership, privacy, reproducibility, and state-mapping contract schemas are unchanged.
- Portable-core guidance now resolves Python through `<PYTHON>` instead of assuming one executable name.
- Magia packaging adds output-alias preflight only; it does not change execution or artifact semantics.
- Mixed package releases remain rejected before mutation.
- Ledger document schema remains `1.0.0`; existing last-known-good/recovery mechanics remain required and do not transfer authority.

## Upgrade

Stage all three 1.10.1 candidates, validate each package, validate byte-equivalent shared contracts and provenance, run the frozen cross-skill suite, run the independent ecosystem change gate, then promote all three as one release decision.

## Rollback

If promotion or cross-skill validation fails, restore the complete prior validated 1.10.0 set. Do not retain a mixed live set. Handoff evidence remains evidence; rollback never rewrites business, planning, or execution authority.
