# Streamlit API Command Guide

This guide is an original command-oriented reference. It links to official documentation for exact signatures and version-specific behavior.

# Write Magic Text Status

### `st.write`

Official reference: https://docs.streamlit.io/develop/api-reference/write-magic/st.write

**Use it when** the app needs general-purpose rendering for strings, dataframes, charts, exceptions, and rich objects. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.write_stream`

Official reference: https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream

**Use it when** the app needs streaming tokens or chunks with a typewriter-like user experience. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `magic`

Official reference: https://docs.streamlit.io/develop/api-reference/write-magic/magic

**Use it when** the app needs automatic rendering of bare expressions when magic is enabled. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.title`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.title

**Use it when** the app needs page-level title text. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.header`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.header

**Use it when** the app needs major section headings. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.subheader`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.subheader

**Use it when** the app needs subsection headings. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.markdown`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.markdown

**Use it when** the app needs markdown content and controlled inline formatting. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.caption`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.caption

**Use it when** the app needs small explanatory text and footnotes. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.badge`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.badge

**Use it when** the app needs compact status badges. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.code`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.code

**Use it when** the app needs syntax-highlighted code blocks. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.echo`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.echo

**Use it when** the app needs rendering code and its result for tutorials. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.latex`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.latex

**Use it when** the app needs LaTeX math rendering. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.text`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.text

**Use it when** the app needs preformatted plain text. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.divider`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.divider

**Use it when** the app needs visual separation between sections. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.html`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.html

**Use it when** the app needs isolated HTML snippets when markdown is insufficient. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.help`

Official reference: https://docs.streamlit.io/develop/api-reference/text/st.help

**Use it when** the app needs quick inspection of Python objects and functions. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.success`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.success

**Use it when** the app needs positive callouts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.info`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.info

**Use it when** the app needs neutral informational callouts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.warning`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.warning

**Use it when** the app needs warning callouts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.error`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.error

**Use it when** the app needs error callouts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.exception`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.exception

**Use it when** the app needs exception display with tracebacks. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.progress`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.progress

**Use it when** the app needs progress bars for long-running work. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.spinner`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.spinner

**Use it when** the app needs temporary loading indicators. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.status`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.status

**Use it when** the app needs multi-step status containers. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.toast`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.toast

**Use it when** the app needs transient notifications. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.balloons`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.balloons

**Use it when** the app needs celebration animation. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.snow`

Official reference: https://docs.streamlit.io/develop/api-reference/status/st.snow

**Use it when** the app needs decorative animation. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

# Data Charts Media

### `st.dataframe`

Official reference: https://docs.streamlit.io/develop/api-reference/data/st.dataframe

**Use it when** the app needs interactive dataframe display. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.data_editor`

Official reference: https://docs.streamlit.io/develop/api-reference/data/st.data_editor

**Use it when** the app needs editable tabular data with typed columns. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.column_config`

Official reference: https://docs.streamlit.io/develop/api-reference/data/st.column_config

**Use it when** the app needs column type, formatting, validation, and display configuration. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.table`

Official reference: https://docs.streamlit.io/develop/api-reference/data/st.table

**Use it when** the app needs static table rendering. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.metric`

Official reference: https://docs.streamlit.io/develop/api-reference/data/st.metric

**Use it when** the app needs KPI and metric display with delta. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st` JSON display command

Official reference: https://docs.streamlit.io/develop/api-reference/data/st JSON display command

**Use it when** the app needs expandable JSON inspection. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.line_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.line_chart

**Use it when** the app needs simple line charts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.area_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.area_chart

**Use it when** the app needs simple area charts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.bar_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart

**Use it when** the app needs simple bar charts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.scatter_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.scatter_chart

**Use it when** the app needs simple scatter charts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.map`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.map

**Use it when** the app needs map visualization from latitude and longitude columns. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.altair_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart

**Use it when** the app needs declarative Vega-Lite charts. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.plotly_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart

**Use it when** the app needs interactive Plotly figures. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.pyplot`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.pyplot

