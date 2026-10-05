---
name: reproducibility-engineer
description: Engineer reproducibility for exactly one existing Agent Skills-compatible skill when the goal is to reduce controllable run-to-run or cross-agent variance without changing the skill's ownership boundary. Use for bounded reproducibility audit, transformation, validation, or packaging. Do not use for general skill optimization, benchmark-only scoring, net-new skills, ordinary application code, or prompt-only rewrites; route those to skill-booster, skill-benchmark, or skill-creator-juiced as appropriate.
---

# Reproducibility Engineer

## At a Glance

- **Purpose:** Make one existing Agent Skills-compatible skill repeatedly satisfy the same semantic contract for materially equivalent inputs and environments, up to the target class's real reproducibility ceiling.
- **Use when:** Reproducibility, repeatability, or cross-agent consistency is an explicit objective, or Skill Booster has selected a bounded reproducibility transformation.
- **Do not use when:** The task is general skill optimization, benchmark-only scoring, net-new skill creation, ordinary application code, or prompt-only rewriting without a reproducibility objective.
- **Outcome:** Controllable variance is reduced with explicit contracts and gates; irreducible model, external, or subjective variance stays bounded and reported rather than disguised as determinism.

## Activation and Routing

Activate only when there is exactly one existing skill target, reproducibility materially affects the requested outcome, and the target's capability/ownership boundary can remain intact. Route general optimization to `skill-booster`, benchmark-only measurement to `skill-benchmark`, and net-new or ownership-changing design to `skill-creator-juiced`.

For a target that can modify itself, freeze controller, generation, evaluator, candidate, and last-known-good identities before mutation and load [`references/self-hosting-reproducibility.md`](references/self-hosting-reproducibility.md).

## Modes

| Mode | Use for | Mutation |
|---|---|---|
| `audit-only` | diagnose variance sources and the reproducibility ceiling | no |
| `plan-only` | define a bounded transformation contract and gates | no |
| `apply` | reduce observed controllable variance in the existing skill | yes |
| `validation-only` | verify an already-modified skill | no unless explicitly authorized |
| `package` | validate and build the final `skill.zip` | only repairs required by declared gates |

Default to `apply` only when the user explicitly asks to make the target reproducible/repeatable; otherwise select the narrowest mode that satisfies the request.

## Core Invariants

- Resolve exactly one target root and mutate only authorized target files.
- Preserve an immutable baseline before edits; snapshot material external source bytes before analysis when their identity affects a decision.
- Protect `.git`, secrets, credentials, user fixtures, expected outputs, golden baselines, frozen evaluators, generated baseline evidence, and unrelated repositories.
- Keep the portable Agent Skills core host-neutral; host adapters remain optional and capability detection takes precedence over host-name branching.
- Full `apply`, `validation-only`, and `package` evidence requires writable filesystem access and Python 3.10+ for bundled validators; otherwise mark those script gates `not-run` and do not claim they passed.
- Freeze evaluators before candidate mutation; evaluator drift invalidates the comparison and requires restart or explicit re-baselining.
- Trace legacy owners, consumers, compatibility commitments, migrations, tests, and validators before removing or transferring behavior.
- Never weaken semantics, safety, tests, evaluators, evidence, thresholds, or protected paths to manufacture reproducibility.
- Freeze the final passing candidate; any later edit invalidates affected evidence and requires revalidation.
- Package only frozen candidate bytes; reject output aliases and preserve last-known-good/recovery evidence on failure.
- Claim only what executed or supplied evidence supports; structural, behavioral, runtime, stochastic, portability, and perceptual evidence are not interchangeable.

## Reproducibility Ceiling and Control Placement

| Target class | Mechanically enforce | Keep bounded judgment |
|---|---|---|
| `objective-artifact` | normalization, schema/IR, deterministic mechanics, validators, hashes | minimal |
| `tool-action` | pre/postconditions, authority, idempotency/retry, request construction, receipts | external outcomes/timing |
| `research-analytic` | source hierarchy, traceability, output contract, claim/evidence rules | conclusions/interpretation |
| `constrained-subjective` | structure, process, constraints, evidence collection | perceptual/editorial quality |

State the ceiling before transformation. Place each control at the lowest reliable layer that preserves meaning: `runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`. Never move genuine judgment into code merely to appear deterministic.

