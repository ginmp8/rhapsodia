# Discover — evidence-first static inspection

**Purpose:** locate implementation surfaces in untrusted artifacts without running target bytes, project scripts or hidden dependencies.
**Load when:** investigating repositories, ZIP/TAR, binaries, assemblies, Android/Apple packages, JS/source maps, firmware signatures or API recordings.
**Decision impact:** determines parser dispatch, evidence level, byte/entry budgets, semantic adapter eligibility and the limits of static reachability claims.

## Safe discovery workflow

1. Fingerprint original artifact SHA-256; inspect file kind, archive member names/sizes/symlinks, cumulative expansion budgets, exclusions, possible secrets and provenance before parsing. Never extract/archive-install/execute user programs for routine discovery.
2. `recon.py inventory|search|symbols|graph|strings|diff` yields bounded repository-level structural evidence. Source regex-based matches are `lexical_candidate`, not compiler-resolved calls.
3. `workbench.py INPUT -o report.json --max-items 300 [--full]` dispatches recognized formats and emits `matched_candidates`, `analyzed`, `skipped`, `errors`, `complete`, and `coverage_scope`. Return code `3` indicates incomplete recognized coverage; `complete:true` is about supported constructs, not decompilation.
4. Focus one known artifact with `dotnet_analysis.py`, `jvm_analysis.py`, `dex_analysis.py`, `wasm_semantics.py`, `evm_analysis.py`, `native_symbols.py`, `web_analysis.py`, `app_manifests.py` or `format_probes.py`. Record line offsets/byte offsets/method tokens where available.
5. Trace declared entrypoints, exported APIs, routes, message handlers, serializers, return/error shapes, state, ordering, retries, proxies, dynamic dispatch, dependency injection, reflection, codegen and externally supplied dependencies. Unknown targets stay unknown.
6. `tool_adapters.py detect` checks for local optional specializers **without executing them**. Only run ILSpyCmd/JADX/Ghidra/Kaitai after explicit authorization and independent parsing-environment approval. `tools/roslyn/` reads **trusted** MSBuild projects, never untrusted projects at discovery time. `import-roslyn` labels supplied semantic exports as claimed.
7. Consolidate relevant JSON evidence with `evidence_ir.py build <report> --sqlite <db> -o <out>` and `evidence_ir.py export --sqlite <db> -o <graph>` when cross-file relationships matter. The graph does not prove execution reachability.

## Evidence levels and output

Use `declared` for literal interfaces/metadata, `decoded_call_site` for bytecode call instructions, `lexical_candidate` for regex patterns, `claimed_semantic_resolution` for imported reports not independently verified, `runtime_observed` only for authorized actual execution with receipt, `inferred` for hypotheses and `unknown` for gaps. Preserve hashes, paths/anchors, partial/error counters, parser/runtime versions and next test obligations. Hand off a **behavior contract** for reconstruction; static interface mapping alone cannot certify equivalent code.
