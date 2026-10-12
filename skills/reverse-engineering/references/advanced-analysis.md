# Optional specialist decompilation and semantic analysis

**Purpose:** route to actual third-party tools when their semantics exceed the bundled offline decoders.
**Load when:** detailed .NET, Android, native code, proprietary binary formats, Roslyn symbols or Ghidra/JADX/Kaitai output is needed.
**Decision impact:** distinguishes installed capability from execution permission, static approximations from compiler evidence, and generated output from behavior.

## Capability detection and authorization

The **portable core** requires Python 3.10+ only; `tool_adapters.py detect` uses PATH and never invokes/downloads a tool. Execute external analyzers only in an **independently assessed trusted parsing environment** and with the operator's explicit permission. External parsers can have vulnerabilities when handling hostile binaries; the flags do not create isolation.

```sh
<PYTHON> scripts/tool_adapters.py detect
<PYTHON> scripts/tool_adapters.py run --provider ilspy --input trusted.dll --output-dir NEW_DIR --execute-authorized --environment-approved
<PYTHON> scripts/tool_adapters.py run --provider jadx --input trusted.apk --output-dir NEW_DIR --execute-authorized --environment-approved
<PYTHON> scripts/tool_adapters.py run --provider ghidra --input trusted.elf --output-dir NEW_DIR --execute-authorized --environment-approved
<PYTHON> scripts/tool_adapters.py run --provider kaitai --input sample.bin --schema trusted.ksy --output-dir NEW_DIR --execute-authorized --environment-approved
```

`--tool-path` accepts an absolute existing executable; `--timeout` is bounded to 1–900 seconds. External tools must already exist. Each run hashes the original, prevents destination overwrites, limits diagnostic streams and output files, builds a manifest, and writes the output directory from a validated local staging area. **No generated files are imported or executed**. The Kaitai provider currently compiles a trusted `.ksy` specification into parser source; it does **not** execute that generated source on the input bytes.

## .NET semantic export (optional .NET 10 helper)

`tools/roslyn/RoslynEvidence.csproj` uses `Microsoft.CodeAnalysis.CSharp.Workspaces`/`Workspaces.MSBuild` 5.9.0 and `Microsoft.Build.Locator` 1.11.2. Source is bundled; .NET SDK and packages must be preprovisioned externally. Only **trusted projects** may be evaluated: MSBuild imports/targets/resolvers can run code. No user-supplied unknown `.csproj`/`.sln` may be opened during static discovery.

```sh
# On an authorized machine with the SDK and the pinned packages already restored:
dotnet run --no-restore --project tools/roslyn/RoslynEvidence.csproj -- TRUSTED.csproj --output NEW-roslyn-report.json
<PYTHON> scripts/tool_adapters.py import-roslyn --input NEW-roslyn-report.json -o semantic.json
<PYTHON> scripts/evidence_ir.py build semantic.json -o semantic-graph.json
```

The helper extracts declared member symbols, compiler-resolved invocation targets and project-file/compiler metadata. It is not full-build/solution equivalence. `import-roslyn` labels supplied compilation metadata as **claimed**: only a separately verified trusted compiler invocation justifies stronger evidence. Without the SDK, the built-in ECMA-335 CIL/metadata decoder remains functional.

## Native/Android tools and evidence boundary

- **ILSpyCmd:** `-p -o ... assembly.dll` -> C# project approximation. Runtime reflection, EF proxies and dynamic dispatch remain unknown.
- **JADX:** `-j 1 -r -d ... file.apk` -> Java/Kotlin-like DEX decompilation; generated output is approximation, not running Java source.
- **Ghidra:** bundled `tools/ghidra/export_functions.py` Jython postscript is invoked through installed `analyzeHeadless` to emit a JSON symbol/call-reference ledger. Program analysis is static, not automated 1:1 pseudocode reconstruction.
- **Kaitai Struct:** installed `ksc -t python -d ... spec.ksy` produces source parsers; do not load generated parsers for untrusted specifications without separate safety review.

See official sources [ILSpy](https://github.com/icsharpcode/ILSpy), [JADX](https://github.com/skylot/jadx), [Ghidra](https://ghidra-sre.org/), [Kaitai](https://doc.kaitai.io/user_guide.html), [Roslyn](https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/work-with-semantics). Actual versions and installations must be verified at use time; these links do not imply tools are installed.
