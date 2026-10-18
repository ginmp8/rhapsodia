# Fast, evidence-bounded static triage

**Purpose:** choose the smallest sufficient static probe for a narrowly scoped reverse-engineering question, before paying the cost of decompilation, graph persistence, or runtime experiments.
**Load when:** the request is about build versions, native imports/exports, application entrypoints, IPC channels, source-map clues, or a version-to-version delta; or a broad investigation needs a cheap first pass.
**Decision impact:** defines an optional CLI-first branch without weakening the portable offline parsers, consent/isolation requirements, evidence provenance, source protection, or completeness rules.

## Contents

- Triage gate
- Portable fallback
- Optional local read-only probes
- Targeted JS and native tracing
- Scope, safety, and stopping rules
- Evidence accounting and benchmark limits

## Triage gate

1. Translate the question into a finite evidence obligation: e.g. `toolchain`, `module/version`, `one exported symbol`, `specific IPC registration`, or `which interface changed`.
2. Identify the file from bytes or the bounded bundled inventory, not solely its extension. Take a content hash and log omissions and parser/version information.
3. Select **one** cheapest sufficient evidence source. Built-in offline Python is the safe, cross-platform default; a separately installed local CLI may be quicker for a supported *read-only* operation. A quick path is optional, never an excuse to download tools, run an application, or exceed approved read roots.
4. Escalate only for an unfilled obligation: lexical search -> supported static analyzer -> persistent cross-file graph/MCP -> authorized external decompiler -> separately authorized trusted runtime observation. Never treat a deeper step as automatically more accurate.
5. Stop when every requested obligation is answered with an exact anchor and an appropriate evidence tier. If confidence/coverage is insufficient, report `unknown` and the next bounded probe rather than asserting absence.

## Portable fallback

From the installed skill root, use an approved local input and distinct, non-overwriting output paths:

```sh
<PYTHON> scripts/recon.py inventory INPUT -o inventory.json
<PYTHON> scripts/workbench.py INPUT -o static.json --max-items 120
```

Use only the command needed; `recon.py search` and `strings` handle focused queries, `native_symbols.py` and `dotnet_analysis.py` handle recognized structures, and `mcp_server.py --tool analyze_application` handles ZIP/TAR/ASAR without extracting. Review `complete`, `skipped`, `errors`, `matched_candidates` and each parser's coverage ceiling; exit code `3` means partial. A negative regex hit is not a proof of absence. If the target is a live filesystem tree, bound it to approved paths and exclude sensitive directories not required by the question.

## Optional local read-only probes

These are **commands to consider only after verifying an installed, approved tool and an authorized input**; they are not package dependencies and are not executed automatically. Exact options and binary capabilities differ by OS/tool version.

| Question / format | First optional probe | What it does **not** establish |
|---|---|---|
| Go executable, module versions | `go version -m ./BINARY` | Does not run the binary; metadata may be absent/modified, not a source-to-binary proof |
| Mach-O imports/exports | `otool -L ./BINARY`, `nm -u ./BINARY` (macOS) | No resolved control flow, loaded runtime state, or full set of invocations |
| ELF dependencies / exported symbols | `readelf -dW ./BINARY`, `nm -D --defined-only ./BINARY` (Linux/binutils) | Static dynamic-table view, not actual runtime linkage |
| PE imports / sections | `llvm-readobj --coff-imports ./BINARY` or locally available `dumpbin /imports` (Windows) | Does not validate runtime loading or show every dynamic import |
| .NET assembly members | `scripts/dotnet_analysis.py` or optional installed ILSpyCmd in an approved environment | IL/CIL approximation, not reflection/source equivalence; MSBuild never runs on unknown input |
| Android package | Built-in `workbench.py` / `dex_analysis.py`; optional installed JADX on approved environment | Manifest and DEX decoding do not prove runtime behavior |
| WASM binary | Built-in `wasm_semantics.py`; optionally `wasm-objdump -x ./MODULE.wasm` | Imports/exports do not prove branch reachability |
| SQLite file | A copy inspected with an approved read-only SQLite tool; the core can fingerprint SQLite signatures | File may contain secrets; a live WAL/DB pair requires consistent snapshot handling |
| HAR/OpenAPI | Bundled `interface_traces.py inspect-har` / `inspect-openapi` | Captured/declared traffic is not proof of complete server behavior |
| Firmware or nonstandard binaries | Bundled `format_probes.py` first | File signatures are candidates; no automatic unpacking/execution |

