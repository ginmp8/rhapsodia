# Widgets, Forms, and Callbacks

## Widget selection matrix

- `st.button`: one-time action.
- `st.download_button`: download generated content.
- `st.checkbox` or `st.toggle`: boolean choices.
- `st.radio`: small single-choice set where all options should be visible.
- `st.selectbox`: larger single-choice set.
- `st.multiselect`: multiple values from a controlled vocabulary.
- `st.slider`: numeric or date range exploration.
- `st.text_input`: short exact value.
- `st.text_area`: paragraph-scale input.
- `st.file_uploader`: user-supplied files.
- `st.data_editor`: structured editable table.
- `st.feedback`: quick rating for outputs.

## Label design

Good labels are domain-specific and explain the action or data. Use help text for constraints, examples, and side effects. Avoid labels that only mirror variable names.

## Keys

Use explicit keys when:

- widgets appear inside loops;
- a component is reused;
- widgets are conditionally rendered;
- pages share conceptual controls;
- state must persist through option changes.

Use stable business identifiers:

```python
for row in rows:
    st.checkbox(row["label"], key=f"approve_{row['id']}")
```

## Forms as transaction boundaries

A form should usually return a validated data structure:

```python
with st.form("customer_search"):
    tax_id = st.text_input("Tax ID")
    status = st.selectbox("Status", ["Any", "Pending", "Approved"])
    submitted = st.form_submit_button("Search")

if submitted:
    errors = validate_search(tax_id, status)
    if errors:
        st.error("Fix the highlighted filters before searching.")
    else:
        st.session_state.search = {"tax_id": tax_id, "status": status}
```

## Callback discipline

Use callbacks for small state updates:

```python
def clear_filters():
    st.session_state.filters = {}

st.button("Clear filters", on_click=clear_filters)
```

Avoid callbacks for complex I/O because errors become less visible and harder to test. Prefer explicit procedural code after a button or form submit.

## Validation patterns

- Validate user input before calling external APIs.
- Show field-level guidance when possible.
- Keep raw validation details in logs, not user messages, when sensitive.
- Disable destructive actions until required inputs exist.
- Use confirmation checkboxes or dialogs for irreversible operations.

## Uploaded files

Uploaded files are file-like objects. Check name, size, extension, MIME hints, and parser errors. Do not trust extensions alone. For large files, consider chunking or summarize before rendering.

## Data editor workflow

1. Load source data.
2. Create a display/edit copy with stable row IDs.
3. Configure columns and disabled fields.
4. Capture edited data.
5. Compute diff.
6. Show diff preview.
7. Save only after confirmation.

## Accessibility and UX

- Prefer visible labels over placeholder-only inputs.
- Keep controls near the outputs they affect.
- Use disabled states and help text instead of letting invalid actions fail late.
- Do not overload the sidebar with unrelated controls.
- Show loading and empty states intentionally.
