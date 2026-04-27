# Common Governance

Use Magnomo for human-ready governance around delivery work. It is self-contained and does not require Mago or Magia files.

## Operational Roots

- load canonical defaults from [canonical-paths.md](canonical-paths.md)
- `BOARD_ROOT` is the active board root for the run
- use prompt-provided `BOARD_ROOT` when present; otherwise derive it from the canonical defaults with concrete `board_id` and `cycle_version`
- when a spec-scoped governance artifact is in scope, derive its selected package path from `BOARD_ROOT` with concrete `spec_id`
- emit board-scoped Magnomo artifacts under `BOARD_ROOT`
- emit spec-scoped Magnomo artifacts under the selected spec package
- do not invent alternate governance roots, missing spec packages, or parallel documentation roots outside this entrypoint

Ownership model:

```text
mago     = AI-ready planning and specification
magia    = implementation, validation, and repository execution
magnomo = human-ready delivery governance, roadmap, status, and reporting
```

## Evidence Rules

- Prefer explicit artifact evidence over inference.
- Preserve uncertainty as `unknown`, `null`, or an explicit risk.
- Do not treat pull-request merge, branches, commits, checks, review status, deployments, or last commit age as Magnomo source of truth.
- Treat Magnomo roadmap artifacts as upstream human intent, not implementation plans.

## Artifact Sources

- `ops.yaml` is the structured source of truth for delivery metadata for one selected spec package.
- `status.md` is a human-readable status for one selected spec package, derived from `ops.yaml` and supplied evidence.
- Roadmap artifacts are human intent and prioritization, not implementation plans.
- Portfolio and release communication aggregate at board scope.
- Reporting artifacts communicate delivered scope, evidence, risk, rollout, and follow-up without becoming execution records.
- Mago `technical-design.md`, when present and supplied as evidence, is architecture planning input for Magnomo communication or governance decisions; Magnomo may link or summarize it but must not edit it.

## Template Script Gate

- Treat `assets/templates/` as script input first, not copy-paste material.
- Use `scripts/write_artifact_scaffold.py` or a narrower local writer whenever creating, refreshing, or normalizing a template-backed Magnomo artifact.
- Use `scripts/validate_artifact.py` or the narrower local validator after writing or editing a template-backed artifact.
- Read template text directly only as a last-resort contract reference when no local script can perform the write or validation operation.
