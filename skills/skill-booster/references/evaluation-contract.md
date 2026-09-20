# Evaluation Contract

Use before editing a target skill.

## Baseline record

```yaml
target: <path>
mode: <audit-only|plan-only|apply-optimization|validation-only|package>
evaluator: <command or specialist report>
evaluator_status: <executed|planned|blocked>
score: <number|null>
gates:
  - {name: <gate>, status: <pass|fail|planned|blocked>}
reproducibility:
  state: <invoke-audit|invoke-apply|not-applicable|blocked|unavailable|planned>
  selected_mode: <audit-only|apply|none>
  specialist_status: <invoked|not-applicable|blocked|unavailable|planned>
  downstream_owner: <skill-improver|reproducibility-engineer|none>
  material_signals: []
  decision_validation: <pass|fail|planned|blocked>
hypothesis_discovery:
  policy: <required|advisory|not-available>
  status: <pass|pass-with-warnings|no-mutation-recommended|planned|blocked>
  generated_count: <number|null>
  selected_for_current_cycle: []
change_gate:
  policy: <required|advisory|not-available>
  status: <pass|pass-with-warnings|fail|insufficient-evidence|planned|blocked>
  blocking_regressions: []
blocked_paths: [.git, secrets, credentials, fixtures, expected_outputs, benchmark_baselines, generated_evidence, old_zips]
hosts:
  requested: [portable-core]
  capabilities: {}
  python_launcher: <resolved command|null>
  portability_validation: <pass|fail|planned|blocked>
source_integrity:
  manifest: <path|null>
  snapshot_identity_sha256: <sha256|null>
  pinned_revision: <revision|null>
  verification: <pass|fail|not-applicable|planned|blocked>
```

## Freeze rules

After baseline, do not change scenarios, expected outputs, evaluator scripts, scoring config, benchmark inputs, fixtures, generated baseline reports, or metric logic to make results pass. If evaluator design is itself in scope, normalize it as a separate hypothesis and state whether criteria changed or only schema/compatibility changed. When external files or repository evidence materially determine the experiment, capture exact source bytes before analysis and keep that source identity frozen as well.

After the last passing final gate, freeze the candidate content with `scripts/freeze_candidate.py`. Any later target edit invalidates final evidence and requires affected validation plus a new manifest. Packaging must verify the same frozen candidate immediately before archive creation.

## Reproducibility decision contract

Evaluate `references/reproducibility-routing.md` after initial benchmark/harness evidence and before `skill-hypothesis-discovery`. Create a JSON decision record and validate it with:

```text
<PYTHON> scripts/validate_reproducibility_decision.py <DECISION_JSON>
```

Rules:

- `invoke-audit`: actual `reproducibility-engineer` invocation in `audit-only`; findings feed hypothesis discovery; normal downstream patch owner is `skill-improver`.
- `invoke-apply`: actual invocation in `apply`; use only for an explicit reproducibility objective or already selected bounded reproducibility hypothesis; downstream owner is `reproducibility-engineer` for that batch only.
- `not-applicable`: no material controllable variance remains; requires evidence and no material signals in the decision record.
- `blocked`/`unavailable`: preserve applicable signal evidence but do not claim specialist execution.
- A checklist review is never equivalent to specialist invocation.

Do not invoke merely because the target has scripts, evals, validators, or a complex workflow. The specialist must remove an observed source of variance or add useful evidence.

## Pre-evolution state contract

For complete optimization, keep an external work-state record that can later support multi-candidate comparison without changing the target package. Use the templates from `assets/templates/` and validate them with `scripts/validate_pre_evolution_state.py`.

Required semantics when the artifact is material:

- capability map: semantic capabilities, owners, consumers, validators, invariants;
- transformation registry: bounded changes classified as `repair`, `optimization`, or `experiment` and tied to capability/evidence ids;
- experiment registry: parent/candidate/transformation/evaluator identities plus outcome, including rejected/inconclusive candidates;
- evaluation plan: staged `L0` through `L5` ladder and promotion evidence requirement.

