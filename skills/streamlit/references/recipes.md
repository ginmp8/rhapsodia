# Recipes

## Cached dashboard filter

```python
@st.cache_data(ttl=300)
def load_orders(status: str, region: str):
    return query_orders(status=status, region=region)

with st.sidebar.form("filters"):
    status = st.selectbox("Status", ["All", "Pending", "Closed"])
    region = st.selectbox("Region", ["All", "North", "South"])
    apply_filters = st.form_submit_button("Apply")

if apply_filters or "orders" not in st.session_state:
    st.session_state.orders = load_orders(status, region)

st.dataframe(st.session_state.orders)
```

## Confirmed write action

```python
with st.form("approve"):
    st.write("Approve selected request?")
    note = st.text_area("Approval note")
    confirmed = st.checkbox("I reviewed the request")
    submitted = st.form_submit_button("Approve", disabled=not confirmed)

if submitted:
    result = approve_request(request_id, note)
    st.success(f"Approved request {result.reference}")
```

## Editable table with diff

```python
edited = st.data_editor(df, key="editor", disabled=["id"])
changed = edited.compare(df, keep_shape=False, keep_equal=False)
if not changed.empty:
    st.write("Pending changes")
    st.dataframe(changed)
    if st.button("Save changes"):
        save_changes(edited)
```

## Chat with fakeable backend

```python
def generate_response(prompt: str) -> str:
    return f"You said: {prompt}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer = generate_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
```

## Download dataframe

```python
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download CSV",
    data=csv_bytes,
    file_name="report.csv",
    mime="text/csv",
)
```

## Empty and error states

```python
if data.empty:
    st.info("No records match the current filters.")
    st.stop()

try:
    render_chart(data)
except Exception as exc:
    st.error("The chart could not be rendered with the current data.")
    st.caption("Try narrowing the filters or contact support if this persists.")
```
