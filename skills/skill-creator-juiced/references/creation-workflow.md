# Creation Workflow

Use this workflow for net-new skills and major redesigns.

## Phase 1: Intake

Capture only what is needed to design the package:

- target skill name or proposed name;
- concrete user prompts that should activate the skill;
- prompts that should not activate it;
- expected inputs and outputs;
- required language, tone, formatting, and citation rules;
- tools, connectors, files, repositories, scripts, or assets the skill may use;
- examples of correct and incorrect output;
- constraints, blocked paths, safety boundaries, and validation expectations.

If examples are missing but the request is clear, proceed with assumptions and create planned scenarios. Ask only when missing details change ownership, tools, safety, or output format.

## Phase 2: Capability boundary

Decide whether the target is:

- one focused skill;
- one skill with modes;
- a router skill;
- multiple skills;
- a prompt or documentation asset rather than a skill.

Use `../references/design-principles.md` for the decision. Record the decision in the final response.

## Phase 3: Package architecture

Design the package before writing long content:

- `SKILL.md`: compact control plane;
- `references/`: detailed rules, rubrics, schemas, templates in markdown, workflow branches;
- `scripts/`: deterministic helpers, validators, converters, report generators;
- `assets/`: output templates, icons, boilerplate, static files;
- `examples/`: human-readable calibration cases;
- `evals/`: planned scenario suites or machine-readable cases;
- `../agents/openai.yaml`: user-facing display metadata.

Avoid deep reference chains. Every important reference should be directly linked from `SKILL.md` or from a clearly declared branch reference.

## Phase 4: Draft the package

Write in this order:

1. frontmatter name and description;
2. mission and core rules;
3. workflow decision tree or mode router;
4. resource loading map;
5. output contract;
6. stop conditions;
7. branch references and templates;
8. scripts and validators;
9. examples and evals.

Keep instructions imperative and specific. Remove obvious background.

## Phase 5: Specialist quality passes

Apply the routing in `../references/specialist-orchestration.md`. Use lighter static review for low-risk skills and full juiced review for high-impact or requested production-ready packages. For redesigns or quality-upgrade work with multiple possible improvement directions, no supplied bounded hypothesis, saturated evidence, or unclear next experiment, run `skill-hypothesis-discovery` or apply its checklist to produce a prioritized, non-mutating hypothesis backlog before invoking `skill-improver`. For existing-skill updates, redesigns, hardening candidates, cleanup candidates, and token-efficiency candidates, run `skill-change-gate` or apply its checklist before accepting the candidate. For net-new skills without before/after evidence, use `skill-change-gate` only as an advisory final gate or mark it not-applicable with rationale.

## Phase 6: Validate and package

Run local gates where available:

```bash
python ../scripts/juiced_quality_gate.py <target-skill-folder>
python ../scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --validate
```

Also run platform or package validators when available. If bundling scripts, run at least a representative smoke test. For redesign or quality-upgrade work, include the `skill-hypothesis-discovery` result or not-applicable rationale when it influenced the selected improvement path. For modified existing skills, include a `skill-change-gate` decision or checklist result in the validation evidence before packaging.

Package only after validation passes. The final archive should be named `skill.zip`. Exclude caches, generated reports, old packages, secrets, credentials, and blocked paths.

## Phase 7: Report

Report what is factual from commands separately from design judgment. State assumptions, skipped gates, `skill-hypothesis-discovery` status when applicable, `skill-change-gate` status when applicable, and next quality pass if any.
