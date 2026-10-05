---
name: skill-cleanup-and-simplification
description: 'Use when the primary task is to clean or simplify an existing Agent Skills-compatible package or small supporting project: classify dead or unreferenced resources, remove proven generated residue, consolidate real duplicates, eliminate stale scaffold, or plan cleanup debt without changing domain behavior. Do not use as the primary workflow for security review, benchmark scoring, full hardening, consistency repair, prompt redesign, token-only compression, net-new skill creation, ordinary application refactoring, or domain behavior changes.'
---

# Skill Cleanup and Simplification

## Purpose and routing

Clean skill packages without changing what they own or how they behave. The core job is evidence-backed removal, consolidation, integration, and cleanup planning: classify first, trace consumers before declaring anything dead, preserve progressive-loading resources, and validate every mutation.

Use this skill when cleanup/simplification is the primary objective. Route security findings to a security skill, cross-file contradictions or ownership drift to consistency repair, package-wide release/readiness work to hardening, and instruction/token compression whose primary goal is context reduction to a token-efficiency skill.

Cleanup is not redesign. Preserve activation boundaries, public contracts, evaluator evidence, expected behavior, and host portability unless direct evidence plus validation authorize a change. The portable core uses local files and Python 3.10+ standard-library helpers; `agents/openai.yaml` is optional adapter metadata.

## Mode router

Choose one primary mode. For end-to-end mutation use: baseline -> inventory -> classify -> plan -> dry-run -> apply -> validate -> freeze/report.

| Mode | Use for | Mutation |
|---|---|---:|
| `cleanup-audit` | Inventory residue, stale scaffold, duplicate candidates, unused support resources, and hygiene debt. | No |
| `simplification-plan` | Propose bounded cleanup with evidence, risk, validation, and rollback. | No |
| `duplicate-consolidation` | Merge proven duplicate guidance/scripts/templates while preserving unique semantics and consumers. | Yes |
| `dead-resource-review` | Classify resources as `used`, `integrable`, `duplicate`, `obsolete`, `generated`, `blocked`, or `unknown`. | No by default |
| `safe-cleanup-apply` | Apply an approved cleanup plan with identity checks, dry-run, recovery, validation, and receipt. | Yes |
| `technical-debt-plan` | Prioritize cleanup/context-efficiency debt without mutating. | No |
| `post-cleanup-validation` | Validate links, scripts, package shape, side effects, and required gates after change. | No |
| `cleanup-report` | Report changed, retained, blocked, rolled-back, and unresolved resources. | No |

## Critical rules

- Exactly one target root must be resolved before mutation; keep work reports, snapshots, receipts, and generated evidence outside the target.
- Build reachability from the recorded root registry and typed direct/transitive references before calling a resource dead. If known runtime/build/packaging/external consumers are not represented, declare them as roots or retain the candidate.
- Use only the canonical states: `used | integrable | duplicate | obsolete | generated | blocked | unknown`. `unknown` is fail-closed and is never auto-removable.
- Protection outranks cleanup: do not auto-edit/delete `.git`, secrets/credentials, fixtures, tests/evals, expected/golden/snapshot data, benchmark/evaluator evidence, archives, symlinks, user read-only paths, or unrelated files.
- Generated-looking names such as `dist/`, `build/`, `coverage/`, or `node_modules/` are weak signals only. Strong generation evidence or explicit corroboration is required.
- Only byte-identical content may be mechanically classified `duplicate`. Normalized, structural, or semantic similarity requires review and preservation of unique semantics.
- Before mutation preserve an immutable baseline/rollback source and file/tree identity. For external evidence that decides deletion/obsolescence, pin exact source bytes or an immutable VCS object.
- A deletion candidate must be canonical, inside target, non-symlinked, unprotected, classification-eligible, supported by fresh evidence, identity-matched immediately before deletion, and recoverable.
- `obsolete` needs explicit approval plus strong replacement/migration/target/user/validator evidence. Weak generated-like candidates need explicit approval plus corroborating generator/manifest/target/user evidence.
- Dry-run the exact plan before apply when the helper is available. Apply only the reviewed plan; do not discover extra deletions opportunistically during mutation.
- Target validation commands must be explicit approved argv arrays, bounded by timeout, executed with `shell=False`, and never auto-discovered from untrusted target content during apply.
- Any required checkpoint/final validation failure triggers whole-transaction rollback. If recovery is incomplete, report `recovery-required`; never claim success from stale evidence.
- Preserve behavior, activation, public contracts, evaluators, and expected outputs. If a requested change needs redesign, prompt rewrite, security remediation, or domain refactoring, stop or hand off instead of expanding scope.
- Keep structural, behavioral, runtime-transaction, and reviewer-judgment evidence separate. A pass in one layer does not imply another.
- Freeze the final passing candidate. Any later material edit invalidates affected evidence and requires revalidation.

