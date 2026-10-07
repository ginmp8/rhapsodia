# Creation Workflow

## At a Glance

- **Purpose:** Define the ordered end-to-end creation/redesign workflow from lifecycle/context intake and artifact selection through validation, freeze, canonical packaging, and reporting.
- **Load when:** Creating a net-new skill, materially redesigning one, or resuming a quality-upgrade at its earliest unresolved lifecycle stage.
- **Decision impact:** Enforces artifact selection before topology, capability/portability boundaries, evaluation and reproducibility decisions, specialist ownership, validation/acceptance, final freeze, and package/report integrity.

## Contents

- Phase 1: Lifecycle, context, origin, identity, baseline, and capabilities
- Phase 2: Artifact Selection Gate
- Phase 3: Skill capability boundary
- Phase 4: Portable package architecture
- Phase 5: Draft or update and define evaluation
- Phase 6: Reproducibility decision
- Phase 7: Specialist passes
- Phase 8: Evaluate and generalize
- Phase 9: Diagnostic repair
- Phase 10: Validate
- Phase 11: Acceptance, freeze, and canonical packaging
- Phase 12: Report


Use this workflow for net-new skills, updates, portability work, and major redesigns. Enter at the target's current lifecycle state rather than restarting completed work. When invoked by Skill Booster on an external skill, consume Booster's trust/intake evidence; Creator Juiced owns portability redesign, not quarantine/security intake.

## Phase 1: Lifecycle, context, origin, identity, baseline, and capabilities

First classify the current state: `raw-idea`, `requirements-known`, `draft`, `existing-skill`, `candidate-under-evaluation`, or `validated-candidate`. Start at the earliest unresolved stage.

Harvest established context from the conversation and supplied artifacts before asking questions: prompts, corrections, rejected approaches, workflow order, selected tools, expected inputs/outputs, constraints, examples, terminology, target runtimes/clients, and acceptance criteria. Ask only for missing facts that materially change semantics, authority, safety, or acceptance.

Classify creation origin using exactly one primary label:

- `extract-from-run`: repeated or successful real execution, corrections, or failure/recovery history are the strongest source;
- `synthesize-from-artifacts`: existing documents, schemas, runbooks, code, or other artifacts are the strongest source;
- `design-from-spec`: an explicit requirement/specification is the strongest source;
- `adapt-existing`: an existing skill package is the baseline being changed.

Record the strongest source and material evidence gaps. This is lightweight provenance, not a substitute for formal research traceability. When external research materially drives requirements, hand off source-to-finding-to-requirement/change accounting to the research-traceability owner instead of inventing a second matrix here.

Capture only what changes execution:

- target skill identity and writable root when the Artifact Selection Gate keeps the request in skill scope;
- concrete prompts that should and should not activate it;
- expected inputs and outputs;
- required evidence, tools, files, repositories, scripts, or assets;
- semantic/runtime profiles or portability expectation; portability work defaults to `portable-core,openai,codex,claude,copilot,cursor` unless explicitly narrowed;
- client/distribution surfaces only when discovery, installation, packaging, or publication matters;
- runtime capabilities: filesystem read/write, command execution, Python or other runtimes, network, connectors, subagents, browser, artifact delivery;
- blocked paths, secrets, fixtures, expected outputs, evaluator assets, and validation expectations.

For an existing skill, preserve an immutable baseline snapshot or equivalent before material edits. Run target-owned validators first when possible and record failures before repair. For a net-new skill, use `without-skill` as the behavioral baseline when the execution environment makes that comparison meaningful. If a valid baseline cannot run, record `not-run` and do not claim measured improvement.

## Phase 2: Artifact Selection Gate

Before designing `SKILL.md`, decide whether a skill is the correct customization primitive.

Prefer:

- always-on policy, coding convention, or persistent project behavior -> instructions/rules;
- task-specific reusable workflow or domain procedure loaded when relevant -> skill;
- specialist persona with distinct permissions, toolset, or context lifecycle -> custom agent;
- new live data/action capability -> tool or MCP/service integration;
- mandatory lifecycle enforcement, interception, or observability -> hook/policy/runtime mechanism;
- distribution bundle spanning several customization components -> plugin/package wrapper;
- one-off wording or non-operational reusable text -> prompt/document/template.