**Use it when** the app needs Matplotlib figures. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.pydeck_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart

**Use it when** the app needs deck.gl map and layer visualizations. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.vega_lite_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.vega_lite_chart

**Use it when** the app needs Vega-Lite specs. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.graphviz_chart`

Official reference: https://docs.streamlit.io/develop/api-reference/charts/st.graphviz_chart

**Use it when** the app needs Graphviz diagrams. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.image`

Official reference: https://docs.streamlit.io/develop/api-reference/media/st.image

**Use it when** the app needs image display. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.audio`

Official reference: https://docs.streamlit.io/develop/api-reference/media/st.audio

**Use it when** the app needs audio display. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.video`

Official reference: https://docs.streamlit.io/develop/api-reference/media/st.video

**Use it when** the app needs video display. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.logo`

Official reference: https://docs.streamlit.io/develop/api-reference/media/st.logo

**Use it when** the app needs app logo branding. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.pdf`

Official reference: https://docs.streamlit.io/develop/api-reference/media/st.pdf

**Use it when** the app needs PDF display when available. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

# Widgets Layout Execution

### `st.button`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.button

**Use it when** the app needs momentary actions and explicit user-triggered events. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.download_button`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.download_button

**Use it when** the app needs browser downloads from generated data. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.link_button`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.link_button

**Use it when** the app needs buttons that navigate to external links. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.page_link`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.page_link

**Use it when** the app needs navigation links between pages. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.checkbox`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.checkbox

**Use it when** the app needs boolean toggles. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.toggle`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.toggle

**Use it when** the app needs boolean switch UI. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.radio`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.radio

**Use it when** the app needs single selection from visible options. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.selectbox`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox

**Use it when** the app needs single selection from larger option lists. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.multiselect`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect

**Use it when** the app needs multi-selection. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.pills`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.pills

**Use it when** the app needs compact selection pills. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.segmented_control`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.segmented_control

**Use it when** the app needs segmented option picker. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.slider`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.slider

**Use it when** the app needs numeric, date, or range selection. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.select_slider`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.select_slider

**Use it when** the app needs slider across discrete values. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.number_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.number_input

**Use it when** the app needs numeric typed input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.date_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.date_input

**Use it when** the app needs date input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.time_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.time_input

**Use it when** the app needs time input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.datetime_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.datetime_input

**Use it when** the app needs datetime input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.text_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.text_input

**Use it when** the app needs short text input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.text_area`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.text_area

**Use it when** the app needs longer text input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.chat_input`

Official reference: https://docs.streamlit.io/develop/api-reference/chat/st.chat_input

**Use it when** the app needs chat prompt input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.file_uploader`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader

**Use it when** the app needs browser file uploads. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.camera_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input

**Use it when** the app needs camera image capture. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.audio_input`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input

**Use it when** the app needs audio capture input. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.feedback`

Official reference: https://docs.streamlit.io/develop/api-reference/widgets/st.feedback

**Use it when** the app needs thumb/star feedback capture. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.columns`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.columns

**Use it when** the app needs horizontal layout. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.container`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.container

**Use it when** the app needs grouped layout block. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.empty`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.empty

**Use it when** the app needs placeholder replacement. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.expander`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.expander

**Use it when** the app needs collapsible details. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.popover`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.popover

**Use it when** the app needs button-triggered overlay container. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.sidebar`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.sidebar

**Use it when** the app needs sidebar layout region. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.tabs`

Official reference: https://docs.streamlit.io/develop/api-reference/layout/st.tabs

**Use it when** the app needs tabbed sections. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.form`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form

**Use it when** the app needs batched input submission. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.form_submit_button`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form_submit_button

**Use it when** the app needs form submission trigger. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.dialog`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog

**Use it when** the app needs modal interaction flow. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.fragment`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment

**Use it when** the app needs isolated partial reruns. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.stop`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.stop

**Use it when** the app needs early stop. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.rerun`

