# Build, Analyzers, CI/CD, and Automatic Quality

## Recommended defaults

- `TreatWarningsAsErrors=true`.
- Nullable enabled.
- Central package management.
- Formatting via `.editorconfig`.
- Static analyzers appropriate to the team.
- Test, coverage, security scan, and package validation in CI.

## CI gates

- restore locked/deterministic packages;
- build warnings-as-errors;
- unit tests;
- integration tests where feasible;
- format/analyzer checks;
- secret scan;
- dependency vulnerability scan;
- container/image scan when deploying containers.

## Rule

Do not claim code is production-ready unless build, tests, configuration, security, and deployment checks are known or explicitly marked unverified.
