---
name: reproducibility-engineer
description: Engineer reproducibility for an existing Agent Skills-compatible skill across ChatGPT/Codex, Claude, GitHub Copilot, Cursor, and other compatible hosts by analyzing and modifying the package so repeated runs satisfy the same semantic contract, quality gates, and evidence standards. Use specifically when the goal is deterministic/repeatable/reliable/Archify-like behavior, cross-agent consistency, lower model improvisation, or adding schemas, scripts, validators, evals, regression gates, repair loops, frozen evaluators, receipts, versioned contracts, or atomic delivery. Do not use for generic skill review/benchmarking, net-new skill creation, ordinary application code, or prompt-only rewrites unless reproducibility is the explicit goal.
---

# Reproducibility Engineer

Transform an existing skill from an instruction bundle into an operationally reproducible package. Reduce model freedom where objective mechanisms can replace it, preserve model judgment where it is genuinely useful, and prove the final state with frozen evaluation evidence.

## Non-negotiable definition

Reproducibility means the same inputs and supported environment repeatedly satisfy the same semantic contract, quality gates, and delivery guarantees. It does not mean identical natural-language bytes unless the target domain can actually guarantee them.

Never make a skill look more reproducible by weakening semantics, safety, evidence, validators, tests, or acceptance thresholds.

## Modes

Choose one primary mode:

| Mode | Use for | Mutation |
|---|---|---|
| `audit-only` | diagnose reproducibility weaknesses and ceiling | no |
| `plan-only` | produce a bounded transformation plan and contract | no |
| `apply` | modify an existing skill toward reproducible behavior | yes |
| `validation-only` | verify an already-modified skill | no unless explicitly allowed |
| `package` | validate and build the final `skill.zip` | only repairs needed to pass declared gates |

For "make this skill Archify-like/reproducible", default to `apply`, then validation. Package only when requested or clearly expected.

## Authority and protected evidence

- Mutate only the target skill folder unless the user explicitly expands scope.
- Before mutation, preserve a baseline snapshot or equivalent immutable before-state.
- Protect `.git`, secrets, credentials, user fixtures, expected outputs, golden baselines, frozen evaluator files, generated baseline evidence, and unrelated repositories.
- Once an evaluator is frozen, never edit it to make a candidate pass. If an evaluator is wrong, invalidate that experiment, repair the evaluator separately, freeze a new baseline, and restart comparison.
- Do not silently delete legacy behavior. Trace current owners, consumers, compatibility commitments, migrations, tests, and validators first.

## Progressive loading

Read target `SKILL.md` first. Then load only the references needed for the active stage:

- [`references/reproducibility-model.md`](references/reproducibility-model.md): ceilings, maturity levels, and variability taxonomy.
- [`references/transformation-playbook.md`](references/transformation-playbook.md): concrete Archify-style transformation patterns and repair order.
- [`references/evaluation-contract.md`](references/evaluation-contract.md): frozen evaluators, comparison arms, metrics, acceptance, and claim rules.
- [`references/validator-patterns.md`](references/validator-patterns.md): validator design by output/workflow class and receipt contract.
- [`references/integrity-and-recovery.md`](references/integrity-and-recovery.md): exact input snapshots, immutable source provenance, output alias safety, recovery-aware commits, and durable receipts.
- [`references/scenario-design.md`](references/scenario-design.md): activation, boundary, edge, regression, adversarial, and holdout scenarios.
- [`references/self-hosting-reproducibility.md`](references/self-hosting-reproducibility.md): controller/baseline/candidate generation controls for skills that modify themselves, including recursion, promotion, and last-known-good invariants.
- [`references/report-contract.md`](references/report-contract.md): final evidence/report structure.
- [`evals/activation-scenarios.json`](evals/activation-scenarios.json): planned self-coverage for this meta-skill; never treat it as executed evidence until a harness runs it.
- [`assets/templates/reproducibility-report.md.template`](assets/templates/reproducibility-report.md.template): copy/fill only when a durable report artifact is useful.

Use bundled scripts as deterministic helpers. Their outputs are evidence, not substitutes for semantic review.
`scripts/_common.py` is an internal shared library consumed by the bundled command-line validators and is not a user-facing command.

## Host portability

Treat the open Agent Skills format as the canonical core. Do not make the workflow semantically depend on ChatGPT, Claude, GitHub Copilot, Cursor, or any other single host. When the user asks about cross-platform behavior, the host is uncertain, or runtime assumptions affect execution, read [`references/host-portability.md`](references/host-portability.md).

### Runtime capabilities

Before running bundled scripts:

1. detect capabilities rather than branching only on product name: readable/writable filesystem, Python 3.10+, command execution, network access, subagents, and artifact delivery;
2. resolve `<PYTHON>` to the host's available Python 3.10+ execution method instead of assuming the executable is named `python`;
3. use relative package paths and host-neutral filesystem semantics;
4. treat `agents/openai.yaml` as an optional OpenAI UI/dependency adapter, never as a core requirement;
5. preserve host-specific extensions on target skills unless the requested work includes portability normalization.

Full `apply`, `validation-only`, and `package` evidence requires a writable filesystem and Python 3.10+ for the bundled deterministic validators. If those capabilities are unavailable, continue only with the safe subset the host can execute, mark script-based gates `not-run`, and do not claim a package-validation pass.

## Reproducibility workflow

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

`activation -> input normalization -> mode/router -> reference loading -> decisions -> generation -> validation -> repair -> delivery -> packaging`

For self-hosted workflows, extend the map with `controller freeze -> candidate isolation -> evaluator visibility -> generation identity -> promotion -> rollback/last-known-good`.

For each source classify it as:

- `mechanical`: move to code, schema, parser, renderer, or deterministic transform;
- `constrained-heuristic`: define defaults, ordering, tie-breakers, bounded enums, and stop rules;
- `model-judgment`: define evidence requirements, rubric, allowed freedom, and independent review;
- `external-nondeterminism`: pin versions/snapshots where possible, capture exact source bytes when evidence matters, and record environment/time/source identity.

Prefer the lowest reliable control layer:

`runtime/script > schema/type > validator/gate > reference/rubric > free-form prompt`.

Do not move judgment into code merely to appear deterministic. Apply the control-placement matrix in `references/reproducibility-model.md` when the lane is ambiguous.

### 4. Create and freeze the transformation contract

Create a working contract from [`assets/templates/reproducibility-contract.json`](assets/templates/reproducibility-contract.json), or generate a scaffold:

```text
<PYTHON> scripts/create_reproducibility_contract.py --target <TARGET> --audit <WORK>/audit-before.json --out <WORK>/reproducibility-contract.json
<PYTHON> scripts/validate_reproducibility_contract.py <WORK>/reproducibility-contract.json
```

The contract must identify hard gates, protected paths, variability items, evaluators, scenario groups, acceptance rules, and delivery guarantees before material mutation begins.

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
12. move long branch knowledge out of `SKILL.md` into progressive references;
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

Use identical scenario prompts/files across paired arms. Repeat stochastic scenarios when a strong improvement claim matters.

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
```

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
12. machine-readable receipts are complete, parseable, and refer to the exact committed bytes.

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
- behavioral comparison when measured;
- final gates and residual risks;
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