## Workflow at a Glance

1. **Establish:** target, baseline, capabilities, writable/protected scope, material source/evaluator identities, and whether packaging is required.
2. **Classify:** reproducibility ceiling; separate controllable variance from irreducible model/external/subjective variance.
3. **Map variance:** discovery/activation -> Top-100 -> input normalization -> routing -> references -> decisions -> generation -> validation -> repair -> delivery -> packaging.
4. **Freeze contract:** hard gates, protected paths, variability items, evaluators/scenarios, acceptance rules, and delivery guarantees before material mutation.
5. **Transform minimally:** use the lowest reliable control layer; add machinery only for an observed variance source or evidence gap.
6. **Repair causally:** failing diagnostic -> smallest supported fix -> same gate -> adjacent gates; stop a branch after two non-improving repair rounds unless evidence changes the hypothesis.
7. **Evaluate:** baseline vs candidate on identical scenarios; add environment profiles, repeated trials, no-skill/full-context arms, or holdouts only when the claim requires them.
8. **Prove and freeze:** verify source/evaluator identity, target-owned tests, context/package gates, then freeze exact candidate bytes.
9. **Deliver atomically:** package only frozen bytes, verify package/receipt identity, and preserve last-good/recovery artifacts on failure.

## Acceptance Gates and Stop Conditions

Acceptance gates require protected/frozen evidence to remain unchanged; mandatory target validators/tests and applicable context/package gates pass; no blocking activation, semantic, safety, compatibility, validation, or packaging regression remains; every quality/portability/reliability claim stays within the target ceiling and executed/supplied evidence; and final package/receipt identity matches the frozen candidate.

Stop when target identity is ambiguous; required baseline/evaluator/source identity cannot be preserved; a mandatory trustworthy gate cannot run; protected evidence would need mutation; passing would require weakening a hard gate; source/evaluator drift invalidates comparison; or requested determinism exceeds the target's real ceiling.

## Output Summary

Every substantive run reports target/mode/baseline identity, reproducibility ceiling and irreducible variance, changed files, evaluator/source identity, exact validation outcomes, accepted/rejected transformations, final gates, Top-100/reference-depth status, and residual risks. Report a package path only when the archive exists and validation passed.

## Direct Reference Map

- **Ceiling / transformation / validators:** [`references/reproducibility-model.md`](references/reproducibility-model.md), [`references/transformation-playbook.md`](references/transformation-playbook.md), [`references/validator-patterns.md`](references/validator-patterns.md).
- **Evaluation / scenarios / stochastic claims:** [`references/evaluation-contract.md`](references/evaluation-contract.md), [`references/scenario-design.md`](references/scenario-design.md), [`references/stochastic-evaluation.md`](references/stochastic-evaluation.md).
- **Integrity / reporting:** [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md), [`references/report-contract.md`](references/report-contract.md).
- **Portability / environment:** [`references/host-portability.md`](references/host-portability.md), [`references/environment-provenance.md`](references/environment-provenance.md).
- **Adaptive / multi-stage:** [`references/workflow-reproducibility.md`](references/workflow-reproducibility.md), [`references/execution-lineage.md`](references/execution-lineage.md).
- **Self-hosting:** [`references/self-hosting-reproducibility.md`](references/self-hosting-reproducibility.md).

All mandatory Markdown is linked directly from `SKILL.md`; reference-to-reference links are navigation only. For authored supporting Markdown over 100 lines, require **Purpose**, **Load when**, and **Decision impact** before a synchronized `Contents` map; generic topic lists do not satisfy the preview contract.

## Detailed workflow

### 1. Establish target identity and baseline

1. Resolve exactly one target skill root containing `SKILL.md`.
2. Record target path, current version/identity when present, requested behavior, host/runtime profile, detected capabilities, writable scope, blocked paths, and whether final packaging is required plus its requested profile. If the target will modify itself, also load `references/self-hosting-reproducibility.md` and freeze controller/generation/last-known-good identity before candidate mutation.
3. Preserve an immutable baseline before edits: copy, clean VCS commit, or equivalent snapshot.
4. If external files or repository evidence materially determine the transformation or acceptance decision, capture the exact source bytes before analysis and use that snapshot as evidence. Prefer immutable VCS object reads for pinned revisions; do not let working-tree edits or replacement refs silently redefine a pinned source. Read `references/integrity-and-recovery.md` when this applies.
5. Run target-owned validators/tests/package checks first when available. Record exact commands and exit status.
6. Run:

