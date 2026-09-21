# Self-Improvement Orchestration

Use this reference when the target skill can modify itself or the user explicitly requests self-improvement. `skill-booster` is the global orchestration owner for improvement specialists; individual specialists keep only local, stable integrations needed by their own contract.

## Orchestration boundary

The Booster decides **which evidence/provider is needed and in what order**. It must not copy specialist internals into its own implementation, and it must not require downstream specialists to discover or sequence the whole improvement ecosystem.

A specialist may know another specialist when the relationship is direct and stable (for example, an experiment workflow using an independent change gate). That local coupling is acceptable. Broad catalog awareness remains Booster-owned.

## Self-improvement roles

| Need | Primary provider | Booster consumes |
|---|---|---|
| candidate lifecycle, isolated target transformation, rollback/promotion state | `skill-improver` | controller/baseline/candidate identities, hypothesis decision, promotion receipt |
| isolated behavioral execution, evaluator-only visibility, leakage/trace evidence | `skill-harness` | execution-evidence envelope and leakage status |
| baseline/candidate/without-skill comparison and metric deltas | `skill-benchmark` | comparable-arm report, provenance, capability metric delta |
| semantic capability preservation or loss | `skill-quality-reviewer` | capability-delta matrix: added/preserved/regressed/removed/redundant/unproven |
| activation/frontmatter/routing/boundary change | `skill-prompt-and-activation-review` | frozen activation-evaluator evidence and routing regressions |
| material controllable variance or self-hosting reproducibility risk | `reproducibility-engineer` | variability map, reproducibility contract, bounded transformation evidence |
| hypothesis backlog when the next change is unclear | `skill-hypothesis-discovery` | evidence-bound ranked hypotheses |
| final structural/semantic acceptance | `skill-change-gate` | pass/fail/insufficient-evidence decision tied to candidate identity |

Use only the providers whose evidence is material to the candidate. Complete optimization may still run a broader declared passbook, but self-improvement itself does not make every specialist mandatory.

## Routing rules

1. **Detect self-improvement** when the target package is the same logical skill responsible for the requested transformation, or the request explicitly asks the skill to improve itself.
2. **Freeze the controller before routing transformation work.** The active controller/evaluator must remain outside the candidate transformation surface.
3. **Route candidate-change ownership to the transformation owner.** The Booster does not edit the active controller in place and does not reimplement candidate lifecycle logic.
4. **Route evidence by touched surface:**
   - behavioral execution or hidden graders -> Harness;
   - comparative performance claim -> Benchmark;
   - capability additions/removals/ownership changes -> Quality Reviewer;
   - description/trigger/non-trigger/overlap/routing changes -> Prompt & Activation Review;
   - material reproducibility variance -> Reproducibility Engineer.
5. **Reconcile evidence, do not merge ownership.** Each provider returns its own contract. The Booster records identity, status, blockers, and relevance.
6. **Final acceptance remains independent.** Improvement score or specialist approval never overrides a blocking change-gate result.
7. **Promote only exact frozen bytes.** Package/install receipts must match the candidate identity accepted by the final gates.

## Optimization state ownership

For self-improvement, keep capability, transformation, and evaluation-plan artifacts outside the candidate transformation surface; keep experiment artifacts only when actual experiments or multi-candidate comparisons run. The Booster owns aggregation/orchestration of these records. Providers may emit compatible records for their own outputs, but they must not rewrite global history or promote workflow policy.

A self-generated target win can support target promotion after frozen gates pass. It is not sufficient on its own to change the Booster's canonical workflow; workflow-policy promotion is a separate cross-target decision.

## Ordering for a self-improvement cycle

A proportional default is:

```text
controller freeze
  -> baseline + evaluator freeze
  -> optional Harness/Benchmark baseline evidence
  -> optional reproducibility audit
  -> hypothesis selection
  -> Skill Improver produces isolated candidate
  -> candidate validation
  -> optional touched-surface reviewers
       Harness / Benchmark / Quality Reviewer / Activation Review
  -> Skill Change Gate
  -> promotion receipt verification
  -> package/install exact frozen candidate
```

Do not allow a downstream specialist to call the full chain again. If a specialist discovers a need outside its scope, it returns a handoff/evidence requirement to the Booster.

## Evidence reconciliation

For each provider record:

```text
provider
reason_selected
input_identity
output_identity
status
execution_type
evidence_layer
blocking_findings
claim_limitations
```

Conflicts resolve by ownership:

- execution isolation/leakage facts -> Harness evidence;
- numeric comparative deltas -> Benchmark evidence;
- semantic capability existence/loss -> Quality Reviewer judgment backed by evidence;
- activation/routing defects -> Prompt & Activation Review;
- reproducibility controls -> Reproducibility Engineer;
- candidate acceptance -> Change Gate.

When two providers disagree outside their ownership, do not invent a tie-breaker. Preserve both findings and route the disputed question to the owner of that criterion.

## Anti-coupling rules

- Do not require `skill-improver`, Harness, Benchmark, Quality Reviewer, Prompt & Activation Review, or Reproducibility Engineer to enumerate all other improvement skills.
- Do not duplicate specialist rubrics or validators inside Booster; reference their outputs/contracts.
- Do not create peer-to-peer orchestration loops.
- Direct pairwise integration is allowed only where one skill's stable output is a natural input to the other and no global routing decision is involved.
- The Booster may know the full catalog because orchestration is its responsibility.


### Evolutionary self-improvement

When the self-improving target uses evolutionary mode, keep three identities separate and immutable during a generation: active Booster/controller, Skill Evolution/search controller, and frozen evaluator set. Candidate Booster variants live outside both controllers. Skill Evolution may select/search among candidate Booster variants but cannot promote or replace the active Booster; an external/unchanged Booster proof path must verify the selected candidate before promotion.
