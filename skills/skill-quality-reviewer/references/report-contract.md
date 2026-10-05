# Report Contract

## At a Glance

- **Purpose:** Define the required human-facing report structure for each review mode and the evidence language expected by the bundled report validator.
- **Load when:** Load when drafting or validating full-review, quick-triage, compare-versions, report-validation, or legacy-audit output.
- **Decision impact:** Controls required sections, headings, evidence disclosures, verdict framing, score presentation, capability deltas, and correction-input placement.

## Contents

- Full review
- Quick triage
- Compare versions
- Report validation
- Evidence language


Match the user's language unless explicitly requested otherwise. Keep evidence labels and legacy classifications consistent. The canonical English section names below are used by the bundled structural validator; when producing a localized report that must pass that validator, retain these section headings and localize their contents.

## Full review

```markdown
# Skill Quality Review

## Executive Summary
- Target:
- Mode: `full-review` | `legacy-audit`
- Review type: static judgment | executed validation | mixed
- Review profile: portable-core | named specification + portable-core | named host profile(s)
- Verdict: ✅ `READY` | 🟡 `READY_WITH_COMMENTS` | 🔴 `REWORK_REQUIRED` | 🟣 `NEEDS_MORE_CONTEXT`
- Weighted score: n/100
- Score basis: static reviewer indicator | mixed evidence; never universal readiness
- Evidence coverage: structural/package=...; semantic=...; behavioral=...; runtime=...; host-semantic=...
- Confidence: high | medium | low — reason
- Finding counts:
- Legacy classification counts:
- Correction input status: ready | ready with questions | blocked

## Scope and Evidence
### Reviewed
### Not reviewed
### Assumptions
### Commands executed
| Command/check | Status | Evidence |

## Review Profile
- Review layers: normative conformance | package integrity | operational quality
- Spec baseline: locator + version/revision/retrieval identity | not-applicable | blocked
- Host profiles: portable | openai | codex | claude | copilot | cursor | other
- Host-semantic evidence/freshness:
- Model-judge calibration: not-used | uncalibrated | calibrated-against-reference | human-confirmed
- Behavioral trial policy: not-required | single-run-observation | repeated-trials | blocked

## Evidence Coverage and Confidence
| Layer | Status: complete/partial/not-run/blocked | Strongest evidence | Claim ceiling |
|---|---|---|---|
| Structural/package | | | |
| Semantic | | | |
| Behavioral | | | |
| Runtime | | | |
| Host-semantic | | | |

- Confidence: high | medium | low
- Confidence reason:

## Review Evidence Manifest
- Manifest status: measured | observed | not-run | blocked
- Manifest artifact/identity:
- Target identity:
- Reviewer identity:
- Evaluator/scenario identity:
- Source/spec identity:
- Identity limitations:

## Reconstructed Skill Contract
- Role and owner:
- Activation:
- Non-activation:
- Modes:
- Current inputs, identifiers, schemas, states, and versions:
- Outputs:
- Canonical sources:
- Consumers and handoffs:
- Validation:
- Stop conditions:

## Canonical Source Map
| Concept | Canonical source | Owner/writer | Consumers | Conflicts or gaps |
|---|---|---|---|---|

## Behavioral Invariants
1. ...

## Legacy and Compatibility Assessment
- Summary:
- Classification counts:
- Blocked decisions:

### Legacy Classification Matrix
| Item | Skill/package | Location | Classification | Normal-path reachable | Migration isolated | Recommended action | Evidence |
|---|---|---|---|---:|---:|---|---|

### Ownership Matrix
| Artifact or decision | Correct owner | Writers found | Consumers | Authority violation | Result |
|---|---|---|---|---:|---|

### Compatibility Matrix
| Contract | Real producer version | Real consumer version | Accepted | Rejected | Evidence |
|---|---|---|---:|---:|---|

### Runtime Coupling Matrix
| Caller | Dependency | Mechanism | Required at runtime | Canonical alternative | Classification |
|---|---|---|---:|---|---|

For `legacy-audit`, include all four matrices even when empty. For ordinary `full-review`, retain relevant rows and write `No material candidate observed in the inspected scope` for matrices with no applicable evidence. Do not infer absence from keyword searches alone.

## Scorecard
| ID | Dimension | Weight | Raw 0-5 | Weighted | Evidence | Main deduction |
|---|---|---:|---:|---:|---|---|

The weighted score is an internal static quality indicator. It does not override gate failures, evidence coverage, confidence, or claim ceilings.

### Gate Overrides
- ...

## Findings
### F-001 - 🟠 `MAJOR` - ...
Use every required field from `references/finding-model.md`.

## Rejected Hypotheses and Positive Signals
### Rejected hypotheses
### Positive signals

## Validation Gaps
- ...

## Prioritized Remediation Plan
| Order | Finding | Action | Depends on | Closure evidence |

## Correction Input
Use `references/correction-input-contract.md` and place the complete copy-paste-ready input here.

## Final Verdict
- Verdict:
- Applies to review profile:
- Why:
- Evidence ceiling:
- Remaining uncertainty:
- Next review gate:
```

