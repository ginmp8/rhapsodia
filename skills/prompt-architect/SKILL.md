---
name: prompt-architect
description: use when asked to create, rewrite, improve, review, validate, benchmark, harden, or package prompts, system prompts, chat modes, github copilot agent prompts, custom instructions, agent instructions, or reusable skill instructions. especially use for prompt engineering requests that require preserving user intent, choosing the correct control lever, resolving conflicting requirements, integrating sources, defining execution profiles and testable output contracts, separating prompt guidance from runtime enforcement, designing evaluation scenarios, or producing validation evidence. do not use merely to execute a task described by a prompt when the user is not asking to design or assess the prompt itself.
---

# Prompt Architect

Turn rough prompt ideas or existing prompt artifacts into bounded, testable behavioral contracts. Preserve legitimate semantic freedom, but make activation, requirements, conflicts, execution assumptions, output shape, enforcement, validation claims, and repair decisions reproducible enough that repeated reviews are materially comparable.

Treat the reusable semantic contract as the source of truth. Render or adapt that contract to the intended executor only after the execution profile is known well enough to justify host/model-specific guidance.

## Reproducibility ceiling

Prompt design is a **constrained-subjective** task. Structure, requirement preservation, evidence handling, scenario shape, execution-profile identity, mechanical lint, and claim rules can be enforced. Wording quality, decomposition, and some trade-offs remain model judgment.

Do not claim byte-identical outputs, universal prompt quality, universal prompting techniques, or behavioral improvement from static inspection alone.

## Activation contract

Activate for requests to:

- create a reusable prompt, system prompt, agent prompt, chat mode, custom instruction, or prompt template;
- improve, rewrite, harden, simplify, compress, or restructure an existing prompt;
- review or score prompt quality without executing the prompt's task;
- test or validate prompt behavior, activation, ambiguity, output compliance, runtime assumptions, or safety boundaries;
- build reusable prompt assets, prompt contracts, scenario suites, execution profiles, or prompt specifications.

Do **not** activate merely because a prompt is present when the user asks to execute, summarize, translate, or extract information from it.

When intent is ambiguous, prefer the user's explicit verb. If the target artifact itself is missing and cannot be recovered from context, ask for that artifact rather than inventing it.

## Modes and routing

Choose exactly one primary mode before drafting:

| Mode | Trigger | Primary output |
|---|---|---|
| `create` | create a new prompt from a task or idea | final prompt + optional design/validation notes |
| `improve` | modify an existing prompt | revised prompt + change ledger + validation evidence |
| `review-only` | evaluate without rewriting | findings + rubric + prioritized fixes |
| `validation-only` | test an existing prompt | scenario results + defects + evidence label |
| `package-guidance` | build reusable prompt assets | prompt spec/templates/scenarios |

Routing precedence when multiple intents appear:

1. obey explicit prohibitions such as "review only" or "do not rewrite";
2. if the user requests both rewrite and validation, use `improve` and include validation;
3. if the user requests only execution of the prompt's task, do not enter prompt-design mode;
4. otherwise choose the narrowest mode that satisfies the request.

Never silently switch modes after evidence collection. If a later requirement changes the mode materially, state the switch and why.

## Right-lever gate

Before changing prompt text, identify the smallest control layer that can actually change the failing criterion:

`prompt -> model/configuration -> context/retrieval -> native schema/tool contract -> application/runtime control -> fine-tuning -> architecture`

Use `prompt` or `mixed` only when prompt behavior is genuinely part of the solution. If the requested outcome depends mainly on another layer, say so and either route the work there or limit Prompt Architect to the prompt-controlled portion.

Do not claim that prompt text can enforce authorization, isolation, transactional side effects, secret handling, or other runtime guarantees that require application/runtime controls.

## Core invariants

Preserve these across all modes:

- user-provided goals, domain terminology, variables, constants, examples, language, required style, and explicit constraints unless higher-priority instructions or safety rules require otherwise;
- protected examples or quoted text exactly when the user marks them immutable;
- source-required semantics when the prompt is derived from authoritative documentation;
- safety, privacy, legal, compliance, evidence, and validation requirements;
- tool availability and execution boundaries of the intended executor;
- output contracts that downstream consumers rely on;
- a host-neutral semantic core unless the user explicitly requests a host-specific artifact.

Do not remove semantic content merely to shorten, beautify, or make a validator pass.

Do not expose hidden chain-of-thought. When the prompt needs visible reasoning, request concise rationale, evidence, checks, calculations, or decision criteria instead.

## Input normalization

Before producing a final prompt, resolve or explicitly mark assumptions for:

