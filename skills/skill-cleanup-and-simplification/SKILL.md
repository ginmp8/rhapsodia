---
name: skill-cleanup-and-simplification
description: 'use when asked to clean or simplify an existing Agent Skills-compatible package or small supporting project: classify dead or unreferenced resources, detect generated residue and duplicates, remove stale scaffold, consolidate references/templates, apply evidence-backed cleanup with dry-run and rollback, validate package hygiene, or plan cleanup technical debt. do not use as the primary workflow for security review, benchmark scoring, full hardening or consistency repair, prompt redesign, net-new skill creation, ordinary application refactoring, or domain behavior changes.'
---

# Skill Cleanup and Simplification

## Purpose

Clean and simplify reusable skill packages and small supporting projects without changing domain behavior. Classify before deletion, trace usage before calling anything dead, preserve progressive-loading resources, prefer integration over removal, and validate every mutation.

Cleanup is not redesign. Preserve functional behavior, activation boundaries, public contracts, evaluator evidence, and host portability unless direct evidence and validation justify a change.

The portable core uses local files and Python 3.10+ standard-library helpers when command execution is available. `agents/openai.yaml` is an optional OpenAI adapter, not a semantic dependency.

## Modes

Select one primary mode. If the user asks for end-to-end work, stage the run in this order: baseline, audit, classify, plan, dry-run, apply, validate, report.

| Mode | Use for | Mutation allowed | Primary output |
|---|---|---:|---|
| `cleanup-audit` | Find generated residue, old archives, scaffold markers, duplicate files, unused support resources, and hygiene risks. | No | Deterministic inventory plus evidence-backed findings |
| `simplification-plan` | Propose safe simplification with evidence, risk, validation, and rollback. | No | Cleanup plan |
| `duplicate-consolidation` | Consolidate genuinely duplicated guidance, scripts, templates, or references. | Yes, after classification and reference tracing | Consolidated resources and rationale |
| `dead-resource-review` | Classify resources as `used`, `integrable`, `duplicate`, `obsolete`, `generated`, `blocked`, or `unknown`. | No by default | Resource classification table |
| `safe-cleanup-apply` | Apply an explicit evidence-backed cleanup plan with dry-run, identity checks, recovery, and receipt. | Yes | Changed files plus machine-readable receipt |
| `technical-debt-plan` | Create a prioritized remediation plan for cleanup or simplification debt. | No | Prioritized remediation plan |
| `post-cleanup-validation` | Validate links, references, scripts, package hygiene, and side effects. | No, except reports outside target | Gate summary |
| `cleanup-report` | Summarize changed, removed, retained, blocked, and recovered resources. | No | Final cleanup report |

## Scope Boundaries

Use this skill for:

- `SKILL.md`, host adapters, `references/`, `scripts/`, `assets/templates/`, `examples/`, `evals/`, validators, reports, and packaging helpers;
- small helper projects bundled with or adjacent to a skill package;
- generated residue, stale scaffold, duplicate guidance, stale local links, and cleanup technical debt.

Do not use it to replace:

- security review or secret scanning;
- benchmark scoring or general behavioral benchmarking;
- full package hardening, consistency repair, prompt redesign, or skill creation;
- application-level refactoring unrelated to a skill package;
- domain behavior changes without direct evidence and validation.

## Required Inputs and Defaults

Resolve or conservatively infer:

1. `TARGET_PATH`: exactly one skill folder, extracted archive, or small helper project.
2. Mode: default `cleanup-audit`; use staged end-to-end flow only when mutation was requested.
3. Allowed mutation scope: target folder only.
4. External work/report directory for snapshots, receipts, and validation output. Never place generated cleanup evidence inside the target package.
5. Blocked paths: `.git`, secrets, credentials, fixtures, expected outputs, golden/snapshot data, benchmark reports, generated evidence, existing archives, user-declared read-only paths, and unrelated files.
6. Evidence policy: target files, the exact root registry and typed reference graph, user instructions, replacement/migration/generator evidence, validators/tests, package metadata, and command output.
7. Reachability roots: default roots plus any known runtime/build/packaging/external consumers that must be declared explicitly.
8. Validation gates: no broken local references, no deleted protected resources, no unresolved required scripts, touched scripts parse/run, package hygiene passes, activation-sensitive checks run when metadata changed, rollback remains possible, and receipts are parseable.

