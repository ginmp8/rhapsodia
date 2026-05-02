# Expectations

Input:

- Multiple delivery and roadmap items from Magiarca-owned sources.

Generated artifacts:

- `portfolio.yaml`
- `portfolio.md`

Validation expectations:

- `validate_portfolio.py --portfolio-yaml portfolio.yaml --portfolio-md portfolio.md` exits `0`.
- No warnings are expected.

Warnings:

- None.

Proves:

- Portfolio rollups can span Mago-linked specs and roadmap-only features.
- Portfolio data does not maintain branch, review, check, or deployment state.
