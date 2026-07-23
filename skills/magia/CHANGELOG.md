# Changelog


## 1.9.0 - 2026-07-23

- Added privacy-minimized contract-v3 handoffs with workflow lineage.
- Added deterministic read-only routing and persistent handoff ledger contracts.
- Preserved independent Nomia, Mago, and Magia ownership.
- Compatibility impact: breaking coordinated release; contract-v2 envelopes and mixed package versions are rejected before mutation.

## [1.8.0] - 2026-07-23

- Declare PyYAML as a runtime dependency through `requirements.txt` and `release.json`, add runtime dependency validation, clean-environment YAML smoke coverage, and source/archive package gates.
- Harden strict handoff v2 consumption with closed payloads, bounded freshness, future-timestamp rejection, non-empty evidence references, stable reason codes, and non-actionable draft exit semantics.
- Remove residual `contract-v1`, generic `priority`, and `order_hint` guidance from current Magia instructions and extend semantic instruction validation.
- Add the coordinated release attestation ledger and external live-routing evidence contract without runtime peer imports or ownership transfer.
- Preserve ADHOC, RALPH, ADAPT, execution authority, current identifiers, and exact coordinated compatibility.

### Compatibility

- Coordinated exact ecosystem release `1.8.0`; all three packages must move together.
- Handoff schema remains `2.0.0`; draft consumption now fails process control by default and requires explicit inspection allowance.

## [1.7.0] - 2026-07-22
- Integrate convergence validation, public artifact adapters, and both validation selectors into the canonical load order and resource map.
- Add a fail-closed resource-integration validator and distinguish preliminary risk inference from explicit proof-category selection.
- Clarify independent one-owner context loading without introducing a cross-skill execution facade.

- Execute the complete pytest suite inside the MAGIA package gate with collected/executed/pass/fail counts and a suite digest.
- Replace obsolete positive activation paths with canonical board, cycle, and spec identities.
- Add distributed routing, lifecycle, shared provenance, negative ecosystem harness, release metadata, and declared development requirements.
- Preserve MAGIA execution ownership and coordinated exact compatibility with Mago and Nomia `1.7.0`.

### Compatibility

- Coordinated exact ecosystem release `1.7.0`; mixed versions remain rejected before mutation or closure.


## 1.6.0 - 2026-07-22

- Adopt exact ecosystem compatibility with Mago and Nomia `1.6.0`.
- Upgrade ecosystem handoffs to strict schema v2 with deterministic ids, exact package versions, no unsupported aliases, and object-shaped priority contracts.
- Carry and validate byte-equivalent priority, handoff, and compatibility contracts locally without runtime dependency on peer skills.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Reject unsupported handoff schemas and aliases; only the current strict v2 contract is accepted.

## 1.5.0 - 2026-07-22

- Added a versioned, mechanically validated ecosystem handoff contract carried locally by MAGIA.
- Added a local producer/consumer CLI for `mago_to_magia`, `magia_to_mago`, and `magia_to_nomia` envelopes with provenance, freshness, conflicts, unknowns, package versions, and state-mapping metadata.
- Added positive, negative, stale, conflict, authority, mapping, and round-trip tests without introducing runtime dependency on Mago or Nomia.
- Integrated the shared contract into planning-handoff, validation/closure, package validation, archive validation, and resource discovery.

## 1.4.0 - 2026-07-21

- Added a compact execution-entry contract for faster safe starts while preserving ADHOC, RALPH, ADAPT, planning, and governance boundaries.
- Added deterministic read-only repository orientation, conservative execution-wave analysis, and risk-based validation-category selection without executing repository commands or inventing results.
- Added a non-authoritative execution and recovery projection covering task/evidence state, live/dead locks, transaction journals, blockers, and the next safe action.
- Added progressive quickstarts for direct work, board execution, legacy adaptation, governed changes, blocked handoffs, validation, and recovery.
- Added 20 focused tests for the new capabilities; the complete suite now contains 92 passing tests.
- Preserved truthful evidence statuses, smallest-sufficient-change discipline, recoverable state transactions, source-of-truth authority, and Mago/Nomia ownership boundaries.

## 1.3.0 - 2026-07-21

- Added explicit standard/governed risk escalation for contract, data, security, compliance, availability, financial, and multi-repository work.
- Added evidence precedence, change classification, compatibility, migration, rollback/recovery, operations, and authority gates without changing MAGIA ownership boundaries.
- Converted mode selection into a compact evidence-and-closure matrix and integrated all package resources through explicit progressive-loading links.
- Added release compatibility discipline requiring truthful changelog/version decisions, final-state folder/archive validation, and SHA-256 evidence.
- Preserved existing runtime behavior and passed the full 72-test suite plus package, boundary, instruction, planning-handoff, security, and structural gates.

## 1.2.0 - 2026-07-21

- Require selected RALPH tasks to resolve to current PRD intent and a planned validation check through explicit anchors or deterministic legacy semantic linkage.
- Require dependency-safe task order unless planning explicitly marks a task `[parallel]` or `[independent]`.
- Resolve validation-evidence Traceability sources against the selected task or current PRD objective/acceptance criterion before any done-state mutation.
- Add adversarial regression tests proving unrelated tasks and invented traceability sources cannot authorize closure.
- Centralize package inclusion/exclusion policy so validation scans exactly the files eligible for the archive and ignores only known generated artifacts.
- Normalize activation scenario schema for deterministic shared harness validation while retaining regression/adversarial provenance in `suite`.

## 1.1.1 - 2026-07-20

- Hardened transaction recovery against target and backup traversal, symlinks, malformed journals, duplicate entries, and unauthorized execution-state files.
- Added dead-owner lock recovery, live-owner protection, incomplete pre-journal cleanup, process-start metadata, directory durability sync, and preflight snapshot drift detection.
- Strengthened RALPH readiness semantics so canonical sections, concrete criteria, executable validation actions, and explicit expected outcomes are required; negated and scaffold-marker content is rejected.
- Added nine adversarial regression tests covering the newly enforced G2, G5, and G8 controls.
- Bound Traceability rows to the same passed executed check and rejected meta-only or explicitly absent evidence.
- Made package security scanning fail closed for oversized, binary, and undecodable content while narrowing redacted-example handling to the matched assignment value.
- Added real calendar-date validation for cycle IDs, spec IDs, and execution dates.

## 1.1.0 - 2026-07-20

- Added semantic validation evidence and task-to-check traceability gates.
- Added recoverable multi-file execution-state transactions with candidate validation.
- Enforced authorized roots for scaffold writes and blocked symlink escapes.
- Added secret-content and symlink scanning for source folders and packaged archives.
- Added concrete RALPH readiness checks for objectives, acceptance criteria, tasks, and validation plans.