## Quick-start workflow

1. **Establish:** resolve target, mode, writable/protected scope, external work directory, known external/dynamic consumers, runtime capabilities, and required gates.
2. **Baseline:** preserve immutable rollback evidence, target identity, and target-owned pre-change validation when safe/available.
3. **Inventory:** run `scripts/cleanup_inventory.py`; record the exact root registry, typed edges, transitive reachability, duplicate tiers, and generation signals.
4. **Classify:** apply the seven-state taxonomy. Retain `unknown`; prefer integrating useful unreferenced resources over deleting them.
5. **Plan:** record each mutation path, action, state, evidence kind, expected hash, rollback source, checkpoint, validation gate, declared roots, and approved validation commands. Prefer plan v2.
6. **Dry-run:** execute `scripts/cleanup_apply.py` without `--apply`; reject path/identity/classification/root/protection mismatches before mutation.
7. **Apply:** rerun the same plan with `--apply`; preserve last-known-good bytes, validate checkpoints/final state, and roll back the whole transaction on required failure.
8. **Prove:** run `scripts/validate_cleanup_package.py`, target-owned gates, and mechanics regressions when this skill itself changed; freeze exact passing bytes and report retained/blocked resources as explicitly as removals.

## Direct resource map

All required Markdown is directly reachable from this file; nested links are navigation only, never the sole route to required rules.

- [`references/safe-cleanup-rules.md`](references/safe-cleanup-rules.md): load before deletion/apply decisions; owns deletion eligibility, protected paths, plan-v2 safety, validation-command rules, transactions, idempotency, rollback, and receipts.
- [`references/resource-classification.md`](references/resource-classification.md): load when deciding `used/integrable/duplicate/obsolete/generated/blocked/unknown`; owns precedence, evidence strength, generated signals, and duplicate tiers.
- [`references/reference-graph.md`](references/reference-graph.md): load when reachability may miss runtime/build/packaging/external consumers; owns default/declared roots, typed edges, coverage limits, and root identity.
- [`references/technical-debt-prioritization.md`](references/technical-debt-prioritization.md): load only for cleanup/context-efficiency debt prioritization; owns scoring and safety-over-score rules.
- `scripts/cleanup_inventory.py`: deterministic read-only inventory and reference graph.
- `scripts/cleanup_apply.py`: plan preflight, dry-run/apply, checkpoints, recovery, rollback, and JSON receipt.
- `scripts/validate_cleanup_package.py`: structural/package/context validator; it does not prove behavioral correctness.
- `scripts/run_cleanup_regressions.py` + `evals/cleanup-regression-scenarios.json`: deterministic mechanics regression suite.
- `evals/activation-scenarios.json`: planned routing coverage only; never call it executed evidence unless a live harness runs it.
- `assets/templates/cleanup-plan.md.template` and `assets/templates/cleanup-report.md.template`: durable human-readable outputs.

## Required inputs and evidence model

Resolve or conservatively infer:

1. `TARGET_PATH`: exactly one skill folder, extracted archive, or small helper project.
2. Primary mode; default to `cleanup-audit` unless mutation was requested.
3. Allowed mutation scope; default to the target folder only.
4. External work/report directory for baselines, receipts, and validation output.
5. Protected paths and user-declared read-only resources.
6. Exact root registry: default roots plus known runtime/build/packaging/external consumers.
7. Evidence available for replacement, migration, generation, duplication, and obsolescence claims.
8. Required validation gates and safe approved target validation commands, if any.

If evidence is insufficient, classify `unknown`, keep the resource, and state what evidence is missing. A shallow grep, missing import, old timestamp, fill-marker-looking text, or unreferenced path alone never proves removal safety.

## Execution details

### 1. Establish baseline

Read the target `SKILL.md` first when present. Record canonical target path, capabilities, protected scope, deterministic identity, and pre-change validation. Do not mutate if a trustworthy rollback source cannot be preserved.

### 2. Build inventory and usage graph

When Python 3.10+ execution is available:

```text
<PYTHON> -S scripts/cleanup_inventory.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-inventory.json
# Add repeated --root kind:relative/path for known consumers static discovery cannot represent.
```

Inventory must record canonical resources, exact roots, typed edges, transitive reachability, exact-duplicate signals, generated-evidence strength, and only the seven canonical states. Missing declared roots, unsafe symlinks, evaluators/tests/contracts, and protected namespaces fail closed.

