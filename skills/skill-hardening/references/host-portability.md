# Host Portability

## Purpose

Keep hardening behavior portable across Agent Skills hosts. Validate one host-neutral semantic core and isolate product-specific discovery, metadata, permissions, and runtime constraints at the edges.

## Portable core

Require only one root `SKILL.md` with valid `name` and `description`, package-local relative references, and optional `scripts/`, `references/`, `assets/`, `examples/`, or `evals/` when the skill actually needs them. `license`, `compatibility`, `metadata`, and `allowed-tools` are recognized portable-spec fields; `allowed-tools` remains experimental and must not be required for correctness or permission bypass.

Do not make the core depend on vendor-private APIs, sandbox paths, user-home installation paths, or a host-specific metadata file.

## Profiles

| Profile | Contract |
|---|---|
| `portable-core` | Open Agent Skills semantic core; source of truth for cross-host behavior. |
| `openai` | Same core; `agents/openai.yaml` may exist as optional OpenAI adapter metadata. |
| `codex` | Same core; repository/user discovery is a host concern, not package semantics. |
| `claude` | Same core; preserve intentional Claude extensions only as optional host-specific metadata, never as a portable-core dependency. |
| `copilot` | Same core; discovery locations and tool approvals are host concerns. |
| `cursor` | Same core; Cursor-specific fields/discovery remain optional host extensions. |

A “multi-platform” claim means structural portability across every requested profile. Runtime behavior remains `not-proven` until it is actually executed on that host/runtime.

## Capability-first execution

Record capabilities before execution: filesystem read/write, command execution, Python 3.10+, network, independent evaluator/subagent support, and artifact delivery. Missing capability is `blocked`/`not-run`, never an inferred pass.

Resolve `<PYTHON>` from the current host. Bundled helpers use only the Python standard library and relative package paths.

## Validation

Run:

```text
<PYTHON> scripts/validate_portability.py --target <TARGET> --hosts portable-core,openai,codex,claude,copilot,cursor
```

The helper checks structural portability only. Product-specific metadata semantics must be validated by a current host-specific validator when that adapter is part of the requested delivery.

## Freshness

Host discovery paths, size limits, and proprietary extensions change faster than the core specification. Re-check current official host documentation whenever such unstable details affect a delivery decision instead of freezing them as universal package rules.
