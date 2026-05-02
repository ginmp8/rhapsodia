# Common Governance

Use Magnomo for human-ready governance around delivery work. It is self-contained and does not require Mago or Magia files.

## Roots

Load [canonical-paths.md](canonical-paths.md). `BOARD_ROOT` is the active board root: prompt-provided after validation, otherwise derived from concrete `board_id` and `cycle_version`. Spec-scoped artifacts derive from `BOARD_ROOT/specs/<spec_id>/`. Emit board-scoped artifacts under `BOARD_ROOT`, spec-scoped artifacts under the selected spec package. Do not invent alternate roots, missing packages, or parallel docs roots.

Ownership:

```text
mago     = AI-ready planning and specification
magia    = implementation, validation, and repository execution
magnomo = human-ready delivery governance, roadmap, status, and reporting
```

## Evidence Rules

- Prefer explicit artifact evidence over inference.
- Preserve uncertainty as `unknown`, `null`, or explicit risk.
- Do not treat PR merge, branches, commits, checks, review status, deployments, or last commit age as Magnomo source of truth.
- Treat roadmap artifacts as upstream human intent, not Mago execution-handoff plans.

## Artifact Sources

- `ops.yaml`: structured delivery metadata for one spec.
- `status.md`: human status for one spec, derived from `ops.yaml` and supplied evidence.
- Roadmap artifacts: human intent/prioritization, not Mago execution-handoff plans.
- Portfolio and release communication aggregate at board scope.
- Reporting artifacts communicate delivered scope, evidence, risk, rollout, and follow-up without becoming execution records.
- Supplied Mago `technical-design.md` may be linked/summarized as evidence for communication or governance decisions, but never edited by Magnomo.

## Template Script Gate

Treat `assets/templates/` as script input first. Use `scripts/write_artifact_scaffold.py` or narrower writers for template-backed creation, refresh, or normalization. Validate with `scripts/validate_artifact.py` or narrower validators. Read template text directly only as last-resort contract reference when no local script can write or validate.
