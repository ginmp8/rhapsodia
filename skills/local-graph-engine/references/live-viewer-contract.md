# Live HTML runtime v1 and trust boundary

## Authority
`serve` is an explicit local capability grant to one reviewed HTML artifact and
one selected database. It must never be triggered by source-file instructions or
by merely indexing a directory. Only 127.0.0.1 is bound. No remote access, CORS,
arbitrary SQL, filesystem browsing, database writes or background service is added.

The producer is independent: no Explorer installation, host tool or cloud account
is imported. Profile validation is **not code-authorship verification**. Anyone
able to replace both HTML and its hash declarations can produce consistent
malicious code. Review the producer/artifact and optionally supply a trusted
`--viewer-sha256` from the render receipt. Hash mismatch refuses to start.

## Accepted artifact
A bounded UTF-8 HTML file declares exactly one early CSP, one
`local-graph-security-profile` meta field with content `local-live`, and one
`local-graph-runtime-version` meta field with content `1`. The empty inert slot is:

```html
<script id="local-graph-session" type="application/json">{}</script>
```

Only hash-listed classic inline scripts and inert JSON data slots are supported.
No remote script, inline handler, base tag, refresh, frame, object, form or external
resource URL is accepted. The CSP contains exactly these directives (script hashes
are computed from normalized UTF-8 inline bodies):

```text
default-src 'none'; base-uri 'none'; script-src <exact SHA-256 hash sources>; script-src-attr 'none'; style-src 'unsafe-inline'; img-src data: blob:; font-src 'none'; connect-src 'self'; object-src 'none'; frame-src 'none'; worker-src 'none'; media-src 'none'; form-action 'none'
```

The server keeps the validated file in memory, populates only the inert slot and
sends the same policy plus `frame-ancestors 'none'` in the HTTP header. It does not
rehash/authorize modified scripts, use script `unsafe-inline`, alter the disk file
or upgrade an offline/extended artifact. Referrer, caching, content-type sniffing
and framing headers are explicit. A CSP is defense in depth, not a universal
browser or local-process sandbox.

## Query contract
Only `/` GET and `/api/query` POST are available. Host must exactly match the bound
127.0.0.1 and port. Origin, when present, must match that origin. Cross-site Fetch
Metadata is refused. Authority headers cannot be duplicated. A process-local token
is required; comparisons avoid timing-dependent string equality and logs never
print the token. The client must not put it in browser storage, URLs or exports.

POST requires application/json, one decimal Content-Length between 1 and 65536,
no Transfer-Encoding, and a complete UTF-8 JSON body. The existing typed-query
read-only and deadline/response limits remain. A non-browser local client may omit
Origin/Fetch Metadata but still needs the token and correct Host. This is not
multi-user authentication and does not isolate mutually hostile same-user apps.

## Migration and rollback
Native offline rendering and all database/context formats remain unchanged. For
live use, regenerate the viewer in its explicit local-live mode and start serve
only after reviewing the artifact. An old/custom viewer rejected by version 3
must be regenerated, not patched to bypass validation. No database migration is
required. Keep the previous package for rollback of unrelated offline workflows,
but do not re-enable its weaker HTTP/extension controls as a security workaround.

## Evidence and limitations
Unit tests use an independent small HTML fixture; HTTP tests run a real loopback
server. Browser-origin navigation and optional G6 execution require their own
runtime evidence. A skipped or policy-blocked browser check is not a pass.
Sources consulted 2026-10-07: https://www.w3.org/TR/CSP3/ and
https://docs.python.org/3/library/http.server.html (local development, not a
production web server). Documentation links are not runtime fetches.