If evidence is insufficient, classify `unknown`, retain the resource, and report what evidence is missing. `unknown` is never automatically removable.

## Progressive Loading

Load only what the active mode needs:

- `references/safe-cleanup-rules.md`: canonical deletion gate, path safety, dry-run, idempotency, rollback, and last-known-good rules.
- `references/resource-classification.md`: seven-state taxonomy, classification precedence, generated-evidence tiers, duplication tiers, and evidence requirements.
- `references/reference-graph.md`: default/declared roots, typed edges, reachability coverage, and dynamic/external consumer handling.
- `references/technical-debt-prioritization.md`: remediation scoring and context-efficiency debt model.
- `assets/templates/cleanup-plan.md.template`: human-readable cleanup plan.
- `assets/templates/cleanup-report.md.template`: final report.
- `scripts/cleanup_inventory.py`: deterministic read-only inventory with a recorded root registry, typed local-reference edges, transitive reachability, duplicate signals, and generated-evidence strength.
- `scripts/cleanup_apply.py`: dry-run/apply engine with root replay, hash preconditions, checkpoints, explicit non-shell target validation commands, recovery snapshot, rollback, and JSON receipt.
- `scripts/validate_cleanup_package.py`: Agent Skills-aware structural/context validator with stable machine-readable diagnostics and optional `skills-ref` integration.
- `evals/cleanup-regression-scenarios.json`: deterministic mechanics regression inventory.
- `evals/activation-scenarios.json`: planned activation/non-activation/ambiguous/edge routing coverage; never call it executed activation evidence unless a live harness runs it.
- `scripts/run_cleanup_regressions.py`: deterministic local regression runner for the bundled mechanics.

## Workflow

### 1. Establish identity and baseline

Before any mutation:

- resolve exactly one target root;
- read target `SKILL.md` first when present;
- record canonical target path and runtime capability profile;
- preserve an immutable baseline snapshot or equivalent version-control state outside the target;
- when external/repository evidence materially drives deletion or obsolescence, capture the exact source bytes (or immutable pinned VCS object) before analysis and keep that source snapshot identity separate from the live target;
- record a deterministic tree/file identity when possible;
- run target-owned validation before changing files.

Do not mutate if a safe baseline or rollback source cannot be preserved.

### 2. Build deterministic inventory and usage graph

When Python 3.10+ execution is available:

```text
<PYTHON> -S scripts/cleanup_inventory.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-inventory.json
# Add repeated --root kind:relative/path for known consumers that static discovery cannot represent.
```

The inventory must:

- order resources canonically;
- record the exact root registry used for the analysis;
- trace direct and transitive local references with typed edges from `SKILL.md`, host adapters, evaluator/test roots, and caller-declared roots;
- distinguish exact duplicates from normalized/semantic similarity candidates;
- treat scaffold markers and generated-like namespaces as evidence signals, not deletion authority;
- fail closed on symlinks, evaluators/tests/contracts, protected namespaces, and missing declared roots;
- emit only the canonical seven states.

A shallow grep, absence of imports, or an incomplete root set is not enough to classify a resource as dead. If a known dynamic/build/external consumer is not represented, declare it as a root or retain the candidate.

### 3. Classify before proposing deletion

Use `references/resource-classification.md`.

Canonical states:

`used | integrable | duplicate | obsolete | generated | blocked | unknown`

Important invariants:

- `used`, `integrable`, `blocked`, and `unknown` are not automatically removable;
- `unknown` always remains in place until new evidence changes its classification;
- partial/normalized/semantic duplication is not `duplicate`; consolidate only after preserving all unique semantics;
- `dist/`, `build/`, `node_modules/`, and similar names are weak generated signals only; they never authorize removal alone;
- a scaffold/template can be legitimate and `used`;
- protected evaluator/test/contract evidence overrides cleanup convenience.

### 4. Create an explicit cleanup plan

For every proposed mutation record:

