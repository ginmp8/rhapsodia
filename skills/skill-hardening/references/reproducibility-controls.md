# Reproducibility Controls

## Definition and ceiling

Reproducibility means the same inputs and supported environment repeatedly satisfy the same semantic contract, quality gates, and delivery guarantees. It does not promise identical natural-language bytes when judgment/stochasticity is irreducible.

Classify the target as `objective-artifact`, `tool-action`, `research-analytic`, or `constrained-subjective` and state remaining nondeterminism.

## Baseline and identities

Before material edits preserve an immutable before-state, inventory the target, compute a deterministic tree identity, and record target-owned mandatory validators/tests. Keep generated evidence outside the target.

```text
<PYTHON> scripts/reproducibility_controls.py tree-hash --target <TARGET> --json-output <WORK>/identity-before.json
```

Keep source/research identity, baseline identity, evaluator identity, candidate identity, package identity, and receipt identity separate.

## Hardening contract v2

Use `assets/templates/hardening-contract.json.template` for new runs. Schema v2 adds:

- explicit `host_profiles`, always including `portable-core`;
- conditional `evidence_profiles` for `environment_provenance`, `stochastic_evaluation`, and `execution_lineage`, each with an applicability decision and reason.

Schema v1 remains readable for existing evidence. Do not force advanced profiles on static work merely for completeness.

```text
<PYTHON> scripts/reproducibility_controls.py validate-contract --contract <WORK>/hardening-contract.json --json-output <WORK>/contract-validation.json
```

## Variability map

Map material variance across:

`activation -> input normalization -> mode/router -> reference loading -> decisions -> generation -> validation -> repair -> delivery -> packaging`

Classify controls as `mechanical`, `schema-type`, `constrained-heuristic`, `model-judgment`, or `external-nondeterminism`. Prefer the lowest reliable layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form instruction`.

Do not encode genuine semantic judgment as fake deterministic code.

## Frozen evaluator

Freeze only assets that decide acceptance: scenarios/prompts, fixtures, expected outputs, grader rules, thresholds, and independent validators. Keep implementation/generators outside the frozen set.

```text
<PYTHON> scripts/reproducibility_controls.py freeze --root <TARGET> --path evals --output <WORK>/evaluator-manifest.json
<PYTHON> scripts/reproducibility_controls.py verify --root <TARGET> --manifest <WORK>/evaluator-manifest.json --json-output <WORK>/evaluator-verification.json
```

If the evaluator is wrong, invalidate/refreeze/restart; never edit it after seeing candidate results and continue the same comparison.

## Conditional advanced profiles

- **Environment/provenance:** require when model/provider/tools/dependencies/cache/locale/time/concurrency can materially change a comparison.
- **Stochastic evaluation:** require repeated trials only for strong reliability/improvement claims about stochastic behavior.
- **Execution lineage:** require when multi-stage dependency/replay/invalidation identity is material.

Ordinary static/package repairs should mark these non-applicable with reasons rather than accumulating machinery.

## Repair and freeze

Use identical deciding inputs for baseline/candidate comparisons. Fix the narrowest diagnosed failure and rerun that gate first. Stop a branch after two non-improving rounds unless new evidence changes the hypothesis. Never weaken a hard gate/frozen evaluator to pass.

After all applicable gates pass, freeze the candidate. Any later edit invalidates affected evidence. Package only that frozen candidate and bind package/receipt identities to the committed bytes.