Official reference: https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun

**Use it when** the app needs programmatic rerun. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

# State Connections Navigation Auth

### `st.session_state`

Official reference: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

**Use it when** the app needs per-session state across reruns. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.cache_data`

Official reference: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data

**Use it when** the app needs cached data values and transformations. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.cache_resource`

Official reference: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource

**Use it when** the app needs cached singleton resources such as clients and models. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.query_params`

Official reference: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params

**Use it when** the app needs browser query parameters. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.context`

Official reference: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.context

**Use it when** the app needs browser/session context information. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.secrets`

Official reference: https://docs.streamlit.io/develop/api-reference/connections/st.secrets

**Use it when** the app needs secret lookup. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.connection`

Official reference: https://docs.streamlit.io/develop/api-reference/connections/st.connection

**Use it when** the app needs connection factory for external systems. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `SQLConnection`

Official reference: https://docs.streamlit.io/develop/api-reference/connections/st.connections.sqlconnection

**Use it when** the app needs SQL query convenience connection. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `SnowflakeConnection`

Official reference: https://docs.streamlit.io/develop/api-reference/connections/st.connections.snowflakeconnection

**Use it when** the app needs Snowflake connection integration. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `BaseConnection`

Official reference: https://docs.streamlit.io/develop/api-reference/connections/st.connections.baseconnection

**Use it when** the app needs base class for custom connections. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.login`

Official reference: https://docs.streamlit.io/develop/api-reference/user/st.login

**Use it when** the app needs start OIDC login flow. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.logout`

Official reference: https://docs.streamlit.io/develop/api-reference/user/st.logout

**Use it when** the app needs clear logged-in user session. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.user`

Official reference: https://docs.streamlit.io/develop/api-reference/user/st.user

**Use it when** the app needs read authenticated user info. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.navigation`

Official reference: https://docs.streamlit.io/develop/api-reference/navigation/st.navigation

**Use it when** the app needs programmatic multipage navigation. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.Page`

Official reference: https://docs.streamlit.io/develop/api-reference/navigation/st.page

**Use it when** the app needs page declaration for navigation. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.switch_page`

Official reference: https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page

**Use it when** the app needs programmatic page switch. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?

### `st.set_page_config`

Official reference: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config

**Use it when** the app needs browser tab, layout, menu, and icon config. Prefer this command when it gives the user a direct, native Streamlit interaction instead of building custom HTML or JavaScript.

**Design guidance**
- Put the command close to the data or decision it explains; avoid dumping unrelated UI at the top of the script.
- Give every user-facing label a business meaning. Labels like `Option 1` or `value` are less useful than labels that name the filter, metric, stage, or action.
- Use stable `key=` values for widgets when the page is complex, generated from loops, or split across conditional branches.
- Decide whether the command is display-only, state-changing, or expensive. Display-only commands can sit in normal script flow; state-changing commands need explicit session-state handling; expensive commands usually need caching or a form boundary.

**State and rerun notes**
- Streamlit reruns the script after most widget interactions. Design code so the top-to-bottom rerun is harmless and deterministic.
- Do not hide irreversible work directly behind an automatically changing widget. Use a button, form submit, confirmation dialog, or explicit callback.
- Keep per-user selections in `st.session_state`; keep shared expensive resources in `st.cache_resource`; keep reusable computed data in `st.cache_data`.

**Common pitfalls**
- Treating widget return values as persistent storage instead of using `st.session_state` for multi-step flows.
- Performing database writes, API calls, or file mutations on every rerun.
- Building custom HTML before checking whether a native Streamlit command already solves the use case.
- Forgetting that multiple users can execute the same app concurrently.

**Review checklist**
- Is the command appropriate for the interaction type?
- Are labels, help text, and defaults clear?
- Are keys stable when the command appears conditionally or repeatedly?
- Is expensive or side-effecting work protected from accidental reruns?
- Is the behavior testable with `streamlit.testing.v1.AppTest` or a small manual smoke test?
