# LLM and Chat Apps

Use this reference for chat interfaces, streaming responses, message history, retrieval apps, prompt controls, feedback, and cost or safety guardrails.

## Chat state

Store chat history in session state. Keep messages compact and avoid storing large documents directly in the message list. Persist conversations externally only when the product requirements and privacy model are explicit.

## Streaming

When streaming model output, separate display streaming from final message persistence. Append the final assistant message once the stream completes so reruns do not duplicate partial content.

## Retrieval apps

For retrieval-augmented apps:

- keep uploaded document parsing separate from vector index creation;
- cache reusable indexes only when privacy boundaries allow it;
- show retrieved source snippets or citations when the user needs trust;
- expose retrieval filters and reset controls;
- handle empty or low-confidence retrieval explicitly.

## Prompt and cost controls

Make model, temperature, retrieval depth, and maximum output length visible only when useful to the target audience. Add guardrails for prompt injection, sensitive data, and unexpectedly large context.

## Feedback

Capture feedback with message ids or stable turn ids, not just list positions that may change after reruns. Store feedback separately from prompt text when possible.

## Safety checks

Do not log secrets, raw private documents, or sensitive prompts. For internal tools, state the data retention and access model in the app or deployment notes.
