# Coverage matrix — core versus specialist adapters

**Purpose:** communicate implemented paths and evidence ceilings without confusing integration scaffolding with tested runtime parity.
**Load when:** target selection, parity claims, adapter/host choice, or an audit of missing behavior is material.
**Decision impact:** determines which executable capability can be invoked, what remains unknown, and whether any host-specific prerequisite must be reported.

## Definitions

- **Core:** implemented with Python 3.10+ stdlib and bounded local inputs.
- **Adapter:** executable integration included, external binary/library/browser is *not* included or implicitly installed. Always verify availability, authority and environment at run time.
- **Trusted-only:** potentially runs arbitrary instructions; requires independent prior approval and adequate external safeguards. A CLI switch is not proof of isolation.
- **Static / runtime claim:** report input identity, exact format subset, partial/skipped/error counts and provenance tier; do not equate parsing with recovery or observed behavior.

| Area | Included executable path | Non-goals / proof ceiling |
|---|---|---|
| Persistent investigation / MCP | `mcp_server.py`, `investigation_api.py`, 13 named bounded offline tools and CLI, local SQLite `investigation_store.py` | MCP stdio modern/legacy subset; no HTTP transport, background tasks, remote target execution, RBAC or attested isolation |
| Virtual ZIP/TAR/ASAR and directory | `artifact_index.py` no-extraction inventory and bounded content reads, hash/exclusion tracking | Symlinks/unpacked ASAR skipped; parser subsets; OS permission boundary, not full sandbox |
| JS/TS/Electron application flow | `application_graph.py` static import/export/router/IPC graph, trace and version diff | Lexical candidates, no runtime graph, TypeScript compiler, source-map reconstruction or dynamic resolution |
| PE resources, ELF/core notes, Apple bundles | `artifact_reports.py` and `investigation_api.py` portable metadata, payload hashes and declared Apple plist fields | No disassembly, crash symbolication, native ABI recovery or complete resources |
| Reconstructed obligations / partial-order | `reconstruction_contract.py` signed finite receipt verification, binding/fixture ledger, event DAG comparison | Requires independent trusted signer and authorized original observations; no universal equivalence |
| Repositories / ZIP / TAR | `recon.py`, `workbench.py` inventory/symbols/search/diff/graph/strings | No whole-program AST binding, dynamic import resolution, source reconstruction |
| PE/ELF/Mach-O | `native_symbols.py`, `format_probes.py`; optional Ghidra headless adapter with bundled Jython export | No built-in disassembler, pseudocode, fully resolved indirect calls/ABI, core dumps |
| .NET CIL and C# | `dotnet_analysis.py` metadata/decoded CIL; optional ILSpyCmd and `.NET 10` Roslyn exporter source | No full compiler/decompiler in Python; MSBuild is trusted-only; no runtime proxy/reflection resolution |
| JVM / DEX / APK | `jvm_analysis.py`, `dex_analysis.py`, `app_manifests.py`; optional JADX | JVM class/DEX call sites are subsets, no compiled Java/Kotlin equivalence or resources.arsc mapping |
| WASM and EVM | `wasm_semantics.py`, `evm_analysis.py` instructions/candidates | No full WAT generator, exhaustive proposal support, symbolic stack or ABI inference |
| JS/TS, source maps, Electron | `web_analysis.py` patterns, source maps and HAR; browser optional | No universal bundler resolution, JS execution sandbox or live IPC tracing |
| Firmware / binary formats | `format_probes.py` signature candidates; optional Kaitai `.ksy` compiler adapter | Kaitai tool compiles a trusted schema; output parser is not executed here; no firmware unpack/decrypt |
| Recorded API | `web_analysis.py`, `interface_traces.py inspect-har/inspect-openapi/replay` | Network replay is trusted-only, no server-side state visibility or full HTTP proxy |
| UI/browser legacy | `browser_capture.py` Playwright action + DOM hash + limited network metadata | Requires installed Playwright/Chromium; no full crawler or browser isolation |
| UI/browser enhanced | `web_investigator.py detect/capture/explore`, trusted offline fixtures, bounded DOM/network metadata, action and local timing, same-origin link discovery | Trusted targets only; no OS isolation or automatic remote endpoint validation; fixture execution never proves remote network behavior |
| Functional/performance/security trace rules | `web_audit.py` with frozen, typed JSON-Pointer assertions | No inferred business oracles, full Core Web Vitals, accessibility audit or security clearance; missing fields stay incomplete |
| Passive credential-marker scanning | `source_marker_scan.py` with bounded redacted findings | Read-only candidate patterns, not validity or absence proof |
| Browser-to-API route correlation | `correlate_web_evidence.py` method/route shape matches; `evidence_ir.py` browser/fixture/correlation graph | Inferred candidate relations only; no backend method-execution proof |
| Static + bounded browser evidence IR | `evidence_ir.py` normalizer, append-only SQLite graph, JSON export | Labels static/fixture/runtime/inferred separately; not authoritative whole-program reachability |
| Typed observation | `behavior_lab.py` V1/V2, tagged bytes/bigint/decimal/undefined/special-float/offset-datetime | Tagged values are representational envelopes; external adapters must preserve source semantics |
| Probes / fuzz | `probe_engine.py generate/fuzz`, seeded structural mutations, optional external `by_case` edge feedback | No target instrumentation, no automatic coverage-guided feedback loop or output oracle predictions |
| State inference | `state_inference.py offline/active`, optional AALpy L* | Finite observed/inferred hypothesis, no universal automata equivalence; active execution trusted-only |
| Trusted differential replay | `oracle_runner.py`, `behavioral_pipeline.py`, strict compare, signature-preserving shrink | One-shot stdin/stdout protocol, not full PTY/concurrency/interleaving model, not source recovery |
| Filesystem effects | `effect_capture.py`, trusted `--capture-fs` | Only hashes regular files inside cwd, not outside paths, network, DB or spawned-process effects |
| Runtime policy | `execution_policy.py`, static/trusted-local/OCI-pinned argv | No built-in sandbox, no preinstalled container image/tool, no isolation attestation |

## Verification boundaries

The bundled Python tests cover parsers, deterministic contracts, simulated tool adapters and trusted local fixtures. External engines (ILSpyCmd, Ghidra, JADX, Kaitai, Roslyn SDK, AALpy) require independent actual-runtime validation before declaring provider interoperability on a host. Live browser capture requires an approved reachable site/browser environment. Structural package checks in OpenAI/Codex/Claude/Copilot/Cursor formats do not prove their runtimes ran.

The REA reference is not bundled; this skill offers independent implementations and adapters, not 1:1 functional parity with another commercial/open-source reverse-engineering platform. Every output must explicitly report unsupported cases and partial coverage.
