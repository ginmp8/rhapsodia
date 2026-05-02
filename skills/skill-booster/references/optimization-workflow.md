# Optimization Workflow

Use this ordered workflow for every target skill. Keep the order unless an earlier stop condition applies.

## Phase 0: Intake

Capture:

- target path or extracted zip location;
- desired mode: `audit-only`, `plan-only`, `apply-optimization`, `validation-only`, `package`;
- final artifact expectation;
- writable scope and blocked paths;
- known failures, user feedback, benchmark reports, or previous outputs;
- required language and output conventions.

If the user says "do the full optimization", use `apply-optimization` followed by validation and package when gates pass.

## Phase 1: Preflight and Inventory

Run structural preflight:

```bash
python scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>
```

Inventory:

- `SKILL.md` frontmatter and body;
- `agents/openai.yaml`;
- `references/`;
- `scripts/`;
- `assets/` and `assets/templates/`;
- `examples/`;
- `evals/`;
- validators, package scripts, reports, and generated files.

Output: target inventory, risks, unavailable resources, and candidate objectives.

## Phase 2: Baseline and Evaluator Freeze

Use the strongest available evaluator, in this order:

1. existing target evaluator or CI-style validation command;
2. `skill-benchmark` report;
3. `skill-harness` scenario suite;
4. static structural validator;
5. planned evaluator if no execution is possible.

Freeze before mutation:

- scenarios;
- expected outputs;
- benchmark inputs;
- scoring config;
- validator scripts;
- generated baseline report;
- blocked paths.

Output: baseline score or gate set, evaluator identity, frozen inputs, and blocked paths.

## Phase 3: Juiced Escalation and Architecture Before Text

Run `skill-creator-juiced` as the design-governance pass when the target appears to need major redesign, mode/router decisions, split strategy, or production-ready package orchestration. Then run `skill-package-architecture-review` before rewriting instructions.

Decide one of:

- keep unified skill;
- add modes;
- introduce router behavior;
- split into separate skills;
- stop because target is not a skill.

Prefer keeping one package only when one operational role explains all modes.

## Phase 4: Activation and Prompt Contract

Run `skill-prompt-and-activation-review`; add `prompt-architect` when complex prompt bodies or agent instructions exist.

Improve:

- frontmatter description;
- triggers and non-triggers;
- ambiguous request handling;
- stop conditions;
- output contract;
- tool and resource loading rules.

## Phase 5: Consistency, Docs, Code, and Security

Run these passes before cleanup or token compression:

- `skill-consistency-repair` for contradictions and broken internal links;
- `documentation-quality` for references, examples, templates, and usage guidance;
- `karpathy-guidelines` for scripts, validators, technical examples, and commands;
- `security-and-governance-review` for secrets, unsafe commands, dependency risk, permissions, and tool authority.

Patch only target-scope files.

## Phase 6: Validation Before Cleanup

Run `skill-testing-and-validation` before deleting or compressing files.

Check:

- modified scripts run or syntax-check;
- package structure validates;
- local links resolve;
- known scenario suite still passes or remains planned;
- no blocked path changed.

## Phase 7: Cleanup and Simplification

Run `skill-cleanup-and-simplification` after useful resources have been integrated.

Remove only:

- generated noise;
- caches;
- old packages;
- obsolete duplicate guidance;
- unused scaffold files;
- resources outside declared workflow.

Do not delete a resource merely because it is long. Migrate long branch rules to `references/` when they are useful.

## Phase 8: Token Reduction

Run `skill-token-efficient` after behavior, architecture, safety, and output contract are stable.

Compress in this order:

1. duplicate guidance;
2. filler and rationale;
3. repeated negatives;
4. examples that do not calibrate behavior;
5. branch detail moved from `SKILL.md` to `references/`;
6. frontmatter description last and conservatively.

Immediately re-run validation after compression.

## Phase 9: Final Hardening and Package

Run `skill-hardening` in final readiness mode.

Confirm:

- target validates;
- support files are integrated;
- scripts have safe interfaces;
- security risks are addressed or logged;
- package excludes caches, reports, secrets, old zips, and files outside target scope.

Package only when validation passes:

```bash
python <packager> <TARGET_SKILL_PATH> <OUTPUT_DIR>
```

The archive name must be `skill.zip`.

## Phase 10: Final Benchmark and Closure

Run final `skill-benchmark` with the same or comparable baseline evaluator. Then return to `skill-improver` for accept/reject closure.

Report:

- baseline versus final;
- delta;
- accepted hypotheses;
- rejected hypotheses;
- commands;
- pass ledger;
- final package path;
- remaining risks and next hypothesis.