### 3. Classify and select actions

Follow [`references/resource-classification.md`](references/resource-classification.md). `used`, `integrable`, `blocked`, and `unknown` are not automatically removable. A scaffold/template can be legitimate and `used`. Protected evaluator/test/contract evidence overrides cleanup convenience.

### 4. Build plan v2

For each mutation record canonical path, action, classification, evidence, expected SHA-256 when deleting, behavior risk, rollback source, checkpoint, validation gate, exact declared roots, and any explicitly approved non-shell validation command. The plan declares intent; apply preflight must independently re-check live evidence.

### 5. Dry-run

```text
<PYTHON> -S scripts/cleanup_apply.py \
  --target <TARGET_PATH> \
  --plan <PLAN_JSON> \
  --work-dir <EXTERNAL_WORK_DIR> \
  --receipt <REPORT_DIR>/cleanup-receipt-dry-run.json
```

Dry-run must not mutate target bytes. Reject noncanonical/path-escape/symlink/output-alias risk, protected or fail-closed states, missing evidence, classification mismatch, root drift, and identity mismatch.

### 6. Apply recoverably

```text
<PYTHON> -S scripts/cleanup_apply.py \
  --target <TARGET_PATH> \
  --plan <PLAN_JSON> \
  --work-dir <EXTERNAL_WORK_DIR> \
  --receipt <REPORT_DIR>/cleanup-receipt.json \
  --apply
```

Preserve last-known-good bytes before deletion. Checkpoints localize failures but remain one transaction. Rerunning a successful plan must be idempotent: already-absent resources are reported, not recreated.

### 7. Validate and freeze

```text
<PYTHON> -S scripts/validate_cleanup_package.py --target <TARGET_PATH> --output <REPORT_DIR>/cleanup-validation.json
```

Also run target-owned tests/validators/package checks and touched-script commands when safe and required. For changes to this skill's mechanics:

```text
<PYTHON> -S scripts/run_cleanup_regressions.py --skill-root <SKILL_ROOT> --json <REPORT_DIR>/cleanup-regressions.json
```

Do not claim completion if a required gate failed or did not run. Freeze exact passing bytes; any later edit requires affected revalidation.

## Consolidation rules

Consolidate only when resources serve the same purpose and no unique semantic constraint remains. Exact hash equality may establish `duplicate`; normalized/structural/semantic similarity is review-only. Choose one clear source of truth, preserve unique semantics, update every consumer/link/path, retain compatibility aliases only when externally required, then rerun inventory and validation. Do not turn consolidation into architecture or prompt redesign.

## Technical-debt planning

For `technical-debt-plan`, score ease, impact, risk, and confidence from 1-5 using [`references/technical-debt-prioritization.md`](references/technical-debt-prioritization.md). Safety gates always override the numeric score. Context-efficiency metrics are diagnostics, never deletion authority.

## Stop conditions

Stop or return a bounded result when target identity is ambiguous; no safe baseline exists; protected resources would be edited; deletion depends only on weak/incomplete evidence; an `unknown` resource cannot be reclassified; progressive-loading/external compatibility may be affected without validated replacement; path/symlink/output safety is unprovable; identity changes between plan and apply; required validation fails; rollback cannot restore trust; or the requested work is really security review, benchmark scoring, full hardening, consistency repair, prompt/token redesign, or domain behavior change.

## Output contract

For substantive runs report: mode/target/baseline; capabilities and commands actually executed; seven-state classification summary; exact root registry and consumer evidence; generation/duplication evidence strength; dry-run result; applied/retained/blocked/rolled-back/already-absent resources; checkpoint/structural/activation-sensitive/target-owned/package validation; protected and unresolved `unknown` resources; recovery and receipt state; context-efficiency metrics when relevant; and residual risks, assumptions, coverage gaps, and reviewer judgment.

Use `measured` only for executed/supplied evidence. Planned activation scenarios, static inspection, and reviewer interpretation must remain labeled as such.

## Finalization checklist

Before claiming completion verify: immutable rollback evidence; fresh classification from the current inventory/root registry; dynamic/build/external consumer coverage or explicit gaps; transitive typed reference tracing; all `unknown` retained; useful unreferenced resources integrated or explicitly retained; dry-run before apply; canonical/symlink/output preflight; protected paths unchanged; local links resolve; touched scripts parse/run on representative input; required validations pass or rollback/recovery is reported; activation-sensitive checks run when routing metadata changed; receipts parse and bind to the attempted transaction; rerun idempotency where applicable; and no target edit occurred after the final passing validation/freeze.
