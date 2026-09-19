# Common Governance

Use nomia for human-ready governance around delivery work. It is self-contained and does not require Mago or Magia skill files.

## Roots

Load [canonical-paths.md](canonical-paths.md). `BOARD_ROOT` is the active board root: prompt-provided after validation, otherwise derived from concrete `board_id`, `year`, and immutable `cycle_id`. Spec-scoped artifacts derive from `BOARD_ROOT/specs/<spec_id>/`. Emit board-scoped artifacts under `BOARD_ROOT`, spec-scoped artifacts under the selected existing spec package. Do not invent alternate roots, missing packages, registry records, or parallel docs roots.

Ownership:

```text
mago  = AI-ready planning and specification
magia = implementation, validation, and repository execution
nomia = human-ready delivery governance, roadmap, status, and reporting
```

The three skills are independent. nomia encodes the shared artifact contract locally and never imports, executes, or depends on another skill package at runtime.

## Evidence Rules

- Prefer explicit artifact evidence over inference.
- Preserve uncertainty as `unknown`, `null`, or explicit risk.
- Do not treat PR merge, branches, commits, checks, review status, deployments, or last commit age as nomia source of truth unless supplied as evidence for a governance statement.
- Treat roadmap artifacts as upstream human intent, not Mago execution-handoff plans.
- Treat `cycle_id` and `spec_id` as immutable physical identities, not semantic release versions.
- Treat feature, proposed, accepted, or release versions as optional governance metadata only when supplied; they never determine filesystem paths.
- A non-null `candidate_spec_id` must be supplied or traceable to an existing planning registry. `ready_for_spec: true` may remain valid with a null candidate while Mago has not registered the spec yet.

## Artifact Sources

- `ops.yaml`: structured delivery metadata for one spec.
- `status.md`: human status for one spec, derived from `ops.yaml` and supplied evidence.
- Roadmap artifacts: human intent/prioritization, not Mago execution-handoff plans.
- Portfolio and release communication aggregate at board scope.
- Reporting artifacts communicate delivered scope, evidence, risk, rollout, and follow-up without becoming execution records.
- Supplied Mago planning artifacts or registry records may be linked/summarized as evidence for communication or governance decisions, but never edited by nomia.
- Supplied Magia implementation or validation evidence may be summarized with attribution, but nomia does not claim technical validation authority.

## Template Script Gate

Treat `assets/templates/` as script input first. Use `scripts/write_artifact_scaffold.py` or narrower writers for template-backed creation, refresh, or normalization. Validate with `scripts/validate_artifact.py` or narrower validators. Read template text directly only as last-resort contract reference when no local script can write or validate.
