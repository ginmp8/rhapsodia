@skill-booster

Optimize the target skill package using the full Skill Booster workflow.

TARGET_SKILL_PATH: @TARGET_SKILL

Path context:
- Treat `TARGET_SKILL_PATH` as the resolved path to the target skill package root.
- In Markdown documentation and reusable command examples, use `<target-skill-root>` as the placeholder for `TARGET_SKILL_PATH`.
- Do not write `<target-skill-root>` into YAML, JSON, scripts, configs, fixtures, or runtime artifacts. Use relative paths or the resolved target path instead.
- For scripts/resources inside the currently active skill package, use `<skill-root>` only as a Markdown documentation placeholder; runtime files must resolve the path or receive it explicitly.

Mode:
Full optimization. Do not stop at audit/plan unless blocked.

Goal:
Improve the target skill end to end: activation precision, workflow clarity, output contract, consistency, documentation, validation, security, hygiene, token efficiency, and packaging readiness.

Requirements:
- Use the full specialist sequence defined by skill-booster.
- Invoke available specialists when required by the workflow.
- Do not substitute available specialists with checklist-only review.
- Before finalizing, verify that the required specialist sequence was satisfied.
- If the full workflow cannot be completed, report what was completed, what was blocked, and do not claim full optimization.

Scope:
Only edit files inside the target skill package.
Package as skill.zip only if validation and package checks pass.
