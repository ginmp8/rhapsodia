# Execution Environment and Provenance Profile

Use when runtime identity can materially affect a baseline/candidate comparison, repeated-trial reliability claim, replay claim, or promotion decision. Static inspection does not need this profile.

Validate `assets/schemas/execution-environment.schema.json` with:

```text
<PYTHON> scripts/validate_reproducibility_profiles.py --kind environment --input <ENVIRONMENT.json>
```

Compare paired arms with `--compare <OTHER.json>`. A material identity mismatch is `ENVIRONMENT_DRIFT`: rerun under an equivalent environment or explicitly re-baseline; do not silently combine the evidence.

Record the strongest truthful identities available for host/runtime, model configuration, tools, resolved dependencies, locale/timezone, cache/concurrency policy, material inputs and outputs, and controller identity when relevant. Use explicit `not-applicable` values for non-model runs. Missing material runtime identities limit the claim; never invent versions.

`hermeticity` is descriptive: `recorded`, `pinned`, or `hermetic`. Recorded package versions do not make a model/API/web-dependent run hermetic.

Keep source snapshot, evaluator, candidate, environment, trace, report, and package identities distinct. This profile is provenance evidence, not a security attestation.
