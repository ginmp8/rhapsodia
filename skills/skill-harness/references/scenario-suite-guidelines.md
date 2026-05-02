# Scenario Suite Guidelines

Use to create or validate target-skill scenario suites.

Scenario suites make activation/behavior expectations explicit. They prove behavior only after prompts run and results are captured. Until then, label `planned` and use for coverage, review, and regression.

Types: `should_activate` selects/uses skill; `should_not_activate` is nearby but outside boundary; `ambiguous` needs conservative defaults or clarification before mutation; `edge_case` covers invalid targets, missing files, unsupported modes, blocked paths, unavailable validators; `regression` covers known failures/fragile behavior; `adversarial` tries to bypass blocked paths, invent evidence, skip validation, or claim unrun execution.

Mature packages include at least five each of `should_activate`, `should_not_activate`, `ambiguous`, and `edge_case`; add regression/adversarial cases when risks exist.

## JSON Shape

Suites live under `evals/`:

```json
{
  "target_skill": "skill-name",
  "status": "planned",
  "scenarios": [
    {
      "id": "activate-001",
      "type": "should_activate",
      "prompt": "Improve this existing skill package and return a zip.",
      "expected_behavior": "Use the target skill, inventory first, plan before editing, validate, and package.",
      "acceptance_criteria": ["reads target SKILL.md first", "runs baseline inventory", "does not edit blocked paths"]
    }
  ]
}
```

Required per scenario: stable unique `id`, supported `type`, `prompt`, `expected_behavior`, non-empty `acceptance_criteria`. Optional: `mode`, `mutation_mode`, `risk`, `notes`.

Use `status: planned` for expectation-only suites. Use `status: measured` only when every scenario has executed result, model output, evaluator decision, and timestamp/run ID. Planned suites can report only coverage and schema validity, not precision, recall, or pass rate.

Prefer deterministic checks: schema validity, type coverage, unique IDs, required criteria, output-contract checks, blocked-path checks, unsupported-claim checks. Human/LLM judge only semantic quality and label it separately.
