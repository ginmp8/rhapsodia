# Trusted behavioral replay, HTTP/browser evidence and execution policy

**Purpose:** collect finite runtime observations without confusing a CLI flag with permission or isolation.
**Load when:** user authorizes execution of a trusted reference/candidate, filesystem effect capture, HTTP replay, browser navigation, or externally isolated execution.
**Decision impact:** picks allowed runtime route, exact effect scope, non-network default, privacy controls, observable status and abort conditions.

## Execution decision

1. **Untrusted binary/source:** static discovery only. Never run unknown uploads in the ChatGPT sandbox or auto-fetch dependencies.
2. **Previously reviewed trusted executable:** require explicit authorization and use `oracle_runner.py` or `behavioral_pipeline.py`. `--execute-authorized` is only a CLI interlock; runner has no network isolation and no OS filesystem sandbox.
3. **Separately assessed pinned OCI environment:** `execution_policy.py oci-pinned --execute-authorized --isolation-approved --image local/oracle@sha256:<64hex> -o argv.json` emits a Docker/Podman command array. This command contains `--pull=never`, `--network=none`, read-only root, nonroot UID, dropped capabilities and no host mounts. It does not start containers, verify daemon isolation, prevent container escapes or authenticate operator consent. A trusted operator may provide the resulting argv JSON to `oracle_runner.py` after confirming the image preexists.

## Trusted file effect observation

```sh
<PYTHON> scripts/oracle_runner.py --cases stimuli.jsonl --argv-file trusted-argv.json --cwd TRUSTED_DIR --output runtime.jsonl --execute-authorized --capture-fs
<PYTHON> scripts/behavioral_pipeline.py --cases stimuli.jsonl --reference-argv reference.json --candidate-argv candidate.json --reference-cwd REF --candidate-cwd CAND --output-dir NEW --execute-authorized --capture-fs
```

`--capture-fs` hashes regular files beneath **the program working directory** before/after each case; emits `create/modify/delete` entries in `observation.effects`. It never stores file contents. Symlinks/special files, file count/size over budget and snapshot failures invalidate that run. No outside-directory, process, database, network or syscall effects are monitored. A case's state can persist across cases unless operator resets it; `--capture-fs` and `--shrink-trials` are intentionally incompatible due to non-resettable effects. Comparing recorded effects is only as complete as the capture scope.

## Trusted HTTP interface recovery and replay

```sh
<PYTHON> scripts/interface_traces.py inspect-har --input recorded.har -o har-routes.json
<PYTHON> scripts/interface_traces.py inspect-openapi --input openapi.json -o openapi-routes.json
<PYTHON> scripts/interface_traces.py replay --cases requests.jsonl --origin http://127.0.0.1:8080 --execute-authorized -o replies.jsonl
```

For request cases supply JSONL `{id,input:{method,path,query?,headers?,json?,body_base64?}}`. Replay accepts an **explicit bare origin**, no embedded URL redirection; redirects are not followed. Loopback is the safe default. `--allow-nonlocal` requires a separately approved remote-network environment. Authorization/cookie/API-key headers are refused; response observation is status, body size and hash (plus optional `--capture-json` for approved non-sensitive test responses). HAR inspection strips query strings, cookies, headers and bodies. Network effects represent **client-observed calls**, not server-internal modifications. HTTP cases are not evidence of equivalence unless the same inputs are replayed under comparable environments.

## Trusted browser capture (optional Playwright)

```sh
<PYTHON> scripts/browser_capture.py --origin http://127.0.0.1:8080 --actions browser-actions.json --execute-authorized --browser-executable /path/to/chromium -o browser.json
```

`browser-actions.json` is an array of `{type:"goto",path:"/relative"}`, `{type:"click"|"text-hash",selector:"..."}`, or `{type:"fill"|"press",selector:"...",value:"..."}`. Browser launch, scripts and UI interactions are **runtime execution**; use trusted, test-only sites. Playwright must already be installed; no browser download. Only exact-origin browser requests are routed; this is not an OS firewall. Service Workers/downloads are disabled, off-origin requests aborted, captured DOM text represented by SHA/length unless `--include-text` explicitly requests it. Screenshot file capture is opt-in. Browser state starts from a new context but server state is not reset. If the host blocks network/browser runtime, return a real failure, not fabricated output.

## Evidence and comparisons

Record input/case/command hashes, target binaries where verifiable, environment, seed, timezone, reset policy, evaluated state, observed effects and trial counts. The default comparator uses exact types/order and full explicit observation fields. Timeout/error/invalid runner responses block `PASS_OBSERVED_CASES`. Do not assert exhaustive equivalence, isolation or absence of external effects from a limited capture.

## Enhanced investigation and reproducibility

`web_investigator.py` is a separate optional browser pipeline; it does not modify legacy `browser_capture.py`. See [Dynamic investigation](dynamic-investigation.md) directly from `SKILL.md` for exact authorized execution/fixture commands. **Offline fixture** runs execute pre-reviewed local HTML/JS inside Chromium `page.set_content`; never infer actual remote HTTP behavior. Network route interception is not an OS sandbox. `web_audit.py` performs only finite explicitly supplied expectations, `source_marker_scan.py` is passive, and route matching is inferred. Preserve action/fixture hashes, viewport, browser version, locale, state-reset, request metadata/limits and policy identity before comparing repeated runs.
