# Host portability

Keep the semantic workflow in portable Agent Skills files (`SKILL.md`, `scripts/`, `references/`, `assets/`, `evals/`, `tests/`). Host-specific metadata is an adapter only.

## Capability detection

Before execution, detect:

1. filesystem read;
2. filesystem write when baseline/candidate evidence is required;
3. command execution;
4. Python 3.10+ for bundled helpers;
5. target runtime/tool availability;
6. network only when a gate legitimately requires it;
7. optional advanced testing tools only after the problem selects that strategy;
8. artifact persistence/delivery when packaging/report output is requested.

Branch on capability, not product name. ChatGPT/Codex, Claude, GitHub Copilot, Cursor, and other Agent Skills-compatible hosts may expose different tool names or install locations while still supporting the same semantic workflow.

## Python execution

Resolve a usable Python 3.10+ execution method. The CLI spelling may be `python3`, `python`, `py -3`, or a host code-execution facility. Once running, bundled scripts use `sys.executable` for child Python commands and `pathlib` for paths.

Bundled deterministic helpers use the standard library. Optional project-owned property/stateful, fuzz, contract, or mutation frameworks are capabilities, not core package dependencies.

## Execution context and evidence identity

`scripts/environment_fingerprint.py` records a bounded safe context and never dumps the environment wholesale. Missing locale/timezone/hash-seed/CI metadata should remain `null`/false rather than being invented.

`scripts/evidence_identity.py` binds receipts to material target bytes while excluding transient runtime/build evidence such as interpreter caches. The identity is content-based and uses normalized relative paths so host-specific absolute install paths do not become the candidate identity.

## Portable packaging

The bundled packager rejects symlink inputs, output/report aliases, and delivery paths inside the validated target tree. It normalizes ZIP timestamps and permission metadata before hashing the archive. This avoids Unix/Windows metadata drift while preserving source file bytes. Package outputs remain artifacts outside the skill root.

## Degraded mode

If execution is unavailable, static research/planning may continue, but executable gates are `not-run` or `blocked`. If filesystem write is unavailable, do not claim a repair was applied. If runtime/tool discovery is incomplete, do not silently substitute another command merely to obtain a pass.

If an advanced testing strategy is selected but its project-owned tool is unavailable, report that strategy `blocked`/`not-run`; do not install a dependency or choose a weaker metric unless the user explicitly authorizes the change and the test plan is re-baselined.

## Optional adapter

`agents/openai.yaml` may describe OpenAI UI/invocation behavior. Ignoring it must not change command selection, classification, gates, reliability/oracle rules, repair rules, or evidence requirements.
