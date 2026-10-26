# Agent teams and host integration

## Core requirements

Required for executable improvement: authorized repository read/write, isolated working state, bounded command execution and an available verification command. Python 3 is optional for metric comparison. Network, browser, subagents and external services are optional unless the task's actual oracle requires them. Missing a required capability means `blocked`; optional loss means perform a documented serial or manual equivalent, never invent the result.

## PandaCode usage

PandaCode is a host/orchestrator, not this skill's implementation dependency. Install/discover this Agent Skills folder in the **underlying coding CLI or agent** using that agent's supported skill mechanism. PandaCode alone does not prove the CLI loaded this file; confirm the active agent can read and follow the skill. Prefer the host's isolated worktree support only after verifying its actual working-directory and permission behavior.

A suggested PandaCode request:

> Use software-improvement-loop in performance mode. Reduce application startup time while preserving behavior and memory guardrails. Capture a repeatable baseline first, propose bounded hypotheses, isolate candidates, execute tests and repeated measurements, and keep only a verified improvement. At most three candidate attempts; do not merge or deploy.

## When multiple agents help

Use multiple workers only when independent tasks, isolation or verification adds measurable value. One controller keeps the frozen evaluation and budgets. Example optional roles:

- A read-only researcher identifies hotspots and read/write sets.
- An oracle author prepares and freezes tests **before** a candidate is developed, without editing production code.
- One implementer writes candidate code to one isolated worktree.
- A verifier with a fresh context runs prescribed commands and reviews the diff without modifying the candidate to make checks pass.

Multiple parallel candidates require separate isolated worktrees, identical frozen evaluators and a single integration owner. Unknown read/write overlap must serialize. Concurrent agents never share mutable verification criteria. Model names and vendor-specific CLI syntax are intentionally excluded from the portable core.

## Cross-host mapping

`portable-core`: file/command capabilities; `openai`, `codex`, `claude`, `copilot`, `cursor`: the same semantic workflow when the host exposes equivalent read/write/command facilities. These are **structural targets**, not proven runtime behavior. A client without Agent Skills discovery may require documented manual invocation; do not claim installation or activation success without executing it there. VS Code, Visual Studio and PandaCode are distribution/client surfaces, not interchangeable agent runtimes.