```text
<PYTHON> scripts/inventory_target.py --target <TARGET> --json <WORK>/inventory-before.json
<PYTHON> scripts/reproducibility_audit.py --target <TARGET> --json <WORK>/audit-before.json
<PYTHON> scripts/validate_context_loading.py --target <TARGET> --json <WORK>/context-loading-before.json
```

The audit is structural evidence only. Never call its maturity result a behavioral benchmark. When portability is part of the request, also record which host-specific extensions exist and whether they are optional adapters or core dependencies; use `references/host-portability.md` as the interpretation contract.

### 2. Determine the reproducibility ceiling

Classify the target using `references/reproducibility-model.md`:

- `objective-artifact`: most correctness can be mechanically checked.
- `tool-action`: preconditions, actions, postconditions, idempotency, and receipts can be checked.
- `research-analytic`: evidence traceability and output conformance are enforceable; conclusions retain bounded judgment.
- `constrained-subjective`: structure and process are enforceable; perceptual/editorial quality still needs rubric or human/image-capable review.

State the ceiling explicitly. Do not promise byte-level determinism for stochastic or subjective outputs.

### 3. Build a variability map

Map every material source of variance across:

`discovery/activation -> top-100 control surface -> input normalization -> mode/router -> reference loading -> decisions -> generation -> validation -> repair -> delivery -> packaging`

For adaptive/model-generated orchestration, also separate `planner identity -> accepted workflow plan -> execution trace -> evaluator`; load `references/workflow-reproducibility.md` so plan-generation variance is not confused with same-plan execution variance. When a multi-stage reproducibility claim depends on node dependencies or replay, persist the optional lineage profile from `references/execution-lineage.md` rather than relying on trace prose alone.

For self-hosted workflows, extend the map with `controller freeze -> candidate isolation -> evaluator visibility -> generation identity -> promotion -> rollback/last-known-good`.

For each source classify it as:

- `mechanical`: move to code, schema, parser, renderer, or deterministic transform;
- `constrained-heuristic`: define defaults, ordering, tie-breakers, bounded enums, and stop rules;
- `model-judgment`: define evidence requirements, rubric, allowed freedom, and independent review;
- `external-nondeterminism`: pin versions/snapshots where possible, capture exact source bytes when evidence matters, and record environment/time/source identity; use `references/environment-provenance.md` when runtime identity is material to comparability.