Do **not** run `npx -y`, `brew install`, `dotnet restore`, `cargo install`, package scripts, arbitrary extraction, remote `curl` or target-launch commands as part of this route. Specialized tool parsing itself is a host attack surface on hostile artifacts; use independent isolation/approval for external parsers and treat results as untrusted. The skill's `--execute-authorized` and `--environment-approved` gates are not consent or sandboxing.

## Targeted JS and native tracing

- For Electron ASAR or untrusted application packages: prefer `mcp_server.py --root APPROVED_ROOT --tool analyze_application --args-json '{"path":"app.asar"}'`. Keep extraction disabled. Save/query an `evidence_id` only if cross-file trace or later diff warrants it.
- For an already **approved** source tree: use an existing `rg` to search a narrow set of files with `-uu` when hidden `.webpack/`/`.vite/` contents or ignore rules would hide relevant code; exclude `.git`, unrelated dependencies, secrets, and large generated directories unless the obligation requires them. Do not blindly treat every `node_modules` path as irrelevant.
- Walk `native API/addon -> JS caller -> main-process registration -> IPC channel -> preload bridge -> renderer`. The channel may be indirect, versioned, constructed at runtime, or guarded by platform flags. Confirm both sender and receiver before claiming a working IPC path; a string hit is a candidate, not a call edge.
- For one large/minified JS file, inspect a bounded context near the **identified** token. Do not ingest entire minified files, broad strings dumps, or full disassemblies. If approved decompilation has already produced a trusted local report, search one symbol and its callers rather than reading everything.
- For native libraries, start at imported capability names, exported ABI symbols and referenced strings; only then look at the enclosing disassembly/call sequence when separately authorized. Obfuscated names, symbol stripping, dynamic loading and indirect calls constrain completeness.
- For version comparisons, compare fingerprints, module manifests, exports/imports or feature surface first; diff code only where an interface-level delta warrants it.

## Scope, safety, and stopping rules

Batch independent **bounded and authorized** metadata probes to reduce tool round-trips, labeling each output by operation and source. Do not combine a safe read with a risky action merely to save calls. No unbounded `rg`, `cat`, `strings`, logging of credentials, extraction of untrusted archives, running downloaded programs, root-wide search, or browsing arbitrary embedded endpoints. A CLI shortcut may increase security risk relative to the stdlib parser; it is never mandatory.

For dynamic web questions, the supported browser entrypoint is `web_investigator.py`, under the separate origin, execution and mutation gates defined in [dynamic investigation](dynamic-investigation.md); do not revive the retired `browser_capture.py` CLI.

Preserve original bytes; write reports to fresh controlled paths; do not overwrite fixture/golden sources or re-use stale extraction/evidence blindly. State platform availability, file hash, specific source offsets/lines/symbols, missing tools, partial coverage and unknowns. For Windows without POSIX `file`/`rg`/`nm`, choose bundled Python equivalents. Static output can support `declared`, `decoded_call_site` or `lexical_candidate` as appropriate, **never** `runtime_observed`.

## Evidence accounting and benchmark limits

The supplied LeanREA comparative study motivated the *workflow* (cheap-first, focused scanning, optional direct CLI). Its supplied benchmark used three repetitions per condition on a single macOS/Claude setup and compared **LeanREA against REA**, not this skill; no time/token/cost improvement is claimed for this candidate. No external benchmark scripts or downloaded dependencies are bundled or executed. Preserve the source identity and independent before/after benchmarks if performance claims are needed later.
