# Custom Components v2

## Decision rule

Use a custom component only when native Streamlit elements cannot provide the required interaction. For new interactive components on a Streamlit version that supports Components v2, prefer `st.components.v2` over legacy v1 component APIs.

## Architecture

Declare/register the component once, then expose a small Python wrapper with typed/domain-friendly arguments. Keep registration/build details internal to the wrapper. Mount multiple instances with stable keys.

The frontend receives component data/context and returns state or trigger values through the supported v2 bridge. Keep persistent state and one-shot event triggers conceptually separate. Rehydrate frontend state from Python inputs on reruns.

## Lifecycle and isolation

Scope DOM queries/resources to the component instance, not the global document. Clean up listeners, observers, framework roots, and subscriptions when the component unmounts. Style isolation prevents accidental CSS leakage; it is not a security sandbox.

## Security

Treat component JavaScript as trusted application code. Do not evaluate arbitrary user-provided scripts or inject untrusted HTML as executable behavior. Validate data crossing the JS/Python boundary before protected actions.

## Theming

Use Streamlit-provided theme variables when available so components follow light/dark/custom themes. Avoid hard-coded app-global CSS unless the component explicitly requires it.

## Packaging

For packaged components, prefer the official current Streamlit component template and its build/manifest conventions rather than hand-scaffolding stale v1 examples. Validate in an actual Streamlit runtime; import-only checks do not prove frontend assets mount correctly.

## Testing

Test Python wrapper/data logic with pytest/AppTest where representable. Test JavaScript, DOM, CSS, event wiring, focus, and browser behavior with browser/E2E validation.
