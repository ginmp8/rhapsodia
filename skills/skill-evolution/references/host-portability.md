# Host Portability

Keep the semantic core Agent Skills-compatible: `SKILL.md`, relative `references/`, `scripts/`, `assets/`, and JSON contracts. Do not require a vendor-private invocation API, absolute installation path, shell dialect, or host-only metadata for correctness.

## Capability-first execution

Detect capabilities instead of branching primarily on product name:

- readable/writable filesystem;
- Python 3.10+ or equivalent code execution;
- ability to invoke caller-provided mutation/evaluation actions;
- artifact/report delivery;
- stable evaluator/runtime identity when comparisons depend on it.

Resolve `<PYTHON>` from the active environment (`python3`, `python`, `py -3`, or host code execution) rather than hard-coding one launcher. Bundled helpers use the Python standard library and relative paths.

If mutation/evaluation actions cannot be invoked, use `plan-only`, `selection-only`, or `validation-only`. Never fabricate candidate creation or measured evaluation.

## Host adapters

The portable core is intended to remain usable from ChatGPT/Codex, Claude/Claude Code, GitHub Copilot, Cursor, and other Agent Skills-compatible hosts. Host-specific discovery paths, permission metadata, or UI configuration are distribution adapters, not search semantics.

Treat `agents/openai.yaml` as optional OpenAI UI metadata. Preserve other intentional host adapters when present, but ignoring any adapter must leave the core contracts, validators, and workflow understandable and executable with equivalent capabilities.

When installation/discovery locations matter to a delivery task, verify current host documentation instead of encoding volatile paths into this skill's semantic contract.
