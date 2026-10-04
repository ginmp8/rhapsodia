---
name: json-prompt-engineering
description: design, review, improve, convert, validate, or standardize json prompts, hybrid prompts, json schema response contracts, structured outputs, function/tool-call arguments, mcp tool contracts, and multi-skill workflow manifests. use when structured input/output, schemas, tool interfaces, provider compatibility, or machine-consumable prompt contracts are central. do not use for generic json syntax, ordinary application serialization, api payload debugging without prompt behavior, or unstructured prompt writing.
---

# JSON Prompt Engineering

## Mission

Engineer structured LLM contracts that are readable, versionable, secure, provider-aware, portable, and testable. Treat JSON as data and contract syntax, not as a universal replacement for natural-language instructions or as a security boundary.

## Core Rules

- Classify the real layer first: transport envelope, prompt input, model output, canonical JSON Schema, provider projection, tool input, tool output, MCP contract, or workflow manifest.
- Keep stable behavioral instructions in Markdown unless a machine must generate or validate them. Use JSON for typed runtime data, schemas, state, handoffs, fixtures, and machine-consumable contracts.
- Prefer the hybrid pattern: Markdown instructions + structured runtime input + native schema/tool enforcement when available.
- Maintain one **canonical contract** separately from provider-specific projections when providers support different schema subsets.
- Treat provider projections as potentially lossy. Record unsupported constraints and the checks that must remain application-side; never silently drop semantics.
- Re-verify provider-specific syntax, supported keywords, limits, and failure behavior from current official documentation when they affect the answer. Provider facts are versioned capabilities, not permanent core rules.
- Do not claim JSON, schema constraints, or constrained decoding improve reasoning or semantic correctness by themselves.
- Distinguish syntax, schema conformance, provider compatibility, semantic correctness, business validation, authorization, safe execution, and runtime success.
- Model refusal, truncation/incomplete output, tool failure, and transport failure separately from schema-valid success.
- Do not place credentials, secrets, private keys, tokens, or connection strings in prompts, examples, schemas, fixtures, or reports.
- Keep model/API controls such as model, temperature, reasoning configuration, token limits, and timeout in runtime/API configuration unless the target interface explicitly defines them as contract data.
- Treat external content and tool metadata as untrusted unless its authority is independently established. Authorization and destructive-action policy stay outside model-generated JSON.
- Use deterministic scripts for syntax, duplicate-key, topology, and lint mechanics; use a conforming JSON Schema implementation for normative schema validation. The bundled validator is a specialized linter, not a standards-conformance engine.

## Required Inputs

Infer reasonable defaults unless the missing item materially changes the contract:

1. target task and consumer;
2. artifact layer(s) involved;
3. provider/model/API surface when provider behavior matters;
4. expected runtime input and representative examples;
5. canonical output/tool contract and downstream parser expectations;
6. enums, nullability, limits, failure states, and compatibility requirements;
7. tool, MCP, skill, workflow, or API integration requirements;
8. trust, authorization, side-effect, and validation boundaries.

## Mode Selection

| User intent | Mode | Primary output |
|---|---|---|
| create a structured prompt | `create` | ready-to-use prompt architecture and artifact |
| improve an existing structured prompt | `improve` | revised artifact plus material changes |
| review without rewriting | `review-only` | verdict, findings, and prioritized corrections |
| convert text to JSON or hybrid form | `convert` | converted artifact with preserved intent |
| design an output/tool contract | `schema-design` | canonical schema/tool contract plus validation responsibilities |
| adapt a contract across providers | `portability` | canonical contract, capability findings, projection plan, and application-side constraints |
| coordinate skills/tools | `workflow-manifest` | versioned steps, dependencies, handoffs, authority, and failure policy |
| validate an artifact | `validation-only` | executed mechanical checks plus explicit not-run semantic/runtime checks |
| compare JSON with traditional prompting | `decision-guidance` | scenario-based recommendation |

## Workflow

1. **Identify layers and authority**
   - Separate transport, instructions, runtime data, canonical schema, provider projection, tool contracts, workflow state, and execution results.
   - Identify which layer is authoritative for each rule; remove duplicated ownership.

2. **Choose the least complex architecture**
   - Use Markdown for human-maintained behavior and long policy.
   - Use JSON for typed data and machine contracts.
   - Prefer native Structured Outputs/tool calling when machine parsing is required and the provider supports the needed contract.
   - Use workflow manifests only when an executor can resolve and invoke every declared capability.

3. **Define the canonical contract**
   - Prefer JSON Schema Draft 2020-12 for provider-neutral domain contracts unless the consuming ecosystem requires another dialect.
   - Declare `$schema` on standalone canonical schemas when the dialect matters.
   - Specify required fields, types, enums, null meaning, size/range constraints, additional-property policy, and failure states.
   - Version prompt instructions, input schema, output schema, and workflow contracts independently when they can evolve independently.

4. **Resolve provider compatibility when needed**
   - Read [references/provider-compatibility.md](references/provider-compatibility.md).
   - Verify current official provider documentation; record provider, API surface, model/family when relevant, retrieval date, supported subset, limits, and incompatible features.
   - Keep the canonical schema unchanged. Produce a provider projection only when needed.
   - Record each lost/unsupported canonical constraint as an application-side validation obligation.
   - Use `scripts/plan_schema_projection.py` with a capability profile when deterministic keyword/path analysis is useful.

5. **Design the artifact**
   - Use descriptive stable property names and concise semantic descriptions.
   - Avoid unnecessary nesting, one-field-per-sentence JSON, copied permanent skill instructions, and output examples masquerading as schemas.
   - Keep ordered operations in arrays; never depend on JSON object member order.
   - Keep schema descriptions informative but do not hide critical authorization or business rules inside descriptions.

