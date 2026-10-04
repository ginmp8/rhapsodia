# Execution Environment and Provenance

Use this profile only when runtime identity can materially change a comparison, replay, promotion, or delivery claim. Static prompt inspection and purely structural validation do not require it.

## Contract

The portable shape is [execution-environment.schema.json](../assets/schemas/execution-environment.schema.json). Validate one profile with:

```text
<PYTHON> scripts/validate_execution_environment.py <ENVIRONMENT_JSON>
```

Compare two paired arms with:

```text
<PYTHON> scripts/validate_execution_environment.py <LEFT_JSON> --compare <RIGHT_JSON>
```

A comparison result containing `ENVIRONMENT_DRIFT` means the arms are not materially environment-equivalent. Rerun under a comparable profile or explicitly re-baseline; do not silently mix the evidence.

## Minimum material identity

Record explicitly:

- run and host identity;
- runtime/OS identity;
- model provider, model name, and model-configuration identity; use explicit `not-applicable` values for non-model runs;
- tool and resolved dependency identities;
- locale and timezone;
- cache and concurrency policy;
- digests for material inputs and outputs;
- controller identity when a controller/worker boundary matters.

`run_id`, input digests, and output digests describe one run. They do not replace the material environment identity used to decide whether paired evidence is comparable.

## Hermeticity vocabulary

- `recorded`: material identities are recorded, but ambient external state may vary;
- `pinned`: material versions/configuration are pinned where the host permits;
- `hermetic`: no undeclared material inputs affect the supported execution.

Do not call an agent/model execution hermetic merely because local package versions are recorded. Provider-side model changes, web/API state, clocks, caches, schedulers, and other external inputs may remain nondeterministic.

## Claim rule

Keep source snapshot, evaluator identity, prompt/candidate identity, environment identity, artifact identity, and delivery receipt identity separate. If a material environment field is unavailable, record the strongest truthful value and downgrade the comparison claim to `not-proven` rather than fabricating equivalence.
