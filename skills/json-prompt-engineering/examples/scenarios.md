# Calibration Scenarios

## Create a hybrid prompt

User: "Create a prompt to review C# code in batches and return JSON to my API."

Expected behavior:

- select `create`;
- recommend hybrid architecture;
- keep review rules in Markdown;
- represent each file as structured JSON input;
- define a native output schema;
- state application-side validation requirements.

## Review an over-engineered prompt

User provides a deeply nested JSON object containing long escaped policies and asks for review.

Expected behavior:

- select `review-only`;
- identify unnecessary nesting and mixed responsibilities;
- recommend Markdown instructions plus JSON runtime data;
- preserve the original objective and constraints.

## Create a workflow manifest

User: "Build a JSON manifest that runs Nomia, Mago, and Magia in sequence."

Expected behavior:

- select `workflow-manifest`;
- state that the manifest needs an executor;
- use skill references rather than copied permanent prompts;
- include actions, dependencies, input/output contracts, and failure policy;
- validate unique IDs and dependency topology.

## Do not activate

User: "How do I serialize a C# record using System.Text.Json?"

Expected behavior: do not activate; this is ordinary JSON serialization and .NET implementation work.

## Ambiguous

User: "I need this to return JSON."

Expected behavior: determine whether this concerns response formatting, API transport, schema enforcement, or ordinary serialization. Proceed with an explicit assumption when context makes the intended layer clear; otherwise ask one focused question.
