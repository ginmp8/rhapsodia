# Expectations

Input:

- Large initiative that needs feature candidate decomposition.

Generated artifacts:

- `roadmap.yaml`
- `roadmap.md`
- `governance-decisions.md`
- `feature-map.yaml`

Validation expectations:

- `validate_roadmap.py --roadmap roadmap.yaml --feature-map feature-map.yaml` exits `0`.
- `validate_artifact.py governance-decisions.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- nomia can decompose a large initiative without writing Mago-owned PRD, task, or validation-plan detail.
- Only features with enough confidence become Mago handoff candidates.
- Material roadmap sequencing decisions are recorded as governance decisions, not mutable RFC proposals.
