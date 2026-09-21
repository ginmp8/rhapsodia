---
name: skill-token-efficient
description: use when asked to audit, refactor, compress, validate, compare, or package target skill instructions for lower token cost while preserving activation, scope, workflow, safety, validation, outputs, evidence/citation traceability, refs, and readability. covers skill.md, descriptions, prompts, refs, examples, templates, and instruction packages. do not use for ordinary writing, generic code refactors, benchmark-only scoring, or deleting safety/validation/evidence/citation rules.
---

# Skill Token Efficient

Reduce instruction tokens without semantic loss. Token reduction is a cost metric, never proof of improvement.

## Inputs and boundaries

Resolve before edits: exactly one `TARGET`; mode `audit|plan|apply|validate|package`; level `readable` (default), `dense`, or `max-safe`; writable scope; tokenizer; token scope; semantic contract; evaluator; rollback. Default to `estimator-v1` and `instructions`; identify/version model-specific tokenizers such as `tiktoken:<encoding>`.

Protect `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, frozen/generated evidence, old archives, read-only files, and unrelated repos. `apply` mutates only an isolated staged candidate; `audit`, `plan`, and `validate` do not mutate; `package` packages only a frozen passing candidate.

## Stop Conditions

Stop before mutation if identity, authority, scope, rollback, tokenizer, or required validation is unresolved, or if passing would require weakening a hard gate.

## Portability

Keep the Agent Skills core host-neutral: package-relative resources, capability-based Python 3 resolution, no required vendor-private tool names or install paths. Host-specific adapters are optional adapters; metadata such as `agents/openai.yaml` never becomes a core dependency. See [reproducibility controls](references/reproducibility-controls.md).

## Load on demand

- [Compression playbook](references/compression-playbook.md): levels, tactics, protected regions, anti-patterns.
- [Semantic preservation](references/semantic-preservation.md): invariants, equivalence, protected surfaces, readability.
- [Reproducibility controls](references/reproducibility-controls.md): baseline/candidate identity, tokenizer, evaluator freeze, rollback, evidence, portability, receipts.
- [Validation and reporting](references/validation-and-reporting.md): commands, gates, metrics, package checks, report contract.
- [Refactor contract template](assets/templates/refactor-contract.json) + [schema](assets/schemas/refactor-contract.schema.json): fill and validate before `apply` with [contract validator](scripts/validate_refactor_contract.py).
- [Refactor report template](assets/templates/refactor-report.md.template): optional durable report.
- [Refactor audit](scripts/refactor_audit.py): deterministic token/reference/preservation comparison.
- [Eval-suite validator](scripts/validate_eval_suite.py): planned regression-suite coverage validation.
- [Packager](scripts/package_skill.py): deterministic staged packaging and optional receipt.
- [Activation scenarios](evals/activation-scenarios.json): planned/frozen coverage; presence is not behavioral execution.
- [Refactor examples](examples/refactor-examples.md): compact calibration examples.

## Apply workflow

1. **Baseline**: inspect `SKILL.md` and relevant resources; inventory validators; preserve an immutable baseline snapshot with exact tree identity; run target-owned checks.
2. **Stage**: copy baseline to an isolated candidate. Stop if staging or byte-for-byte recovery is unreliable.
3. **Freeze**: fill/validate the refactor contract, pin tokenizer and token scope, enumerate invariants/protected surfaces, and freeze deciding scenarios/evaluators before mutation.
4. **Measure**: collect baseline metrics using the command contract in [Validation and Reporting](references/validation-and-reporting.md).
5. **Refactor**: prefer deduplication and progressive loading. Use `readable` for activation/control-plane text, `dense` for low-risk detail, and `max-safe` only after preservation/readability evidence supports it.
6. **Compare**: evaluate baseline and candidate with the same tokenizer, scope, contract, and frozen evaluator. Report token delta separately from preservation evidence.
7. **Gate**: resolve every `manual`/`scenario` invariant independently; validate target scripts/tests, scenario coverage, local refs/progressive loading, protected surfaces, portability/compatibility, and package rules. Behavioral claims require executed evidence.
8. **Freeze and deliver**: after all applicable gates pass, record final tree identity and make no further edits. Perform output alias preflight: canonicalize destinations and reject aliases with target/protected inputs. Package exact frozen bytes, validate receipt/hash, and preserve installed/last-good state on failure.

## Hard gates

Reject a candidate if it weakens activation/scope, safety, validation, evidence/citation, compatibility, output contract, progressive loading, or readable execution; loses an unauthorized protected literal/reference; changes frozen evidence; fails target/package checks; uses incomparable tokenization; or differs from its final frozen identity/receipt. Never accept solely because token count decreased.

## Output contract

Report target/mode and baseline/candidate identities; tokenizer method/kind/scope; before/after counts and deltas; semantic/protected-surface and activation/scope/output evidence; progressive-loading/local-reference status; changed surfaces and accepted/rejected transformations; commands/results with evidence labels; rollback/residual risk; final frozen identity; and package/receipt paths only after validation.
