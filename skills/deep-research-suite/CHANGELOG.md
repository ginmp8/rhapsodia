# Changelog

## [0.3.0] - 2026-10-18

- Added conditional, source-located long/multi-document coverage workflow, including material middle sections, paraphrased evidence and contradictory passages before synthesis.
- Added explicit position-sensitive and semantic-retrieval scenario guidance without modifying outline/fields/result schema or asserting model-level performance.
- Updated the optional OpenAI adapter to supported `CHAT`/`CODEX` product identifiers for portability validation.

**Compatibility:** Existing modes, CLI commands, YAML and JSON contracts, validation/resume/report behavior remain unchanged. Long-context guidance adds checks only when relevant, with explicit budget/unknown handling.

**Validation:** See current-run receipts for exact checks; static tests alone do not establish long-context model reliability.

## [0.2.0] - 2026-10-14

- Clarified activation, no-use boundaries, portable host capabilities, evidence safety and deterministic commands within 72 entrypoint lines.
- Introduced structured source/claim identity and linkage checks, strict research-readiness separate from structural validity, required-by-default fields, and explicit incomplete states.
- Added reproducible per-item semantic scope/schema/source fingerprints, version-bound resume checks, optional freshness-age policy and guarded atomic result stamping. This does not verify live source freshness.
- Reworked strict and partial Markdown reporting to reject invalid results, preserve disputes, link material claims near evidence, escape untrusted Markdown and prevent overwrite of input artifacts and require explicit authorization for external output paths.
- Hardened restricted-YAML validation, stable item IDs and duplicate detection without a third-party runtime dependency.
- Added explicit evaluation criteria and expanded offline negative, adversarial, compatibility and recovery tests. Preserved optional multi-agent research and prior plugin interface/default prompts.

**Compatibility:** Maintains `outline.yaml`, `fields.yaml`, flat/nested item JSON and the existing CLI paths. Behavior intentionally tightens: fields without `required: false` are required, uncertain/missing evidence is not `research_ready`, safe resume requires a stamp, and partial reporting excludes invalid/incomplete records. Existing workspaces may need targeted revalidation before automatic reuse. No automatic migration, destructive rewrite or external source verification is performed.

**Validation:** See the release gate receipt shipped separately with this update for actual executed checks; the changelog does not imply live host/browser testing.
