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
7. artifact persistence/delivery when packaging/report output is requested.

Branch on capability, not product name. ChatGPT/Codex, Claude, GitHub Copilot, Cursor, and other Agent Skills-compatible hosts may expose different tool names or install locations while still supporting the same semantic workflow.

## Python execution

Resolve a usable Python 3.10+ execution method. The CLI spelling may be `python3`, `python`, `py -3`, or a host code-execution facility. Once running, bundled scripts use `sys.executable` for child Python commands and `pathlib` for paths.

## Degraded mode

If execution is unavailable, static research/planning may continue, but executable gates are `not-run` or `blocked`. If filesystem write is unavailable, do not claim a repair was applied. If runtime/tool discovery is incomplete, do not silently substitute another command merely to obtain a pass.

## Optional adapter

`agents/openai.yaml` may describe OpenAI UI/invocation behavior. Ignoring it must not change command selection, classification, gates, repair rules, or evidence requirements.
