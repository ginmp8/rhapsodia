# Validation and claim boundaries

## Commands
From this skill root, run `<PYTHON> -B -m unittest discover -s tests -v`. Keep PYTHONDONTWRITEBYTECODE=1 when validating frozen packages. Tests write into temporary directories and preserve bundled original fixtures.
For the Explorer, test_browser.py uses installed Playwright and a browser selected by LOCAL_GRAPH_BROWSER or an available Chromium executable. Without these optional test tools the browser class is skipped; skipped is not a runtime pass. Browser tests load the generated HTML into an isolated blank document and block/record unexpected requests. Native file:// opening and host UI preview policies remain separate.

## Evidence categories
Structural: frontmatter, references, schemas, portable paths, packaging. Behavioral: executed ingestion/query/history/export/invalid-input tests. Browser: actual DOM/interactions/errors/network/viewport tests in the exercised browser. Perceptual: screenshot inspection, not algorithmic truth. Host: only actual execution in a given client establishes client runtime support.
The delivery report lists exact counts, versions, optional skips and checks. No benchmark, model-routing reliability, penetration test, complete MCP conformance or universal OS/browser compatibility is implied.

## Relevant oracles
Source preserves identifiers, zero/false, duplicates and original assertions. Failed patches roll back; other sources survive refresh; replay is idempotent; graph direction and bounded path results match fixtures; private writes and output aliases are rejected; offline UI has no unexpected requests; tables/matrix/timeline use the supplied values; malicious labels are text; generated HTML and ZIP bytes replay identically.

## Node gesture regression
`tests/test_node_drag.py` exercises mouse drag, zoom/pan/CSS coordinate transforms, live incident/parallel/self-loop edges, background pan, click jitter, pointer capture outside the canvas, Escape cancellation, secondary-button rejection, emulated touch, keyboard movement, retention across filters/views, validated state save/restore, legacy state compatibility, reset/layout changes, data immutability and SVG export. These are browser tests, not evidence that every physical input device or optional G6 bundle has been tested.

## Added regression surface
`test_walkthrough_browser.py`, `test_walkthrough_hardening.py` and `test_traversal.cjs` cover bounded layers/paths/cycles, motion guards, drag coexistence, mobile containment, semantic relationship labels and export isolation. Required optional tools must be present for the matching runtime claim; skips are reported.

## Security profiles
`test_explorer_security.py` checks profile separation, receipt honesty, pinned
extension bytes, restrictive CSP, parser-safe source JSON and output preservation.
`test_security_browser.py` executes synthetic injection/network-block probes and
all five export formats with CSP active; no bypass-CSP setting is used.
`test_live_client.cjs` executes the production client block with a fake DOM and
transport to check URL/options, byte budgets, timeout, cancellation and concurrency.
Its Node wrapper skips when Node is unavailable. This is not real-browser HTTP
integration proof. `file://` and actual browser loopback navigation remain separate
environment-dependent checks. Existing DOM waits use locator assertions rather
than eval-based polling, without weakening the production CSP.
