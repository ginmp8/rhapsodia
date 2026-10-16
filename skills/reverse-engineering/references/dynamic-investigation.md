# Dynamic Web Investigation — optional, bounded

**Purpose:** characterize UI states and client-visible behavior of authorized trusted applications, then save reproducible observations.
**Load when:** a user needs web feature investigation, workflow characterization, link exploration, DOM/network metadata, responsive overflow, or browser-assisted reconstruction.
**Decision impact:** choose authorized live origin vs *reviewed offline fixture*, enforce separate interaction permission, classify observation truth and limitations.

## Preconditions and trust

- Start unknown/untrusted artifacts with static inspection only. Do not run arbitrary unknown uploaded JavaScript/HTML in the sandbox. The HTML fixture option is for independently reviewed, explicitly approved synthetic/trusted HTML, **not** a sandbox for hostile content.
- `--execute-authorized` is a CLI interlock, not user consent or OS isolation. Browser navigation executes target JavaScript. Interactions (click, fill, press, select, hover, drag, scroll) additionally require `--mutations-approved` after explicit approval. Test accounts/data only.
- Live browser capture needs optional, previously installed Playwright/Chromium. `scripts/web_investigator.py detect` checks packages/binaries without executing a browser. `--browser-executable` accepts an absolute preinstalled binary for non-Playwright-managed installations.
- The operator supplies one exact `--origin` with no credentials, query or path. Nonlocal origins additionally require `--allow-nonlocal` and a separately approved network policy. Routes reject off-origin requests at browser interception, but this is **not** an OS firewall, hostname pinning, or comprehensive socket isolation.
- No background jobs, auto-downloads, authentication extraction, broad internet scans, remote untrusted code, anti-bot circumvention, arbitrary JS string evaluation, or browser extension execution. Stop if a capability is unavailable; continue with offline static evidence only.

## Executable commands

```sh
<PYTHON> scripts/web_investigator.py detect
<PYTHON> scripts/web_investigator.py capture --origin http://127.0.0.1:8080 --actions examples/web-actions.json --fixture-root examples/web-fixture --execute-authorized --mutations-approved -o trace.json
<PYTHON> scripts/web_investigator.py explore --origin http://127.0.0.1:8080 --fixture-root examples/web-fixture --execute-authorized --max-pages 2 -o pages.json
```

`capture` is the canonical browser entrypoint. It takes a JSON array of at most 100 operations: `goto {path}`, `click {selector}`, `fill {selector,value}`, `press {selector,value}`, `hover {selector}`, `drag {selector,target}`, `select {selector,value}`, `scroll {selector,pixels}`, and `text-hash {selector}`; each object also needs `type` and no extra fields. Selectors and values are size-bounded. `--viewport-width/height` select a bounded viewport. Screenshots are opt-in with `--screenshot` and may contain private data; `--include-text` also opts into sensitive DOM/text capture. `text-hash` hashes the entire selected-element text and, when explicitly requested, includes up to 4096 selected-text characters. Capture records up to 2000 request/response events and counts further events as dropped. The output format is `web-investigation` with per-action `steps`, not the previously published standalone capture schema.

`explore` visits a bounded number of same-origin, query-free GET links only, without form submission or mutation. **GET navigations can cause server effects** and therefore still require authorized trusted applications. Unsupported routes, fragment-only links, and other origins are skipped. Default is 5 pages, maximum 20.

## ChatGPT sandbox fallback

When HTTP navigation is blocked, supply a trusted `--fixture-root`. It reads only nonsymlink `.html` files beneath that directory and calls Playwright `page.set_content` instead of navigating to a remote origin. Running the approved HTML is still JS execution; interceptors attempt to block network resources but do not prove OS isolation. Offline traces have `network_evidence=false`, `evidence_type=trusted-offline-html-fixture`. Any network events from a fixture must not be treated as real backend requests. This tests interaction mechanics/fixture behavior, **not** actual external apps, their APIs, or security.

## Evidence contract and limitations

- The trace records action indices, elapsed local time, selected-text hashes, DOM aggregate/hash, link relationships, browser request/response method/path/status metadata, selected security-header **presence only**, and console/page error counts. HTTP headers/bodies, cookies, search parameter values, entered values, raw console messages and credentials are not captured.
- `steps[n].events_from/events_to` gives a **time-window association** between an action and observed browser events, not a causal proof of its handler or underlying server code. Client route metadata is not a backend call graph.
- Local action duration and `navigation_duration_ms` are preliminary indicators, not fully calibrated Core Web Vitals or performance benchmarks. The viewport `horizontal_overflow` flag is not a general visual regression/accessibility assessment.
- Output is exclusive-create and hash-linked. Re-run with identical target, browser version, viewport, state/reset, actions, locale, dependencies and explicit expectations before comparing runs. Dynamic timing and network conditions cannot be promised byte-identical.
- For finite assertions use [Web audits](web-audits.md); for graph correlation use `scripts/correlate_web_evidence.py` then `scripts/evidence_ir.py build`. Both references are also linked directly from `SKILL.md`.
