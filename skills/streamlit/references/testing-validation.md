# Testing and Validation

## Validation ladder

Use the narrowest validation that proves the claim.

1. Static review: inspect code for rerun, cache, state, security, and deployment issues.
2. Import/syntax check: catches obvious Python errors.
3. `streamlit run` smoke test: confirms the app starts.
4. Manual browser smoke: confirms main flow works.
5. AppTest: exercises widgets and assertions in Python.
6. Integration tests: validate database/API boundaries with controlled fixtures.
7. Deployment smoke: confirms runtime config, secrets, network, and auth.

Do not claim a higher rung without evidence.

## AppTest basics

Use AppTest for deterministic interactions that do not require a real browser.

Example shape:

```python
from streamlit.testing.v1 import AppTest


def test_app_starts():
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    assert at.title[0].value == "Dashboard"
```

Widget interaction example:

```python
def test_filter_changes_output():
    at = AppTest.from_file("app.py").run()
    at.selectbox(key="status_filter").select("Approved").run()
    assert "Approved" in at.markdown[0].value
```

Exact selectors depend on widgets and Streamlit version. Keep tests close to actual UI keys.

## What to test

High-value tests:

- app starts without exceptions;
- required session state is initialized;
- form submission updates output;
- invalid uploads show errors;
- empty data shows empty state;
- cache wrappers are called with expected parameters;
- critical charts/tables render after filters;
- auth guard stops unauthenticated access;
- download button creates expected content.

Low-value tests:

- asserting every text label;
- snapshots that change frequently;
- testing Streamlit internals;
- broad tests that require live production credentials.

## Smoke test script

For simple apps, include a lightweight start check:

```bash
python -m py_compile app.py
streamlit run app.py --server.headless true
```

In automated environments, a proper smoke test may need a timeout and HTTP check. Do not leave a server running indefinitely in CI.

## Review report structure

When reviewing an app, use severity and evidence.

```markdown
## Findings
1. [high] Shared cache may leak tenant data - `load_rows()` uses current user implicitly and has no user/tenant cache key.

## Fix
Pass `tenant_id` and `user_id` explicitly into the cached function.

## Validation
Add an AppTest or unit test that calls the data loader with two tenants and verifies separate keys/results.
```

## Deployment validation

Before saying an app is deployment-ready, verify or ask for:

- requirements.txt or dependency manager;
- Python version;
- Streamlit version;
- secrets/config method;
- port/headless settings for containerized deploy;
- auth model;
- data source network access;
- file upload limits;
- logging and error visibility;
- rollback path.

## Security validation

Check:

- no hardcoded secrets;
- no `st.write(st.secrets)` or raw config dumps;
- upload type/size/schema validation;
- cache isolation for user data;
- SQL parameterization;
- safe error messages;
- auth guard before private data display;
- no arbitrary file path reads based on user input;
- no unsafe deserialization of uploaded files.

## Quality gate checklist

For a substantial Streamlit app answer or review:

- App starts locally.
- Main interaction path is documented.
- State keys are deterministic.
- Cache boundaries are explicit.
- Error and empty states exist.
- Secrets are externalized.
- Tests or smoke checks are provided.
- Deployment assumptions are visible.

## Suggested test files

```text
tests/
  test_app_start.py
  test_filters.py
  test_upload_validation.py
  test_state.py
```

Keep UI tests limited. Put pure data transformations in normal unit tests.

## Example testable app design

Move pure logic out of Streamlit UI:

```python
# src/transform.py
def filter_orders(df, status):
    if status == "All":
        return df
    return df[df["status"] == status]
```

Then test it without Streamlit:

```python
def test_filter_orders_filters_status(sample_orders):
    result = filter_orders(sample_orders, "Approved")
    assert set(result["status"]) == {"Approved"}
```

Use AppTest for UI wiring; use ordinary unit tests for pure logic.
