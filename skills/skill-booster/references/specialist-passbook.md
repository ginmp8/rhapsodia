# Specialist Passbook

Every complete Skill Booster run must execute, apply by checklist, or classify each pass below. The ordered ledger is grouped by the six canonical phases. Specialist names identify capabilities, not a vendor-private invocation API.

Status values: `pass`, `fail`, `blocked`, `not-run`, `not-applicable`, `applied-by-checklist`, `planned`.
Execution types: `invoked-skill`, `deterministic-script`, `checklist-only`, `blocked`, `unavailable`, `not-applicable`, `not-run`.

## Mutation ownership invariant

During `diagnose`, specialists are evidence providers by default. They may inspect and recommend but must not silently mutate the candidate. Each selected transformation batch has exactly one declared mutation owner. Default owner is `skill-improver`; `reproducibility-engineer` may own a bounded `invoke-apply` batch; another specialist may own a batch only when explicitly delegated and its own contract permits mutation.

## Ordered pass ledger

| # | Phase | Pass | Default role | Purpose / minimum evidence |
|---:|---|---|---|---|
| 1 | establish | `skill-creator-juiced` | provider | design governance, portability ownership, redesign/router/split escalation; preserve portable core |
| 2 | establish/diagnose | `skill-benchmark` | provider | baseline maturity/evidence; separate static from behavioral evidence |
| 3 | establish/diagnose | `skill-harness` | provider | freeze repeatable scenarios/evaluator visibility; activation/non-activation/ambiguous/edge/regression coverage |
| 4 | diagnose | reproducibility decision + optional `reproducibility-engineer` | provider or bounded mutator | classify controllable variance; `invoke-audit` feeds diagnosis, `invoke-apply` owns only the selected reproducibility batch |
| 5 | diagnose | `skill-quality-reviewer` | provider | reconstruct capabilities/canonical contract; capability delta/legacy/semantic defects |
| 6 | diagnose | `skill-package-architecture-review` | provider | package structure, loading, ownership, integration, keep/split/router evidence |
| 7 | diagnose | `context-architect` | provider | affected files/consumers/dependencies/ripple and safe sequence |
| 8 | diagnose | `skill-prompt-and-activation-review` | provider | activation, non-activation, ambiguity, overlap, boundary evidence |
| 9 | diagnose | `prompt-architect` | provider | instruction/prompt contract clarity where complex prompting is material |
| 10 | diagnose | `skill-consistency-repair` | provider by default | contradictions, integration gaps, ownership drift; emit repair evidence unless explicitly delegated to mutate |
| 11 | diagnose | `documentation-quality` | provider | docs/reference/example/template quality and verified commands |
| 12 | diagnose | `karpathy-guidelines` | provider | script/technical-artifact quality, CLI/error behavior, unnecessary complexity |
| 13 | diagnose | `security-and-governance-review` | provider | secrets, authority, unsafe commands/files, governance and residual risk |
| 14 | diagnose | `skill-testing-and-validation` | provider | existing validators/tests/links/package gates and missing validation surfaces |
| 15 | diagnose | `skill-cleanup-and-simplification` | provider by default | classify duplication/scaffold/generated noise before any deletion; emit cleanup hypotheses |
| 16 | diagnose | `skill-token-efficient` | provider by default | identify context/token waste without weakening activation/safety/evidence semantics |
| 17 | select | `skill-hypothesis-discovery` | planner | dedupe evidence into 5-10 bounded candidates, classify repair/optimization/experiment, select top 1-3/current next |
| 18 | mutate | `skill-improver` | default mutator | apply one selected bounded transformation, preserve baseline/evaluator, record transformation/experiment identity |
| 19 | evaluate | `skill-change-gate` | independent gate | candidate regression/acceptance decision; blocking regressions reject or require repair |
| 20 | evaluate | `skill-testing-and-validation` | validator | rerun affected deterministic gates and candidate validation after mutation |
| 21 | prove | `skill-hardening` | closure provider/mutator only if explicitly delegated | final package maturity, integration, validation, scope exactness; any mutation reopens affected gates |
| 22 | prove | final `skill-change-gate` | independent gate | final no-blocking-regression acceptance after hardening/closure |
| 23 | prove | final `skill-benchmark` | provider | baseline/candidate delta at the evidence level required by the claim; include parent/control when relevant |
| 24 | prove | final `skill-improver` closure | lifecycle owner | close accept/reject/revert state, rollback evidence, candidate identity, promotion receipt readiness |
| 25 | prove | final `skill-token-efficient` closure | provider by default | audit final avoidable context waste; if it mutates, rerun affected validation and final gate before freeze |

## Reproducibility pass rules

- Always classify pass 4 before `skill-hypothesis-discovery`.
- `invoke-audit` is diagnostic evidence and does not mutate.
- `invoke-apply` is allowed only for an explicit reproducibility objective or selected bounded reproducibility transformation; run pass 19 before accepting that batch.
- `not-applicable`, `blocked`, and `unavailable` require evidence and do not count as specialist invocation.
- Validate the routing record with `<PYTHON> scripts/validate_reproducibility_decision.py <DECISION_JSON>`.

## Provider rules

- A provider may return findings, capability refs, evidence gaps, candidate hypotheses, and validation requirements.
- A provider does not gain mutation authority merely because it found a defect.
- Findings produced after pass 17 that are outside the selected transformation become follow-up hypotheses unless required for candidate validity/safety.
- When a provider is explicitly delegated as mutation owner, record that delegation in the transformation registry and rerun affected gates afterward.

## Pass rules

- Never skip passes silently; classify each one.
- For an explicit required sequence, invoke every available specialist. Checklist-only is allowed only when unavailable, blocked, unsafe, or not-applicable and does not satisfy invocation.
- `pass` requires actual invocation or equivalent deterministic script/gate. Manual review is `applied-by-checklist`.
- `skill-hypothesis-discovery` is not a mutator.
- A failed nonblocking provider can still be reported, but readiness claims require explicit gate rationale.
- Never alter fixtures, expected outputs, frozen benchmark baselines, secrets, generated evidence, old zips, or unrelated files to make a pass look successful.
- After the final passing gate, freeze the exact candidate. Any target edit invalidates affected evidence.

## Required sequence reconciliation gate

Before final readiness, completion, or package claims, reconcile any user-required sequence against actual execution evidence with `scripts/validate_specialist_reconciliation.py`.

Required JSON ledger fields:

```json
{
  "required_specialists": [],
  "available_specialists": [],
  "invoked_specialists": [],
  "checklist_only": [],
  "blocked": [],
  "unavailable": [],
  "not_applicable": [],
  "not_run": [],
  "assume_required_available": false
}
```

Finalization is blocked when a required specialist is unclassified, `not-run`, checklist-only under an explicit sequence, or available but not invoked/blocked/not-applicable. A report may say `full optimization completed` only when this gate passes or no explicit specialist sequence was supplied.


## Evolutionary mode branch

`skill-evolution` is **not pass 26** and is not part of the canonical 25-pass ledger. It is a mode-specific search controller inserted after the Select phase when `evolutionary-optimization` is explicit. Booster services its candidate requests through the existing mutation/evaluation owners, then resumes the normal Prove phase for the finalist(s). Canonical mode must remain fully functional when Skill Evolution is unavailable.
