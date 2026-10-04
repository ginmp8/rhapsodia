# Supply Chain, Dependencies, CI/CD, and Script Security

## Dependency governance

- Use Central Package Management for multi-project repositories when it reduces version drift.
- Prefer explicit non-floating versions for production dependencies unless the repository deliberately owns another policy.
- Remove unused packages and review every new dependency against existing runtime/repository capability before adding it.
- Treat pre-release packages as explicit risk decisions.
- Record the selected SDK and resolved dependency graph when reproducibility or a production/security gate depends on restore/build behavior.

## .NET 10 NuGet audit

For projects targeting .NET 10 or later, `dotnet restore` defaults `NuGetAuditMode` to `all`, so known vulnerabilities in transitive dependencies are reported as well as direct dependencies.

When `TreatWarningsAsErrors` makes NU1901-NU1904 fail restore, do not disable auditing merely to get green CI. A deliberate policy may keep those audit codes as warnings via `WarningsNotAsErrors` while CI/security policy separately decides which severities block promotion. Preserve visibility and explicit risk ownership.

When a vulnerable dependency is transitive:

1. use `dotnet nuget why` or equivalent graph evidence to find the top-level path;
2. prefer upgrading the responsible direct/top-level package;
3. use a direct override or central transitive pin only when compatibility is verified and ownership/cleanup is explicit;
4. record advisory suppression/risk acceptance narrowly rather than disabling audit globally.

## Central package, lock-file, and transitive-pinning trade-offs

Central Package Management centralizes versions; it does not automatically freeze the entire restore environment.

- Use packages.lock.json/locked restore when exact resolved graph repeatability is a release/repository requirement.
- Pin SDK behavior as well; SDK/NuGet updates can affect restore even with a lock file.
- Use `CentralPackageTransitivePinningEnabled` only when the repository intentionally owns the override. For packable libraries, pinned transitives can become explicit package dependencies, changing the produced dependency surface.
- Do not pin a transitive merely to silence a vulnerability without testing the direct package's compatibility expectations.

## CI/CD security and evidence

- Do not print secrets.
- Use least-privilege tokens.
- Separate restore, build, test, dependency/security scan, package, and deploy gates.
- Require appropriate approval/policy for production deployment.
- Capture restore/audit output, selected SDK, and package graph/lock identity when relevant to the claim.
- Rebuild self-contained/container artifacts after applicable runtime/base-image security updates.

## Script security

Review scripts for shell injection, path traversal, unsafe archive extraction, broad deletes, unsafe file writes, untrusted deserialization, credential leakage, and execution of untrusted inputs.

## Fresh-source anchors

- NuGet audit: https://learn.microsoft.com/nuget/concepts/auditing-packages
- Central Package Management: https://learn.microsoft.com/nuget/consume-packages/central-package-management
- Package lock files: https://learn.microsoft.com/nuget/consume-packages/package-references-in-project-files
