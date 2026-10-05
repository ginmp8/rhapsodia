---
name: reproducibility-engineer
description: Engineer reproducibility for one existing Agent Skills-compatible skill across portable hosts when reproducibility itself is the goal or a bounded reproducibility batch has been selected. Use to reduce controllable variance across agents and runs with explicit contracts, deterministic mechanics, schemas, validators, evals, frozen evidence, repair loops, receipts, and atomic/versioned delivery while preserving the skill's responsibility boundary. Do not use for generic skill optimization/review/benchmarking, net-new skill creation, ordinary application code, or prompt-only rewrites; route general optimization to skill-booster and ownership-changing redesign to skill-creator-juiced.
---

# Reproducibility Engineer

## At a Glance

- **Purpose:** Make one existing Agent Skills-compatible skill reproducible at its real semantic ceiling without changing what the skill owns.
- **Use when:** Reproducibility/repeatability/cross-agent consistency is the explicit goal, or Skill Booster has selected a bounded reproducibility transformation for the target.
- **Do not use when:** The request is generic skill improvement, benchmark-only scoring, net-new skill creation, ordinary application code, or prompt-only rewriting without a reproducibility objective.
- **Outcome:** Repeated runs with the same material inputs in a supported environment satisfy the same semantic contract, hard gates, evidence standards, and delivery guarantees; byte-identical model prose is not promised unless the target class can guarantee it.

## Activation and Routing

Use this skill only when all of these are true: there is exactly one existing skill target, reproducibility is material to the requested outcome, and the target's responsibility boundary can remain intact. For general optimization use `skill-booster`; for ownership-changing/new-skill design use `skill-creator-juiced`; for benchmark-only measurement use `skill-benchmark`.

Preserve the target's existing capability boundary. A self-hosting target is a special branch: freeze controller, generation, evaluator, candidate, and last-known-good identities before mutation and load the self-hosting reference directly.

## Modes

| Mode | Use for | Mutation |
|---|---|---|
| `audit-only` | diagnose reproducibility weaknesses and ceiling | no |
| `plan-only` | produce a bounded transformation plan and contract | no |
| `apply` | modify an existing skill toward reproducible behavior | yes |
| `validation-only` | verify an already-modified skill | no unless explicitly allowed |
| `package` | validate and build final `skill.zip` | only repairs required by declared gates |

Default to `apply` when the user explicitly asks to make a skill reproducible/repeatable/Archify-like; otherwise choose the narrowest mode supported by the request.

## Core invariants

- Resolve exactly one target skill root and mutate only its authorized scope.
- Preserve an immutable baseline before edits; snapshot material external source bytes before they can drift.
- Protect `.git`, secrets, credentials, user fixtures, expected outputs, golden baselines, frozen evaluators, generated baseline evidence, and unrelated repositories.
- Keep the portable Agent Skills core host-neutral; treat host adapters as optional and detect capabilities instead of branching only on host name.
- Full `apply`, `validation-only`, and `package` evidence requires writable filesystem access and Python 3.10+ for bundled deterministic validators; otherwise mark script gates `not-run` and do not claim package-validation pass.
- Freeze evaluators before candidate mutation; evaluator drift invalidates the comparison and requires restart/re-baseline.
- Trace legacy owners, consumers, compatibility commitments, migrations, tests, and validators before removing behavior.
- Never weaken semantics, safety, tests, evaluators, evidence, thresholds, or protected paths to manufacture reproducibility.
- A final passing candidate is frozen; any later edit invalidates affected evidence and requires revalidation.
- Package only the exact frozen candidate; preflight output aliases and preserve last-good/recovery evidence on failure.
- Never claim benchmark uplift, runtime portability, stochastic reliability, or subjective quality without matching executed/supplied evidence.

## Reproducibility ceiling and control placement

| Target class | Mechanically enforce | Keep bounded judgment |
|---|---|---|
| `objective-artifact` | normalization, schema/IR, deterministic mechanics, validators, hashes | minimal |
| `tool-action` | pre/postconditions, authority, idempotency/retry, request construction, receipts | external outcomes/timing |
| `research-analytic` | source hierarchy, traceability, output contract, claim/evidence rules | conclusions/interpretation |
| `constrained-subjective` | structure, process, constraints, evidence collection | perceptual/editorial quality |