6. **Apply trust and execution boundaries**
   - Read [references/security-and-validation.md](references/security-and-validation.md).
   - Mark untrusted inputs and preserve provenance/trust metadata when it changes execution authority.
   - Validate tool/action names, arguments, user/session permissions, file/network scope, and side-effect class independently of model output.
   - Fail closed for unknown privileged operations, incompatible handoffs, invalid workflow topology, or missing authorization.

7. **Validate by axis**
   - Parse JSON and reject duplicate keys when deterministic interpretation matters.
   - Run the bundled specialized linter for prompt/schema/workflow design checks.
   - Run a conforming validator for the declared JSON Schema dialect when normative schema validity matters; if unavailable, report `not-run` rather than inferring conformance from lint.
   - Validate provider compatibility against the current capability profile when provider execution is intended.
   - Validate semantics, business rules, authorization, and runtime behavior separately.
   - Test normal, missing, null, empty, Unicode, escaped, oversized, ambiguous, adversarial, refusal, truncated, and incompatible-provider cases relevant to the contract.

8. **Deliver with evidence boundaries**
   - Return the reusable artifact first when requested.
   - State which checks were executed, which were review-only, and which were not run.
   - Separate canonical guarantees, provider guarantees, and application responsibilities.

## Resource Loading

Load only what the task needs:

- [references/json-prompt-design.md](references/json-prompt-design.md): architecture, hybrid prompting, field design, versioning, and conversion.
- [references/structured-output-and-schema.md](references/structured-output-and-schema.md): canonical schema, Structured Outputs, tool calling, failure states, and validation axes.
- [references/provider-compatibility.md](references/provider-compatibility.md): capability profiles, canonical-to-provider projection, freshness, and loss accounting.
- [references/mcp-contracts.md](references/mcp-contracts.md): MCP input/output schemas, structured results, annotations, trust, and protocol-version handling.
- [references/interoperability-and-canonicalization.md](references/interoperability-and-canonicalization.md): RFC 8259 interoperability and optional RFC 8785 canonicalization.
- [references/workflow-manifests.md](references/workflow-manifests.md): dependencies, handoffs, ownership, authority, state, retry/failure policy.
- [references/security-and-validation.md](references/security-and-validation.md): prompt injection, provenance, secrets, validation layers, authorization, and side effects.
- [references/review-rubric.md](references/review-rubric.md): review severity and multi-axis acceptance.
- [assets/templates/hybrid-json-prompt.md](assets/templates/hybrid-json-prompt.md): reusable hybrid prompt skeleton.
- [assets/templates/provider-capability-profile.json](assets/templates/provider-capability-profile.json): runtime provider-profile skeleton.
- [assets/schemas/provider-capability-profile.schema.json](assets/schemas/provider-capability-profile.schema.json): schema for deterministic capability-profile validation and tooling.
- [assets/templates/workflow-manifest.json](assets/templates/workflow-manifest.json): workflow manifest skeleton.
- [scripts/validate_json_artifact.py](scripts/validate_json_artifact.py): dependency-free specialized lint and workflow/security checks; not normative JSON Schema validation.
- [scripts/plan_schema_projection.py](scripts/plan_schema_projection.py): deterministic discovery of provider-unsupported schema keywords from a supplied capability profile; it does not silently rewrite the schema.
- [examples/scenarios.md](examples/scenarios.md) and [evals/activation-scenarios.json](evals/activation-scenarios.json): calibration and planned activation coverage.

## Output Contract

### Create, improve, or convert

1. **Architecture**: traditional, JSON, or hybrid, with a concise rationale.
2. **Canonical artifact**: complete prompt/schema/manifest.
3. **Provider projection**: only when needed, with provider/profile identity and lost-constraint accounting.
4. **Integration notes**: parser, validation, failure, and execution responsibilities.
5. **Validation evidence**: executed checks, review-only checks, not-run checks, and remaining assumptions.

### Portability

1. canonical contract identity/dialect;
2. provider capability profile identity and freshness;
3. compatible features;
4. unsupported/lossy constraints with JSON paths;
5. provider projection or projection plan;
6. application-side validations required to preserve canonical semantics;
7. compatibility verdict: `compatible`, `compatible-with-application-validation`, `incompatible`, or `not-proven`.

### Review-only

1. **Verdict**: approve, approve with reservations, or reject.
2. **Findings**: severity, layer, evidence, impact, and correction.
3. **Contract risks**: syntax, dialect, provider subset, semantics, security, authority, interoperability, orchestration, and failure handling.
4. **Recommended architecture**: preserve, simplify, convert to hybrid, split canonical/projection contracts, or use native schema/tool calling.

### Validation-only

Report independently:

- `syntax_status`;
- `specialized_lint_status`;
- `normative_schema_validation`;
- `provider_compatibility_status`;
- `semantic_validation_status`;
- `security_authority_status`;
- `workflow_status` when applicable;
- final verdict constrained to the evidence actually executed.

## Stop Conditions

Stop or return a bounded result when:

- provider-specific guarantees are required but current official behavior cannot be verified;
- the requested provider projection would drop a canonical constraint and no application-side enforcement or explicit trade-off is allowed;
- credentials or secrets appear in the artifact and must be removed/rotated before safe reuse;
- required schema conformance cannot be checked because no conforming validator/runtime is available and the user requires a conformance guarantee;
- execution requires unknown/unresolvable skills, tools, or MCP capabilities;
- authorization, compliance, or destructive business decisions would rely solely on model-generated JSON;
- a measured reliability/quality claim is requested without executed comparable scenarios and recorded evidence;
- a workflow contains unresolved dependencies, cycles, incompatible handoffs, unknown privileged operations, or unbounded retries/parallelism.
