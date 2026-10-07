# Local Graph Explorer 3.0.0

## Overview
Offline native rendering now uses a restrictive hash-based CSP. Animated reading,
manual drag, pan/zoom, minimap, five views and local exports remain available.
The package does not need a cloud service, remote asset or another skill.

## Breaking changes
Custom G6 JavaScript and HTML templates are refused by offline/local-live profiles.
They require `--security-profile extended` plus each expected file SHA-256.
Extended receipts do not claim offline isolation. Live queries require a separate
`--security-profile local-live` artifact and an explicitly started compatible server.

## Migration
Native `render view.json --output graph.html` still selects offline. For reviewed
custom files add `--g6-sha256` or `--template-sha256`, respectively, and select the
extended profile. Regenerate local-live HTML for server use; an old offline file
is not silently upgraded. No GraphView or saved-state conversion is required.
See [security profiles](references/security-profiles.md) for exact commands.

## Required actions
Review custom code before calculating/pinning its hash; a supplied hash is not an
approval. Minimize confidential fields before rendering or sharing: the HTML embeds
the whole supplied GraphView, including properties/evidence hidden by UI filters.
Previously generated HTML remains unchanged; regenerate it to receive these controls.

## Rollback
Keep an earlier archive for comparison, but do not restore unrestricted code loading
or implicit live access to suppress an error. Preserve source data and view state.

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