State the ceiling before transformation. Use the lowest reliable control layer that preserves meaning: `runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`. Do not move genuine judgment into code merely to appear deterministic.

## Workflow at a Glance

1. **Establish** target, immutable baseline, capabilities, writable/protected scope, source/evaluator identities, and package expectation.
2. **Classify** the reproducibility ceiling and separate irreducible model/external nondeterminism from controllable variance.
3. **Map variance** across discovery/activation -> Top-100 -> normalization -> routing -> references -> decisions -> generation -> validation -> repair -> delivery -> packaging.
4. **Freeze the contract**: hard gates, protected paths, variability items, evaluator/scenario identities, acceptance rules, and delivery guarantees before material mutation.
5. **Transform minimally** using the lowest reliable control layer; add machinery only for an observed variance source or evidence gap.
6. **Repair causally**: failing diagnostic -> smallest supported fix -> same gate -> adjacent gates; stop after two non-improving rounds unless evidence changes the hypothesis.
7. **Evaluate** baseline vs candidate on identical scenarios; add environment profiles, repeated trials, no-skill/full-context arms, or holdouts only when the claim requires them.
8. **Prove and freeze** source/evaluator identity, target-owned tests, package/context gates, then exact candidate bytes.
9. **Deliver atomically** only from frozen bytes; verify receipt identity and preserve last-good/recovery artifacts on failure.

## Acceptance Gates and Stop Conditions

Acceptance is blocked by semantic/safety/compatibility regressions, changed protected/frozen evidence, failing required validation, candidate/package identity mismatch, unsupported behavioral or portability claims, or edits after final freeze. Keep structural, behavioral, runtime, and perceptual/editorial evidence claims separate.

Stop when target identity is ambiguous; a required baseline/evaluator/source identity cannot be preserved; protected evidence would be edited; a trustworthy required gate cannot run; passing would require weakening a hard gate; source/evaluator drift makes comparison invalid; or the requested determinism exceeds the target's real ceiling.

## Direct Reference Map

- **Ceiling and transformation choice:** [`references/reproducibility-model.md`](references/reproducibility-model.md), [`references/transformation-playbook.md`](references/transformation-playbook.md), [`references/validator-patterns.md`](references/validator-patterns.md).
- **Evaluation evidence:** [`references/evaluation-contract.md`](references/evaluation-contract.md), [`references/scenario-design.md`](references/scenario-design.md), [`references/stochastic-evaluation.md`](references/stochastic-evaluation.md).
- **Integrity and reporting:** [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md), [`references/report-contract.md`](references/report-contract.md).
- **Portability and environment:** [`references/host-portability.md`](references/host-portability.md), [`references/environment-provenance.md`](references/environment-provenance.md).
- **Adaptive/multi-stage workflows:** [`references/workflow-reproducibility.md`](references/workflow-reproducibility.md), [`references/execution-lineage.md`](references/execution-lineage.md).
- **Self-hosting:** [`references/self-hosting-reproducibility.md`](references/self-hosting-reproducibility.md).

Load only the branch-relevant files above. Required Markdown must be directly reachable from `SKILL.md`; Markdown-to-Markdown links may aid navigation but must never be the sole route to mandatory instructions. For authored supporting Markdown over 100 lines, require a decision-useful preview with explicit **Purpose**, **Load when**, and **Decision impact** before a synchronized `Contents` map; a generic topic list is not sufficient.

## Detailed workflow

### 1. Establish target identity and baseline

1. Resolve exactly one target skill root containing `SKILL.md`.
2. Record target path, current version/identity when present, requested behavior, host/runtime profile, detected capabilities, writable scope, blocked paths, and package expectation. If the target will modify itself, also load `references/self-hosting-reproducibility.md` and freeze controller/generation/last-known-good identity before candidate mutation.
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
