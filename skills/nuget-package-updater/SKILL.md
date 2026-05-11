---
name: nuget-package-updater
description: update and validate nuget central package management versions in directory.packages.props for local copilot or chatgpt-assisted dotnet work. use when asked to check, upgrade, modernize, or validate nuget package versions, especially when selecting the latest stable non-prerelease version, rejecting deprecated unlisted or vulnerable versions through nuget v3 registration and vulnerabilityinfo metadata, respecting packages locked or pinned in directory.packages.props, validating compatibility with a target framework such as net10.0, and producing deterministic reports and docs/pkgs-versions decision records before modifying files.
---

# NuGet Package Updater

## Purpose

Use this skill to update NuGet package versions declared in `Directory.Packages.props` through the bundled deterministic Python script. Do not manually guess package versions.

The script is the source of truth for version selection. It reads `PackageVersion` entries, queries NuGet V3 metadata, rejects unsafe candidates, respects local locks, optionally validates target-framework compatibility with `dotnet restore`, updates only selected `Version` attributes, and writes a decision record under `docs/pkgs-versions/`.

Never use MCP for this workflow. Do not use MCP tools, MCP package metadata, or MCP-assisted edits for package update decisions. Always use the bundled script and its generated report.

## Local-first workflow

1. Locate the repository root or the relevant `Directory.Packages.props` file.
2. Run `scan` first to list packages and detect locked entries.
3. Run `check` before writing changes, including `--write-decision-doc`.
4. Review the report and the Markdown decision document under `docs/pkgs-versions/`.
5. Only run `update --write` after the user explicitly requested file changes.
6. After write mode, run local validation such as `dotnet restore`, `dotnet build --no-restore`, and the repository test command if available.

Do not use Azure Pipeline snippets, CI-specific guidance, or MCP unless the user explicitly asks about a different topic. This skill defaults to local execution with Copilot or ChatGPT assistance.

## Required commands

From the skill folder, or after copying `scripts/nuget_update.py` into a repo-local tools folder, run:

```bash
python scripts/nuget_update.py scan --file Directory.Packages.props --report-format markdown
```

Check available safe updates without writing and create the decision record:

```bash
python scripts/nuget_update.py check --file Directory.Packages.props --target-framework net10.0 --report-format markdown --write-decision-doc
```

Apply safe updates and create the decision record:

```bash
python scripts/nuget_update.py update --file Directory.Packages.props --target-framework net10.0 --write --report-format markdown --write-decision-doc
```

For local Copilot usage, prefer copying `assets/copilot/nuget-package-updater.instructions.md` to `.github/instructions/nuget-package-updater.instructions.md` and `scripts/nuget_update.py` to `tools/nuget-updater/nuget_update.py` in the repository.

## NuGet API rules

Use the script's NuGet V3 API implementation instead of ad hoc HTTP calls:

- `SearchAutocompleteService`: enumerate stable listed package versions using `prerelease=false` and `semVerLevel=2.0.0`.
- `RegistrationsBaseUrl`: read package version metadata and reject versions with `catalogEntry.deprecation`, `catalogEntry.listed == false`, or `catalogEntry.vulnerabilities`.
- `VulnerabilityInfo`: download vulnerability index/pages and reject candidate versions matching vulnerable NuGet version ranges.

If any required metadata cannot be trusted, do not update manually. Fix feed access, SDK availability, or policy inputs and rerun the script.

## Safety rules

Always preserve these defaults unless the user explicitly asks for a non-default dry-run/test scenario:

- Select stable versions only; reject preview, alpha, beta, rc, dev, nightly, and other prerelease labels.
- Reject unlisted package versions.
- Reject deprecated package versions.
- Reject package versions with known vulnerabilities from Registration metadata or VulnerabilityInfo ranges.
- Respect packages locked or pinned in `Directory.Packages.props`.
- Block major upgrades unless `--allow-major` is passed.
- Validate candidate compatibility with the requested target framework unless the user is doing an explicit offline parser test.
- Do not update MSBuild property-based versions, wildcard versions, ranges, or non-literal versions.
- Do not use MCP or manual version selection.

If the script reports that metadata could not be trusted, do not update the package manually.

## Lock conventions

Treat a package as locked when the script reports `locked by directory.packages.props` or similar. The script recognizes lock intent in `PackageVersion` entries, including examples like:

```xml
<PackageVersion Include="Example.Package" Version="1.2.3" Locked="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" Pin="true" />
<PackageVersion Include="Example.Package" Version="1.2.3" UpdatePolicy="locked" />
<!-- nuget-updater: lock -->
<PackageVersion Include="Example.Package" Version="1.2.3" />
```

Do not remove or bypass locks unless the user explicitly asks to unlock the package.

## Compatibility rule

Treat an update as valid only when the script selects a stable, listed, non-deprecated, non-vulnerable candidate and restore validation succeeds for the requested target framework. For `.NET 10`, use `--target-framework net10.0`.

If the script reports `sdk-does-not-support-target-framework`, do not conclude that the package is incompatible. Tell the user their local machine likely lacks an SDK that understands the requested target framework.

If the script reports `no safe allowed candidate is compatible`, do not force the update.

## Decision document rule

For every real `check` or `update` request, create a Markdown decision document under `docs/pkgs-versions/` by passing `--write-decision-doc`. This document records why each package was updated, left unchanged, locked, skipped, or errored.

Default command pattern:

```bash
python scripts/nuget_update.py update --file Directory.Packages.props --target-framework net10.0 --write --report-format markdown --write-decision-doc
```

Use `references/decision-document.md` for the required structure and interpretation rules.

## Output handling

When presenting results to the user, summarize:

- packages updated;
- packages unchanged;
- packages locked and their lock reason;
- packages skipped because of deprecation, vulnerability, unlisted state, major-version policy, or compatibility;
- errors requiring environment or feed changes;
- decision document path under `docs/pkgs-versions/`;
- local validation commands run after the update.

Prefer Markdown output for human review:

```bash
python scripts/nuget_update.py update --file Directory.Packages.props --target-framework net10.0 --write --report-format markdown --report nuget-update-report.md --write-decision-doc
```

## References

- `references/usage.md`: command reference and report interpretation.
- `references/local-copilot-setup.md`: recommended local Copilot setup.
- `references/decision-document.md`: decision document standard.
- `assets/copilot/nuget-package-updater.instructions.md`: ready-to-copy Copilot instruction file.
