# Validation and Reporting

## Token metrics

Always report the tokenization identity before counts. Required fields: `method`, `kind`, comparison `scope`, implementation/version when available, before count, after count, delta, reduction percentage, per-file deltas, and local section regressions. Use the same method for both arms.

`estimator-v1` is deterministic but approximate for model billing/context. `tiktoken:<encoding>` is exact only for that encoding and must not silently fall back.

Machine-readable diagnostics must distinguish token reduction from preservation failures and identify the failing subject/category rather than returning a generic pass/fail.

## Preservation gates

Fail when any applicable condition holds:

- activation, scope, safety, validation, compatibility, output, stop, or evidence/citation duties weaken;
- a required protected literal is missing without authorized equivalence;
- a mechanical invariant fails;
- a `manual`/`scenario` invariant lacks the evidence needed for the claim being made;
- a baseline-reachable instruction reference becomes unreachable or a local reference breaks;
- progressive loading is replaced by orphaned or always-loaded branch detail;
- token reduction is the only positive evidence;
- touched scripts/tests/package validation fail;
- the final candidate differs from the frozen identity or receipt.

## Commands

Baseline:

```text
<PYTHON> -S <skill-root>/scripts/refactor_audit.py --target <BASELINE> --tokenizer estimator-v1 --token-scope instructions --output <REPORT_DIR>/baseline.json
```

Contract:

```text
<PYTHON> -S <skill-root>/scripts/validate_refactor_contract.py <CONTRACT>
```

Scenario coverage:

```text
<PYTHON> -S <skill-root>/scripts/validate_eval_suite.py <skill-root>/evals/activation-scenarios.json
```

Compare:

```text
<PYTHON> -S <skill-root>/scripts/refactor_audit.py --before <BASELINE> --after <CANDIDATE> --contract <CONTRACT> --tokenizer estimator-v1 --token-scope instructions --output <REPORT_DIR>/comparison.json --markdown <REPORT_DIR>/comparison.md --fail-on-preservation-loss
```

Syntax/package:

```text
<PYTHON> -S -m py_compile <skill-root>/scripts/*.py
<PYTHON> -S <skill-root>/scripts/package_skill.py --target <CANDIDATE> --output <ARTIFACT_DIR>/skill.zip --receipt <ARTIFACT_DIR>/skill.receipt.json --validate
```

## Report contract

Keep token efficiency and semantic preservation separate:

- mode, target, baseline/candidate identities;
- tokenizer identity and count kind;
- total/file/section token deltas;
- semantic-invariant results by category and verification type;
- protected-surface results by category;
- activation/scope/output regression evidence and whether it was executed or only planned;
- deterministic local-reference/progressive-loading status;
- changed files/sections and accepted trade-offs;
- exact commands/status;
- manual/scenario evidence still required;
- rollback/last-good path;
- final frozen identity;
- package and receipt hashes/paths only after validation;
- residual risks/irreducible judgment.
