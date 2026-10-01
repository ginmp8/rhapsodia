# Adaptive Orchestration for Optimization Runs

## Purpose

Allow Skill Booster to reduce wall-clock and context coupling without changing the canonical six-phase optimization architecture or specialist ownership. Parallelism is an execution optimization, not a new evidence or promotion model.

## Invariants

- The six phases and their gates remain authoritative.
- The specialist passbook is an evidence/ownership ledger; its numbering is not automatically a wall-clock serialization requirement.
- Providers are read-only during Diagnose unless separately delegated as the one transformation owner.
- Exactly one owner mutates a selected transformation batch.
- Lower-level blocking gates still stop higher-cost evaluation.
- The same frozen baseline/evaluator/candidate identities must feed parallel arms when comparability is claimed.
- Global orchestration remains Booster-owned; specialists do not recursively dispatch the ecosystem.

## Safe fan-out candidates

After Establish has frozen target/evaluator identities, independent read-only providers may run concurrently when they do not consume each other's output. Common examples include package architecture, activation review, documentation review, security review, and token audit against the same baseline.

Do not parallelize a provider whose input depends on another provider's derived artifact. `skill-hypothesis-discovery` still waits for material diagnostics. Transformation still waits for selection. Final gates still wait for candidate validation.

## Evaluation parallelism

After required structural/deterministic gates pass, independent focused reviewers/evaluators may run concurrently against the same frozen candidate. Keep hidden/evaluator-only material isolated and do not share one evaluator arm's adjudication with another before completion when independence matters.

## Fresh-context challenge

For material candidate changes, an independent challenge/review arm may be used to search for regressions, unsupported claims, or capability loss. It supplements but never replaces `skill-change-gate` or target validators.

## State and trace

When adaptive orchestration is used, record at least:

- orchestration strategy;
- frozen baseline/candidate/evaluator identities;
- provider/stage ids and dependencies;
- parallelism and budget limits;
- status/result identity for each provider;
- barriers used before Select, Transform, Evaluate, and Prove;
- termination or escalation reason.

The run may use a portable workflow plan when available, but Booster must remain fully functional without an external orchestration skill/runtime.

## Host portability

Use native host capabilities when available. Serial execution is the portable fallback when it preserves semantics. Do not install or require Claude-specific workflows, LangGraph, CrewAI, AutoGen, Orca, MCP, or another runtime merely to obtain concurrency.
