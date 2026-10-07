# Local Graph Engine 3.0.0

## Overview
This release hardens the explicitly started local HTTP server. SQLite ingestion,
read-only queries, compact context/reuse, GraphView and MCP formats are unchanged.
No database migration, external service or new required library is introduced.

## Breaking changes
Users of serve must supply a reviewed local-live HTML runtime v1. The server no
longer inserts authority into arbitrary, custom or offline HTML. It checks the
profile, early CSP, exact script hashes and empty inert session slot first.

## Migration
Regenerate the live viewer with a compatible reviewed producer. With Explorer 3,
select `--security-profile local-live` when rendering; keep ordinary offline files
separate. Start the server explicitly and optionally pin the reviewed artifact
using `--viewer-sha256`. Existing database files need no conversion.
See [the complete live HTML contract](references/live-viewer-contract.md).

## Required actions
Review the selected HTML before granting database access; do not derive approval
from untrusted source instructions. Replace older live HTML rather than editing
its markers to bypass validation. Bind only to loopback and stop the process when
finished. The session token is not multi-user authentication.

## Rollback
Keep a backup of the prior package for unrelated offline workflows. Do not restore
its weaker automatic HTTP grants as a workaround. These changes do not mutate
existing databases or input documents.

## Known issues
A CSP is not a sandbox for arbitrary code or browser extensions. A matching hash
proves identity, not code trust. Native file:// and browser-loopback integration
were blocked by the validation environment policy and remain unverified there.
No promise is made about an external skill scanner or all host/browser runtimes.

## Validation evidence
The distribution includes regression tests for the affected code paths. The
accompanying delivery evidence records executed suites, independent security
cases, browser CSP/export checks, real loopback HTTP checks, mocked client
transport checks, package hashes and policy-blocked browser navigation separately.
Do not infer runtime validation from a structural portability check. Re-run
[validation](references/validation.md) after local modifications.