## Quick triage

Limit to the five highest-value findings. Keep claim ceilings explicit even when the compact mode omits the full evidence manifest.

```markdown
## Quick Triage
- Target:
- Scope/review profile:
- Verdict:
- Review type:
- Evidence ceiling:
- Confidence:
- Legacy/compatibility signal status:

## Top Findings
1. **🟠 `MAJOR` - Issue:** evidence -> classification when applicable -> impact -> smallest fix -> validation.

## Gaps
- ...

## Correction Input
- Include a compact copy-paste-ready remediation block when the target is sufficient.
```

## Compare versions

```markdown
# Skill Change Review

## Executive Summary
- Baseline:
- Candidate:
- Baseline identity:
- Candidate identity:
- Evaluator/scenario identity:
- Review profile:
- Evidence coverage/confidence:
- Verdict: accept | accept with comments | reject | needs more context
- Net quality effect:

## Comparison Evidence
| Surface | Baseline | Candidate | Effect | Evidence status |

## Capability Delta
| Capability | Baseline evidence | Candidate evidence | Classification | Behavioral proof | Impact |

Use classifications from `references/capability-delta-review.md`. A static capability delta must be labeled static/observed and must not be presented as measured behavioral improvement. Changed evaluator/scenario/spec/host identity is a comparability gap unless explicitly re-baselined.

## Introduced Regressions
## Resolved Defects
## Unchanged Defects
## Legacy Reintroduction, Removal, or Migration Effects
## Ownership and Runtime-Coupling Effects
## Uncertain Differences
## Score Delta
State whether the delta is static judgment or measured evidence and keep score change separate from evidence-strength change.
## Acceptance Decision
## Correction Input
```

Do not infer improvement from fewer files, fewer tokens, deleted legacy content, more tests, or a higher static score alone. Connect the change to preserved current behavior, explicit rejection, migration isolation, ownership, validation, and frozen identities.

## Report validation

```markdown
# Review Report Validation

## Report Under Review
## Verdict
## Missing Required Sections
## Review Profile and Evidence-Coverage Defects
## Provenance / Identity Defects
## Unsupported Claims
## Finding Quality Failures
## Score/Verdict Inconsistencies
## Legacy Classification and Matrix Gaps
## Correction Input Defects
## Minimal Repairs
```

## Evidence language

- `measured`: executed scenario, validator, syntax check, package check, or supplied result whose identity/status is sufficient for the claim.
- `observed`: direct file or report inspection.
- `inferred`: conclusion supported by observed evidence.
- `planned`: not executed.
- `blocked`: unavailable because of scope, access, missing owner, consumer, version, migration, specification, host, or evaluator evidence.

Do not use `measured` for a checklist score, uncalibrated holistic judge score, or static scenario inventory. Do not state that the skill is bug-free, optimal, production-ready, legacy-free, fully portable, behaviorally reliable, or fully validated unless the declared profile and evidence layers support that exact claim.
