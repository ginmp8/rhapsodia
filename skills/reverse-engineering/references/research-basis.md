# Research-backed design decisions (source-aware, 2026-10-12)

**Purpose:** link documented techniques to the skill's actual implementation or explicit optional/guided modes.
**Load when:** justifying the architecture, a technique, a coverage claim or a capability trade-off.
**Decision impact:** prevent unsupported promises, hidden dependency adoption or conflation of static inspection and runtime equivalence.

| Evidence / primary source | Finding | Skill implementation status |
|---|---|---|
| [Roslyn semantic models](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/work-with-semantics) | Syntax trees do not resolve all types/symbols without semantic context. | `tools/roslyn/` bundles an optional .NET 10 semantic exporter source and pinned packages; execution needs separately provisioned SDK and trusted project. |
| [Tree-sitter](https://github.com/tree-sitter/tree-sitter/blob/master/docs/src/index.md) | Concrete syntax tree parsing is extensible and incremental. | Optional source parser, not a claim of reference/call resolution. |
| [Hypothesis stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html) | Testing state-action sequences finds issues invisible to isolated examples. | `state_inference.py` offline/active and `probe_engine.py` generate bounded state-action sequences; Hypothesis itself optional. |
| [Hypothesis property testing](https://hypothesis.readthedocs.io/) | Constrained generators find edge cases and shrink failures. | `probe_engine.py fuzz` uses deterministic input mutation plus optional externally observed feedback; `behavioral_pipeline.py` shrinks while preserving mismatch class/pointer. |
| [Pact contract testing](https://docs.pact.io/) | Contract tests check used integration messages, not total business parity. | Treat HTTP/message contracts as one oracle class, not full equivalence. |
| [Pact specification](https://docs.pact.io/implementation_guides/pact_specification) | Cross-language matching rules must be consistent. | Strict canonical NDJSON case matching and recorded comparison configuration. |
| [RFC 8259](https://www.rfc-editor.org/info/rfc8259/) | Duplicate JSON names and numeric representations can differ between implementations. | Reject duplicate keys/nonfinite constants; preserve types; no silent normalization. |
| [RFC 8785](https://www.rfc-editor.org/info/rfc8785/) | JCS canonicalization constrains its input and numeric handling. | Do not call Python sort_keys JCS; hash original corpus bytes instead. |
| [Zeller & Hildebrandt](https://www.st.cs.uni-saarland.de/publications/files/zeller-tse-2002.pdf) | Failure reduction requires rerunning an oracle and preserving failure. | `behavioral_pipeline.py --shrink-trials` runs actual reference/candidate programs and retains a mismatch (not proof of global minimum). |
| [Pex / Microsoft Research](https://www.microsoft.com/en-us/research/publication/pex-white-box-test-generation-for-net/) | Concolic path exploration can generate inputs with constraints. | Optional only; no built-in symbolic solver claim. |
| [KLEE paper](https://llvm.org/pubs/2008-12-OSDI-KLEE.pdf) | Symbolic tests face path explosion and environment-model complexity. | Optional research route; require bounded coverage claims. |
| [OSS-Fuzz](https://google.github.io/oss-fuzz/) | Coverage-guided fuzzing needs language-specific instrumentation/harness. | `probe_engine.py fuzz` generates seeded bounded hypotheses; actual target coverage instrumentation or OSS-Fuzz integration is not bundled. |
| [AFL++](https://aflplus.plus/docs/) | Persistent harness efficiency assumes state reset. | `state_inference.py active` and trusted replay require reset confirmation; generated fuzz inputs have no assumed outputs. |
| [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html) | API schemas and statuses are useful declarative interface contracts. | `web_analysis.py`/`interface_traces.py` parse declared paths; explicit trusted `interface_traces.py replay` records HTTP observations. |
| [OpenTelemetry HTTP spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) | Stable observable trace fields can inform external effects. | `interface_traces.py` hashes observed HTTP responses; OpenTelemetry spans require supplied snapshots, not hidden collection. |
| [Frida documentation](https://frida.re/docs/functions/) | Runtime function hooks can reveal actual arguments/calls when permitted. | Optional user-controlled instrumentation, never bundled/auto-attached. |

**Claim ceilings:** Bundled Roslyn exporter source is optional and not a standalone compiler; third-party decompiler adapters require separate installations, the built-in structural fuzzer generates only inputs, and there is no verified OS sandbox or symbolic executor. Offline comparison is reproducible for valid finite JSONL corpora. The tool's source files are independent of REA; only conceptual/feature benchmarking is derived from that project. Study/source identities must be frozen per optimization run; conceptual references never become runtime validation receipts.

## Independent format readers and optional specializers

- **ECMA-335 (CLI metadata/CIL)**: `dotnet_analysis.py` decodes metadata tables and supported instructions; uses [ECMA-335](https://ecma-international.org/publications-and-standards/standards/ecma-335/) as format reference. No emitted C# source in the stdlib decoder; optional ILSpy/Roslyn adapters are included but require external tools and trusted environment. Dynamic dispatch remains unresolved.
- **JVM class files**: `jvm_analysis.py` reads bytecode constant pools and invocation sites using the [JVM specification](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html); it is not Java decompilation.
- **DEX and Android manifests**: `dex_analysis.py` and `app_manifests.py` use the [Android DEX format](https://source.android.com/docs/core/runtime/dex-format) and Android resource-chunk vocabulary for declarations; optional installed JADX adapter included, no universal Apktool/JADX equivalence.
- **WebAssembly**: `wasm_semantics.py` reads instructions and sections guided by the [WebAssembly core specification](https://webassembly.github.io/spec/core/); not WABT or complete validation.
- **Source maps**: `web_analysis.py` decodes v3 Base64-VLQ mappings per the [ECMA-426 proposal/spec](https://tc39.es/ecma426/); untrusted mappings cannot prove original JS semantics.
- **Mach-O/ELF/PE**: `native_symbols.py` reads section/relocation/load command and import/export tables; no native pseudocode or AST.
- **Apple Info.plist**: `app_manifests.py` uses Python standard-library `plistlib` and intentionally reports only selected declared bundle metadata.

## Additional bounded research used in this iteration (2026-10-12)

| Primary evidence | Engineering implication | Current status |
|---|---|---|
| [Hypothesis stateful tests](https://hypothesis.readthedocs.io/en/latest/stateful.html) | Sequences and state invariants expose failures invisible to single isolated values | Built-in deterministic sequence probes/fuzzing, v2 step validation and offline state inference; no Hypothesis runtime dependency |
| [AALpy automata learning](https://github.com/DES-Lab/AALpy) | Active state machine learning depends on an authorized SUL and an equivalence oracle | `state_inference.py offline/active` implements finite observed transitions; optional AALpy L* integration outputs a bounded learned hypothesis, not a proof |
| [Ghidra headless](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/RuntimeScripts/support/analyzeHeadlessREADME.md) | Binary analysis can be delegated to a separately installed headless engine | Executable `tool_adapters.py run --provider ghidra` invokes a preinstalled authorized headless tool with bundled Jython postscript; no hidden download |
| [CrossLangFuzzer (2026 preprint)](https://arxiv.org/abs/2606.28132) | Differential testing guided by richer representations can find cross-language discrepancies | Motivates the implemented `evidence_ir.py` graph and `probe_engine.py` deterministic structural fuzzing; neither is CrossLangFuzzer or coverage-guided compiler fuzzing |
| [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) | Base64 transports binary bytes with canonical alphabet/padding constraints | V2 `bytes` envelope requires canonical padded base64; bigint, decimal, special-float, datetime-offset and undefined have explicit tags |

Research is a bounded set of sources and is not proof of technique universality; no new third-party runtime dependencies are required. Security and implementation ceilings are tracked in [capability matrix](capability-matrix.md).
