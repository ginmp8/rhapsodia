---
name: json-prompt-engineering
description: use when the user asks to create, review, improve, convert, validate, or standardize json prompts, hybrid prompts, json schema response contracts, structured outputs, function or tool-call arguments, or multi-skill workflow manifests. also use for deciding between json and traditional prompts, diagnosing malformed or over-engineered prompt structures, and designing versioned machine-consumable prompt interfaces. do not use for generic json syntax questions, ordinary application serialization, api payload debugging without prompt behavior, full skill-package creation, or general prompt writing that has no structured-input, structured-output, schema, tool, or orchestration requirement.
---

# JSON Prompt Engineering

## Mission

Design structured prompt interfaces that are readable, versionable, secure, provider-aware, and testable. Treat JSON as a data and contract format, not as a universal replacement for natural-language instructions.

## Core Rules

- First classify the artifact: API request envelope, JSON prompt input, requested JSON response, JSON Schema, Structured Output, tool call, or workflow manifest.
- Keep stable behavioral instructions in natural language or Markdown unless a machine must generate or validate them.
- Use JSON for variable data, typed options, handoffs, workflow state, fixtures, and machine-consumable contracts.
- Prefer the hybrid pattern: Markdown instructions + JSON input + native JSON Schema or tool schema.
- Do not claim that JSON improves reasoning by itself.
- Do not treat JSON syntax, schemas, or delimiters as a security boundary.
- Do not place credentials, secrets, private keys, tokens, or connection strings in prompts or examples.
- Keep API controls such as model, temperature, token limits, timeout, and reasoning configuration in API configuration unless the target provider explicitly defines otherwise.
- Use official current provider documentation for provider-specific compatibility claims. Search when details may have changed.
- Distinguish structural validity from semantic correctness, business validation, authorization, and safe execution.

## Required Inputs

Infer reasonable defaults unless a missing item changes the contract materially:

1. target task and intended consumer;
2. target model or provider when provider-specific behavior matters;
3. expected input data and representative examples;
4. required output format and downstream parser expectations;
5. constraints, enums, nullability, limits, and failure behavior;
6. tool, skill, plugin, workflow, or API integration requirements;
7. security boundaries and validation responsibilities.

## Mode Selection

| User intent | Mode | Primary output |
|---|---|---|
| create a structured prompt | `create` | ready-to-use prompt architecture and artifact |
| improve an existing JSON prompt | `improve` | revised artifact plus material changes |
| review without rewriting | `review-only` | verdict, findings, and prioritized corrections |
| convert text to JSON or hybrid format | `convert` | converted artifact with preserved intent |
| design output contracts | `schema-design` | provider-aware JSON Schema or tool schema |
| coordinate skills or plugins | `workflow-manifest` | versioned steps, dependencies, handoffs, and policies |
| test an artifact | `validation-only` | executed checks, defects, and verdict |
| compare JSON with traditional prompting | `decision-guidance` | scenario-based recommendation |

## Workflow

1. **Identify the real layer**
   - Determine whether JSON is the request transport, prompt content, output contract, tool interface, or orchestration manifest.
   - Correct terminology before designing the artifact.

2. **Choose the least complex architecture**
   - Use traditional Markdown for human-maintained rules and long instructions.
   - Use JSON for structured variable data.
   - Use native Structured Outputs or tool calling for machine-parsed output when available.
   - Use a workflow manifest only when an executor can resolve and invoke the declared skills or tools.

3. **Define the contract**
   - Specify required fields, types, enums, null behavior, limits, additional properties, and failure behavior.
   - Separate prompt version, input-schema version, and output-schema version when they evolve independently.

4. **Design the artifact**
   - Use descriptive, stable property names.
   - Avoid unnecessary nesting, duplicated rules, and copied skill instructions.
   - Keep ordered operations in arrays, not object property order.
   - In multi-skill manifests, use `skill`, `action`, `instruction`, `input`, `output`, and `depends_on`; do not embed full copies of each skill's permanent prompt.

5. **Apply safety and trust boundaries**
   - Mark external content as untrusted data.
   - Require validation before tool execution.
   - Keep authorization and business rules outside the model.
   - Fail closed for unknown skills, unknown actions, invalid schemas, dependency cycles, or incompatible handoffs.

6. **Validate**
   - Validate JSON syntax and duplicate keys.
   - Validate schemas or workflow topology.
   - Test normal, missing, null, empty, Unicode, escaped, oversized, ambiguous, adversarial, and truncated cases.
   - Use `scripts/validate_json_artifact.py` for deterministic local checks when files are available.

7. **Deliver**
   - Return the final artifact first when the user wants a reusable prompt.
   - State whether validation was executed or only planned.
   - Separate provider guarantees from application-side validation requirements.

## Resource Loading

- Read [references/json-prompt-design.md](references/json-prompt-design.md) for architecture, field design, hybrid prompting, and conversion rules.
- Read [references/structured-output-and-schema.md](references/structured-output-and-schema.md) for JSON Schema, Structured Outputs, JSON mode, and tool calling.
- Read [references/workflow-manifests.md](references/workflow-manifests.md) for skill/plugin orchestration, dependencies, handoffs, ownership, and state.
- Read [references/security-and-validation.md](references/security-and-validation.md) for prompt injection, secrets, validation layers, and execution boundaries.
- Read [references/review-rubric.md](references/review-rubric.md) for review-only scoring and severity classification.
- Use [assets/templates/hybrid-json-prompt.md](assets/templates/hybrid-json-prompt.md) when producing a reusable hybrid prompt.
- Use [assets/templates/workflow-manifest.json](assets/templates/workflow-manifest.json) when creating a multi-skill workflow manifest.
- Use [examples/scenarios.md](examples/scenarios.md) for calibration.
- Use [evals/activation-scenarios.json](evals/activation-scenarios.json) for planned activation regression coverage.

## Output Contract

### Create, improve, or convert

1. **Architecture**: traditional, JSON, or hybrid, with one-sentence rationale.
2. **Artifact**: complete ready-to-use prompt, schema, or manifest.
3. **Integration notes**: only details needed to consume or execute it.
4. **Validation**: checks executed, defects fixed, and remaining assumptions.

### Review-only

1. **Verdict**: approve, approve with reservations, or reject.
2. **Findings**: severity, evidence, impact, and correction.
3. **Contract risks**: syntax, schema, semantics, safety, compatibility, or orchestration.
4. **Recommended architecture**: preserve, simplify, convert to hybrid, or replace with native schema/tool calling.

### Validation-only

1. commands or checks executed;
2. syntax and structural status;
3. semantic and security warnings;
4. workflow dependency status when applicable;
5. final pass, pass-with-warnings, or fail verdict.

## Stop Conditions

Stop and report the limitation when:

- the user requests provider-specific guarantees without identifying the provider or allowing current official documentation lookup;
- the artifact contains secrets or credentials that should be removed or rotated;
- a workflow names unavailable or unresolvable skills and execution is required rather than design only;
- an output contract requires unsupported provider schema features;
- authorization, compliance, or business decisions are delegated solely to model-generated JSON;
- a measured reliability claim is requested without executed scenarios and recorded evidence;
- a manifest contains unresolved dependencies, dependency cycles, incompatible handoff contracts, or unknown privileged operations.
