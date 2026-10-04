# Host Portability Contract

Review the Agent Skills package core independently from vendor adapters and keep structural portability separate from host-semantic/runtime evidence.

## Core

Require only `SKILL.md`, package-relative resources, declared helper runtimes, and host-neutral paths. Do not require a vendor adapter for portable-core correctness. `agents/openai.yaml` is optional unless the caller explicitly selects the `openai` profile.

## Profiles

- `auto`: validate adapters only when present; do not infer unrequested host semantics.
- `portable`: evaluate the host-neutral core; adapters are optional.
- `openai`: evaluate portable core plus the OpenAI adapter when present/required.
- `codex`, `claude`, `copilot`, `cursor`: evaluate portable core plus any evidence-backed semantics specific to the selected host. OpenAI metadata remains optional unless the selected host requires it.

Selecting a profile does not prove runtime equivalence. A host-specific readiness claim needs evidence for the semantic surfaces that matter to the claim.

## Host-semantic surfaces

For every explicitly reviewed host, record `verified`, `not-verified`, `not-applicable`, or `blocked` for the relevant surfaces:

| Surface | Review question |
|---|---|
| discovery/install | Where/how can the host discover the package, and is that evidence current? |
| invocation | Automatic, explicit, slash-command, mode/session, or other trigger semantics? |
| scoping | Repository/path/file/session scoping that changes whether the skill is surfaced? |
| context loading | What metadata/body/resources are injected and when? |
| tool/runtime | Which declared runtimes/tools are actually available or permission-gated? |
| local/cloud variants | Do product surfaces differ materially between local, cloud, review, CLI, or IDE execution? |
| extensions | Does the host add metadata/frontmatter that is optional or changes semantics? |
| freshness | Which official source/version/retrieval identity supports the host claim? |

Do not hard-code a vendor's current semantics as a portable-core rule. Inspect current official host documentation or executed host behavior when the user requests that host. If freshness cannot be established, report the host-semantic claim as `not-verified` or `blocked` rather than extrapolating from another implementation.

## Execution

Resolve `<PYTHON>` from host capabilities (`python`, `python3`, `py -3`, an absolute interpreter, or equivalent execution mechanism). Bundled helpers use the standard library and `pathlib`. Do not make correctness depend on Bash, POSIX-only commands, fixed sandbox paths, or one installation directory.

Use generic peer paths such as `<SKILL_CATALOG_ROOT>/<peer-skill>/SKILL.md` in reviewer-owned examples. Literal host paths are evidence only when observed in the target under review.

## Portability claim levels

Report these separately:

- **structural portability:** portable package shape, relative resources, syntax, and adapters;
- **semantic portability:** host discovery/invocation/scoping/context semantics are evidenced and do not change the intended contract unexpectedly;
- **runtime portability:** the required scripts/tools actually execute on the host/environment;
- **behavioral portability:** representative scenarios behave equivalently enough across the tested hosts for the stated claim.

Structural checks do not prove semantic, runtime, or behavioral equivalence. Documentation evidence for host semantics does not prove runtime behavior. Runtime success on one host does not prove another host.
