# Upgrade to RhapsodIA 0.7.0

## Compatibility

RhapsodIA package identity remains `0.7.0`. The final Runtime Harness design in this
release has independent skill/runtime version `1.1.0` and replaces the earlier eager
0.7.0 development candidate. Existing 0.6.0 skills remain independent of the harness.
Seven agent profiles gain optional runtime guidance without new tools or domain authority.

If replacing an earlier 0.7.0 candidate that already created `.rhapsodia/runtime/`, run
an explicit fresh `init --refresh` (or remove only that disposable runtime directory
after writers stop). Runtime snapshot shape/identity changed and old state must not be
silently reused.

## Setup

Use an existing Python 3.10+ supplied by the host:

```text
python -I -S -B scripts/runtime.py --workspace <PROJECT> init --skills-root <RHAPSODIA_SKILLS>
python -I -S -B scripts/runtime.py --workspace <PROJECT> configure --host copilot
```

`init` is intentionally cheap: it records the running Python and bounded skill/agent
catalogs. It does **not** eagerly probe Git, .NET, Node, Docker or another fixed tool list.

## Agent-driven lazy discovery

When an execution-authorized agent needs a missing exact dependency:

```text
python -I -S -B scripts/runtime.py --workspace <PROJECT> ensure tool://dotnet
python -I -S -B scripts/runtime.py --workspace <PROJECT> ensure tool://docker
```

The first successful observation is merged into a new immutable snapshot. Later agents
reuse it. A missing observation is cached until its TTL expires or PATH/PATHEXT changes.
No candidate executable is launched by discovery.

If authorized native work already found an executable outside PATH:

```text
python -I -S -B scripts/runtime.py --workspace <PROJECT> observe-tool tool://custom --path <FILE>
```

If an agent found a stable reusable script/config/file inside the project or a registered
skill root:

```text
python -I -S -B scripts/runtime.py --workspace <PROJECT> observe-resource resource://validation/main --path <FILE>
```

Only locations and file identities are shared. Do not use the runtime registry for
arbitrary notes, permissions, product/technical decisions, test verdicts, secrets or
volatile task state; those belong to domain artifacts/handoffs.

## Host integration

`configure --host` supports generic/Codex, Copilot, Claude and Cursor instruction files
while preserving unrelated content. It does not enable hooks, grant tools or run a
service. `session-start` can be wired into a trusted host-native hook to inject the small
bootstrap card before model work.

Read-only agents use existing observations only. `ensure` and `observe-*` require the
caller to already hold execution/local-state write authority.

## State and portability

State stays in `<PROJECT>/.rhapsodia/runtime/` and is excluded from release archives.
Do not copy `current.json` between machines. Initialize on the receiving host and use
explicit handoff rebind for portable pinned content.

Mutable PATH and Git HEAD no longer invalidate the whole environment. Available tool
files are revalidated on use; negative tool cache is tied to the hashed search space;
resource bytes are rehashed on lookup/handoff.

The core uses only Python standard library and platform-neutral filesystem/process argv
semantics. POSIX/PowerShell bootstrap scripts are optional adapters, not requirements.
