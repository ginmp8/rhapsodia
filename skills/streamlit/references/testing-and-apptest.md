# Testing and AppTest

## Testing strategy

Split tests into three layers:

1. Pure Python unit tests for data transformations, validation, and business rules.
2. Streamlit AppTest tests for UI structure and interactions.
3. Deployment smoke tests for environment, secrets, and connectivity.

## Design for testability

Move business logic into pure functions. Keep Streamlit rendering thin. Inject model/API/database functions so tests can use fakes.

## AppTest basics

Use `streamlit.testing.v1.AppTest` to run app files and inspect rendered elements. Keep tests small and focused on visible behavior.

Example pattern:

```python
from streamlit.testing.v1 import AppTest


def test_initial_page_loads():
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    assert at.title[0].value == "Dashboard"
```

## Interaction tests

Test widget interactions by setting values, clicking buttons, and rerunning. Use stable widget positions or keys where supported. Avoid brittle tests that depend on every markdown element's exact position.

## What to test

- Initial page loads without exception.
- Important controls exist.
- Empty data state renders.
- Invalid input shows a helpful error.
- Submit button changes expected state.
- Data editor diff logic works in pure tests.
- Chat app appends user and assistant messages with a fake model.
- Auth-gated pages do not show private content when logged out.

## What not to test with AppTest alone

- Real browser CSS layout.
- Real identity provider redirects.
- Paid model APIs.
- Production database writes.
- Full performance under concurrent load.

## Smoke commands

Use:

```bash
streamlit run app.py
python -m pytest
python -m compileall .
```

In CI, prefer pytest for pure and AppTest tests. Use a short manual smoke test for deployed settings and secrets.

## Regression checklist

When fixing a Streamlit bug, add a test or at least a documented manual check for the original symptom. Include the triggering widget interaction and expected visible result.
