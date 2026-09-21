---
name: prompt-architect
description: use when asked to create, rewrite, improve, review, validate, benchmark, harden, or package prompts, system prompts, chat modes, github copilot agent prompts, custom instructions, agent instructions, or reusable skill instructions. especially use for prompt engineering requests that require preserving user intent, resolving conflicting requirements, integrating sources, defining testable output contracts, adding examples, designing evaluation scenarios, or producing validation evidence. do not use merely to execute a task described by a prompt when the user is not asking to design or assess the prompt itself.
---

# Prompt Architect

Turn rough prompt ideas or existing prompt artifacts into bounded, testable prompt contracts. Preserve legitimate semantic freedom, but make activation, requirements, conflicts, output shape, validation claims, and repair decisions reproducible enough that repeated reviews are materially comparable.

## Reproducibility ceiling

Prompt design is a **constrained-subjective** task. Structure, requirement preservation, evidence handling, scenario shape, mechanical lint, and claim rules can be enforced. Wording quality, decomposition, and some trade-offs remain model judgment.

Do not claim byte-identical outputs, universal prompt quality, or behavioral improvement from static inspection alone.

## Activation contract

Activate for requests to:

- create a reusable prompt, system prompt, agent prompt, chat mode, custom instruction, or prompt template;
- improve, rewrite, harden, simplify, compress, or restructure an existing prompt;
- review or score prompt quality without executing the prompt's task;
- test or validate prompt behavior, activation, ambiguity, output compliance, or safety boundaries;
- build reusable prompt assets, scenario suites, or prompt specifications.

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

## Core invariants

Preserve these across all modes:

- user-provided goals, domain terminology, variables, constants, examples, language, required style, and explicit constraints unless higher-priority instructions or safety rules require otherwise;
- protected examples or quoted text exactly when the user marks them immutable;
- source-required semantics when the prompt is derived from authoritative documentation;
- safety, privacy, legal, compliance, evidence, and validation requirements;
- tool availability boundaries of the intended executor;
- output contracts that downstream consumers rely on.

Do not remove semantic content merely to shorten, beautify, or make a validator pass.

Do not expose hidden chain-of-thought. When the prompt needs visible reasoning, request concise rationale, evidence, checks, calculations, or decision criteria instead.

## Input normalization

Before producing a final prompt, resolve or explicitly mark assumptions for:

1. target prompt or task idea;
2. intended executor/model/agent;
3. available inputs and context;
4. tools, connectors, repositories, files, or web access;
5. output format, language, length, syntax, and citation rules;
6. constraints, prohibited behavior, safety boundaries, and stop conditions;
7. success criteria and validation method;
8. compatibility commitments, protected regions, and examples that must not change.

Ask one focused question only when a missing fact changes purpose, authority, tool access, safety, or the output contract. Otherwise proceed with labeled assumptions.

For complex work, build a requirement ledger using [prompt-contract.md](references/prompt-contract.md). Distinguish `explicit`, `source-required`, `inferred`, and `optional` requirements, and mark protected items as immutable.

## Workflow

### 1. Establish target identity and baseline

For `improve`, `review-only`, and `validation-only`:

- identify the exact target prompt/version;
- preserve an immutable baseline copy or source snapshot before material rewriting;
- preserve the original before rewriting;
- record protected regions and compatibility commitments;
- if behavioral comparison will be claimed, freeze the scenarios/evaluator **before** editing the prompt.

A scenario suite authored after seeing candidate failures may be useful for regression coverage, but it cannot retroactively prove the original improvement claim. Any **baseline vs candidate** comparison must use the same frozen evaluation basis.

### 2. Collect sources and provenance

Use user-provided files, docs, URLs, repositories, and examples as primary evidence. Load [source-integration.md](references/source-integration.md) when external or multiple sources affect the prompt.

Record which requirements come from which sources. When sources conflict, apply the authority rules in that reference rather than silently blending them.

Do not copy source text wholesale when concise prompt rules are sufficient. Do not fabricate unavailable source requirements or citations.

### 3. Audit before rewriting

Audit in execution order:

`objective -> audience/executor -> inputs -> authority/conflicts -> tools/sources -> workflow -> output contract -> examples -> safety/privacy -> validation readiness`

Use [prompt-quality-rubric.md](references/prompt-quality-rubric.md) for complex rewrites or `review-only` mode.

Separate:

- **observation**: directly present in the prompt/source;
- **inference**: likely intent not explicitly stated;
- **recommendation**: proposed design choice;
- **blocking conflict**: cannot be resolved without authority or clarification.

### 4. Design or revise with bounded freedom

Use [prompt-architecture-workflow.md](references/prompt-architecture-workflow.md).

Prefer this canonical order when sections are needed:

`task -> context -> inputs/assumptions -> workflow -> tool/source rules -> constraints -> output contract -> examples -> edge cases/stop conditions`

Omit sections that add no execution value. Preserve an existing governed structure when changing it would create compatibility risk without fixing a concrete defect.

Use imperative, testable instructions. Define defaults and tie-breakers where repeated interpretations would otherwise diverge.

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

Bundled deterministic helpers: [prompt_lint.py](scripts/prompt_lint.py), [validate_prompt_contract.py](scripts/validate_prompt_contract.py), and [validate_scenario_suite.py](scripts/validate_scenario_suite.py).

These checks prove only the properties they inspect. A lint pass is not a behavioral benchmark.

### 6. Validate with frozen scenarios

Load [validation-scenarios.md](references/validation-scenarios.md).

Use the same scenarios for baseline and candidate when making a comparison. Include the smallest set that covers the material risk: core, boundary, ambiguity, conflict, regression, adversarial, or runtime/tool behavior.