These are experiment-state artifacts, not benchmark fixtures. Keep them outside the candidate mutation surface so a candidate cannot rewrite its own history or acceptance evidence.

Cross-run experiment history may influence discovery only as provenance-bound evidence. Do not convert a previous target's result into a universal policy without comparable target class, capability surface, evaluator contract, and environment.

## Metrics

Prefer multiple signals: structure validity, requested-host portability, host capability resolution, reproducibility decision/result, `skill-hypothesis-discovery` backlog quality, `skill-change-gate` status, activation coverage, output-contract adherence, local-link integrity, script smoke status, security findings, contradiction count, package status, final candidate hash, archive hash, total/local token deltas, and benchmark score. Treat saturated scores as gates; add auxiliary metrics such as unresolved risks, local token regressions, scenario coverage, unreferenced resources, or package gates.

## Skill-hypothesis-discovery contract

Use `skill-hypothesis-discovery` after initial benchmark/harness and reproducibility-routing evidence when possible. It must generate evidence-backed hypotheses, not random edits. A normal full-optimization pass should produce 5-10 candidate hypotheses, dedupe and rank them, and recommend the next 1-3 for the current cycle. Reproducibility audit findings, when present, are candidate evidence rather than automatically accepted patches. If no useful mutation is justified, record `no-mutation-recommended` and avoid experimental patches unless the user supplies a concrete hypothesis or a required repair exists.

```yaml
hypothesis_discovery_result:
  status: <pass|pass-with-warnings|no-mutation-recommended|applied-by-checklist|blocked>
  generated_count: <number>
  selected_count: <number>
  top_hypotheses: []
  no_mutation_rationale: <string|null>
  evidence_sources: []
```

## Hypothesis record

```yaml
id: H1
statement: <if we change x, y improves because z>
owner: <skill-improver|reproducibility-engineer|other>
files: []
expected_effect: <metric/gate>
validation: <command/scenario>
status: <accepted|rejected|blocked|planned>
evidence: <score, gates, or rationale>
```

Accept only when the hypothesis came from the discovery backlog or was explicitly supplied/justified, required gates pass, `skill-change-gate` reports no blocking regression, blocked/frozen paths are protected, no activation/safety/output regression appears, and required metrics meet the threshold. Reject or revert when gates fail, score worsens without accepted trade-off, compression removes protected duties, scope expands beyond target, or a duplicated owner attempts to mutate the same batch independently.

## Skill-change-gate contract

Use `skill-change-gate` as an acceptance gate for material candidate patches, including reproducibility `apply` batches, and as a final regression gate after hardening or token compression. When the specialist is unavailable, apply its checklist locally and mark the pass `applied-by-checklist`; do not mark it `pass` unless the specialist actually ran or equivalent deterministic evidence was inspected.

```yaml
change_gate_result:
  policy: <required|advisory>
  status: <pass|pass-with-warnings|fail|insufficient-evidence|applied-by-checklist|blocked>
  decision_for_caller: <accept|reject|repair-before-accept|gather-evidence|advisory-only>
  blocking_regressions: []
  material_concerns: []
  accepted_tradeoffs: []
```

For full optimization, use `required` policy by default. A blocking regression prevents acceptance even when a benchmark score improves. `pass-with-warnings` may proceed only when material concerns are documented as accepted trade-offs or follow-up hypotheses.

## Final delivery contract

The final delivered archive must correspond to the final frozen candidate. Record:

```yaml
final_delivery:
  candidate_manifest: <path>
  freeze_verification: <pass|fail>
  candidate_sha256: <sha256>
  archive: <path>
  archive_sha256: <sha256>
  receipt_version: <number>
  receipt_stage: <committed|failed>
  atomic_replace: <true|false>
  last_good_preserved_on_failure: <true|false>
  recovery: []
  package_validation: <pass|fail>
```

Do not claim final readiness when the target was edited after freeze, freeze verification failed, material source identity changed without explicit re-baselining, requested-host portability failed, package/report path preflight failed, packaging failed, last-known-good preservation failed, rollback recovery was discarded, or the package receipt does not match the delivered archive.
