# Optional Roslyn source-snapshot adapter

Requires an installed .NET 10 SDK with its bundled Roslyn compiler assemblies.
No separate package download is required by this project. The Python Engine does
not require .NET and never starts this adapter implicitly.

Build only this trusted adapter, not the project being inspected:

```text
dotnet restore LocalGraph.Roslyn.csproj --configfile NuGet.Config -p:ImportDirectoryBuildProps=false -p:ImportDirectoryBuildTargets=false
dotnet build LocalGraph.Roslyn.csproj --no-restore -c Release -p:ImportDirectoryBuildProps=false -p:ImportDirectoryBuildTargets=false
dotnet bin/Release/net10.0/LocalGraph.Roslyn.dll /path/to/source my-dataset > csharp-patch.json
<PYTHON> ../../scripts/graph.py --db /path/to/graph.db apply-patch csharp-patch.json
```

Run from this adapter directory; replace paths for the local shell. Keep SDK and
output binaries on the same operating system. A portable source package is not
a universal prebuilt executable. The SDK must already contain its target packs;
this project clears package sources rather than downloading missing components.

The adapter parses classes, interfaces, methods, declarations and invocation
sites; resolves statically bound symbols where the in-memory compilation has
sufficient references; and records unresolved calls and compiler diagnostics.
It reads source only. It never loads an inspected csproj, custom MSBuild task,
analyzer, generator, plugin, or executable code from the source tree.

Important limits: one compilation for the selected snapshot, runtime references
only, no package/project restore, no runtime dispatch/DI/reflection claims, no
conditional build symbols. A solution with multiple build configurations or
external dependencies may produce unresolved sites. Inspect coverage rather
than treating missing edges as proof of no dependency.

Version 2 delivery evidence: source included, compilation/runtime **not-run** in
the creation environment because .NET was unavailable. The Python and browser
core do not depend on this optional adapter. Run the command above in a .NET SDK
environment before relying on Roslyn output.
