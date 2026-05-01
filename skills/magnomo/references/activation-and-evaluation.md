# Activation and Evaluation

Use this reference when checking whether Magnomo should activate, when maintaining `examples/activation-scenarios.json`, or when evaluating scenario coverage before packaging the skill.

## Activation Decision

Activate Magnomo when the user asks to create, update, normalize, validate, or report on Magnomo-owned governance artifacts, including delivery metadata, ops/status/stakeholder/replanning records, portfolio views, roadmap artifacts, feature maps, RFC proposals, ADR records, feature reports, release notes, internal notes, and readiness or contract validation.

Do not activate Magnomo for implementation work, repository code changes, tests, runners, deployments, pull requests, commits, branches, Mago planning artifacts, Magia execution records, or implementation task decomposition. Use Magnomo only when Mago or Magia material is supplied as evidence for governance output; never require or modify their files.

When the request is ambiguous, decide whether the requested outcome is a Magnomo governance artifact. If not enough information exists to resolve the owner or artifact family, ask for the missing scope or report a blocker before repository-facing writes.

## Routing Decision Ladder

Apply this ladder before selecting a mode:

1. Identify the requested outcome, not just the nouns in the prompt. Status, roadmap, release, and handoff requests activate only when the output is a Magnomo-owned governance artifact or report.
2. Classify ownership. Magnomo owns governance records and readiness validation; Mago owns planning packages and implementation task decomposition; Magia owns execution records and repository work.
3. Split mixed requests. Do the Magnomo-owned governance part, refuse or mark untouched the Mago, Magia, implementation, deployment, source-control, test, runner, branch, commit, and pull-request portions.
4. Check repository-facing inputs. Before writing board-scoped or spec-scoped files, require `BOARD_ROOT`, `board_id`, and `cycle_version`; require `SPEC_PACKAGE_PATH` when a selected spec package matters.
5. Check evidence. Preserve owners, dates, deployment state, review state, validation results, and release facts as unknown unless supplied by user evidence or existing Magnomo artifacts.
6. Select exactly one mode. If multiple modes appear valid, choose the narrowest mode that produces the requested Magnomo-owned artifact family and list deferred artifacts as not touched.


## Scenario Assets

Magnomo maintains two complementary scenario assets:

- `examples/activation-scenarios.json` is the native package gate. It uses Magnomo's compact `category`, `expected_activation`, `expected_behavior`, and `notes` schema and is validated by `scripts/validate_activation_scenarios.py`.
- `evals/activation-boundary-scenarios.json` is the harness-compatible suite. It uses prompt-level `type` and `acceptance_criteria` fields so external skill harnesses can review activation, non-activation, ambiguous, edge-case, regression, and adversarial expectations without depending on Magnomo-specific schema names.

Keep both assets aligned when activation boundaries change. The native suite proves package coverage; the harness suite makes evaluator criteria explicit. Neither asset proves measured behavior until its prompts are executed and reviewed.

## Scenario Categories

The scenario suite must include at least five cases in each category:

- `should_activate`: direct Magnomo governance artifact requests.
- `should_not_activate`: requests owned by implementation, Mago, Magia, deployment, source control, or unrelated writing.
- `ambiguous`: requests that require scope, mode, or artifact-family resolution before writing.
- `edge_case`: valid Magnomo requests involving missing inputs, invalid paths, multi-mode pressure, or unknown volatile facts.
- `regression`: cases that protect previously important behavior such as preserving unknowns, selecting exactly one mode, and refusing cross-skill writes.
- `adversarial`: prompts that pressure Magnomo to invent evidence, bypass validators, write outside canonical paths, or modify protected artifacts.

## Scenario Validation Rules

Each scenario must have:

- stable `id` with the category prefix: `A` for `should_activate`, `N` for `should_not_activate`, `B` for `ambiguous`, `E` for `edge_case`, `R` for `regression`, and `X` for `adversarial`
- valid `category`
- unique `prompt` long enough to exercise realistic activation behavior
- `expected_activation` as `true`, `false`, or `null`
- concrete `expected_behavior` that states the expected Magnomo action, refusal, blocker, or validation route
- `notes` identifying the risk or capability being tested

For deterministic package validation, scenario metrics are coverage metrics only. Do not report activation precision, recall, robustness, or output conformance as measured unless the prompts were actually executed and results were captured.

## Evaluation Metrics

Use these structural metrics before packaging:

- category coverage: every required category has at least five scenarios
- activation label coverage: `true`, `false`, and `null` expected activations are all represented
- behavior specificity: every scenario states the expected Magnomo action or refusal
- boundary coverage: scenario set includes implementation, Mago, Magia, deployment, source-control, missing-input, path-boundary, and evidence-invention boundaries

Use measured behavioral metrics only after running scenarios through an explicit evaluator. When no evaluator has been run, label scenario conformance as `planned` or `not measured`.

## Scenario Maintenance Protocol

When changing activation behavior or examples:

1. Update the smallest scenario set that covers the changed boundary.
2. Preserve at least five cases per category; prefer six or more when adding a new boundary so future deletions do not drop coverage below the gate.
3. Update `evals/activation-boundary-scenarios.json` whenever the change affects external harness expectations or acceptance criteria.
4. Keep golden output files as fixtures unless the expected artifact shape has intentionally changed.
5. Run `scripts/validate_activation_scenarios.py` after native scenario edits and `scripts/validate_skill_package.py` after harness scenario or structural edits.
6. Report validator output separately from measured prompt execution. A passing scenario-file validator proves coverage and schema only; it does not prove that the assistant routed every prompt correctly.

## Packaging Gate

Run:

```bash
python .github/skills/magnomo/scripts/validate_activation_scenarios.py .github/skills/magnomo/examples/activation-scenarios.json
python .github/skills/magnomo/scripts/validate_skill_package.py --target .github/skills/magnomo
python .github/skills/magnomo/scripts/validate_golden_examples.py --skill-root .github/skills/magnomo
```

The package is not ready if native scenario validation fails, harness scenario coverage is invalid, required categories are missing, golden examples fail, or any package validator error remains. For release packaging, prefer `scripts/package_skill.py --target .github/skills/magnomo --output <output-dir>/skill.zip` because it reruns the structural, activation, and golden gates before writing the archive.
