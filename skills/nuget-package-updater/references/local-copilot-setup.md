# Local Copilot setup

Use this skill as a local repository workflow, not as an Azure Pipeline workflow.

## Recommended setup

1. Copy `scripts/nuget_update.py` to `tools/nuget-updater/nuget_update.py`.
2. Copy `assets/copilot/nuget-package-updater.instructions.md` to `.github/instructions/nuget-package-updater.instructions.md`.
3. Create `docs/pkgs-versions/` or let the script create it when `--write-decision-doc` is used.
4. Ask Copilot to run the script instead of editing NuGet versions directly.
5. Never ask Copilot to use MCP for package update decisions.
6. Review the generated Markdown decision document before accepting changes.
7. Run local restore/build/tests after updates.

## Copilot prompt examples

```text
Use the NuGet updater script to check safe package updates for net10.0. Do not write changes yet. Do not use MCP. Create the docs/pkgs-versions decision document.
```

```text
Update Directory.Packages.props using the NuGet updater script. Respect locked packages and do not update deprecated, unlisted, or vulnerable versions. Do not use MCP. Create the docs/pkgs-versions decision document.
```

```text
Explain why these packages were skipped in docs/pkgs-versions/nuget-package-update-decisions-*.md.
```

## Local validation checklist

After any update, run:

```bash
dotnet restore
dotnet build --no-restore
```

Then run the repository-specific test command if one exists.