Keep authoring scenarios separate from genuine holdouts. A scenario bundled with the skill is visible to the authoring process and therefore is not a true holdout by itself.

### 7. Repair by diagnosis

For each material failure:

1. identify the exact scenario/criterion that failed;
2. identify one causal prompt defect;
3. apply the smallest change that addresses that defect;
4. rerun the same check/scenario;
5. then run adjacent regression checks.

Stop after three validation cycles, or earlier after two consecutive cycles without improvement on the same material defect set. Report unresolved defects instead of random-searching wording.

Never weaken safety, evidence, required semantics, frozen scenarios, or acceptance criteria merely to obtain a pass.

### 8. Freeze after pass

Once the declared checks pass, the **frozen candidate** must not receive unvalidated semantic edits. Any later semantic edit invalidates the affected validation evidence and requires rerunning the relevant checks.

For reusable files, package only the frozen bytes. Use **atomic delivery** where possible: canonicalize output destinations first, reject any output alias with the input skill tree or sibling outputs, stage/validate before replacement, preserve the **last-good** artifact, and rollback on a failed multi-output commit. Emit a durable receipt tied to the committed bytes with SHA-256 when packaging is material evidence.

## Evidence and claim rules

Use [evidence-and-claims.md](references/evidence-and-claims.md) whenever validation or comparison claims are material. Keep structural, behavioral, runtime, and perceptual evidence separate; never upgrade a weaker evidence layer into a stronger claim.

## Output contracts

### `create` / `improve`

Default shape when the user does not request prompt-only output:

1. **Prompt** — complete copy-ready prompt.
2. **Change ledger** — only material additions/removals/behavior changes; omit for new prompts when unnecessary.
3. **Validation** — scenarios/checks actually run, evidence labels, result, and residual risks.
4. **Assumptions/conflicts** — only unresolved items that materially affect execution.

If the user requests only the final prompt, return only the final prompt after performing any feasible checks privately.

### `review-only`

1. **Findings** — severity, location/subject, evidence, impact, recommended fix.
2. **Rubric** — versioned criteria from [prompt-quality-rubric.md](references/prompt-quality-rubric.md).
3. **Critical gates** — pass/fail/blocked.
4. **Rewrite strategy** — bounded plan only; do not rewrite unless requested.

Do not report a synthetic overall score unless the user explicitly asks for one and the rubric defines how to calculate it.

### `validation-only`

1. **Target identity**.
2. **Scenario/evaluator identity and freeze state**.
3. **Results by scenario**.
4. **Defects with stable severity**.
5. **Evidence label**.
6. **Verdict**: `pass`, `pass-with-reservations`, `fail`, or `blocked`.

### `package-guidance`

Return only the reusable assets needed: prompt contract/spec, templates, scenarios, and validation instructions. Keep package-specific host adapters optional unless the user requests one.

## Progressive references

Load only what the active mode needs:

- [prompt-architecture-workflow.md](references/prompt-architecture-workflow.md): requirement ledger, rewrite patterns, conflict resolution, and deterministic defaults.
- [prompt-contract.md](references/prompt-contract.md): machine-readable contract semantics and protected requirements.
- [prompt-quality-rubric.md](references/prompt-quality-rubric.md): versioned review rubric, critical gates, scoring anchors, and severities.
- [source-integration.md](references/source-integration.md): source hierarchy, provenance, conflicts, and citation/evidence rules.
- [validation-scenarios.md](references/validation-scenarios.md): frozen scenario design, defect taxonomy, claim boundaries, and repair loop.
- [assets/templates/final-prompt.md.template](assets/templates/final-prompt.md.template): default prompt skeleton.
- [assets/templates/prompt-contract.json.template](assets/templates/prompt-contract.json.template): reusable contract scaffold.
- [assets/templates/prompt-review-report.md.template](assets/templates/prompt-review-report.md.template): review report scaffold.
- [assets/templates/scenario-suite.json.template](assets/templates/scenario-suite.json.template): scenario suite scaffold.
- [evals/activation-scenarios.json](evals/activation-scenarios.json): canonical v2 host-neutral activation/regression suite; planned until actually executed. It intentionally carries the shared fields required by the current Harness and Prompt/Activation Review validators.
- [examples/prompt-architect-scenarios.md](examples/prompt-architect-scenarios.md): human-readable usage examples.

## Portability

Keep the core host-neutral. Do not make prompt semantics depend on ChatGPT, Claude, GitHub Copilot, Cursor, or another host unless the user targets that host explicitly.

Treat [`agents/openai.yaml`](agents/openai.yaml) as an optional OpenAI adapter; it may reference the optional UI asset [`assets/icon.svg`](assets/icon.svg). The portable core targets the common Agent Skills package model and must remain usable on OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, and Cursor when the host provides the capabilities required by the selected mode. For host-specific prompts, isolate host-specific tool names, file conventions, and invocation rules in clearly labeled sections so the semantic core remains portable when possible.

Before claiming package readiness, run [`scripts/validate_skill.py`](scripts/validate_skill.py) and the applicable portability validator. Packaging uses [`scripts/package_skill.py`](scripts/package_skill.py), which invokes the target validator before committing the archive.

## Stop conditions

Stop or return a bounded partial result when:

- the target prompt/artifact is required but unavailable;
- authority between conflicting requirements cannot be determined safely;
- required source material is inaccessible and guessing would change semantics;
- the requested rewrite would remove protected safety, compliance, privacy, evidence, or compatibility constraints;
- the only way to pass validation is to edit frozen scenarios/evaluators or weaken acceptance criteria;
- a measured benchmark is requested but no executable evaluator/harness is available;
- the intended executor's tool capabilities are unknown and materially change prompt behavior;
- requested hidden chain-of-thought disclosure is essential to the proposed design.
