# LLM, Chat, and RAG Apps

## Basic chat architecture

Use `st.chat_message` for transcript rendering and `st.chat_input` for user prompts. Store visible messages in `st.session_state`. Keep model clients in `st.cache_resource`.

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = run_model(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

## Streaming

Use `st.write_stream` when the backend yields chunks. Keep streamed output synchronized with the stored final message. If streaming fails mid-response, show a recoverable error and do not store partial output as if it were complete.

## RAG pattern

1. Validate the user question.
2. Retrieve relevant documents using a scoped retriever.
3. Show citations or source snippets when appropriate.
4. Generate an answer constrained to retrieved context.
5. Store prompt, answer, citations, and feedback metadata.
6. Provide feedback controls with `st.feedback` or buttons.

## State model

Separate:

- visible chat transcript;
- hidden retrieval context;
- model configuration;
- user feedback;
- cost/latency telemetry;
- uploaded documents;
- authentication context.

Do not place API keys or full private documents in chat history.

## Safety and governance

- Do not expose secrets in prompts, logs, or downloadable traces.
- Redact sensitive document snippets when showing retrieval evidence.
- Make it clear when answers are generated and may need verification.
- Capture feedback separately from the conversation text.
- Add authorization checks before retrieval from private stores.
- Use rate limits or request throttling for expensive models.

## Cost and latency controls

- Cache model clients, not private user prompts.
- Cache stable retrieval indexes as resources.
- Limit retrieved context size.
- Stream long responses.
- Provide stop/reset controls.
- Track token or request counts when the platform allows.

## Testing chat apps

Use AppTest for initial state, message submission, and visible output. For model calls, inject a fake response function. Do not call real paid APIs in unit tests by default.
