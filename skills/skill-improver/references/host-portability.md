# Host Portability

Use when the target or improvement workflow must work across ChatGPT/Codex, Claude, GitHub Copilot, Cursor, or another Agent Skills-compatible host.

## Portable semantic core

The semantic workflow must remain understandable without host-specific metadata:

- one skill directory with `SKILL.md`;
- portable YAML frontmatter `name` and `description`;
- relative `scripts/`, `references/`, `assets/`, and optional `evals/`;
- lowercase hyphenated skill name;
- scripts using standard-library Python where possible;
- no correctness dependency on a vendor-only metadata file or CLI.

`agents/openai.yaml` is an optional OpenAI adapter, not part of the semantic core. Preserve intentional host extensions, but do not make other hosts depend on them.

## Capability-first execution

Detect capabilities before choosing a branch:

1. filesystem read;
2. filesystem write;
3. Python 3.10+ or equivalent script execution;
4. command execution;
5. network/research when freshness matters;
6. independent evaluator/subagent support;
7. artifact delivery/persistence.

If a hard gate depends on a missing capability, report `not-run` or `blocked`; do not silently treat it as pass.

## Python portability

Use `<PYTHON>` in instructions to mean the host's available Python 3.10+ execution method. Common CLI spellings include `python3`, `python`, and Windows `py -3`, but hosts may expose code execution through tools rather than a shell.

Inside scripts:

- use `sys.executable` for child Python processes;
- use `pathlib` for filesystem work;
- avoid Bash-only pipelines and POSIX-only utilities in semantic requirements;
- avoid hard-coded `/tmp`, drive letters, or path separators;
- emit actionable errors when a required executable is absent.

## Autonomous runner adapters

`scripts/skill_improver_loop.py` includes a Codex adapter for backward compatibility. Treat it as an optional execution adapter, not the portable workflow definition.

For other agent CLIs, use the generic command adapter:

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET> \
  --agent-adapter command \
  --agent-command-template '<CLI> ... {prompt} ...' \
  <other evaluator/gate options>
```

The template is tokenized without a shell and supports these exact placeholders:

- `{prompt}`: generated bounded patch instruction;
- `{cwd}`: repository root;
- `{target}`: target skill path.

Do not interpolate untrusted text into a shell string. If a third-party CLI cannot accept a prompt/path safely as normal argv, use the host's native execution mechanism instead of forcing the generic adapter.

## Packaging

Portable packaging rules:

1. package only the skill folder;
2. exclude caches, generated reports, secrets, previous archives, and transient state;
3. freeze/hash the exact candidate before packaging;
4. validate package contents after the final change;
5. treat vendor metadata as optional adapters unless the requested destination requires them.

## Degraded execution

If the host can read but cannot execute scripts, audit/plan branches may continue. Mutation may proceed only when the missing hard gate is not required for safety. Do not claim package validation, frozen-evaluator verification, or reproducibility hardening if those required checks did not run.

## Legacy alias portability

The deprecated `skill-improvement` name may exist as a host-specific or catalog compatibility shim. It must delegate semantically to this package and must not contain an independent improvement engine. Hosts that do not support aliases should prefer installing only `skill-improver`; existing legacy state remains historical evidence and is not silently rewritten.