The gate is host-neutral: classify by behavior and lifecycle, not by whichever product label is most familiar. If the best artifact is not a skill, stop skill construction and hand off to the appropriate owner. Do not implement the other primitive inside Creator Juiced merely to keep the workflow moving.

If the result is `skill` or a package whose semantic core contains a skill, continue. Record the decision and rationale when it is not obvious.

## Phase 3: Skill capability boundary

For skill-scoped work, decide whether the target should remain:

- one focused skill;
- one skill with modes;
- a router skill;
- multiple skills.

Use `references/design-principles.md`. Preserve one skill across runtimes/clients when the operational responsibility is the same. Do not fork by vendor, IDE, or distribution surface without a semantic lifecycle reason.

## Phase 4: Portable package architecture

Design the host-neutral core first. During this phase also read `references/reproducibility-by-design.md` and classify the skill's reproducibility ceiling before selecting deterministic resources:

- `SKILL.md`: compact control plane and Agent Skills frontmatter;
- `references/`: detailed rules, contracts, schemas, host notes, workflow branches;
- `scripts/`: deterministic helpers, validators, converters, report generators;
- `assets/`: output templates and static resources;
- `examples/`: human-readable calibration cases;
- `evals/`: planned or executable scenarios;
- `agents/openai.yaml`: optional OpenAI adapter, not portable core.

Keep required workflow resources directly discoverable from `SKILL.md` or one declared root index. References should normally be one level deep from the control plane. A deeper chain is acceptable only for optional detail whose parent remains directly discoverable; do not hide required execution rules behind multi-hop references.

Read `references/host-portability.md` when more than one semantic profile is requested, a client/distribution surface is named, or host behavior is material. Keep semantic/runtime compatibility separate from client/distribution discovery. Keep install paths outside the semantic contract. For evidence-driven or mutating skills, decide now whether exact source snapshots, immutable VCS provenance, canonical output preflight, recovery-aware delivery, or durable receipts are justified; do not bolt them on only after failures.

Before substantial drafting, define a small realistic seed evaluation whenever the intended behavior can be exercised. For net-new skills, run or at least specify the `without-skill` baseline; for existing skills, use the immutable prior version. Freeze expected properties/evaluator rules before using observed failures to author extensive instructions. If runtime execution is unavailable, record the seed plan as `not-run` and limit claims accordingly.

## Phase 5: Draft or update and define evaluation

Write in this order:

1. standard frontmatter name and activation description;
2. mission, scope, modes, defaults, and authority boundaries;
3. workflow/router and progressive resource map;
4. output/evidence contract and stop conditions;
5. branch references, schemas, templates, and host adapters;
6. deterministic scripts and validators;
7. examples and evals.

For existing skills, make the smallest coherent update that satisfies the requested capability. Preserve unrelated behavior. For net-new or redesigned skills, require a proof-of-need for every substantial instruction, reference, script, asset, or adapter: explicit user requirement, observed baseline failure, domain/safety invariant, portability/security necessity, or previously validated regression. Remove resources justified only by imagined completeness.

Apply model-neutral minimality while drafting. For every non-invariant instruction, ask whether supported agents materially fail, drift, or violate the contract without it. Keep the instruction when evidence or a credible failure mode justifies it; otherwise omit it. Model- or host-specific workarounds require provenance/freshness and belong in an adapter or scoped host reference, not in the portable core.

Treat approximately 500 lines or 5,000 tokens in `SKILL.md` as a review threshold, not an automatic split rule. When the threshold is exceeded, first move branch-specific detail to direct references; preserve cohesion when one operational responsibility still explains the package.

Apply the local `references/reproducibility-by-design.md` checklist before specialist routing. Record material variance as mechanical, constrained heuristic, model judgment, or external nondeterminism. Move only objective/fragile behavior downward; preserve judgment where it is the point of the skill.

Read `references/evaluation-and-generalization.md` when behavioral quality matters. Refine the already-defined seed set rather than inventing the evaluator after seeing the candidate. Keep objective assertions for objectively checkable behavior and use independent/human/perceptual review for subjective properties. Add trace, catalog-pressure, model-capability, or judge-calibration arms only when the skill materially depends on them. Do not force subjective quality into artificial numeric checks.

## Phase 6: Reproducibility decision

Apply `references/reproducibility-routing.md` after architecture, activation boundaries, and the local reproducibility-by-design pass are understood.

