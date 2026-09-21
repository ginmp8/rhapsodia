# Reproducibility Controls

Use for applied hardening, behavioral improvement claims, or package delivery. These controls govern the hardening run; they do not replace target-owned validators.

## Ceiling

Classify the target before promising repeatability:

- `objective-artifact`: mechanics and outputs are mostly machine-checkable.
- `tool-action`: preconditions, bounded actions, postconditions, idempotency, and receipts are checkable; external outcomes can vary.
- `research-analytic`: evidence and report conformance are checkable; conclusions retain bounded judgment.
- `constrained-subjective`: process and hard gates are checkable; quality still needs independent editorial or perceptual review.

Record remaining nondeterminism. Do not translate legitimate judgment into arbitrary code merely to raise structural maturity.

## Baseline and candidate identity

Before material edits:

1. preserve an immutable copy, clean commit, or equivalent before-state;
2. inventory the target and record a deterministic tree hash;
3. run target-owned mandatory validators and tests;
4. keep generated evidence outside the target package.

```text
<PYTHON> scripts/reproducibility_controls.py tree-hash --target <TARGET> --json-output <REPORT_DIR>/identity-before.json
```

Recompute the identity after validation. A hash proves byte identity of included files, not behavioral quality.

## Hardening contract

Copy and fill `assets/templates/hardening-contract.json.template` before material mutation when the run changes behavior, validators, scenarios, or packaging. Validate it:

```text
<PYTHON> scripts/reproducibility_controls.py validate-contract --contract <REPORT_DIR>/hardening-contract.json --json-output <REPORT_DIR>/contract-validation.json
```

The contract records target/baseline identity, ceiling, protected paths, variability controls, evaluators, hard gates, acceptance rules, and delivery requirements. Every change must trace to an observed variance, supported hypothesis, or required gate.

## Frozen evaluator

Freeze only assets that will decide candidate acceptance: prompts, fixtures, expected outputs, grader rules, thresholds, and independent validator files. Do not freeze candidate generators or implementation files that the plan must change.

```text
<PYTHON> scripts/reproducibility_controls.py freeze --root <TARGET> --path evals --path tests/fixtures --output <REPORT_DIR>/evaluator-manifest.json
<PYTHON> scripts/reproducibility_controls.py verify --root <TARGET> --manifest <REPORT_DIR>/evaluator-manifest.json --json-output <REPORT_DIR>/evaluator-verification.json
```

If a frozen evaluator is wrong, invalidate the comparison. Repair and refreeze it as a separate baseline step; never edit it after seeing candidate results and continue the same experiment.

## Variability map

Map material variance across:

`activation -> input normalization -> mode/router -> reference loading -> decisions -> generation -> validation -> repair -> delivery -> packaging`

Classify each item:

- `mechanical`: script, parser, deterministic transform, or runtime control;
- `schema-type`: schema, enum, or typed intermediate representation;
- `constrained-heuristic`: defaults, ordering, tie-breakers, budgets, and stop rules;
- `model-judgment`: evidence requirements, rubric, bounded freedom, and independent review;
- `external-nondeterminism`: pinned source/version where possible plus environment/time/source identity.

Prefer the lowest reliable control layer: runtime/script, then schema/type, validator/gate, reference/rubric, and finally free-form instructions.

## Comparison and repair

- Use identical prompts, files, thresholds, and evaluator versions for baseline and candidate.
- Keep holdout scenarios outside authoring feedback when a strong improvement claim matters.
- One hard failure can reject a candidate; one successful stochastic run rarely proves reliability.
- Repair from a diagnostic code or concrete gate failure. Apply the smallest supported change and rerun the same gate.
- Stop a branch after two consecutive non-improving repairs unless new evidence changes the hypothesis.

## Evidence and claims

Keep evidence layers separate:

- structural: package shape, links, schemas, hashes, static gates;
- behavioral: executed scenarios and evaluator decisions;
- runtime: actual application, browser, tool, or integration behavior;
- perceptual: independent human or image-capable review.

Use `measured`, `observed`, `derived`, `supplied`, `planned`, or `blocked`. Planned suites and static maturity never prove behavioral improvement.

## Freeze after pass

After all acceptance gates pass, record the candidate identity and treat it as frozen. Any subsequent edit invalidates affected validation and requires rerunning it. Package only that frozen candidate. The package receipt must retain candidate tree SHA-256, archive SHA-256, archive file count, and validation result, and should also bind the committed stage, receipt version, last-good preservation, and recovery state to the delivered bytes. Package/receipt outputs must resolve outside the frozen target and must not alias each other.
