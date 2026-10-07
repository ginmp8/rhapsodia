# Validation and claim boundaries

## Commands
From this skill root, run `<PYTHON> -B -m unittest discover -s tests -v`. Keep PYTHONDONTWRITEBYTECODE=1 when validating frozen packages. Tests write into temporary directories and preserve bundled original fixtures.
For the Explorer, test_browser.py uses installed Playwright and a browser selected by LOCAL_GRAPH_BROWSER or an available Chromium executable. Without these optional test tools the browser class is skipped; skipped is not a runtime pass. Browser tests load the generated HTML into an isolated blank document and block/record unexpected requests. Native file:// opening and host UI preview policies remain separate.

## Evidence categories
Structural: frontmatter, references, schemas, portable paths, packaging. Behavioral: executed ingestion/query/history/export/invalid-input tests. Browser: actual DOM/interactions/errors/network/viewport tests in the exercised browser. Perceptual: screenshot inspection, not algorithmic truth. Host: only actual execution in a given client establishes client runtime support.
The delivery report lists exact counts, versions, optional skips and checks. No benchmark, model-routing reliability, penetration test, complete MCP conformance or universal OS/browser compatibility is implied.

## Relevant oracles
Source preserves identifiers, zero/false, duplicates and original assertions. Failed patches roll back; other sources survive refresh; replay is idempotent; graph direction and bounded path results match fixtures; private writes and output aliases are rejected; offline UI has no unexpected requests; tables/matrix/timeline use the supplied values; malicious labels are text; generated HTML and ZIP bytes replay identically.

## Added regression surface
`test_context.py` and `test_context_integration.py` cover byte accounting, filtered evidence, caller-held reuse/invalidation, canonical-schema compatibility, CLI/MCP and same-selection measurement. Required optional tools must be present for the matching runtime claim; skips are reported.

## Local HTTP security
`tests/test_live_security.py` uses an independent runtime-v1 HTML fixture and real
loopback HTTP to test explicit live authority, script/CSP identity, unsafe page
rejection, origin/token/Host/metadata checks, JSON/size/transport controls and
read-only byte preservation. The shared HTML contract is tested without importing
a viewer package. Real browser-to-server navigation is a separate optional check;
HTTP tests alone are not end-to-end browser integration evidence.