1. target prompt or task idea;
2. success criteria and the right solution lever;
3. intended logical executor plus material provider/host/model/version or capability profile;
4. runtime instruction surfaces and data-trust boundaries;
5. available inputs, stable/dynamic/untrusted context, and context budget/overflow behavior;
6. tools, connectors, repositories, files, schemas, or web access;
7. which requirements are prompt-controlled versus enforced by native schema, tool contract, application, approval, or evaluator;
8. output format, language, length, syntax, and citation rules;
9. constraints, prohibited behavior, safety boundaries, and stop conditions;
10. validation method, evaluator identity, comparison policy, and claim level;
11. compatibility commitments, protected regions, and examples that must not change.

Ask one focused question only when a missing fact changes purpose, authority, tool access, safety, enforcement, or the output contract. Otherwise proceed with labeled assumptions.

For complex work, build a requirement ledger using [prompt-contract.md](references/prompt-contract.md). Distinguish `explicit`, `source-required`, `inferred`, and `optional` requirements, and mark protected items as immutable.

## Workflow

### 1. Establish target, baseline, and execution profile

For `improve`, `review-only`, and `validation-only`:

- identify the exact target prompt/version;
- preserve an immutable baseline copy or source snapshot before material rewriting;
- preserve the original before rewriting;
- record protected regions and compatibility commitments;
- record the material execution profile or capability profile when behavior depends on it;
- if behavioral comparison will be claimed, freeze the scenarios/evaluator **before** editing the prompt.

A scenario suite authored after seeing candidate failures may be useful for regression coverage, but it cannot retroactively prove the original improvement claim. Any **baseline vs candidate** comparison must use the same frozen evaluation basis and a materially comparable execution profile.

### 2. Collect sources and provenance

Use user-provided files, docs, URLs, repositories, and examples as primary evidence. Load [source-integration.md](references/source-integration.md) when external or multiple sources affect the prompt.

Record which requirements come from which sources. When sources conflict, apply the authority rules in that reference rather than silently blending them.

Do not copy source text wholesale when concise prompt rules are sufficient. Do not fabricate unavailable source requirements or citations.

### 3. Audit before rewriting

Audit in execution order:

`success criterion/right lever -> objective -> executor/profile -> inputs/context -> design authority -> runtime authority/trust -> tools/sources -> enforcement -> workflow -> output contract -> examples -> safety/privacy -> validation readiness`

Use [prompt-quality-rubric.md](references/prompt-quality-rubric.md) for complex rewrites or `review-only` mode.

Separate:

- **observation**: directly present in the prompt/source;
- **inference**: likely intent not explicitly stated;
- **recommendation**: proposed design choice;
- **blocking conflict**: cannot be resolved without authority or clarification.

### 4. Design the semantic contract, then render for the executor

Use [prompt-architecture-workflow.md](references/prompt-architecture-workflow.md).

For complex or reusable prompts, work in this order:

`semantic requirements -> execution profile -> authority/trust -> context contract -> enforcement map -> rendered prompt/runtime controls -> evaluation contract`

Load [runtime-contract.md](references/runtime-contract.md) when provider/host/model identity, instruction authority, tool schemas, or runtime controls matter. Load [context-engineering.md](references/context-engineering.md) for long/dynamic/untrusted context. Load [environment-provenance.md](references/environment-provenance.md) when runtime identity can affect paired comparison evidence. Load [host-adapters.md](references/host-adapters.md) only when host-specific instruction surfaces or prompting behavior matter.

Prefer this rendered-prompt order when sections are needed:

`task -> context -> inputs/assumptions -> workflow -> tool/source rules -> constraints -> output contract -> examples -> edge cases/stop conditions`

Omit sections that add no execution value. Preserve an existing governed structure when changing it would create compatibility risk without fixing a concrete defect.

Use imperative, testable instructions. Define defaults and tie-breakers where repeated interpretations would otherwise diverge. Treat XML, few-shot examples, roles, self-check instructions, chain decomposition, context placement, and similar techniques as conditional strategies, not universal defaults.

### 5. Apply deterministic checks where available

Resolve `<PYTHON>` to an available Python 3.10+ launcher for the current host; do not assume the executable is named `python` or `python3`. Bundled helpers use only the standard library, and sibling script calls must use the active interpreter. If process execution or Python is unavailable, mark deterministic gates `blocked` rather than fabricating a pass.

When the prompt is available as a file, run:

```text
<PYTHON> scripts/prompt_lint.py <PROMPT_FILE> --json --require-output-format --require-success-criteria
```

For a reusable prompt contract:

```text
<PYTHON> scripts/validate_prompt_contract.py <CONTRACT_JSON>
```