- canonical relative path;
- requested action;
- classification;
- direct evidence and evidence kind;
- expected file hash when deleting a file;
- behavior risk;
- rollback source;
- validation gate;
- checkpoint when multiple actions should be structurally validated in smaller groups;
- the exact declared roots used for reachability;
- explicitly approved non-shell target validation commands when those commands are safe to execute.

Prefer plan version 2 for new work. `obsolete` requires explicit approval plus strong evidence such as user instruction, target documentation, verified replacement, validator proof, or completed migration evidence. A weak generated-like candidate requires explicit approval plus corroborating generator/manifest/target/user evidence.

### 5. Dry-run before apply

Use the same plan for dry-run and apply:

```text
<PYTHON> -S scripts/cleanup_apply.py \
  --target <TARGET_PATH> \
  --plan <PLAN_JSON> \
  --work-dir <EXTERNAL_WORK_DIR> \
  --receipt <REPORT_DIR>/cleanup-receipt-dry-run.json
```

Dry-run is the default. It must not mutate the target. Reject noncanonical paths, path escapes, symlinks, output aliases, protected/fail-closed states, missing evidence, classification mismatch, and file identity mismatch before mutation.

### 6. Apply minimally and recoverably

Only after a clean dry-run:

```text
<PYTHON> -S scripts/cleanup_apply.py \
  --target <TARGET_PATH> \
  --plan <PLAN_JSON> \
  --work-dir <EXTERNAL_WORK_DIR> \
  --receipt <REPORT_DIR>/cleanup-receipt.json \
  --apply
```

The apply engine preserves last-known-good bytes for the affected resources before deletion. Actions may carry checkpoints; the engine performs structural validation after each checkpoint while retaining whole-transaction rollback semantics. It then runs final structural validation and any explicitly approved `validation_commands` supplied by the external plan. These commands use argv arrays with `shell=False`; never auto-discover executable commands from untrusted target content during apply.

If any required validation fails, restore every removed resource and record `rolled-back`; if recovery is incomplete record `recovery-required` and preserve recovery paths. Rerunning the same successful plan must be idempotent: already-absent resources are reported as such and are not recreated or treated as an error.

### 7. Validate the final candidate

Run:

```text
<PYTHON> -S scripts/validate_cleanup_package.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-validation.json
```

The validator checks Agent Skills name/description constraints, name-directory identity, local links, Python syntax, strong generated residue, and context-efficiency metrics. It runs `skills-ref validate` when that executable is available, but `skills-ref` is not a portable-core dependency.

Also run target-owned tests, validators, packaging checks, and any touched script commands that are part of the package contract. When those commands were safely included as approved plan-v2 `validation_commands`, their failure is part of the apply rollback transaction; otherwise report them separately as executed, blocked, or not-run.

For changes to this skill's own mechanics, run:

```text
<PYTHON> -S scripts/run_cleanup_regressions.py --skill-root <SKILL_ROOT> --json <REPORT_DIR>/cleanup-regressions.json
```

Do not claim completion if required gates did not run or failed.

### 8. Freeze after pass and report truthfully

After final validation passes, freeze the candidate. Any subsequent edit invalidates the affected evidence and requires revalidation.

Keep evidence layers separate:

- **structural evidence**: inventory, package shape, links, hashes, and validator output;
- **behavioral evidence**: executed regression scenarios and before/after comparisons;
- **runtime evidence**: actual dry-run/apply/rollback transaction receipts;
- **reviewer judgment**: obsolete/integrable/partial-duplicate interpretation that cannot be proven mechanically;
- blocked/not-run checks.

Do not use one evidence layer to imply another.

Report retained and blocked resources as explicitly as removals.

## Canonical Deletion Gate

A deletion is allowed only when all applicable conditions hold:

