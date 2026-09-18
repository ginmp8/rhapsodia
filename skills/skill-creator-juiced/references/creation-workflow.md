# Creation Workflow

Use this workflow for net-new skills, updates, portability work, and major redesigns. Enter at the target's current lifecycle state rather than restarting completed work.

## Phase 1: Lifecycle, context, identity, baseline, and capabilities

First classify the current state: `raw-idea`, `requirements-known`, `draft`, `existing-skill`, `candidate-under-evaluation`, or `validated-candidate`. Start at the earliest unresolved stage.

Harvest established context from the conversation and supplied artifacts before asking questions: prompts, corrections, rejected approaches, workflow order, selected tools, expected inputs/outputs, constraints, examples, terminology, target hosts, and acceptance criteria. Ask only for missing facts that materially change semantics, authority, safety, or acceptance.

Capture only what changes execution:

- target skill identity and writable root;
- concrete prompts that should and should not activate it;
- expected inputs and outputs;
- required evidence, tools, files, repositories, scripts, or assets;
- target hosts or portability expectation;
- runtime capabilities: filesystem read/write, command execution, Python or other runtimes, network, connectors, subagents, browser, artifact delivery;
- blocked paths, secrets, fixtures, expected outputs, evaluator assets, and validation expectations.

For an existing skill, preserve an immutable baseline snapshot or equivalent before material edits. Run target-owned validators first when possible and record failures before repair. For a net-new skill, use `without-skill` as the behavioral baseline when the execution environment makes that comparison meaningful. If a valid baseline cannot run, record `not-run` and do not claim measured improvement.

## Phase 2: Capability boundary

Decide whether the target should remain:

- one focused skill;
- one skill with modes;
- a router skill;
- multiple skills;
- a prompt or documentation asset rather than a skill.

Use `design-principles.md`. Preserve one skill across hosts when the operational responsibility is the same. Do not fork by vendor without a semantic reason.

## Phase 3: Portable package architecture

Design the host-neutral core first. During this phase also read `reproducibility-by-design.md` and classify the skill's reproducibility ceiling before selecting deterministic resources:

- `SKILL.md`: compact control plane and Agent Skills frontmatter;
- `references/`: detailed rules, contracts, schemas, host notes, workflow branches;
- `scripts/`: deterministic helpers, validators, converters, report generators;
- `assets/`: output templates and static resources;
- `examples/`: human-readable calibration cases;
- `evals/`: planned or executable scenarios;
- `agents/openai.yaml`: optional OpenAI adapter, not portable core.

Read `host-portability.md` when more than one host is requested or host behavior is material. Keep install paths outside the semantic contract. For evidence-driven or mutating skills, decide now whether exact source snapshots, immutable VCS provenance, canonical output preflight, recovery-aware delivery, or durable receipts are justified; do not bolt them on only after failures.

## Phase 4: Draft or update and define evaluation

Write in this order:

1. frontmatter name and activation description;
2. mission, scope, modes, defaults, and authority boundaries;
3. workflow/router and progressive resource map;
4. output/evidence contract and stop conditions;
5. branch references, schemas, templates, and adapters;
6. deterministic scripts and validators;
7. examples and evals.

For existing skills, make the smallest coherent update that satisfies the requested capability. Preserve unrelated behavior.

Apply the local `reproducibility-by-design.md` checklist before specialist routing. Record material variance as mechanical, constrained heuristic, model judgment, or external nondeterminism. Move only objective/fragile behavior downward; preserve judgment where it is the point of the skill.

Read `evaluation-and-generalization.md` when behavioral quality matters. Define a small realistic seed set and the evaluator type appropriate to each property. Keep objective assertions for objectively checkable behavior and use independent/human/perceptual review for subjective properties. Do not force subjective quality into artificial numeric checks.

## Phase 5: Reproducibility decision

Apply `reproducibility-routing.md` after architecture, activation boundaries, and the local reproducibility-by-design pass are understood.