For scenario assets:

```text
<PYTHON> scripts/validate_scenario_suite.py <SCENARIO_JSON>
```

When runtime identity is material to a comparison:

```text
<PYTHON> scripts/validate_execution_environment.py <ENVIRONMENT_JSON>
<PYTHON> scripts/validate_execution_environment.py <BASELINE_ENVIRONMENT_JSON> --compare <CANDIDATE_ENVIRONMENT_JSON>
```

Bundled deterministic helpers: [prompt_lint.py](scripts/prompt_lint.py), [validate_prompt_contract.py](scripts/validate_prompt_contract.py), [validate_scenario_suite.py](scripts/validate_scenario_suite.py), and [validate_execution_environment.py](scripts/validate_execution_environment.py).

These checks prove only the properties they inspect. A lint pass is not a behavioral benchmark.

### 6. Validate with frozen scenarios and evaluator identity

Load [validation-scenarios.md](references/validation-scenarios.md) and [evaluation-integrity.md](references/evaluation-integrity.md) when comparison claims are material.

Use the same scenarios for baseline and candidate when making a comparison. Include the smallest set that covers the material risk: core, boundary, ambiguity, conflict, regression, adversarial, long-context, execution-profile, or runtime/tool behavior. When provider/model/tool/runtime identity can materially affect a paired result, capture and compare the execution-environment profile; environment drift makes the pair `not-comparable` until rerun or explicitly re-baselined.

Keep authoring scenarios separate from genuine holdouts. A scenario bundled with the skill is visible to the authoring process and therefore is not a true holdout by itself.

When an LLM judge decides a comparative claim, control material evaluator bias with fixed evaluator identity and, when warranted, candidate blinding, position swap, repeated trials, and explicit ties. Do not force those controls for non-comparative or deterministic checks where they add no value.

### 7. Repair by diagnosis

For each material failure:

1. identify the exact scenario/criterion that failed;
2. identify one causal prompt/contract defect;
3. apply the smallest change that addresses that defect;
4. rerun the same check/scenario;
5. then run adjacent regression checks.

Stop after three validation cycles, or earlier after two consecutive cycles without improvement on the same material defect set. Report unresolved defects instead of random-searching wording.

Never weaken safety, evidence, required semantics, frozen scenarios, execution-profile identity, or acceptance criteria merely to obtain a pass.

### 8. Freeze after pass

Once the declared checks pass, the **frozen candidate** must not receive unvalidated semantic edits. Any later semantic edit invalidates the affected validation evidence and requires rerunning the relevant checks.

A material change in provider, host, model/snapshot, instruction surface, tool/schema contract, or other execution-profile identity invalidates behavioral/runtime evidence that depends on that identity. Revalidate or explicitly limit the claim; do not silently reuse stale evidence.

For reusable files, package only the frozen bytes. Use **atomic delivery** where possible: canonicalize output destinations first, reject any output alias with the input skill tree or sibling outputs, stage/validate before replacement, preserve the **last-good** artifact, and rollback on a failed multi-output commit. Emit a durable receipt tied to the committed bytes with SHA-256 when packaging is material evidence.

## Optional optimizer-assisted strategy

Optimizer-assisted prompt search is a strategy, not a primary mode. Use it only when:

- the success metric and evaluator are frozen before search;
- the search budget and stop rule are bounded;
- training/development cases are separated from genuine holdouts when overfitting risk matters;
- every candidate preserves protected semantics and hard gates;
- the canonical direct/single-candidate path remains available.

Never treat optimizer output as self-validating or as permission to weaken the evaluator.

## Evidence and claim rules

Use [evidence-and-claims.md](references/evidence-and-claims.md) whenever validation or comparison claims are material. Keep structural, behavioral, runtime, and perceptual evidence separate; never upgrade a weaker evidence layer into a stronger claim. Bind behavioral/runtime claims to the relevant execution-profile identity.

## Output contracts

### `create` / `improve`

Default shape when the user does not request prompt-only output:

1. **Prompt** - complete copy-ready prompt.
2. **Change ledger** - only material additions/removals/behavior changes; omit for new prompts when unnecessary.
3. **Validation** - scenarios/checks actually run, evidence labels, execution profile, result, and residual risks.
4. **Assumptions/conflicts** - only unresolved items that materially affect execution.

If the user requests only the final prompt, return only the final prompt after performing any feasible checks privately.

### `review-only`

1. **Findings** - severity, location/subject, evidence, impact, recommended fix.
2. **Rubric** - versioned criteria from [prompt-quality-rubric.md](references/prompt-quality-rubric.md).
3. **Critical gates** - pass/fail/blocked.
4. **Rewrite strategy** - bounded plan only; do not rewrite unless requested.