- Ordinary net-new text skills can remain specialist `not-applicable` when the local design pass finds no material gap.
- Objective-artifact, tool-action, repository-evidence, benchmark, and package-building skills should be re-evaluated after drafting, especially for source identity, output aliases, receipts, and recovery.
- Existing skills with material uncontrolled variance should use the appropriate `reproducibility-engineer` mode.
- Environment-dependent mechanics, including optional parser/runtime dependencies that change accepted inputs or validation results, are reproducibility signals even when the package has a fallback.
- Record why the specialist was invoked, skipped, unavailable, checklist-only, or cycle-prevented.

Do not require reproducibility machinery when it does not remove a real source of variance.

## Phase 7: Specialist passes

Apply `references/specialist-orchestration.md`. Use the smallest set that owns real risk.

For redesign or quality-upgrade work with several possible directions, use `skill-hypothesis-discovery` before measured optimization. Demonstrated contract gaps with known corrections may remain direct repairs rather than being reframed as experiments. For modified existing skills, use `skill-change-gate` before accepting the final candidate.

## Phase 8: Evaluate and generalize

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

## Phase 9: Diagnostic repair

When a gate or evaluator fails:

1. run or inspect the narrowest failing gate;
2. identify one causal subject;
3. apply the smallest generalizable repair;
4. rerun the same gate;
5. only then run adjacent gates.

If two consecutive repair rounds do not improve the best objective diagnostic count or reviewer outcome, stop that repair branch and report the unresolved issue. Never lower a threshold, weaken semantics/safety, or modify a frozen evaluator to force a pass.

## Phase 10: Validate

When command execution is available:

```text
<PYTHON> scripts/validate_portability.py <target-skill-folder> --hosts portable-core,openai,codex,claude,copilot,cursor --surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor
<PYTHON> scripts/juiced_quality_gate.py <target-skill-folder> --profile portable --hosts portable-core,openai,codex,claude,copilot,cursor --surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor
<PYTHON> scripts/package_skill.py --target <target-skill-folder> --output <output-dir>/skill.zip --profile portable --validate --portability-hosts portable-core,openai,codex,claude,copilot,cursor --distribution-surfaces chatgpt,openai-api,codex,claude-code,copilot-vscode,copilot-visual-studio,cursor --json-output <output-dir>/package-receipt.json
```

Use the target skill's own scripts when working on another skill; paths above are conceptual relative to this skill package. Resolve `<PYTHON>` by capability rather than executable name.

Also run target-owned tests/validators and representative smoke tests for changed scripts. Runtime/profile validation and client/distribution-surface validation are separate evidence layers: static surface mapping never proves the IDE/client actually executed the skill.

## Phase 11: Acceptance, freeze, and canonical packaging

For material changes to an existing skill, obtain a `skill-change-gate` decision or apply its checklist. Blocking regressions prevent acceptance.

Before accepting a behavioral improvement, verify that the supporting evidence used the correct baseline and that the fix generalizes beyond the examples that motivated it. A static or structural pass alone does not establish behavioral improvement.

After all applicable hard gates pass, freeze the candidate. Do not make cleanup or cosmetic edits afterward without rerunning affected validation.

Build one canonical validated skill folder/archive. Distribution surfaces may add wrapper metadata, provenance, install/update guidance, or host adapters, but must not silently mutate the canonical semantic core. Record requested distribution surfaces separately from semantic/runtime profile results.

Package atomically. Preflight both authored and resolved output/receipt destinations, reject aliases with the target or each other, validate staged bytes before commit, and preserve the last-known-good package/receipt on failure. The package receipt should identify the exact archive hash, source identity, semantic profile set, requested distribution surfaces when supplied, and commit stage. If rollback is incomplete, preserve and report recovery paths instead of deleting evidence.

## Phase 12: Report

Separate:

- structural evidence;
- behavioral evidence;
- runtime evidence;
- client/distribution-surface evidence;
- perceptual/editorial evidence;
- efficiency evidence such as tokens, duration, or tool-call count when measured.

Report lifecycle entry state, creation origin, artifact-selection decision, harvested assumptions, baseline choice, semantic/runtime profile support, requested client/distribution surfaces, specialist statuses, reproducibility routing, commands, package hash, residual risks, and not-run gates without inflating evidence.
