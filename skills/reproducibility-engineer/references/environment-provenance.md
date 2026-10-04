# Execution Environment and Provenance Profile

## Purpose

Use this profile when runtime identity can materially change a comparison, replay, promotion, or delivery claim. It complements source snapshots: source provenance proves which bytes were used; the environment profile records the conditions under which those bytes were executed.

Do not require this profile for simple static inspection where runtime identity cannot affect the conclusion.

## Contract

Use `assets/schemas/execution-environment.schema.json` as the portable shape and validate with:

```text
<PYTHON> scripts/validate_execution_evidence.py --kind environment --input <ENVIRONMENT.json>
```

For paired arms that must be comparable:

```text
<PYTHON> scripts/validate_execution_evidence.py --kind environment --input <LEFT.json> --compare <RIGHT.json>
```

A comparison failure with `ENVIRONMENT_DRIFT` means the two arms are not materially environment-equivalent. Either rerun under one environment or explicitly re-baseline; do not silently mix the evidence.

## Minimum evidence

Record explicitly:

- run and host identity;
- runtime/OS identity;
- model provider, model name, and model-configuration identity; use explicit `not-applicable` values for non-model runs rather than omitting the field;
- tool identities and resolved dependency identities;
- locale and timezone;
- cache and concurrency policy;
- digests for material inputs and produced outputs;
- controller identity when a controller/worker or self-hosting boundary matters.

The validator emits `identity_sha256` from the material environment subset. `run_id`, inputs, and outputs are provenance for the individual run and do not by themselves change the environment identity.

## Hermeticity vocabulary

Use the optional `hermeticity` value truthfully:

- `recorded` - material environment identities are recorded, but ambient external state may still vary;
- `pinned` - material versions/configuration are pinned or resolved to stable identities where the host permits it;
- `hermetic` - execution has no undeclared material inputs and can be recreated from declared inputs/dependencies under the supported runtime.

Do not call an agent run hermetic merely because package versions are recorded. Web/API state, clocks, provider-side model changes, hidden caches, and scheduler behavior may remain external nondeterminism.

## Provenance-lite receipt

Treat the profile as a provenance component, not a security attestation. A useful run receipt binds:

`controller/builder -> invocation/model/tools -> resolved dependencies -> environment -> input digests -> output digests`

Keep source snapshot, evaluator identity, candidate identity, environment identity, artifact identity, and delivery receipt identity separate. One digest must not stand in for another evidence layer.

## Degraded hosts

If provider/model/tool/runtime identity is unavailable, record the strongest truthful stable value available and downgrade the claim. Do not fabricate versions or hashes. A comparison that depends on an unavailable material identity is `not-proven`, not environment-equivalent.
