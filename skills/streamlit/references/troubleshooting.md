# Troubleshooting

## Triage flow

1. Identify the symptom: startup failure, blank page, widget/state issue, slow interaction, data error, chart error, deployment failure, auth issue, or upload problem.
2. Ask for or inspect the smallest evidence: error text, traceback, app snippet, requirements, Streamlit version, deployment target, or reproduction steps.
3. Classify root cause: Python error, dependency/config, rerun/state, cache, data/schema, network/secrets, deployment, or browser/client issue.
4. Provide the smallest patch and a validation step.

## App does not start

Common causes:

- syntax error;
- missing package;
- wrong app path;
- Streamlit not installed in environment;
- incompatible Python version;
- import side effect requiring unavailable secrets/network;
- `st.set_page_config` called too late in older patterns.

Checks:

```bash
python -m py_compile app.py
python -c "import streamlit; print(streamlit.__version__)"
streamlit run app.py
```

## Blank page or no output

Check:

- Did the script stop early with `st.stop()`?
- Is an exception hidden in logs?
- Is content behind a condition that is false?
- Is the app waiting on a slow network call?
- Is a widget key collision causing failure?
- Is the app deployed with the wrong entrypoint?

Add visible checkpoints temporarily:

```python
st.write("Reached data loading")
```

Remove debug output before finalizing.

## Widget value resets unexpectedly

Likely causes:

- widget key changes between reruns;
- widget is conditionally hidden and recreated;
- session state key is overwritten each run;
- callback mutates the wrong key;
- multipage page uses a different key name.

Fixes:

- use stable explicit keys;
- initialize with `setdefault`, not unconditional assignment;
- keep widgets mounted when possible;
- separate display label from state key.

Bad:

```python
st.session_state.name = ""
name = st.text_input("Name", key="name")
```

Good:

```python
st.session_state.setdefault("name", "")
name = st.text_input("Name", key="name")
```

## Infinite rerun or repeated refresh

Likely causes:

- unconditional `st.rerun()`;
- callback changes state every run;
- auto-refresh logic without a guard;
- widget default depends on changing value;
- cache clear triggered on every render.

Add guards:

```python
if st.session_state.get("needs_refresh"):
    st.session_state.needs_refresh = False
    st.rerun()
```

Use `st.rerun` sparingly.

## Slow app

Diagnose before optimizing:

- Which line is slow?
- Does it happen every rerun?
- Is the data source slow or the rendering slow?
- Is a large dataframe/chart rendered unnecessarily?
- Are hidden tabs still computing expensive content?

Common fixes:

- `st.cache_data` for query results and transforms;
- `st.cache_resource` for clients/models;
- forms for expensive filters;
- row limits and aggregation;
- lazy details behind a button;
- reduce uploaded-file reparsing.

## Cache seems wrong or stale

Check:

- Missing function arguments in cache key.
- Mutable cached object modified in place.
- `ttl` too long.
- Underscore-prefixed argument excludes something important.
- User/tenant context omitted.
- Cache not cleared after write.

Use explicit cache keys and clear controls.

## Uploaded file fails

Check:

- extension and MIME type;
- file size;
- encoding;
- required columns;
- delimiter;
- Excel sheet name;
- malformed rows;
- privacy constraints.

Display a useful error and sample expected schema.

## Deployment failure

Check:

- app entrypoint;
- dependencies present;
- Python version;
- system packages;
- secrets configured;
- network access to data source;
- file paths relative to app root;
- case-sensitive filenames;
- port/address for Docker;
- logs for first traceback.

## Auth or secrets failure

Check:

- secret name mismatch;
- local secrets file absent;
- environment variable not injected;
- platform secret settings not saved;
- identity provider redirect URI;
- relying on untrusted headers;
- cached auth-dependent data without user key.

Do not print secret values while debugging.

## Error response pattern

When answering troubleshooting requests, use:

```markdown
## Likely cause
[one or two likely root causes]

## Fix
[smallest patch]

## Verify
[command or interaction]

## If it still fails
[next diagnostic evidence to collect]
```

## Common anti-fixes

- Adding `st.rerun()` to every state issue.
- Removing cache entirely instead of fixing cache keys.
- Moving everything into session state.
- Catching all exceptions and hiding them.
- Adding a new framework or component before isolating the bug.
- Hardcoding secrets to "test quickly".
