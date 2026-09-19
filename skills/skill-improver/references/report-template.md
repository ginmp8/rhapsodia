# Skill Improvement Report Template

Use for manual, automated, self-improvement, and package/install runs. Mark evidence as measured only when commands or captured outputs exist.

```markdown
# Skill Improvement Report: <target>

## 1. Target and scope
- Mode: `<benchmark-only | manual-patch | automated-loop | package-install | self-improvement>`
- Objective: `<...>`
- Target/baseline identity: `<...>`
- Runtime capabilities: `<filesystem-read/write, python, command execution, evaluator, artifact delivery>`
- Allowed/protected paths: `<...>`
- Self-improvement generation: `<not-applicable | generation_id>`
- Controller / baseline / candidate identity: `<...>`
- Max self-recursion depth / last-known-good: `<...>`

## 2. Evaluator and source freeze
- Evaluator: `<...>`
- Evaluator hash/locks: `<...>`
- Material source manifest: `<path/not-required>`
- Source verification: `<pass/fail/not-run>`
- Primary metric and direction: `<...>`
- Auxiliary metric when saturated: `<...>`

## 3. Baseline
- Score/status/gates: `<...>`
- Structural evidence: `<...>`
- Behavioral evidence: `<...>`
- Runtime/perceptual evidence: `<...>`

## 4. Hypothesis discovery and selection
- Source: `<supplied | backlog | discovery | built-in fallback>`
- Candidates: `<...>`
- Selected hypothesis/mechanism: `<...>`
- Expected effect: `<...>`
- Accept/reject rule: `<...>`

## 5. Candidate changes
- Files changed: `<...>`
- Mechanical controls moved into scripts/schemas/validators: `<...>`
- Repair rounds and diagnostics: `<...>`
- Deferred/rejected changes: `<...>`

## 6. Evaluation and structural change gate
- Final score/status/gates: `<...>`
- Delta: `<...>`
- Source/evaluator identities unchanged: `<pass/fail>`
- Change gate: `<pass | pass-with-warnings | fail | not-run>`
- Blocking regressions/material concerns: `<...>`

## 7. Final freeze and delivery
- Frozen candidate tree hash/identity: `<...>`
- Edited after final pass: `<no; otherwise validation invalid>`
- Package validation: `<pass/fail/not-run>`
- Authored/canonical output: `<...>`
- Artifact SHA-256: `<...>`
- Receipt: `<path/status>`
- Last-good/recovery result: `<...>`
- Self-improvement promotion decision/receipt: `<not-applicable | promote/reject/hold + receipt validation>`

## 8. Commands and evidence
| Command/check | Status | Evidence layer | Notes |
|---|---|---|---|
| `<...>` | `<pass/fail/not-run/blocked>` | `<structural/behavioral/runtime/perceptual>` | `<...>` |

## 9. Residual risks
- `<irreducible nondeterminism, unexecuted checks, portability caveats, subjective review gaps>`

## 10. Final status
`<reproducibility-hardened | validated-with-limitations | partial | blocked>`
```

Do not use `behaviorally improved` unless paired behavioral evidence actually ran or was supplied and met the predeclared acceptance rule.
