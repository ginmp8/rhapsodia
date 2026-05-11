---
applyTo: "**/{Directory.Packages.props,*.csproj,*.sln}"
---

# NuGet package update workflow

When asked to update NuGet packages, do not manually choose or edit package versions.

Never use MCP for this package update workflow. The only source of truth for selecting and validating package versions is the repository copy of the skill script, normally:

```bash
python tools/nuget-updater/nuget_update.py
```

Use the script first in check mode:

```bash
python tools/nuget-updater/nuget_update.py check \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --report-format markdown \
  --write-decision-doc
```

For write operations, use:

```bash
python tools/nuget-updater/nuget_update.py update \
  --file Directory.Packages.props \
  --target-framework net10.0 \
  --write \
  --report-format markdown \
  --report nuget-update-report.md \
  --write-decision-doc
```

Rules:

- Only use stable NuGet versions.
- Never use preview, alpha, beta, rc, nightly, dev, or prerelease versions.
- Validate package metadata through NuGet V3 `RegistrationsBaseUrl`.
- Cross-check known vulnerabilities through NuGet V3 `VulnerabilityInfo` when the source exposes it.
- Do not update versions that NuGet metadata reports as deprecated, unlisted, or vulnerable.
- Do not update packages marked as locked, pinned, ignored, manual, or no-update in `Directory.Packages.props`.
- Do not bypass `Locked="true"`, `Pin="true"`, `Pinned="true"`, `NoUpdate="true"`, `NuGetUpdaterLocked="true"`, `VersionLocked="true"`, or `UpdatePolicy="locked|pinned|manual|none"`.
- Do not remove lock comments such as `<!-- nuget-updater: lock -->`.
- Do not manually edit a version when the script reports an error. Fix the environment, feed, SDK, or policy first.
- Prefer `Directory.Packages.props` updates over direct `.csproj` package edits.
- Always create a Markdown decision document under `docs/pkgs-versions/` using `--write-decision-doc`.
- After updates, run `dotnet restore`, `dotnet build --no-restore`, and the repository test command if available.
- Include the generated report and decision document path in the final summary.
