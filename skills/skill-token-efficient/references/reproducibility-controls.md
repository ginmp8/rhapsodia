# Reproducibility Controls

## Evidence and identities

Keep **token evidence**, **structural evidence**, **behavioral evidence**, and **runtime evidence** separate; a pass in one layer proves no other layer.

Before edits preserve exact baseline bytes/tree identity outside the mutation workspace and capture exact material source bytes as an immutable source snapshot or pinned VCS evidence when external inputs affect equivalence. `apply` mutates an isolated copy; baseline, frozen evaluators, fixtures, expected outputs, and generated baseline evidence stay protected. Failure normally discards the candidate and keeps installed/last-good bytes; if in-place mutation is unavoidable, require byte-for-byte backup and restore first.

## Tokenization

Pin one method and comparison scope before baseline measurement and keep both unchanged across arms. `estimator-v1` is deterministic/portable but approximate. `tiktoken:<encoding>` is optional and exact only for the identified encoding/package version; never silently fall back. Prefer `instructions` for instruction optimization; `entrypoint` means only `SKILL.md`; `all-text` includes scripts/evals/config text.

## Refactor contract and evaluator freeze

Fill/validate `assets/templates/refactor-contract.json` before mutation. It must cover activation, scope, safety, validation, evidence/citation, compatibility, output contract, readability, progressive loading, and protected URLs/paths/commands/env vars/schemas/flags/proper nouns/versions/numbers. `manual` and `scenario` checks remain hard gates until supported by real evidence.

Freeze exact deciding scenarios, fixtures, expected outputs, validators/graders, thresholds, and comparison configuration. Candidate code must not change them. If an evaluator is wrong, invalidate the comparison, version/freeze the corrected evaluator, and re-baseline.

## Progressive loading and source integrity

`SKILL.md` is the control plane. Detail may move to one-level references only with an explicit loading edge. Deterministically fail broken local refs or unauthorized loss of a baseline-reachable instruction reference; never create apparent savings by orphaning required content.

## Delivery integrity

Before package/receipt writes, canonicalize destinations and reject output aliases with target/input, protected evidence, or sibling receipt. Preflight before mutation so failure leaves last-good bytes unchanged.

After all gates pass: compute final candidate tree identity; make no further edits; stage and validate exact package bytes; compute package SHA-256; emit a durable receipt (`receipt_version` + hashes) tied to exact candidate/package identities; commit atomically where supported. A post-pass edit invalidates freeze; failed packaging must not replace last-good artifacts.

## Host-neutral root

Resolve `<skill-root>` from the package containing `SKILL.md`; never require a host-specific install directory. GitHub Copilot, Cursor, Codex, Claude, and OpenAI may discover the same Agent Skills-compatible package in different locations. Treat those locations and `agents/openai.yaml` as placement/metadata adapters, not semantic workflow dependencies. Keep package references relative and required capabilities explicit.
