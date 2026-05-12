@skill-token-efficient

Refactor the target skill to reduce token usage while preserving behavior, activation accuracy, and human readability.

TARGET: @SKILL_TARGET
MODE: package
LEVEL: dense

Path context:
- Treat `TARGET` as the resolved path to the target skill package root.
- In Markdown documentation and reusable command examples, use `<target-skill-root>` as the placeholder for `TARGET`.
- Use `<skill-root>` only as a Markdown documentation placeholder for the current skill package root.
- Do not write `<skill-root>` or `<target-skill-root>` into YAML, JSON, scripts, configs, fixtures, or runtime artifacts. Use relative paths or resolved paths instead.

Goal:
- reduce token usage in `SKILL.md` and instruction/reference files
- keep the target skill semantically equivalent
- preserve clear human-readable instructions

Preserve:
- activation and non-activation boundaries
- scope and ownership
- modes and workflow order
- required inputs and defaults
- blocked paths
- tool, connector, filesystem, and command rules
- safety/compliance boundaries
- validation and packaging rules
- stop conditions
- output contract

Do not:
- remove behavior-critical rules to save tokens
- weaken safety, validation, stop, or output-contract requirements
- change the target skill’s ownership or domain
- use obscure abbreviations
- make instructions cryptic
- claim validation that was not executed

Execute:
1. Read the target `SKILL.md` first.
2. Run a baseline token audit.
3. Build a semantic invariant map.
4. Apply a conservative token-efficient refactor.
5. Validate local links, touched scripts, semantic invariants, and package gates.
6. Package the refactored target as `skill.zip`.

Return:
- link to the final `skill.zip`
- before/after estimated tokens
- reduction percentage
- files changed
- validation commands and outcomes
- residual risks
