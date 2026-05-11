# Expectations

Input:

- A nomia roadmap feature that is ready to become a Mago candidate spec.

Generated artifacts:

- `roadmap.yaml`
- `feature-map.yaml`

Validation expectations:

- `validate_roadmap.py --roadmap roadmap.yaml --feature-map feature-map.yaml` exits `0`.
- `validate_contracts.py --roadmap roadmap.yaml --feature-map feature-map.yaml` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- nomia can hand source material to Mago without writing implementation-ready planning artifacts.
- Cross-skill traceability is carried by `feature_key` and `candidate_spec_id`.
