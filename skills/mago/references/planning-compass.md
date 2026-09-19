# Planning Compass Projection

The planning compass is a disposable, non-authoritative view derived from one canonical spec package. It reduces navigation cost without creating a second state model.

## Command

```bash
python -B scripts/render_planning_compass.py <package> --output <external-path>.json
python -B scripts/render_planning_compass.py <package> --format markdown --output <external-path>.md
```

The output path must be outside the canonical package. Existing output is not overwritten unless `--force` is explicit.

## What it reports

- canonical identity and selected profile;
- mechanically required, existing, missing, and conflicting artifacts;
- mutation state and recovery blockers;
- mechanically inferred public lifecycle position;
- gates that are mechanically observed and gates that remain `not_observed`;
- next Mago action and the boundary for any Nomia or Magia handoff;
- source paths and manifest digest.

## Evidence limits

The renderer does not execute validators, inspect runtime, accept risk, or claim handoff readiness. When canonical artifacts exist and mutation state is clean, it recommends running the required validators; it never converts file presence into validation success.

A compass output always declares:

```text
authoritative: false
runtime_evidence: not_observed
delivery_governance: not_observed
```

Delete and regenerate the projection whenever canonical state changes.
