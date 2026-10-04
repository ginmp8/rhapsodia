# Testing and AppTest

## Evidence ladder

Use the cheapest layer that can falsify the behavior:

1. **pytest/unit tests** for pure Python logic, validation, parsing, calculations, and data transforms.
2. **`st.testing.v1.AppTest`** for Streamlit script behavior: widget interactions, rendered elements, session state, multipage behavior, and exception-free reruns.
3. **browser/E2E** for rendered DOM/CSS, responsive layout, scroll/focus behavior, custom-component JavaScript, and browser-only selection/event behavior.
4. **deployment smoke/integration** for process startup, secrets, identity-provider redirects, external connectivity, proxies, health checks, and platform/runtime configuration.

A pass at one layer does not imply the next layer passed.

## Design for testability

Move business/data logic into pure functions and keep rendering thin. Inject database/API/model boundaries so unit and AppTest tests can use fakes. Use stable widget keys so tests do not depend on incidental element order.

## AppTest basics

Use the app entrypoint for multipage apps, run once so navigation registers, then switch pages when needed. After every interaction/rerun, check `at.exception` before asserting downstream state.

AppTest is preferred over starting a server/browser for ordinary Streamlit behavior because it is in-process and deterministic. Do not use it as proof of CSS, JavaScript, custom-component runtime, or actual identity-provider redirect behavior.

## Regression expectations

For a bug fix, encode the original triggering interaction and expected visible/state result in the narrowest suitable test. Do not weaken an existing assertion merely to make a candidate pass; if the evaluator is wrong, invalidate and repair it separately.

## Smoke checks

Prefer repository-owned commands. Typical checks include:

```text
<PYTHON> -m pytest
<PYTHON> -m compileall .
streamlit run <entrypoint>
```

Use runtime/browser checks only when the claim actually depends on them. Never report an unexecuted check as passing.
