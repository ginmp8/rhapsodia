# Host Portability Contract

**Contract version:** 1.0.0

The semantic core of this skill is host-neutral Agent Skills content. Host metadata is optional and must not be required to understand or execute the review workflow.

## Supported host profiles

| Profile | Support contract | Required capability |
|---|---|---|
| `portable-core` | `SKILL.md`, references, scripts, assets, and evals remain sufficient | read files; optionally execute Python for deterministic evidence |
| OpenAI / ChatGPT | portable core plus optional `agents/openai.yaml` metadata | host can load Agent Skills-compatible package content |
| Codex | portable core; OpenAI adapter may be ignored | filesystem/tool execution when available |
| Claude | portable core; no OpenAI-private API required | Agent Skills-compatible package loading or equivalent instructions |
| GitHub Copilot | portable core; no GitHub-private runtime required | Agent Skills-compatible package loading or equivalent instructions |
| Cursor | portable core; no Cursor-private runtime required | Agent Skills-compatible package loading or equivalent instructions |

Support means the workflow semantics do not require a vendor-private API. It does not claim that every host exposes identical tools, filesystem access, or command execution.

## Capability-first execution

Before running helpers, detect capabilities rather than branching on host name:

1. file read access;
2. file write access for requested durable reports;
3. Python 3.10+ execution;
4. subprocess execution only when a reviewed package requires it;
5. artifact delivery only when requested.

When a capability is unavailable, degrade explicitly. For example, if Python cannot run, build the evidence classes manually and mark package identity `not-measured`; do not fabricate executed evidence.

## Python launcher policy

Documentation and generated guidance must use `<PYTHON>` as the launcher token. Resolve it from the active environment, for example `python`, `python3`, `py -3`, or an equivalent host-provided Python 3.10+ command.

Bundled helpers use only the Python standard library and must not require shell-specific wrappers. Invoke scripts with argument arrays or equivalent host-safe process execution where possible.

## Filesystem and path rules

- Use package-relative paths in instructions, reports, contracts, and deterministic evidence.
- Never embed sandbox-specific roots such as `/home/...` or `/mnt/data/...` in package content.
- Python helpers use `pathlib` and normalize evidence paths to forward-slash relative paths when serialized.
- Package identity must remain independent of the package's absolute installation path.
- Do not require symlinks, executable-bit semantics, Bash, PowerShell, or a particular working-directory layout for correctness.

## Host adapters

`agents/openai.yaml` is an optional adapter. A missing or ignored adapter must not change the semantic review workflow, rubric, evidence model, report contract, or stop conditions.

Additional host adapters may be added only when they are optional metadata or routing layers. Do not duplicate semantic rules into adapters; keep source truth in the portable core.

## Portability validation

Run:

```text
<PYTHON> scripts/validate_portability.py --target <SKILL_ROOT>
```

The validator checks only mechanically defensible properties: root structure, Python syntax/stdlib usage, sandbox-specific absolute paths, shell-coupled subprocess patterns, path-independent package identity, and optional-adapter isolation. A pass does not prove that a specific host supports every capability; it proves the package does not contain the checked portability blockers.