Do not report a synthetic overall score unless the user explicitly asks for one and the rubric defines how to calculate it.

### `validation-only`

1. **Target identity**.
2. **Execution-profile identity** when material.
3. **Scenario/evaluator identity and freeze state**.
4. **Results by scenario**.
5. **Defects with stable severity**.
6. **Evidence label**.
7. **Verdict**: `pass`, `pass-with-reservations`, `fail`, or `blocked`.

### `package-guidance`

Return only the reusable assets needed: prompt contract/spec, templates, scenarios, execution-profile assumptions, and validation instructions. Keep package-specific host adapters optional unless the user requests one.

## Progressive references

Load only what the active mode needs:

- [prompt-architecture-workflow.md](references/prompt-architecture-workflow.md): requirement ledger, right-lever gate, compile/render workflow, conflict resolution, and deterministic defaults.
- [prompt-contract.md](references/prompt-contract.md): machine-readable v2 contract semantics and protected requirements.
- [runtime-contract.md](references/runtime-contract.md): execution profile, authority/trust separation, enforcement layers, and drift invalidation.
- [environment-provenance.md](references/environment-provenance.md): conditional environment identity, provenance, comparability, and hermeticity vocabulary.
- [context-engineering.md](references/context-engineering.md): context classes, budget, placement, overflow, provenance, and long-context checks.
- [evaluation-integrity.md](references/evaluation-integrity.md): evaluator identity, comparison bias controls, repeated trials, holdouts, and optimizer-assisted search.
- [host-adapters.md](references/host-adapters.md): portable-core boundaries and capability-based host/model adaptation.
- [prompt-quality-rubric.md](references/prompt-quality-rubric.md): versioned review rubric, critical gates, scoring anchors, and severities.
- [source-integration.md](references/source-integration.md): source hierarchy, provenance, conflicts, and citation/evidence rules.
- [validation-scenarios.md](references/validation-scenarios.md): frozen scenario design, defect taxonomy, claim boundaries, and repair loop.
- [assets/templates/final-prompt.md.template](assets/templates/final-prompt.md.template): default rendered-prompt skeleton.
- [assets/templates/prompt-contract.json.template](assets/templates/prompt-contract.json.template): reusable v2 contract scaffold.
- [assets/templates/prompt-review-report.md.template](assets/templates/prompt-review-report.md.template): review report scaffold.
- [assets/templates/scenario-suite.json.template](assets/templates/scenario-suite.json.template): scenario suite scaffold.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): canonical v2 host-neutral activation/regression suite; planned until actually executed.
- [examples/prompt-architect-scenarios.md](examples/prompt-architect-scenarios.md): human-readable usage examples.

## Portability

Keep the semantic core host-neutral. Detect capabilities and instruction surfaces before specializing behavior; do not infer semantics from a host name alone. Load [host-adapters.md](references/host-adapters.md) when host-specific behavior matters.

Treat [`agents/openai.yaml`](agents/openai.yaml) as an optional OpenAI adapter; it may reference the optional UI asset [`assets/icon.svg`](assets/icon.svg). Ignoring that adapter must leave the core workflow usable. The portable core targets the common Agent Skills package model and must remain usable on OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, and Cursor when the host exposes the capabilities required by the selected mode.

For host-specific prompts, isolate tool names, instruction files, message-role semantics, context-placement guidance, and other vendor-specific behavior in the execution profile or clearly labeled adapter sections. Verify volatile host/model behavior against current authoritative documentation before making a strong runtime claim.

Before claiming package readiness, run [`scripts/validate_skill.py`](scripts/validate_skill.py) and the applicable portability validator. Packaging uses [`scripts/package_skill.py`](scripts/package_skill.py), which invokes the target validator before committing the archive.

## Stop conditions

Stop or return a bounded partial result when:

- the target prompt/artifact is required but unavailable;
- authority between conflicting requirements cannot be determined safely;
- required source material is inaccessible and guessing would change semantics;
- the requested rewrite would remove protected safety, compliance, privacy, evidence, or compatibility constraints;
- the requested guarantee requires runtime/application enforcement but only prompt text is available;
- the only way to pass validation is to edit frozen scenarios/evaluators or weaken acceptance criteria;
- a measured benchmark is requested but no executable evaluator/harness is available;
- the intended executor's tool capabilities, instruction surfaces, or execution profile are unknown and materially change prompt behavior;
- a behavioral/runtime claim depends on a changed execution profile that has not been revalidated;
- requested hidden chain-of-thought disclosure is essential to the proposed design.
