# Calibration Scenarios

## Create a hybrid prompt

User: "Create a prompt to review C# code in batches and return JSON to my API."

Expected:
- select `create`;
- keep stable review rules in Markdown;
- represent files as structured runtime input;
- define one canonical output contract;
- use provider-native Structured Output only after resolving the target surface;
- state application-side semantic/authorization validation.

## Port a canonical schema to two providers

User: "I have one JSON Schema used by multiple LLM providers. Make it portable without losing validation rules."

Expected:
- select `portability`;
- preserve the canonical schema;
- verify current provider capability profiles from official docs;
- identify unsupported keyword paths;
- create separate provider projections only as needed;
- list application-side validations for every lost constraint;
- do not force the canonical contract down to the least common denominator.

## Validate a schema

User: "Validate this Draft 2020-12 schema."

Expected:
- run syntax/specialized lint if files/runtime permit;
- use a conforming Draft 2020-12 validator for a normative conformance claim;
- if no conforming validator is available, report normative validation as `not-run` rather than calling lint a conformance pass.

## Review an over-engineered JSON prompt

Expected:
- select `review-only`;
- identify mixed responsibilities, decorative nesting, and duplicated rules;
- recommend Markdown instructions + JSON runtime data + native output contract;
- preserve objective, prohibitions, and failure semantics.

## MCP tool contract

User: "Design the inputSchema and outputSchema for an MCP tool and make it safe for agent use."

Expected:
- select `schema-design`;
- verify the target MCP protocol revision when compatibility matters;
- keep input schema, output schema, tool result, execution error, and authorization separate;
- treat annotations as untrusted unless their server authority is trusted;
- validate user/session permissions outside the model.

## Workflow manifest

User: "Build a JSON manifest that runs Nomia, Mago, and Magia in sequence."

Expected:
- select `workflow-manifest`;
- state that a manifest requires an executor;
- reference capabilities instead of copying permanent prompts;
- include dependencies, contract identities, bounded execution policy, and authority/side-effect requirements;
- validate unique IDs and acyclic topology.

## Do not activate

User: "How do I serialize a C# record using System.Text.Json?"

Expected: do not activate; this is ordinary application serialization.

## Ambiguous

User: "I need this to return JSON."

Expected: determine whether this concerns response formatting, provider Structured Outputs, a schema/tool contract, API transport, or ordinary serialization. Proceed with an explicit assumption only when context resolves the layer.
