---
name: skill-token-efficient
description: use when one existing Agent Skills-compatible package must be audited, refactored, compressed, compared, validated, or packaged to reduce instruction/context cost while preserving activation, scope, authority, workflow, safety, validation, outputs, evidence/citation traceability, references, behavior, portability, and readability. do not use for ordinary writing, generic code refactors, benchmark-only scoring, net-new skill design, or token savings that weaken those contracts.
---

# Skill Token Efficient

Minimize effective instruction/context cost without trading down the target's semantic or execution contract. Raw token reduction is a cost signal, never proof of improvement.

## Activation and non-use boundary

Use only when token/context efficiency is an objective for exactly one existing Agent Skills-compatible instruction package. Do not activate for generic prose shortening, ordinary prompt writing, application-code refactoring, benchmark-only scoring, net-new skill architecture, or requests to remove safety/validation/evidence/citation duties for smaller prompts.

## Operating contract

Resolve before mutation: one `TARGET`; mode `audit|plan|apply|validate|package`; level `readable` (default), `dense`, or `max-safe`; writable/protected scope; rollback; primary tokenizer and surface; optional comparison tokenizers; semantic contract; evaluator. Default to `estimator-v1` over `instructions`; identify/version model-specific tokenizers such as `tiktoken:<encoding>` and never mix counts/deltas across tokenizer identities.

- `audit`, `plan`, `validate`: read-only.
- `apply`: mutate only an isolated staged candidate.
- `package`: consume only an exact frozen candidate that passed required gates.
- Protect `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, frozen/generated evidence, old archives, read-only files, and unrelated repositories.

## Core rules

- Treat the target as a typed procedural contract. Preserve modality, negation, guards, precedence, exceptions, trust boundaries, workflow/tool protocol, outputs, and authorization boundaries.
- Keep token, structural, semantic-review, behavioral, and runtime evidence separate. Static/semantic evidence does not prove behavioral equivalence; runtime/cost claims require explicit comparable profiles, and strong runtime claims require observed execution.
- Keep the portable core host-neutral: package-relative resources, capability-based Python 3 resolution, no required vendor-private tool names/install paths. Host adapters such as `agents/openai.yaml` remain optional.
- `SKILL.md` is the control plane. Required Markdown must be directly reachable from it with an explicit load condition; nested Markdown links may aid navigation but cannot be the only route to required instructions.
- Prefer deduplication, precise wording, and progressive loading. Use `readable` for activation/control-plane text, `dense` for low-risk detail, and `max-safe` only after preservation/readability evidence supports it.

## Stop conditions

Stop before mutation if target identity, authority, writable/protected scope, rollback, tokenizer/surface, evaluator, required validation, or byte-for-byte recovery is unresolved, or if a token win requires weakening a hard gate.

## Apply workflow

1. **Baseline**: inspect `SKILL.md` and relevant resources, inventory validators, preserve exact baseline/tree identity, run safe baseline checks.
2. **Stage**: copy baseline to an isolated candidate; keep baseline, evaluator inputs, fixtures, expected outputs, and generated evidence immutable.
3. **Freeze contract**: fill/validate the refactor contract; pin tokenizer/surface; enumerate invariants/protected surfaces; classify material rules `entrypoint|reference|either`; add load conditions for required referenced rules; freeze deciding scenarios/evaluators before edits.
4. **Measure**: record applicable `catalog`, `entrypoint`, `activated`, reachable `instructions`, and `all-text` surfaces. With runtime profiles, keep uncached input, cache write/read, output, total tokens/cost, and latency separate; never invent rates, cache behavior, or load frequency.
5. **Refactor**: apply only the bounded transformation; preserve activation, authority, scope, workflow, safety, validation, evidence/citation, compatibility, output/stop, readability, and protected literals unless an authorized equivalent is evidenced.
6. **Compare**: use the same primary tokenizer, scope, frozen contract, and evaluator for both arms; measure optional comparison tokenizers independently.
7. **Gate**: resolve applicable `manual`/`scenario` invariants; validate scenario coverage, refs/load conditions, protected surfaces, authority/workflow semantics, target checks, portability, packaging, and claim-evidence boundaries.
8. **Freeze/deliver**: after all gates pass, record final tree identity and make no further edits; canonicalize destinations, reject aliases with target/protected inputs, package exact frozen bytes, verify receipt/hash, preserve last-good state on failure.

## Hard gates

Reject if the candidate weakens activation/scope, authority/precedence, workflow/tool protocol, safety, validation, evidence/citation, compatibility, output/stop contracts, progressive loading/load conditions, or readable execution; loses an unauthorized protected literal/reference; changes frozen evidence; fails required checks; mixes incomparable tokenizers/surfaces; makes behavioral/runtime claims from weaker evidence; or differs from its final frozen identity/receipt. Never accept solely because token count decreased.

## Direct resource map

Load only the resource whose decision is active; all required Markdown is one hop from this file.

- Tactics, levels, risk labels: [Compression playbook](references/compression-playbook.md).
- Moving/merging/deleting/rewriting operative rules: [Semantic preservation](references/semantic-preservation.md).
- Evidence-layer claim boundaries: [Behavioral equivalence](references/behavioral-equivalence.md).
- Identity, tokenizer surfaces, evaluator freeze, rollback, receipts, portability: [Reproducibility controls](references/reproducibility-controls.md).
- Metrics, preservation gates, commands, package checks, reporting: [Validation and reporting](references/validation-and-reporting.md).
- Cost/cache/latency only with an explicit runtime profile: [Runtime economics](references/runtime-economics.md).

Execution assets: [refactor contract](assets/templates/refactor-contract.json), [schema](assets/schemas/refactor-contract.schema.json), [contract validator](scripts/validate_refactor_contract.py), [refactor audit](scripts/refactor_audit.py), [runtime profile](assets/templates/runtime-profile.json), [runtime schema](assets/schemas/runtime-profile.schema.json), [runtime calculator](scripts/runtime_economics.py), [eval validator](scripts/validate_eval_suite.py), [packager](scripts/package_skill.py), [activation scenarios](evals/activation-scenarios.json), [report template](assets/templates/refactor-report.md.template), [examples](examples/refactor-examples.md). Contract v2 adds authority/workflow/placement and claim-evidence controls; v1 remains accepted. Planned scenarios are not executed evidence.

## Output contract

Report target/mode; baseline/candidate identities; primary/comparison tokenizer identities; per-surface and selected-scope counts/deltas without cross-tokenizer mixing; runtime profile identity/evidence kind and input/cache/output/total/cost/latency components when used; invariant/protected-surface and activation/scope/authority/workflow/output evidence; placement/load-condition/reference status; structural, semantic-review, behavioral, runtime evidence separately; changed surfaces and accepted/rejected transformations; exact commands/results with evidence labels; rollback/residual risk; final frozen identity; package/receipt paths only after validation.
