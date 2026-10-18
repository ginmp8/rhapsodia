# Reverse Engineering + Behavioral Reconstruction

One portable Agent Skills package, six modes (`Discover`, `Investigate`, `Characterize`, `Reconstruct`, `Verify`, `Diagnose`) and independent source/binary decoders. **The portable core only needs Python 3.10+ and its standard library**. Optional tools are never installed or downloaded automatically. A successful static analysis never implies successful decompilation, executable safety or behavior equivalence.

**Optional fast static triage:** for a narrow metadata, import/export, IPC or version question, start with one bounded Python read-only probe instead of automatically building a graph, opening MCP or decompiling. The [fast static playbook](references/fast-static-triage.md) describes conditional Go/native/JS shortcuts with a portable Python fallback. External tools are never silently installed, trusted or executed. This is an instruction-level optimization; no time/token speedup over this skill has been measured.

## Capabilities included in this package

| Capability | Shipped implementation | Evidence limitation |
|---|---|---|
| Offline MCP/CLI evidence workbench | `mcp_server.py`, `investigation_api.py`, 13 tools; JSON-RPC stdio; SQLite `investigation_store.py` | No HTTP server/network, target execution, or authenticated runtime observation through these tools |
| Safe virtual application artifacts | `artifact_index.py` ZIP/TAR/ASAR, `application_graph.py` JS/TS/Electron, `artifact_reports.py` PE/ELF/Apple metadata | Bounded static evidence; dynamic semantics are not recovered |
| Reconstruction closure and partial-order | `reconstruction_contract.py` signed receipt verifier and independent event-DAG comparison | Requires operator-key and independently trusted observation corpus; finite proof only |
| Bounded static discovery | `workbench.py`, `recon.py`, individual JVM/CIL/DEX/WASM/EVM/PE/ELF/Mach-O/JS/HAR/OpenAPI/manifest decoders | Recognized declarations/opcodes only, unknown constructs recorded |
| Specialist decompilation | `tool_adapters.py` detection and executable adapters for independently installed ILSpyCmd, JADX, Ghidra, Kaitai Struct; `tools/ghidra/export_functions.py` | External engines must be preinstalled and their parsing environment assessed |
| C# semantic resolution | `tools/roslyn/` .NET 10 source with pinned Roslyn/Locator packages; `tool_adapters.py import-roslyn` | Requires an independently provisioned SDK and **trusted** MSBuild project; not built/tested on this Linux sandbox |
| Behavior contract | `behavior_lab.py` v1/v2 finite NDJSON observations, typed envelopes, strict differential comparisons and characterization | Provided `runner_status` is unauthenticated metadata, not an execution attestation |
| Adaptive structured tests | `probe_engine.py generate/fuzz` accepts corpus, OpenAPI, previous mismatches, external coverage data and seed | Mutated input hypotheses only; does not predict reference outputs or implement coverage instrumentation |
| Stateful learning | `state_inference.py offline`, budgeted trusted `active` oracle, optional AALpy L* | Observed finite transitions/hypotheses, not formal proof of a minimal/equivalent automaton |
| Mismatch diagnosis | `behavioral_pipeline.py` bounded oracle-rerun shrinking with first mismatch pointer and class preservation | Trusted binaries only; state reset required; not globally minimal |
| Process effects | `oracle_runner.py --capture-fs` hashes regular files in trusted working directories | No OS isolation; cannot see outside-cwd, database/network/syscall effects |
| Web/API analysis | `interface_traces.py` HAR/OpenAPI inspection and authorized HTTP status/hash replay | No redirects; no server-internal effects; test inputs can contain sensitive data |
| Interactive browser investigation | `web_investigator.py` as the sole Playwright entrypoint: navigate/click/fill/press, selected-element text hashes, screenshots, hover/drag/select/scroll, viewport, DOM/network/console metadata, local timings and bounded same-origin link exploration | Optional installed browser, separately authorized trusted target; fixture fallback is not HTTP evidence; the previous CLI/output contract was retired in v0.2.0 |
| Functional/performance/security expectation audit | `web_audit.py` with text/hash, HTTP status, DOM change, timing, viewport overflow and header-presence rules | Only finite, independently defined policies; no automated full SAST/DAST or visual/field monitoring |
| Credential-marker detection | `source_marker_scan.py` read-only bounded local source scan with redacted findings | Pattern matches may be false; never validates keys or probes targets |
| Browser-to-API evidence correlation | `correlate_web_evidence.py`, dynamic evidence ingestion in `evidence_ir.py` | Route-shape/time-window associations labeled inferred, not backend-handler proof |
| Evidence graph | `evidence_ir.py build/export`, append-only hash-keyed SQLite sources/nodes/edges | Static evidence relations, not verified dynamic call graphs |
| Runtime policy | `execution_policy.py static/trusted-local/oci-pinned` with pinned image and restrictive OCI argv | OCI is **not** attested isolation and its policy generator does not run or provision containers |

## Offline commands (safe for unknown uploaded files)

