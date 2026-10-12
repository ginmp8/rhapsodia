// Optional, trusted-project-only Roslyn semantic evidence exporter.
// MSBuild project evaluation can execute external targets; NEVER run on untrusted
// repository files. Runtime and packages must be preprovisioned by the operator.
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Build.Locator;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.MSBuild;

if (args.Length != 3 || args[1] != "--output")
{
    Console.Error.WriteLine("Usage: RoslynEvidence <trusted-project.csproj> --output <new-report.json>");
    return 2;
}
var projectFile = Path.GetFullPath(args[0]);
var outFile = Path.GetFullPath(args[2]);
if (!File.Exists(projectFile) || Path.GetExtension(projectFile) != ".csproj" ||
    File.Exists(outFile) || Path.GetFullPath(projectFile) == outFile)
{
    Console.Error.WriteLine("Project must exist; output must be new, distinct from input.");
    return 2;
}
// MSBuildWorkspace may evaluate custom build tasks, imported props and SDK resolvers.
// Only invoke from an independently reviewed/trusted project environment.
MSBuildLocator.RegisterDefaults();
using var workspace = MSBuildWorkspace.Create();
var project = await workspace.OpenProjectAsync(projectFile);
var compilation = await project.GetCompilationAsync();
if (compilation is null)
{
    Console.Error.WriteLine("Project compilation unavailable.");
    return 3;
}
var symbols = new List<object>();
var diagnostics = compilation.GetDiagnostics();
var hasErrors = diagnostics.Any(x => x.Severity == DiagnosticSeverity.Error);
var scannedDocuments = 0;
foreach (var doc in project.Documents)
{
    if (++scannedDocuments > 500 || symbols.Count >= 25000)
        break;
    var syntax = await doc.GetSyntaxRootAsync();
    var model = await doc.GetSemanticModelAsync();
    if (syntax is null || model is null)
        continue;
    foreach (var member in syntax.DescendantNodes().OfType<MemberDeclarationSyntax>())
    {
        if (symbols.Count >= 25000)
            break;
        var symbol = model.GetDeclaredSymbol(member);
        if (symbol is null)
            continue;
        if (member is not BaseTypeDeclarationSyntax && member is not BaseMethodDeclarationSyntax &&
            member is not PropertyDeclarationSyntax && member is not EventDeclarationSyntax &&
            member is not DelegateDeclarationSyntax)
            continue;
        var invocations = member.DescendantNodes(n => n == member || n is not MemberDeclarationSyntax)
            .OfType<InvocationExpressionSyntax>();
        var refs = new SortedSet<string>(StringComparer.Ordinal);
        foreach (var invocation in invocations.Take(200))
        {
            var info = model.GetSymbolInfo(invocation);
            if (info.Symbol is { } target)
                refs.Add(target.ToDisplayString(SymbolDisplayFormat.CSharpErrorMessageFormat));
        }
        var span = syntax.SyntaxTree.GetLineSpan(member.Span);
        symbols.Add(new
        {
            name = symbol.ToDisplayString(SymbolDisplayFormat.CSharpErrorMessageFormat),
            kind = symbol.Kind.ToString(),
            references = refs.ToArray(),
            location = new { document = doc.FilePath is { } file ? Path.GetFileName(file) : doc.Name,
                             line = span.StartLinePosition.Line + 1 },
            evidence_level = "semantic_resolved"
        });
    }
}
var report = new
{
    schema_version = "1.0",
    format = "roslyn-semantic-export",
    source_path = Path.GetFileName(projectFile),
    compilation = new
    {
        project_sha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(projectFile))).ToLowerInvariant(),
        compiler_version = typeof(CSharpCompilation).Assembly.GetName().Version?.ToString() ?? "unknown",
        compilation_error_count = diagnostics.Count(d => d.Severity == DiagnosticSeverity.Error),
        fully_compiled = !hasErrors,
        files_scanned = scannedDocuments,
        scope = "single loaded project with referenced workspace projects; not repository-wide completeness"
    },
    symbols,
    complete = !hasErrors && scannedDocuments <= 500 && symbols.Count < 25000,
    evidence = "compiler semantic model; MSBuild evaluation of trusted project"
};
var parent = Path.GetDirectoryName(outFile);
if (parent is not null) Directory.CreateDirectory(parent);
await File.WriteAllTextAsync(outFile, JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }) + "\n", Encoding.UTF8);
return hasErrors ? 3 : 0;
