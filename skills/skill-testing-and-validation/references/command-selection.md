# Command selection

Use this reference for `run-build`, `run-tests`, `run-lint`, `implement-test-phase`, and `fix-failures`.

## General priority

1. User-provided command.
2. Command already captured in a research or plan artifact.
3. Project-declared command in package.json, Makefile, pyproject.toml, CI, or README.
4. Language-standard command inferred from project markers.
5. Static validation or syntax check when no executable project command exists.

Prefer commands that are narrow, deterministic, and non-destructive. Use the target root as the working directory unless the project structure clearly requires a subdirectory.

## Build commands

| Marker | Preferred command | Notes |
|---|---|---|
| *.sln or *.csproj | `dotnet build` | Use project path when scoped. Use quiet output only if it does not hide errors. |
| package.json | `npm run build`, `npm run compile`, or `npx tsc --noEmit` | Prefer declared scripts. Do not run install automatically. |
| pyproject.toml, Python scripts | `python -m py_compile <files>` | Python projects may not have a build. Compile touched scripts as fallback. |
| go.mod | `go build ./...` | Scope to package when requested. |
| Cargo.toml | `cargo build` | Use workspace commands if present. |
| pom.xml | `mvn test -DskipTests` or `mvn compile` | Prefer wrapper scripts when present. |
| build.gradle | `./gradlew build` or `gradle build` | Prefer wrapper if executable. |
| Makefile | `make build` or `make` | Inspect targets first. |

## Test commands

| Marker | Preferred command |
|---|---|
| package.json with test script | `npm test` or declared `npm run test*` command |
| Jest/Vitest config | declared script, `npx jest`, or `npx vitest run` only if dependencies are available |
| pytest.ini, pyproject.toml, tests/ | `python -m pytest` or `pytest` |
| Python unittest files | `python -m unittest discover` |
| `.sln` or test *.csproj | `dotnet test` |
| go.mod | `go test ./...` |
| Cargo.toml | `cargo test` |
| pom.xml | `mvn test` |
| build.gradle | `./gradlew test` or `gradle test` |
| skill package with validator scripts | run the declared validator and compile modified scripts |

## Lint and format-check commands

Prefer check-only lint when the user asks to validate; prefer fix mode only when the user asks to correct formatting.

| Marker | Check command | Fix command |
|---|---|---|
| package.json | `npm run lint`, `npm run format:check` | `npm run lint:fix`, `npm run format` |
| `.prettierrc` | `npx prettier --check .` | `npx prettier --write .` |
| Python with Ruff | `ruff check .`, `ruff format --check .` | `ruff check --fix .`, `ruff format .` |
| Python with Black | `black --check .` | `black .` |
| `.sln`, *.csproj | `dotnet format --verify-no-changes` | `dotnet format` |
| go.mod | `gofmt -w` only when fixing | `gofmt -w <files>` |
| Cargo.toml | `cargo fmt --check` | `cargo fmt` |

## Safe execution policy

- Do not install dependencies or update lockfiles unless authorized.
- Do not run commands that deploy, publish, upload, delete, migrate, or mutate production state.
- Do not run long or broad commands when a scoped command can answer the question.
- If command discovery is uncertain, report candidates and ask only when the choice materially changes risk; otherwise use the safest narrow fallback.
- Capture enough output to support the result, but summarize long logs.
