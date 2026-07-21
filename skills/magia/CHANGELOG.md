# Changelog

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
