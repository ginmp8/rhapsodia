using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

// This executable parses a local source snapshot, never its project files.
// Its output is a graph-patch-v1; the Python Engine owns validation/persistence.
return Run(args);

static int Run(string[] args)
{
    try
    {
        if (args.Length != 2)
            throw new ArgumentException("Usage: LocalGraph.Roslyn <source-directory> <namespace>. JSON goes to stdout.");
        var root = Path.GetFullPath(args[0]);
        var scope = args[1];
        if (!Directory.Exists(root) || string.IsNullOrWhiteSpace(scope))
            throw new ArgumentException("A local source directory and nonempty namespace are required.");
        var files = Walk(root).Take(5001).OrderBy(p => Path.GetRelativePath(root, p), StringComparer.Ordinal).ToArray();
        if (files.Length > 5000) throw new InvalidOperationException("Source file budget exceeded (5000).");
        var trees = new List<SyntaxTree>();
        var sourceIdentities = new List<string>();
        long bytes = 0;
        foreach (var file in files)
        {
            if (new FileInfo(file).Length > 32 * 1024 * 1024)
                throw new InvalidOperationException("Source file byte budget exceeded.");
            var data = File.ReadAllBytes(file);
            bytes += data.Length;
            if (data.Length > 32 * 1024 * 1024 || bytes > 128 * 1024 * 1024)
                throw new InvalidOperationException("Source byte budget exceeded.");
            var relative = Path.GetRelativePath(root, file).Replace(Path.DirectorySeparatorChar, '/');
            var tree = CSharpSyntaxTree.ParseText(Encoding.UTF8.GetString(data), path: relative);
            if (tree.GetDiagnostics().Any(d => d.Severity == DiagnosticSeverity.Error))
                throw new InvalidOperationException("Syntax errors in " + relative + "; no partial graph emitted.");
            trees.Add(tree);
            sourceIdentities.Add(relative + ":" + Convert.ToHexString(SHA256.HashData(data)));
        }
        var trusted = (AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES") as string ?? "")
            .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries)
            .OrderBy(p => p, StringComparer.Ordinal)
            .Select(p => MetadataReference.CreateFromFile(p));
        var compilation = CSharpCompilation.Create("LocalGraphSnapshot", trees, trusted,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        var nodes = new SortedDictionary<string, Node>(StringComparer.Ordinal);
        var edges = new SortedDictionary<string, Edge>(StringComparer.Ordinal);
        string Id(ISymbol symbol) => "symbol:" + Hash(scope + "\n" + symbol.ContainingAssembly?.Name + "\n" +
            (symbol.GetDocumentationCommentId() ?? symbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)) + "\n" + symbol.Kind);
        string AddSymbol(ISymbol symbol, string locator)
        {
            symbol = symbol.OriginalDefinition;
            var id = Id(symbol);
            if (!nodes.TryGetValue(id, out var node))
            {
                var kind = symbol is INamedTypeSymbol type ? type.TypeKind.ToString().ToLowerInvariant() : symbol.Kind.ToString().ToLowerInvariant();
                node = new Node(id, kind, symbol.ToDisplayString(), new()
                {
                    ["symbol"] = symbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat),
                    ["assembly"] = symbol.ContainingAssembly?.Name,
                    ["external"] = !symbol.Locations.Any(l => l.IsInSource)
                });
                nodes[id] = node;
            }
            node.evidence.Add(Observe(locator, "DERIVED"));
            return id;
        }
        void Link(string a, string b, string relation, string locator, string provenance = "DERIVED")
        {
            var key = a + "\n" + b + "\n" + relation;
            if (!edges.TryGetValue(key, out var edge))
            {
                edge = new Edge(a, b, relation);
                edges[key] = edge;
            }
            edge.evidence.Add(Observe(locator, provenance));
        }
        var unresolved = 0;
        foreach (var tree in trees)
        {
            var relative = tree.FilePath;
            var fileId = "file:" + Hash(scope + "\n" + relative);
            nodes[fileId] = new Node(fileId, "file", relative, new() { ["path"] = relative });
            nodes[fileId].evidence.Add(Observe(relative, "EXTRACTED"));
            var model = compilation.GetSemanticModel(tree);
            foreach (var syntax in tree.GetRoot().DescendantNodes())
            {
                var locator = relative + ":L" + (syntax.GetLocation().GetLineSpan().StartLinePosition.Line + 1);
                if (syntax is BaseTypeDeclarationSyntax or DelegateDeclarationSyntax or BaseMethodDeclarationSyntax
                    or PropertyDeclarationSyntax or EventDeclarationSyntax or VariableDeclaratorSyntax)
                {
                    var symbol = model.GetDeclaredSymbol(syntax);
                    if (symbol is not null)
                    {
                        var id = AddSymbol(symbol, locator);
                        Link(fileId, id, "defines", locator, "EXTRACTED");
                        if (symbol is INamedTypeSymbol named)
                        {
                            if (named.BaseType is { TypeKind: not TypeKind.Error } parent)
                                Link(id, AddSymbol(parent, locator), "inherits", locator);
                            foreach (var implemented in named.Interfaces.Where(i => i.TypeKind != TypeKind.Error))
                                Link(id, AddSymbol(implemented, locator), "implements", locator);
                        }
                    }
                }
                if (syntax is InvocationExpressionSyntax invocation)
                {
                    var owner = model.GetEnclosingSymbol(invocation.SpanStart);
                    var origin = owner is null ? fileId : AddSymbol(owner, locator);
                    var info = model.GetSymbolInfo(invocation);
                    if (info.Symbol is IMethodSymbol target)
                    {
                        Link(origin, AddSymbol(target, locator), "calls", locator);
                    }
                    else
                    {
                        unresolved++;
                        var refId = "call-site:" + Hash(scope + "\n" + relative + "\n" + invocation.SpanStart);
                        nodes[refId] = new Node(refId, "unresolved_call", invocation.Expression.ToString(), new()
                        {
                            ["path"] = relative,
                            ["line"] = invocation.GetLocation().GetLineSpan().StartLinePosition.Line + 1,
                            ["candidate_reason"] = info.CandidateReason.ToString()
                        });
                        nodes[refId].evidence.Add(Observe(locator, "EXTRACTED"));
                        Link(origin, refId, "contains_call_site", locator, "EXTRACTED");
                    }
                }
            }
        }
        var errors = compilation.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error)
            .Select(d => d.Id).GroupBy(id => id).OrderBy(g => g.Key).ToDictionary(g => g.Key, g => g.Count());
        var output = new
        {
            schema_version = "graph-patch-v1",
            source = new
            {
                uri = "roslyn://" + Uri.EscapeDataString(scope) + "/source-snapshot",
                kind = "csharp_snapshot",
                content_hash = "sha256:" + Hash(string.Join("\n", sourceIdentities)),
                metadata = new
                {
                    compiler_version = typeof(CSharpCompilation).Assembly.GetName().Version?.ToString(),
                    source_files = files.Length,
                    unresolved_calls = unresolved,
                    compilation_errors = errors,
                    scope_note = "Single in-memory source compilation with runtime references. No csproj, analyzers, generators, NuGet resolution, conditional build symbols, or runtime dispatch analysis."
                }
            },
            nodes = nodes.Values,
            edges = edges.Values
        };
        Console.WriteLine(JsonSerializer.Serialize(output, new JsonSerializerOptions { WriteIndented = true }));
        return 0;
    }
    catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException or InvalidOperationException)
    {
        Console.Error.WriteLine(ex.Message);
        return 1;
    }
}

