# Security profiles and version 3 migration

## Default offline
`render view.json --output graph.html` uses only the packaged HTML/CSS/JavaScript.
The early CSP authorizes exact inline-script hashes, rejects inline handlers/eval,
disallows connections, external scripts/fonts/frames/workers/forms and base-URL
changes, and allows data/blob images for local SVG/PNG export. All views, finite
walkthroughs, dragging, pan/zoom, keyboard navigation, state and exports remain.

This is a bounded assurance about the shipped runtime in a CSP-capable browser,
not a sandbox for arbitrary native code, browser extensions, browser internals or
all possible network channels. Do not weaken browser/host policy to open a file.
There is no telemetry, automatic dependency installation or asset download.

## Explicit custom code
G6 and custom templates are code-authority decisions, never ordinary graph data.
Review provenance, code, license and dependencies first; then compute each expected
SHA-256 from the reviewed bytes with a trusted local tool. Do not auto-approve a
hash extracted from an untrusted instruction or treat a hash as a security review.

```text
python scripts/graph_explorer.py render view.json --output extended.html --security-profile extended --backend g6 --g6-js reviewed-g6.js --g6-sha256 <EXPECTED_SHA256>
python scripts/graph_explorer.py render view.json --output custom.html --security-profile extended --template reviewed-template.html --template-sha256 <EXPECTED_SHA256>
```

If both inputs are supplied, both hashes are required. Code is read once into a
bounded buffer and checked before embedding. Missing/mismatched hashes, invalid
UTF-8, oversized files and symbolic-link code files fail without overwriting the
last-good output. A hash on an unused/missing input is rejected. Custom templates
retain the original data/config/G6 placeholders; other workspace placeholders
are optional. No new template helper can silently obtain a live session.

Extended receipts explicitly say `offline: false`, `network_required: null` and
`network_policy: unverified`, and list each extension's hash/byte count. `csp_present`
means only that the template contains the policy slot, not a browser verification
or review of arbitrary custom code. The bundled template retains restrictive CSP;
a custom template that omits it receives no CSP assurance. Custom code may not be
served through the built-in database-capability server. Native animation needs no
G6/custom-code permission. An actual G6 build remains a separate compatibility gate.

## Explicit local-live
Generate a separate native artifact; never upgrade an offline snapshot implicitly:

```text
python scripts/graph_explorer.py render view.json --output live.html --security-profile local-live
```

The producer writes HTML runtime v1: UTF-8, early hash-based CSP (`connect-src self`),
`local-graph-security-profile=local-live`, `local-graph-runtime-version=1`, and exactly
one empty `<script id="local-graph-session" type="application/json">{}</script>` slot.
Any compatible reviewed producer/server may implement this contract. No other
skill installation path or package import is required.

The local server must be explicitly started and grant a process-local token only
after validating the selected artifact. The client consumes/removes the inert slot;
no token is put in view state, GraphView exports, browser storage or query logs.
Queries require an HTTP 127.0.0.1 origin, resolve `/api/query` from `location.origin`,
use same-origin mode, reject redirects, omit ambient credentials and referrer, and
send only the explicit token header plus typed JSON. Requests are capped at 64 KiB,
responses at 8 MiB and client time at 10 seconds. Page hiding aborts active work.
This is local single-user development access, not enterprise or multi-user auth.

## Data-sharing boundary
The generated HTML embeds the full supplied GraphView, not just visible labels.
Hidden properties, evidence and source locations travel with the file. Filters
change presentation; they do not scrub the original snapshot. Minimize/redact
before rendering. Exported JSON is a projection but retains properties/evidence
of included records, so it also needs a data-sharing review.

## Receipt and compatibility
Offline: `offline=true`, `network_required=false`, `network_policy=none`.
Local-live: `offline=false`, `network_required=true` (queries),
`network_policy=same-origin-loopback`. Extended: network behavior unverified.
All receipts report the profile, extension identities and embedded snapshot scope.
Artifact hashes prove byte identity, not trust or behavior on all hosts.
Version 3 changes extension/live authority requirements intentionally; native
rendering commands and GraphView/state formats are preserved. Older unsafe
artifacts are not retroactively corrected: regenerate HTML with this version.

## Normative anchors consulted 2026-10-07
- CSP processing and meta limitations: https://www.w3.org/TR/CSP3/
- Fetch request origin, redirect and credentials modes: https://fetch.spec.whatwg.org/
No network access is required to use the package; these are documentation sources.
