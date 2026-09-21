# Specialist Orchestration

Use this reference to select and sequence specialist passes. Specialists are owners of bounded concerns, not decorative checklist items.

## Caller Authority

When an upstream orchestrator delegates a bounded task, the caller remains the global orchestrator and promotion owner. Mutate only the assigned batch, preserve frozen evaluators/search policy/peer contracts, return candidate evidence and blockers, and require a coordinated change set for breaking peer contracts.

## Specialist Map

| Phase | Specialist | Use when | Ownership |
|---|---|---|---|
| requirement shaping | `prompt-architect` | behavior/specification is ambiguous | prompt/instruction contract and success criteria |
| repository context | `context-architect` | skill depends on a codebase or existing implementation | source-truth and impact map |
| code discipline | `karpathy-guidelines` | writing/reviewing bundled technical code | minimal implementation and validation discipline |
| package architecture | `skill-package-architecture-review` | cohesion, modes/router/split, resource layout | package architecture decision |
| activation | `skill-prompt-and-activation-review` | trigger, boundaries, stop conditions, output contract | activation/boundary quality |
| reproducibility | `reproducibility-engineer` | material controllable variance exists | contracts, deterministic controls, validators, freeze/receipt mechanisms |
| documentation | `documentation-quality` | references, examples, usage docs need quality review | human-readable documentation |
| testing | `skill-testing-and-validation` | scripts, validators, packagers, eval files need execution evidence | test/validator evidence and minimal repairs |
| security | `security-and-governance-review` | scripts, tool authority, data, dependencies, or governance risk | security/governance findings |
| consistency | `skill-consistency-repair` | contradictions, broken links, orphaned resources, ownership drift | package consistency |
| cleanup | `skill-cleanup-and-simplification` | stale scaffold, duplicate guidance, caches, obsolete files | package hygiene |
| token efficiency | `skill-token-efficient` | stabilized instructions remain bloated/repetitive | context reduction with semantics preserved |
| harness | `skill-harness` | repeatable scenario execution, baseline arms, holdouts, or evidence capture are needed | harness and evidence capture |
| benchmark | `skill-benchmark` | scorecard, baseline comparison, generalization evidence, or readiness measurement is requested | benchmark report and evidence classification |
| hypothesis discovery | `skill-hypothesis-discovery` | multiple candidate improvements compete | non-mutating prioritized hypothesis backlog |
| measured improvement | `skill-improver` | evaluator frozen and bounded hypothesis selected | measured candidate experiment |
| change acceptance | `skill-change-gate` | existing skill was materially modified | accept/reject decision |
| final hardening | `skill-hardening` | broad maturity/readiness pass is requested or justified | final maturity hardening |

## Default Path

For ordinary new skills:

1. requirement shaping only when underspecified;
2. package architecture;
3. activation/boundary review;
4. draft the package and define a small realistic evaluation set;
5. reproducibility decision gate from `references/reproducibility-routing.md`;
6. use `references/evaluation-and-generalization.md` to select `without-skill` baseline when meaningful, separate objective from subjective evaluation, and protect against eval-specific fixes;
7. documentation, testing, security, consistency, cleanup, and token efficiency only as applicable;
8. expand to held-out scenarios before strong behavioral or activation-improvement claims;
9. advisory change gate only when useful for a net-new package.

Do not run `reproducibility-engineer` automatically on every new skill.

## Existing-skill Redesign / Quality Upgrade

Recommended order:

1. immutable prior-version baseline and target-owned validators;
2. architecture and activation review;
3. reproducibility decision gate;
4. `reproducibility-engineer` in the selected mode when applicable;
5. code/documentation/testing/security/consistency/cleanup/token passes as needed;
6. harness and benchmark when paired baseline/candidate execution, holdouts, or measurement are requested;
7. use `references/evaluation-and-generalization.md` to reject eval-specific fixes and separate objective from subjective evidence;
8. hypothesis discovery and measured improvement only when a real optimization loop is warranted;
9. `skill-change-gate` before acceptance;
10. hardening/final validation when requested or material.

## Reproducibility Handoff Rules

- Read `references/reproducibility-routing.md` before invoking `reproducibility-engineer`.
- `audit-only` findings can feed hypothesis discovery; they do not authorize mutation by themselves.
- When `apply` owns a reproducibility patch, other specialists review or validate that patch rather than independently reimplementing it.
- Do not claim behavioral improvement from structural hardening alone.
- Respect cycle guards. Record `cycle-prevented` instead of recursively invoking the current owner.

## General Handoff Rules

- If a specialist is unavailable, apply a local checklist when possible and record `checklist-only` or `unavailable`; do not pretend it ran.
- A blocking specialist finding must be repaired or explicitly left as a blocker before downstream readiness claims.
- A downstream specialist must not expand the target skill's operational role without evidence and user intent.
- When two specialists overlap, assign a single mutation owner and use the other as reviewer/validator.