- Ordinary net-new text skills can remain specialist `not-applicable` when the local design pass finds no material gap.
- Objective-artifact, tool-action, repository-evidence, benchmark, and package-building skills should be re-evaluated after drafting, especially for source identity, output aliases, receipts, and recovery.
- Existing skills with material uncontrolled variance should use the appropriate `reproducibility-engineer` mode.
- Record why the specialist was invoked, skipped, unavailable, checklist-only, or cycle-prevented.

Do not require reproducibility machinery when it does not remove a real source of variance.

## Phase 6: Specialist passes

Apply `specialist-orchestration.md`. Use the smallest set that owns real risk.

For redesign or quality-upgrade work with several possible directions, use `skill-hypothesis-discovery` before measured optimization. For modified existing skills, use `skill-change-gate` before accepting the final candidate.

## Phase 7: Evaluate and generalize

When behavioral execution is available:

1. run the candidate and the correct baseline on equivalent prompts/files;
2. keep evaluator rules identical across comparison arms;
3. inspect outputs and, when available, execution traces for waste, repeated work, inconsistent routing, and hidden host assumptions;
4. classify each failure as a general failure class before proposing a fix;
5. reject changes that key on exact eval wording, filenames, fixtures, or one-off examples;
6. after the candidate stabilizes, run held-out cases that did not influence the change;
7. repeat stochastic activation/behavior scenarios when a stability claim depends on more than one run.

For activation tuning, use difficult near-misses and adjacent-domain negatives, not trivial irrelevant prompts. For subjective outputs, prefer blind or independent review where practical.

If independent runs repeatedly reinvent the same deterministic helper, stable knowledge lookup, template, or decision heuristic, consider promoting it to `scripts/`, `references/`, `assets/`, or a focused instruction respectively. Do not extract incidental one-off work.

## Phase 8: Diagnostic repair

When a gate or evaluator fails:

1. run or inspect the narrowest failing gate;
2. identify one causal subject;
3. apply the smallest generalizable repair;
4. rerun the same gate;
5. only then run adjacent gates.

If two consecutive repair rounds do not improve the best objective diagnostic count or reviewer outcome, stop that repair branch and report the unresolved issue. Never lower a threshold, weaken semantics/safety, or modify a frozen evaluator to force a pass.

## Phase 9: Validate

When command execution is available:

```text
<PYTHON> scripts/validate_portability.py <target-skill-folder> --profile portable
<PYTHON> scripts/juiced_quality_gate.py <target-skill-folder> --profile portable
<PYTHON> scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --profile portable --validate --json-output <output-dir>/package-receipt.json
```

Use the target skill's own scripts when working on another skill; paths above are conceptual relative to this skill package. Resolve `<PYTHON>` by capability rather than executable name.

Also run target-owned tests/validators and representative smoke tests for changed scripts. Use host-specific runtime validation only when the host is available; otherwise mark it `not-run`.

## Phase 10: Acceptance, freeze, and package

For material changes to an existing skill, obtain a `skill-change-gate` decision or apply its checklist. Blocking regressions prevent acceptance.

Before accepting a behavioral improvement, verify that the supporting evidence used the correct baseline and that the fix generalizes beyond the examples that motivated it. A static or structural pass alone does not establish behavioral improvement.

After all applicable hard gates pass, freeze the candidate. Do not make cleanup or cosmetic edits afterward without rerunning affected validation.

Package atomically. Preflight both authored and resolved output/receipt destinations, reject aliases with the target or each other, validate staged bytes before commit, and preserve the last-known-good package/receipt on failure. The package receipt should identify the exact archive hash, source identity, profile, and commit stage. If rollback is incomplete, preserve and report recovery paths instead of deleting evidence.

## Phase 11: Report

Separate:

- structural evidence;
- behavioral evidence;
- runtime evidence;
- perceptual/editorial evidence;
- efficiency evidence such as tokens, duration, or tool-call count when measured.

Report lifecycle entry state, harvested assumptions, baseline choice, host support, specialist statuses, reproducibility routing, commands, package hash, residual risks, and not-run gates without inflating evidence.
