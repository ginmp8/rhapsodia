---
name: skill-token-efficient
description: use when asked to audit, refactor, compress, validate, compare, or package target skill instructions for lower token/context cost while preserving activation, authority, scope, workflow, safety, validation, outputs, evidence/citation traceability, refs, behavior, and readability. covers skill.md, descriptions, prompts, refs, examples, templates, and instruction packages. do not use for ordinary writing, generic code refactors, benchmark-only scoring, or deleting safety/validation/evidence/citation rules.
---

# Skill Token Efficient

Minimize effective instruction/context cost while preserving activation, authority, behavior, safety, portability, and execution quality. Raw token reduction is a cost signal, never proof of improvement.

## Inputs and boundaries

Resolve before edits: exactly one `TARGET`; mode `audit|plan|apply|validate|package`; level `readable` (default), `dense`, or `max-safe`; writable scope; primary tokenizer; optional comparison tokenizers; token surface/scope; semantic contract; evaluator; rollback. Default to primary `estimator-v1` and `instructions`; identify/version model-specific tokenizers such as `tiktoken:<encoding>`. Keep every tokenizer identity independent; never combine counts or deltas across tokenizers.

Protect `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, frozen/generated evidence, old archives, read-only files, and unrelated repos. `apply` mutates only an isolated staged candidate; `audit`, `plan`, and `validate` do not mutate; `package` packages only a frozen passing candidate.

## Stop Conditions

Stop before mutation if identity, authority, scope, rollback, tokenizer, or required validation is unresolved, or if passing would require weakening a hard gate.

## Portability

Keep the Agent Skills core host-neutral: package-relative resources, capability-based Python 3 resolution, no required vendor-private tool names or install paths. Host-specific adapters are optional adapters; metadata such as `agents/openai.yaml` never becomes a core dependency. See [reproducibility controls](references/reproducibility-controls.md).

## Load on demand

- [Compression playbook](references/compression-playbook.md): levels, tactics, typed-contract preservation, protected regions, anti-patterns.
- [Semantic preservation](references/semantic-preservation.md): invariants, authority, equivalence, placement/load conditions, protected surfaces, readability.
- [Behavioral equivalence](references/behavioral-equivalence.md): evidence layers and claim boundaries for structural, semantic, behavioral, and runtime equivalence.
- [Runtime economics](references/runtime-economics.md): optional vendor-neutral cache/input/output/cost/latency profiles and comparability rules.
- [Reproducibility controls](references/reproducibility-controls.md): baseline/candidate identity, tokenizer, evaluator freeze, rollback, evidence, portability, receipts.
- [Validation and reporting](references/validation-and-reporting.md): commands, gates, metrics, package checks, report contract.
- [Refactor contract template](assets/templates/refactor-contract.json) + [schema](assets/schemas/refactor-contract.schema.json): fill and validate before `apply` with [contract validator](scripts/validate_refactor_contract.py). Contract v2 adds authority/workflow/placement and claim-evidence controls; v1 remains accepted for compatibility.
- [Refactor report template](assets/templates/refactor-report.md.template): optional durable report.
- [Refactor audit](scripts/refactor_audit.py): deterministic surface/tokenizer/reference/preservation comparison.
- [Runtime economics calculator](scripts/runtime_economics.py) + [profile template](assets/templates/runtime-profile.json) + [schema](assets/schemas/runtime-profile.schema.json): optional explicit runtime/cost arithmetic without provider coupling.
- [Eval-suite validator](scripts/validate_eval_suite.py): planned regression-suite coverage validation.
- [Packager](scripts/package_skill.py): deterministic staged packaging and optional receipt.
- [Activation scenarios](evals/activation-scenarios.json): planned/frozen coverage; presence is not behavioral execution.
- [Refactor examples](examples/refactor-examples.md): compact calibration examples.

## Apply workflow

1. **Baseline**: inspect `SKILL.md` and relevant resources; inventory validators; preserve an immutable baseline snapshot with exact tree identity; run target-owned checks.
2. **Stage**: copy baseline to an isolated candidate. Stop if staging or byte-for-byte recovery is unreliable.
3. **Freeze**: fill/validate the refactor contract, pin tokenizer and token scope, enumerate invariants/protected surfaces, classify critical rules as `entrypoint|reference|either`, give referenced required rules explicit load conditions, and freeze deciding scenarios/evaluators before mutation.
4. **Measure**: collect baseline metrics using the command contract in [Validation and Reporting](references/validation-and-reporting.md). Distinguish `catalog`, `entrypoint`, `activated`, reachable `instructions`, and `all-text`; preserve legacy scopes while reporting their different loading semantics. When a runtime profile is supplied, keep uncached input, cache write/read, output, total tokens/cost, and latency separate; never invent rates or cache behavior.
5. **Refactor**: preserve the target as a typed procedural contract, including modality, negation, guards, precedence, exceptions, trust boundaries, workflow/tool protocol, and outputs. Prefer deduplication and progressive loading; use `readable` for activation/control-plane text, `dense` for low-risk detail, and `max-safe` only after preservation/readability evidence supports it.
6. **Compare**: evaluate baseline and candidate with the same primary tokenizer, scope, contract, and frozen evaluator. Measure optional comparison tokenizers independently and never use one tokenizer’s count as another’s baseline. Report token delta separately from structural, semantic-review, behavioral, and runtime evidence.
7. **Gate**: resolve every `manual`/`scenario` invariant independently; validate target scripts/tests, scenario coverage, local refs/progressive loading, protected surfaces, authority/workflow semantics, portability/compatibility, and package rules. Semantic similarity is not behavioral equivalence; behavioral claims require executed scenario evidence. Runtime/cost claims require explicit comparable profiles, and strong runtime claims require observed execution evidence.
8. **Freeze and deliver**: after all applicable gates pass, record final tree identity and make no further edits. Perform output alias preflight: canonicalize destinations and reject aliases with target/protected inputs. Package exact frozen bytes, validate receipt/hash, and preserve installed/last-good state on failure.

## Hard gates

Reject a candidate if it weakens activation/scope, authority or instruction precedence, workflow/tool protocol, safety, validation, evidence/citation, compatibility, output contract, progressive loading/load conditions, or readable execution; loses an unauthorized protected literal/reference; changes frozen evidence; fails target/package checks; mixes incomparable tokenizer identities or surfaces; claims behavioral/runtime equivalence from weaker evidence; or differs from its final frozen identity/receipt. Never accept solely because token count decreased.

## Output contract

Report target/mode and baseline/candidate identities; primary/comparison tokenizer identities and per-surface counts; before/after counts and deltas for each tokenizer independently; optional runtime profile identity/evidence kind and input/cache/output/total/cost/latency components; invariant/protected-surface and activation/scope/authority/workflow/output evidence; placement/load-condition and local-reference status; structural, semantic-review, behavioral, and runtime evidence separately; changed surfaces and accepted/rejected transformations; commands/results with evidence labels; rollback/residual risk; final frozen identity; and package/receipt paths only after validation.
