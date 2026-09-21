# Optimization Workflow

Use this workflow for every target skill. It is organized into six canonical phases. The specialist passbook is a ledger within these phases, not a second architecture. If a stop condition applies, report the blocker instead of editing the target.

## Phase 1: Establish

Capture target path/archive, source class, target class, mode, objective, final artifact, writable/protected scope, evaluator, requested hosts, runtime capabilities, and user-declared read-only files.

For `external-untrusted-skill`, run the Booster-owned static intake before executing target code:

```text
<PYTHON> scripts/inspect_external_skill.py --target <TARGET_OR_ARCHIVE> --json <WORK>/external-intake.json
```

Then run structural/portability preflight as applicable:

```text
<PYTHON> scripts/validate_skill_booster.py --target <TARGET_SKILL_PATH>
<PYTHON> scripts/validate_portability.py --target <TARGET_SKILL_PATH> --hosts <HOSTS>
```

Preserve an immutable baseline and freeze evaluator/scenario/expected-output/metric inputs before target transformation. Snapshot material external source bytes when they affect the decision. Build or consume a capability map when the target is complex, baseline/candidate capability preservation is material, or a change may remove/transfer behavior. Keep the map in the work/evidence area, not inside the target unless the target owns such a contract.

## Phase 2: Diagnose

Run evidence providers against the frozen baseline. Providers are read-only/audit/checklist by default in this phase.

Required early evidence normally includes initial `skill-benchmark`, `skill-harness`, and the reproducibility-routing decision. Then select the additional providers material to the target class and surfaces: capability/quality review, package architecture, context impact, activation/prompt, consistency, documentation, code, security, testing, cleanup, and token/context analysis.

The purpose is to collect evidence before change selection. Do not run `skill-hypothesis-discovery` before material diagnostic providers whose findings are expected to influence the backlog.

A provider may identify a required repair, but that does not grant transformation authority. Record findings with stable evidence ids and affected capability ids when known.

## Phase 3: Select and strategy gate

Reconcile evidence by criterion owner. Classify each proposed change as exactly one of:

- `repair` - demonstrated defect/contract break;
- `optimization` - predeclared measurable improvement on an active metric;
- `experiment` - bounded unproven hypothesis.

Run `skill-hypothesis-discovery` when a hypothesis backlog is needed. A demonstrated repair with a sufficiently known correction does not need to be reframed as an experiment merely to enter the workflow.

Choose the least complex execution strategy:

- `direct-repair` for a known defect and known correction;
- `single-candidate` for a clear bounded optimization/experiment;
- `evolutionary-search-eligible` only when multiple materially different alternatives are plausible and search is justified by evaluator quality and budget.

Eligibility never activates evolutionary execution. If `evolutionary-optimization` was not explicitly selected, continue through the canonical direct/single-candidate path.

Before transformation record as applicable:

- finding or hypothesis id;
- transformation id;
- change intent;
- selected strategy;
- baseline/control identity;
- affected capabilities/files;
- expected effect;
- frozen evaluator/acceptance rule;
- rollback;
- declared transformation owner.

Required repairs may proceed even when the correct claim is "repair completed" rather than "measured improvement".

## Phase 4: Transform

Use an isolated candidate when material risk warrants it. Exactly one owner changes each transformation batch.

Default owner is `skill-improver`. `reproducibility-engineer` owns an `invoke-apply` reproducibility batch only for that selected bounded transformation. Another specialist may own a batch only when the caller explicitly delegates it and the specialist contract allows target changes.

Evidence providers must not silently apply unrelated fixes after selection. New findings discovered during transformation become new evidence/hypotheses unless they are necessary to make the selected batch valid.

## Phase 5: Evaluate

Evaluate the candidate against the same frozen evidence using the staged ladder:

1. `L0-structural` - identity, package shape, references, protected paths, schemas/syntax.
2. `L1-deterministic` - target validators/tests/static contracts.
3. `L2-focused` - selected-change scenarios/metrics and touched-capability checks.
4. `L3-harness` - broader regression/adversarial execution when warranted.
5. `L4-benchmark` - full comparable baseline/control/candidate benchmark when an improvement claim warrants it.
6. `L5-holdout` - independent/evaluator-only holdout for promotion claims exposed to overfitting risk.

A required lower-level failure blocks escalation. `skill-change-gate` is required for material candidate acceptance. Record an experiment only when the selected change is actually experimental or the run compares multiple alternatives. Use ablation only for a real attribution question.

Validate canonical optimization artifacts when present:

```text
<PYTHON> scripts/validate_optimization_state.py \
  --capability-map <WORK>/capability-map.json \
  --transformation-registry <WORK>/transformation-registry.json \
  --evaluation-plan <WORK>/evaluation-plan.json
```

Add `--experiment-registry <WORK>/experiment-registry.json` only when experiments or multi-candidate comparisons actually produced that artifact.

## Phase 6: Prove

After candidate acceptance, run affected hardening/validation, final `skill-change-gate`, final benchmark and holdout only at the evidence level required by the claim, token/readiness closure, source/evaluator identity verification, and portability closure.

For `complete` / `full` optimization, completion also requires terminal disposition of every material actionable finding from Diagnose and final closure: `fixed`, `rejected`, `accepted-trade-off`, `blocked`, or `not-applicable`. Material findings may not remain only `follow-up`, `planned`, `deferred`, or otherwise unclassified while the run is reported complete. If final token-efficiency closure finds material avoidable context waste, open another bounded transformation batch with one owner, rerun affected gates, and continue until that finding has a terminal disposition.

Freeze the exact final candidate:

```text
<PYTHON> scripts/freeze_candidate.py freeze --target <TARGET_SKILL_PATH> --out <WORK>/candidate-manifest.json
<PYTHON> scripts/freeze_candidate.py verify --target <TARGET_SKILL_PATH> --manifest <WORK>/candidate-manifest.json
```

Any later target edit invalidates affected evidence and requires revalidation/re-freeze.

Package only the frozen candidate with recovery-aware atomic delivery. Preserve last-known-good package/receipt on failure. Keep target promotion separate from workflow-policy promotion: results from this target may become advisory history for later optimization, but they must not silently rewrite the Booster's canonical policy.

## Historical evidence rule

Persist current-run transformation history. Persist experiment history only for actual experiments or multi-candidate comparisons. Cross-run history may inform change priority only when provenance is retained. Scope relevance by target class, capability surface, evaluator contract, and environment. A prior win/loss is evidence, not a universal rule.

## Evolutionary mode boundary

Canonical optimization must work without Skill Evolution, search-state artifacts, lineage metadata, or search-specific fields in downstream specialist contracts. Evolutionary readiness is not a completion criterion for canonical optimization.

Population search is never entered implicitly. When `evolutionary-optimization` is explicitly selected, branch to `references/evolutionary-search-routing.md` after Establish/Diagnose/Select. Keep the canonical strategy/result as comparator. Search-controller-specific state stays at that boundary; target transformation, evaluation, final freeze, promotion, and packaging remain owned by the existing Booster workflow. After finalists return, rejoin Evaluate/Prove and run independent final gates.