```sh
# Working directory: installed skill root, Python 3.10+.
# Inputs must be inside /approved/input; /private/evidence must exist beforehand.
python3 -B scripts/mcp_server.py --root /approved/input --state-dir /private/evidence --tool analyze_application --args-json '{"path":"app.zip"}'
python3 -B scripts/mcp_server.py --root /approved/input --state-dir /private/evidence
python3 scripts/workbench.py unknown.zip -o static.json --max-items 300
python3 scripts/recon.py inventory unknown.zip -o inventory.json
python3 scripts/evidence_ir.py build static.json --sqlite evidence.sqlite -o ir.json
python3 scripts/evidence_ir.py export --sqlite evidence.sqlite -o graph.json
python3 scripts/behavior_lab.py characterize examples/v2-stateful.jsonl -o obligations.json
python3 scripts/probe_engine.py fuzz --reference examples/v2-stateful.jsonl --seed 7 --max-cases 50 -o unobserved.jsonl
python3 scripts/state_inference.py offline --corpus examples/v2-state-transitions.jsonl -o states.json
python3 scripts/behavior_lab.py compare examples/reference.jsonl examples/candidate-with-mismatch.jsonl -o comparison.json
python3 scripts/tool_adapters.py detect
python3 scripts/execution_policy.py static
python3 -m unittest discover -s tests -q
```

`workbench.py` does not unpack archives to disk. Bounded partial analysis returns code `3`, invalid input returns `2`. All commands using a bare `-o` destination expect a new safe output file; do not overwrite protected evidence.

## Optional execution (only separately authorized *trusted* targets)

```sh
# The flags do NOT grant user consent or make the process isolated.
python3 scripts/behavioral_pipeline.py --cases cases.jsonl --reference-argv ref-argv.json --candidate-argv cand-argv.json --reference-cwd REF --candidate-cwd CAND --output-dir NEW --execute-authorized --shrink-trials 40
python3 scripts/tool_adapters.py run --provider ilspy --input TRUSTED.dll --output-dir NEW --execute-authorized --environment-approved
python3 scripts/interface_traces.py replay --cases http-cases.jsonl --origin http://127.0.0.1:8080 --execute-authorized -o http-observations.jsonl
python3 scripts/web_investigator.py capture --origin http://127.0.0.1:8080 --actions approved-actions.json --execute-authorized --mutations-approved -o browser.json
python3 scripts/execution_policy.py oci-pinned --execute-authorized --isolation-approved --image local/approved@sha256:INSERT64HEX -o argv.json
```

Each executable is an optional adapter. The analyzers can themselves expose host attack surfaces when parsing a hostile target; use an independently assessed isolation environment. Do not run untrusted uploads, MSBuild projects or target code in this skill's default sandbox. The browser mode needs installed Playwright and a compatible browser; no download occurs. A preapproved image with immutable digest and Docker/Podman must already exist for OCI.

## Browser audit in the ChatGPT sandbox (trusted HTML fixture)

If HTTP browser navigation is blocked, an **approved local HTML fixture** can still be tested with real Playwright/Chromium input events. This does not simulate or prove remote HTTP behavior.

```sh
python3 scripts/web_investigator.py detect
python3 scripts/web_investigator.py capture --origin http://127.0.0.1:8080 --fixture-root examples/web-fixture --actions examples/web-actions.json --execute-authorized --mutations-approved --browser-executable /usr/bin/chromium -o /tmp/re-fixture-trace.json
python3 scripts/web_audit.py --trace /tmp/re-fixture-trace.json --policy examples/web-policy.json -o /tmp/re-fixture-audit.json
python3 scripts/evidence_ir.py build /tmp/re-fixture-trace.json --sqlite /tmp/re-fixture.sqlite -o /tmp/re-fixture-graph.json
```

The binary path is an example, not a portability requirement; use an installed browser discovered on the host. Inputs and outputs must be distinct and report location must be writable; scripts never download dependencies. To test a real trusted site on a host with networking, omit `--fixture-root`, use an approved exact origin and ensure authorization before any mutation. Direct references: [dynamic investigation](references/dynamic-investigation.md), [finite audits](references/web-audits.md).

## Behavioral and security contracts

- Reference input domains, serialization, errors, ordering, state transitions, side effects and runtime environment must be frozen before cloning. Write independent code against the observed contract; test with the unchanged oracle corpus.
- V2 NDJSON accepts aligned `actions/steps`, explicit effects and typed envelopes for binary bytes, bigint, decimal, special float, offset-aware datetime and undefined. V1 data remain valid. See [`examples/v2-stateful.jsonl`](examples/v2-stateful.jsonl).
- Source or captured traces may contain confidential user data. Raw observations (including HTTP case inputs and optional screenshots) can retain secrets even when displayed summaries omit values. Use synthetic traffic and handle evidence as sensitive.
- Generated probes are never actual expected outputs. Finite `PASS_OBSERVED_CASES` certifies agreement on supplied valid cases and nothing stronger.
- Reports preserve missing tools, truncated/incomplete results, provenance tiers and failing runner statuses. No tests are silently rewritten to make a candidate pass.

## Navigation

The entire control plane is in the first 100 lines of `SKILL.md`. All supporting specifications are linked **directly** there: [capability matrix](references/capability-matrix.md), [discover](references/discover.md), [behavior contract](references/behavior-contract.md), [reconstruct](references/reconstruct.md), [verify/diagnose](references/verify.md), [advanced analysis](references/advanced-analysis.md), [probes/state](references/probes-and-state.md), [runtime evidence](references/runtime-evidence.md), [evidence graph](references/graph-and-provenance.md), [trust/provenance](references/trust-and-provenance.md), and [research basis](references/research-basis.md), and [MCP investigation contract](references/interactive-investigations.md).

REA is a comparative *capability reference*, not bundled code or a runtime dependency. The optional overlap audit detects exact hashes/token spans only; it does not grant legal clearance or guarantee universal original invention.
