# Execution, State, and Reruns

## Mental model

A Streamlit app renders by running the Python script. Most user interactions update widget state and rerun the script. This is simple, but bugs appear when code assumes a traditional long-lived web request handler model.

## Design rules

1. Make top-level code safe to rerun.
2. Put expensive work behind cache functions.
3. Put writes behind explicit submit/action boundaries.
4. Initialize session state before widgets that depend on it.
5. Use callbacks for small state transitions, not for large hidden workflows.
6. Use forms to batch input changes.
7. Use fragments when a subsection should refresh independently.
8. Use dialogs for focused confirmation or modal detail flows.

## Session state patterns

### Initialize explicitly

```python
DEFAULTS = {
    "step": "upload",
    "selected_customer_id": None,
    "messages": [],
    "last_error": None,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)
```

### Update through functions

```python
def select_customer(customer_id: str) -> None:
    st.session_state.selected_customer_id = customer_id
    st.session_state.step = "detail"
```

### Avoid mutable shared defaults

When default values are lists or dicts, create them intentionally. Do not share mutable globals across users.

## Callback guidance

Callbacks run before the app rerenders from top to bottom. Keep callbacks short: update session state, clear a form, or set a selected ID. Avoid network calls, database writes, or large computations inside callbacks unless they are guarded and visibly handled.

## Forms

Forms batch widget changes until submit. Use them when multiple inputs should be validated together or when recalculating on every keystroke is wasteful.

Use forms for:

- search filters with many fields;
- data submission;
- review/approval comments;
- configuration panels;
- expensive calculations.

Avoid forms when immediate interaction is the point, such as sliders driving a visual demo.

## Fragments

Fragments isolate reruns for a part of the app. Use them when one component refreshes frequently or performs expensive redraws. Keep shared state explicit, because fragments can make control flow harder to reason about.

## Dialogs

Dialogs work well for confirmations, detail previews, and small forms that should not clutter the main page. Do not hide critical validation feedback only inside a dialog if the main page depends on the result.

## Common failure modes

### Button state disappears

A button returns true only for the run caused by its click. Persist the result into session state if later code needs it.

### Widget resets unexpectedly

Use stable keys and do not change widget type or options structure across reruns without preserving the selected value.

### Duplicate widget key

Every widget in a loop or repeated component needs a unique key derived from stable business identifiers, not the loop index when the order can change.

### Expensive reload on every change

Move data loading into `@st.cache_data` and resource creation into `@st.cache_resource`. Include only meaningful parameters in the cache key.

### Side effect repeats

Store a transaction ID, use a form submit button, and mark completion in session state after the write.

## Debug procedure

1. Print or display selected `st.session_state` keys temporarily.
2. Identify which widget interaction triggers the rerun.
3. Move expensive work into cached functions.
4. Move persistent UI decisions into session state.
5. Replace hidden callback work with explicit button/form logic when behavior is hard to follow.
6. Add a regression test with `AppTest` when practical.