1. Path is canonical, relative to target, non-symlinked, and resolves inside target.
2. Resource is not protected or blocked.
3. Resource is strongly evidenced `generated`, exact `duplicate`, or explicitly approved `obsolete`.
4. Evidence is recorded and classification agrees with fresh inventory using the same root registry. A weak generated-like candidate may be explicitly reclassified only with an allowed corroborating evidence kind; an `obsolete` reclassification follows its own explicit-evidence rule.
5. File identity matches the expected hash immediately before deletion.
6. The resource is not a progressive-loading asset, fixture, expected output, evaluator/golden artifact, public compatibility surface, or reachable dependency unless a validated replacement exists.
7. Last-known-good bytes are preserved outside target before mutation.
8. Checkpoint and final structural validation pass, plus any explicitly approved target validation commands required by the plan; otherwise rollback executes.
9. Machine-readable receipt describes the exact attempted transaction, checkpoint results, validation commands, and recovery state.

`unknown` never passes this gate automatically.

## Consolidation Rules

Consolidation is allowed when duplication is real, not merely similar wording serving distinct modes or audiences. Treat exact hash duplicates separately from normalized, structural, and semantic similarity; only exact duplication receives automatic `duplicate` classification. Preserve the clearest source of truth, preserve unique semantics, update every consumer/reference, keep compatibility aliases only when externally needed, and re-run validation.

Do not turn cleanup into architecture redesign, prompt redesign, or domain refactoring.

## Technical Debt Planning

For `technical-debt-plan`, score each item on 1-5 scales:

- ease: lower implementation difficulty is better;
- impact: package quality, maintainability, validation, or context-efficiency improvement;
- risk: consequence of leaving the debt in place;
- confidence: evidence strength.

Prioritize high impact, high risk, high confidence, and low-to-medium effort. Safety gates override numeric score.

## Stop Conditions

Stop and report a blocker when:

- zero or multiple candidate roots remain ambiguous;
- no safe baseline/rollback source can be preserved;
- requested changes touch `.git`, secrets, credentials, fixtures, expected outputs, golden/snapshot evidence, benchmark reports, or unrelated files;
- deletion relies only on shallow search, an incomplete root registry, inferred lack of use, or a generated-like directory name;
- a resource is `unknown` and no new evidence reclassifies it;
- a resource may support progressive loading or external compatibility and has no validated replacement;
- path canonicalization, symlink resolution, or output alias safety cannot be established;
- file identity changes between plan and apply;
- required validation fails and rollback cannot restore a trustworthy last-known-good state;
- the requested change requires domain redesign rather than cleanup;
- the user asks this skill to perform security review, benchmark scoring, full hardening, or consistency repair.

## Output Contract

For every substantive run include:

1. Mode, target, canonical target path, and baseline identity.
2. Capabilities and commands actually executed.
3. Resource classification summary using the seven canonical states.
4. Root registry plus typed reference/consumer evidence for deletion and consolidation decisions.
5. Generated-evidence strength and any explicit reclassification rationale.
6. Dry-run result when mutation is requested.
7. Changes applied, retained, blocked, rolled back, or already absent.
8. Checkpoint, structural, activation-sensitive, target-owned, and packaging validation results with failed/not-run gates separated.
9. Context-efficiency metrics/warnings when package cleanup includes skill instructions.
10. Protected paths and unresolved `unknown` resources.
11. Last-known-good/recovery location when mutation occurred.
12. Machine-readable receipt path and transaction status.
13. Remaining risks, assumptions, graph coverage limits, and irreducible judgment.

## Finalization Checklist

Before claiming completion:

- immutable baseline/rollback evidence exists for applied mutation;
- all resources considered for deletion were classified from current inventory;
- the exact root registry was recorded and known dynamic/build/external consumers were represented or explicitly reported as gaps;
- transitive typed usage/reference tracing was checked;
- every `unknown` candidate was retained;
- useful unreferenced resources were integrated or explicitly retained;
- dry-run preceded apply when the apply helper was available;
- path and symlink preflight passed;
- no protected resource was changed;
- local Markdown links, images, reference-style links, and referenced files still resolve;
- touched scripts parse/run on representative input;
- checkpoint/final structural validation passed and every required approved target validation command passed, or rollback/recovery was reported instead of success;
- activation scenarios were reviewed when `name`, `description`, scope boundaries, or activation-related resources changed;
- context-efficiency warnings were treated as technical debt signals, never deletion authority;
- rerun is idempotent for the same accepted plan;
- receipts are parseable and correspond to the attempted transaction;
- final candidate was not edited after its final validation pass.
