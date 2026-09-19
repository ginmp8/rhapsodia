---
name: skill-token-efficient
description: use when asked to audit, refactor, compress, validate, compare, or package target skill instructions for lower token cost while preserving activation, scope, workflow, safety, validation, outputs, evidence/citation traceability, refs, and readability. covers skill.md, descriptions, prompts, refs, examples, templates, and instruction packages. do not use for ordinary writing, generic code refactors, benchmark-only scoring, or deleting safety/validation/evidence/citation rules.
---

# Skill Token Efficient

Reduce skill/instruction tokens without semantic loss. Token reduction is a cost metric, not proof of improvement.

## Inputs

Resolve before edits:

- `TARGET`: exactly one skill/instruction package.
- Mode: `audit`, `plan`, `apply`, `validate`, `package`.
- Level: `readable` default, `dense`, `max-safe`.
- Scope: target only. Block `.git`, secrets, credentials, fixtures, expected outputs, benchmark baselines, generated evidence, old archives, read-only files, and unrelated repos.
- Tokenizer: pin one method for both arms. Default portable method: `estimator-v1`; model-specific tokenizers are optional and must be identified/versioned.
- Token scope: `instructions` default for prompt/instruction cost; use `entrypoint` or `all-text` only when that is the declared comparison target.
- Contract: explicit semantic invariants and protected surfaces, frozen before mutation.

## Stop Conditions

Stop without mutation when target identity, write scope, semantic authority, safe baseline/rollback, or required tokenizer is unresolved; when the only path to a pass weakens a hard gate; or when required validation cannot be run and the requested claim depends on it.

## Modes

- `audit`: measure only.
- `plan`: propose only.
- `apply`: mutate a staged candidate, never the immutable baseline.
- `validate`: compare baseline vs candidate; reports only.
- `package`: package only the frozen passing candidate.

## Load When Needed

- `references/compression-playbook.md`: tactics, levels, protected regions, anti-patterns.
- `references/semantic-preservation.md`: invariant categories, equivalence, readability, evidence/citation guardrails.
- `references/reproducibility-controls.md`: baseline, tokenizer, contract, freeze, rollback, receipts, evidence layers.
- `references/validation-and-reporting.md`: commands, gates, metrics, report contract.
- `assets/templates/refactor-contract.json`: copy/fill before `apply`; validate against `assets/schemas/refactor-contract.schema.json` with `scripts/validate_refactor_contract.py`.
- `assets/templates/refactor-report.md.template`: final report skeleton when a durable report artifact is useful.
- `scripts/refactor_audit.py`: deterministic token/reference/preservation comparison.
- `scripts/validate_eval_suite.py`: regression-suite coverage validator.
- `scripts/package_skill.py`: deterministic staged packaging with optional durable receipt.
- `evals/activation-scenarios.json`: frozen activation/scope/protected/output/rollback scenarios; behavioral evidence requires an actual runner.
- `examples/refactor-examples.md`: compact transformations.

## Apply Workflow

1. **Inspect and baseline**: read target `SKILL.md` and relevant refs; inventory files/validators. Preserve exact baseline bytes and hash before mutation. Run target-owned checks first.
2. **Stage candidate**: copy the baseline to a separate candidate workspace. If staging or reliable restore is impossible, do not mutate.
3. **Freeze contract/evaluators**: copy `assets/templates/refactor-contract.json`, identify tokenizer, enumerate semantic invariants and protected surfaces, validate the contract, then freeze scenarios/evaluators used for acceptance. Do not edit them to make a candidate pass.
4. **Baseline metrics**:
   ```text
   <PYTHON> -S <skill-root>/scripts/refactor_audit.py --target <BASELINE> --tokenizer estimator-v1 --token-scope instructions --output <REPORT_DIR>/baseline.json
   ```
5. **Refactor**: use `readable` for `SKILL.md`/activation, `dense` for low-risk refs/examples, and `max-safe` only after preservation/readability gates pass. Prefer deduplication and progressive loading over deleting semantic content.
6. **Compare**:
   ```text
   <PYTHON> -S <skill-root>/scripts/refactor_audit.py --before <BASELINE> --after <CANDIDATE> --contract <CONTRACT> --tokenizer estimator-v1 --token-scope instructions --output <REPORT_DIR>/comparison.json --fail-on-preservation-loss
   ```
   Use the same tokenizer method/version for both arms. Report token delta separately from semantic preservation.
7. **Semantic review**: independently resolve every invariant marked `manual` or `scenario`. Reject candidates that save tokens by weakening activation, scope, safety, evidence/citation, validation, compatibility, output contract, progressive loading, or minimum readable execution.
8. **Regression gates**: validate scenario coverage, target scripts/tests, local refs, package rules, and any target-owned validators. Activation or other behavioral claims require executed scenario evidence; static files are only planned coverage.
9. **Freeze after pass**: rerun audit, record candidate tree identity, and make no further edits. Any edit invalidates the affected evidence and requires revalidation.
10. **Package/deliver**: package the exact frozen candidate and emit a receipt containing candidate/package identities. Promote only after all applicable gates pass. On failure, keep the installed/last-good target unchanged and retain baseline/recovery evidence.

## Hard Gates

Pass only when:

- token counts use one identified method and before/after are both reported;
- semantic invariants are explicit and all mechanical checks pass; manual/scenario invariants have real review evidence;
- protected URLs, paths, commands, env vars, schemas, flags, proper nouns, versions, and numbers are preserved or an authorized equivalent is documented;
- safety, validation, evidence/citation, compatibility, activation/scope, output contract, and readability do not regress;
- baseline-reachable local references remain reachable and progressive loading still works;
- target-owned checks and package validation pass;
- final candidate matches the frozen identity and receipt.

Never accept a candidate solely because total tokens decreased. Never weaken a gate, edit frozen evidence, or compress a critical region without demonstrated equivalence.

## Output Contract

Report separately: mode/target/baseline identity; tokenizer method and count kind; before/after counts and deltas; semantic-preservation status; protected-surface status; activation/scope/output regression evidence; progressive-loading/local-reference status; changed files/sections; validators/commands and outcomes; manual/scenario evidence; accepted/rejected transformations; rollback; residual risks; frozen candidate identity; package/receipt paths only when validated.
