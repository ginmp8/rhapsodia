# Build, Analyzers, CI/CD, and Automatic Quality

## Recommended defaults

- `TreatWarningsAsErrors=true` for compiler/analyzer warnings according to repository policy.
- Nullable enabled.
- Central package management when appropriate.
- Formatting via `.editorconfig`.
- Static analyzers appropriate to the team.
- Restore/audit, test, security scan, and package/deploy validation in CI.

## NuGet audit interaction

.NET 10-targeting restores audit transitive dependencies by default. Do not globally disable audit because warnings-as-errors turns NU1901-NU1904 into restore failures. Make blocking severity/risk-acceptance policy explicit while preserving audit visibility. `WarningsNotAsErrors` can keep those audit codes as warnings when CI has a separate security gate.

## CI gates

- restore with audit output captured;
- SDK selection/reproducibility evidence when material;
- locked/deterministic restore when repository policy requires it;
- build warnings-as-errors;
- unit tests;
- focused integration/functional tests where required;
- expected/discovered test-count check for critical suites;
- format/analyzer checks;
- secret scan;
- dependency vulnerability scan and dependency-path investigation;
- container/image scan when deploying containers;
- published-artifact smoke tests when AOT/trimming/container packaging changes behavior.

## Evidence rule

Do not claim production readiness merely because the build is green. Build, test discovery, dependency/security, configuration, deployment, and runtime/operational gates must have known outcomes or be explicitly unverified.