Prefer the lowest reliable control layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`.

Do not move judgment into code merely to appear deterministic. Apply the control-placement matrix in `references/reproducibility-model.md` when the lane is ambiguous.

### 4. Create and freeze the transformation contract

Create a working contract from [`assets/templates/reproducibility-contract.json`](assets/templates/reproducibility-contract.json), or generate a scaffold:

```text
<PYTHON> scripts/create_reproducibility_contract.py --target <TARGET> --audit <WORK>/audit-before.json --out <WORK>/reproducibility-contract.json
<PYTHON> scripts/validate_reproducibility_contract.py <WORK>/reproducibility-contract.json
```

The contract must identify hard gates, protected paths, variability items, evaluators, scenario groups, acceptance rules, and delivery guarantees before material mutation begins. Contract version 3 also records applicability for the environment/provenance, stochastic-evaluation, and execution-lineage profiles without forcing them on irrelevant runs.

Freeze evaluator assets that will decide candidate acceptance:

```text
<PYTHON> scripts/freeze_evaluator.py freeze --root <TARGET> --path evals --path scripts --out <WORK>/evaluator-manifest.json
```

Narrow the frozen paths to actual evaluator assets when the target mixes generators and validators under one directory. When external source evidence is material, also capture it before analysis:

```text
<PYTHON> scripts/snapshot_sources.py capture --root <SOURCE_ROOT> --path <SOURCE_PATH> --snapshot-dir <WORK>/source-bytes --out <WORK>/source-manifest.json
```

Analyze the captured bytes, not a live source that may change underneath the run.

### 5. Apply the smallest coherent reproducibility upgrades

Use `references/transformation-playbook.md`. Prefer transformations in this order:

1. clarify activation and non-activation boundaries;
2. normalize inputs and explicit mode/router selection;
3. define semantic/output contracts;
4. reduce unnecessary degrees of freedom with strong defaults and bounded options;
5. extract fragile/repetitive mechanics into scripts;
6. add typed schemas or IR when structured generation benefits from compilation/rendering;
7. add independent validators with machine-readable diagnostics;
8. add diagnostic-driven repair rules and bounded stop conditions;
9. add activation, boundary, regression, adversarial, and holdout scenarios;
10. separate artifact validation, runtime validation, and subjective/perceptual review;
11. add freeze-after-pass, atomic delivery, hashes/receipts, and version/migration rules where relevant;
12. make context loading reproducible: if `SKILL.md` exceeds 100 lines, keep purpose/scope, discriminative activation/non-activation routing, mode choice, workflow start, critical invariants/control model, acceptance/stop signals, and direct branch pointers inside the first 100 lines; for authored supporting Markdown over 100 lines, put explicit `Purpose`, `Load when`, and `Decision impact` signals before a synchronized `Contents`/section map; reject generic topic-list previews; keep mandatory Markdown directly reachable from `SKILL.md`;
13. snapshot material source evidence before analysis and verify its identity before acceptance;
14. canonicalize output paths and reject aliases with inputs, protected files, or sibling outputs before any write;
15. make multi-output commits recovery-aware so last-good artifacts and rollback evidence survive failures;
16. make receipts complete, durable, stage-aware, and tied to the exact committed bytes.

Do not add machinery merely because Archify has it. Every added mechanism must eliminate an observed source of variance or create useful evidence.

### 6. Repair by diagnosis, not by taste

After each meaningful candidate batch:

1. run the narrowest failing validator/evaluator;
2. identify one causal subject and its evidence;
3. apply the smallest supported fix;
4. rerun the same gate;
5. only then run adjacent gates.

Prefer one causal control change per repair when geometry, routing, schemas, or output contracts are involved. If two consecutive repair rounds do not improve the best objective error count, stop that branch and report the unresolved diagnostic instead of random-searching.

Never delete semantic information, reduce safety, weaken an evaluator, or lower a threshold merely to get a pass.

### 7. Evaluate behavior against the frozen baseline

Follow `references/evaluation-contract.md`.

When execution infrastructure permits, compare at least:

- old/baseline skill vs candidate skill;
- no-skill baseline when it answers whether the skill adds value;
- full-plugin/full-context arm when surrounding context could interfere with activation or behavior.

Use identical scenario prompts/files across paired arms. When runtime identity can change the result, validate comparable environment profiles before interpreting the pair. Repeat stochastic scenarios when a strong improvement claim matters; use `references/stochastic-evaluation.md` and its validated trial evidence rather than inferring reliability from one run.

Optional paired win/loss significance check:

```text
<PYTHON> scripts/paired_sign_test.py <WORK>/paired-results.json --json <WORK>/sign-test.json
```

Do not call a static score, one good example, or an unexecuted eval file measured behavioral improvement.

### 8. Validate the final candidate and freeze it

Before handoff:

```text
<PYTHON> scripts/freeze_evaluator.py verify --root <TARGET> --manifest <WORK>/evaluator-manifest.json
<PYTHON> scripts/validate_target_package.py --target <TARGET> --json <WORK>/package-validation.json
<PYTHON> scripts/reproducibility_audit.py --target <TARGET> --json <WORK>/audit-after.json
<PYTHON> scripts/validate_context_loading.py --target <TARGET> --json <WORK>/context-loading-after.json
```

If execution evidence profiles were produced, validate each applicable artifact with `scripts/validate_execution_evidence.py`; paired comparisons with material runtime sensitivity must also pass environment comparison, and multi-stage lineage must validate before a lineage/replay claim is accepted.

If a source snapshot was captured, verify it too:

```text
<PYTHON> scripts/snapshot_sources.py verify --manifest <WORK>/source-manifest.json --json <WORK>/source-verification.json
```

A changed live source invalidates claims tied to the earlier live source unless the experiment is deliberately re-baselined. Also rerun all target-owned validators/tests that were part of baseline acceptance.

A final passing candidate is frozen. Do not make unvalidated cleanup or cosmetic edits afterward. If a change is necessary after the pass, validation must start again from the affected gate.

### 9. Deliver atomically and truthfully

When packaging is requested, use the target's own package builder if it is part of the contract. Otherwise use the bundled fallback:

```text
<PYTHON> scripts/package_target.py --target <TARGET> --output <OUTPUT_DIR>/skill.zip --profile portable --json <WORK>/package-receipt.json
```

Package only the exact frozen candidate. Use `--profile openai` only when OpenAI-specific metadata is an explicit delivery requirement; the default `portable` profile validates the host-neutral core. Preflight authored and resolved output paths before mutation: package, receipt, inputs, evaluators, and protected files must not alias each other. A non-zero exit is failure. Do not replace a known-good package with a failed candidate. When a multi-output commit or rollback fails, preserve recovery files and report their exact locations rather than deleting evidence.

Keep these claims separate:

- **structural evidence**: package shape, references, script syntax, frozen hashes;
- **behavioral evidence**: executed scenarios and evaluator decisions;
- **runtime evidence**: actual browser/application/tool behavior;
- **perceptual evidence**: human or image-capable review for subjective quality.

One does not imply another.

## Host portability details

Treat the open Agent Skills format as the canonical core. Do not make the workflow semantically depend on ChatGPT, Claude, GitHub Copilot, Cursor, or any other single host. When the user asks about cross-platform behavior, the host is uncertain, or runtime assumptions affect execution, read [`references/host-portability.md`](references/host-portability.md).

### Runtime capabilities

Before running bundled scripts:

1. detect capabilities rather than branching only on product name: readable/writable filesystem, Python 3.10+, command execution, network access, subagents, and artifact delivery;
2. resolve `<PYTHON>` to the host's available Python 3.10+ execution method instead of assuming the executable is named `python`;
3. use relative package paths and host-neutral filesystem semantics;
4. treat `agents/openai.yaml` as an optional OpenAI UI/dependency adapter, never as a core requirement;
5. preserve host-specific extensions on target skills unless the requested work includes portability normalization;
6. when runtime identity can materially affect a comparison, capture and validate an execution-environment profile instead of treating host/model/tool state as implicit.

### Execution evidence profiles

Use these only when the claim needs them; simple static work must not pay their complexity cost.

| Profile | Use when | Deterministic validator |
|---|---|---|
| environment/provenance | provider, model, tools, dependencies, cache, concurrency, locale, or timezone can affect comparability | `scripts/validate_execution_evidence.py --kind environment` |
| stochastic evaluation | repeated model/agent trials support a reliability or improvement claim | `scripts/validate_execution_evidence.py --kind stochastic` |
| execution lineage | a multi-stage/adaptive workflow needs replay, invalidation, or dependency identity | `scripts/validate_execution_evidence.py --kind lineage` |

Full `apply`, `validation-only`, and `package` evidence requires a writable filesystem and Python 3.10+ for the bundled deterministic validators. If those capabilities are unavailable, continue only with the safe subset the host can execute, mark script-based gates `not-run`, and do not claim a package-validation pass.

## Resource loading details

Read target `SKILL.md` first. Then load only the references needed for the active stage:

- [`references/reproducibility-model.md`](references/reproducibility-model.md): ceilings, maturity levels, and variability taxonomy.
- [`references/workflow-reproducibility.md`](references/workflow-reproducibility.md): planner/accepted-plan/execution-trace identity separation, planning versus execution variance, fresh-context evidence, and adaptive-workflow comparison rules.
- [`references/execution-lineage.md`](references/execution-lineage.md): persistent DAG lineage, canonical outputs, invalidation, and replay rules for material multi-stage workflows.
- [`references/transformation-playbook.md`](references/transformation-playbook.md): concrete Archify-style transformation patterns and repair order.
- [`references/evaluation-contract.md`](references/evaluation-contract.md): frozen evaluators, comparison arms, metrics, acceptance, and claim rules.
- [`references/stochastic-evaluation.md`](references/stochastic-evaluation.md): repeated-trial evidence, uncertainty, `pass^k`, LLM-judge calibration, and replication rules for stochastic claims.
- [`references/validator-patterns.md`](references/validator-patterns.md): validator design by output/workflow class and receipt contract.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): exact input snapshots, immutable source provenance, output alias safety, recovery-aware commits, and durable receipts.
- [`references/environment-provenance.md`](references/environment-provenance.md): execution environment identity, provenance-lite receipts, hermeticity vocabulary, and environment-drift handling.
- [`references/scenario-design.md`](references/scenario-design.md): activation, boundary, edge, regression, adversarial, and holdout scenarios.
- [`references/self-hosting-reproducibility.md`](references/self-hosting-reproducibility.md): controller/baseline/candidate generation controls for skills that modify themselves, including recursion, promotion, and last-known-good invariants.
- [`references/report-contract.md`](references/report-contract.md): final evidence/report structure.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned self-coverage for this meta-skill; never treat it as executed evidence until a harness runs it.
- [`assets/templates/reproducibility-report.md.template`](assets/templates/reproducibility-report.md.template): copy/fill only when a durable report artifact is useful.

Use bundled scripts as deterministic helpers. Their outputs are evidence, not substitutes for semantic review.
`scripts/_common.py` is an internal shared library consumed by the bundled command-line validators and is not a user-facing command.

## Acceptance gates

A candidate is acceptable only when all applicable hard gates hold:

1. target identity and scope are unambiguous;
2. protected evidence stayed unchanged after freeze;
3. target package validation passes;
4. target-owned mandatory validators/tests pass;
5. no blocking regression exists in activation, semantics, safety, compatibility, validation, or packaging;
6. claimed behavioral improvement is supported by executed/supplied evidence, otherwise the claim is limited to structural hardening;
7. subjective quality claims have independent perceptual/editorial evidence when required by the ceiling;
8. the final candidate was not edited after its final pass;
9. package/receipt corresponds to the frozen candidate;
10. material source snapshots/evidence identities remained stable, or the experiment was explicitly invalidated and re-baselined;
11. delivery preflight rejected output aliases and failure recovery preserved last-good artifacts/recovery evidence when applicable;
12. machine-readable receipts are complete, parseable, and refer to the exact committed bytes;
13. paired evidence whose outcome is materially runtime-sensitive has no unresolved environment drift, or the experiment was explicitly re-baselined;
14. strong stochastic reliability/improvement claims use validated repeated-trial evidence and independent replication;
15. multi-stage replay/invalidation claims use a valid lineage artifact when dependency identity is material;
16. context-loading validation passes for long control/reference Markdown, and any semantic exception is explicitly reviewed rather than hidden by structural checks.

## Output contract

Follow `references/report-contract.md`. Every substantive run must report:

- target, mode, scope, and baseline identity;
- reproducibility ceiling and remaining irreducible nondeterminism;
- before/after structural maturity as structural evidence only;
- variability map summary and controls moved downward;
- files changed and why;
- evaluators/scenarios and freeze status;
- exact commands with pass/fail/not-run;
- accepted and rejected transformations;
- behavioral comparison when measured, including repeated-trial reliability/uncertainty when a stochastic profile applies;
- execution environment/provenance identity and any material drift when runtime comparability applies;
- execution-lineage identity/canonical outputs when a multi-stage lineage profile applies;
- final gates, Top-100/reference-depth status, and residual risks;
- package path only when the archive exists and validation passed;
- for self-hosted transformations, controller/baseline/candidate/generation identities, recursion limit, external-promotion status, last-known-good status, and bootstrap-conformance result when checked.

## Stop conditions

Stop or return a bounded partial result when:

- zero or multiple ambiguous target roots exist;
- mutation is requested but no safe baseline/snapshot can be preserved;
- source truth needed for semantic behavior is unavailable;
- a required evaluator cannot be frozen or has been modified during the experiment;
- candidate changes require editing protected fixtures, expected outputs, secrets, credentials, or unrelated repositories;
- compatibility/migration evidence is insufficient for removing existing behavior;
- required target validation fails and cannot be safely repaired in scope;
- material source/evaluator evidence changes after capture and a trustworthy comparison cannot be restarted;
- output targets alias an input, protected path, evaluator, or sibling receipt and cannot be safely separated;
- the only way to pass is to weaken a hard gate;
- the user requires deterministic identity for an output class whose ceiling is inherently subjective/stochastic.
