# LLM, Chat, and AI Apps

## Basic chat structure

A Streamlit chat app needs:

- message history in session state;
- rendering loop for existing messages;
- input widget;
- assistant response generation;
- error and cost handling;
- optional reset/export/feedback controls.

Minimal pattern:

```python
import streamlit as st

st.set_page_config(page_title="Assistant", layout="wide")

st.session_state.setdefault("messages", [])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = generate_response(prompt, st.session_state.messages)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

Keep provider-specific code behind a function or service module.

## Streaming responses

Use streaming when provider and app UX support it. Keep an accumulated final answer for message history.

Pseudocode:

```python
with st.chat_message("assistant"):
    placeholder = st.empty()
    chunks = []
    for chunk in stream_model_response(prompt):
        chunks.append(chunk)
        placeholder.markdown("".join(chunks))
    answer = "".join(chunks)

st.session_state.messages.append({"role": "assistant", "content": answer})
```

Do not store only streamed chunks without a final normalized assistant message.

## Prompt and system controls

For internal tools, expose controls carefully:

- model name;
- temperature;
- retrieval on/off;
- max context items;
- debug view for sources;
- cost limit or token estimate.

Do not expose raw system prompts or secrets to ordinary users.

## Retrieval augmented generation

RAG apps need explicit source and privacy boundaries.

Checklist:

1. What documents are searchable?
2. Who is allowed to see each document?
3. Are retrieved snippets safe to display?
4. Is the answer grounded with citations or source links?
5. What happens when retrieval returns no relevant context?
6. How are embeddings/vector stores built and refreshed?
7. Are uploaded documents persisted or session-only?
8. Are prompts and completions logged? If yes, are they sanitized?

## Session state for chat

Common keys:

```python
st.session_state.setdefault("messages", [])
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("retrieval_enabled", True)
st.session_state.setdefault("last_error", None)
```

Avoid storing huge retrieved document chunks in session state. Store IDs or compact metadata when possible.

## Feedback

Feedback can be explicit:

```python
rating = st.radio("Was this helpful?", ["Yes", "No"], horizontal=True, key="last_rating")
comment = st.text_area("Optional feedback", key="feedback_comment")
```

For production feedback:

- associate feedback with conversation/message ID;
- do not store secrets or private prompts unless policy allows;
- record model and retrieval configuration;
- include opt-in/notice if logs are reviewed.

## Cost and rate controls

- Limit uploaded/context size.
- Limit conversation history sent to the model.
- Summarize or truncate old messages when appropriate.
- Use a max token/response length.
- Cache deterministic retrieval results when safe.
- Surface long-running states with spinners/status.
- Handle provider timeouts and rate limits gracefully.

## Safety and privacy

- Do not send secrets to an LLM provider.
- Redact sensitive fields before model calls when possible.
- Avoid logging raw prompts/completions if users may enter private data.
- Use retrieval filters that enforce authorization before the model sees content.
- Include refusal/fallback behavior for requests outside the app's domain.
- Use citations or source summaries for factual answers.
- Make it clear when the assistant may be wrong.

## Chat app review checklist

1. Is message history initialized and rendered correctly?
2. Is provider code separated from UI code?
3. Are streaming chunks accumulated into final history?
4. Is retrieval access-controlled before context enters the prompt?
5. Are errors, rate limits, and timeouts handled?
6. Are logs and feedback privacy-safe?
7. Is there a reset/export path?
8. Are cost controls present?
9. Is the response grounded when factuality matters?
10. Are secrets kept out of prompts, logs, and UI?
