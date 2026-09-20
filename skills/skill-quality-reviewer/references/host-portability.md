# Host Portability Contract

Review the Agent Skills package core independently from vendor adapters.

## Core

Require only `SKILL.md`, package-relative resources, declared helper runtimes, and host-neutral paths. Do not require a vendor adapter for portable-core correctness. `agents/openai.yaml` is optional unless the caller explicitly selects the `openai` profile.

## Profiles

- `auto`: validate adapters only when present.
- `portable`: evaluate host-neutral core; adapters are optional.
- `openai`: also require/check the OpenAI adapter.
- `codex`, `claude`, `copilot`, `cursor`: evaluate the portable core; OpenAI metadata is optional unless explicitly required.

## Execution

Resolve `<PYTHON>` from host capabilities (`python`, `python3`, `py -3`, an absolute interpreter, or equivalent execution mechanism). Bundled helpers use the standard library and `pathlib`. Do not make correctness depend on Bash, POSIX-only commands, fixed sandbox paths, or one installation directory.

Use generic peer paths such as `<SKILL_CATALOG_ROOT>/<peer-skill>/SKILL.md` in reviewer-owned examples. Literal host paths are evidence only when observed in the target under review.

Report structural, runtime, and behavioral portability separately. Structural checks do not prove runtime or behavioral equivalence on a host.