static IEnumerable<string> Walk(string root)
{
    var excluded = new HashSet<string>([".git", "bin", "obj", ".local-graph", "node_modules"], StringComparer.OrdinalIgnoreCase);
    foreach (var entry in new DirectoryInfo(root).EnumerateFileSystemInfos().OrderBy(e => e.Name, StringComparer.Ordinal))
    {
        if ((entry.Attributes & FileAttributes.ReparsePoint) != 0) continue;
        if (entry is DirectoryInfo directory)
        {
            if (!excluded.Contains(directory.Name))
                foreach (var file in Walk(directory.FullName)) yield return file;
        }
        else if (entry.Extension.Equals(".cs", StringComparison.OrdinalIgnoreCase)) yield return entry.FullName;
    }
}
static string Hash(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
static object Observe(string locator, string provenance) => new
{
    provenance, confidence = 1.0, status = "accepted", locator,
    details = new { meaning = "Static compiler observation, not a runtime execution trace." }
};
sealed record Node(string id, string kind, string label, Dictionary<string, object?> properties)
{
    public List<object> evidence { get; } = [];
}
sealed record Edge(string source, string target, string relation)
{
    public bool directed => true;
    public Dictionary<string, object?> properties { get; } = [];
    public List<object> evidence { get; } = [];
}
