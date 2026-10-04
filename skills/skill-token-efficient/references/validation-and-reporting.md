# Validation and Reporting

## Token metrics

Always report the primary tokenization identity before counts. Required fields: `method`, `kind`, comparison `scope`, implementation/version when available, before count, after count, delta, reduction percentage, per-file deltas, and local section regressions. Use the same primary method/scope for both arms.

Also report the surface vector when available: `catalog`, `entrypoint`, `activated`, `instructions`, and `all-text`. The legacy scopes `entrypoint|instructions|all-text` remain valid. Surface counts describe where text lives/loads; they are not expected-cost estimates unless an explicit observed/declared load profile exists.

`estimator-v1` is deterministic but approximate for model billing/context. `tiktoken:<encoding>` is exact only for that encoding/version and must not silently fall back. Optional `--compare-tokenizer` methods are measured independently; never combine their counts/deltas with the primary tokenizer.

Machine-readable diagnostics must distinguish token reduction from preservation failures and identify the failing subject/category rather than returning a generic pass/fail. The legacy `comparison.improved` field is only a deprecated alias for `token_reduced`; overall improvement is not established by token count.

## Preservation gates

Fail when any applicable condition holds:

- activation, authority, scope, workflow/tool protocol, safety, validation, compatibility, output, stop, or evidence/citation duties weaken;
- a required protected literal is missing without authorized equivalence;
- a mechanical invariant fails;
- a `manual`/`scenario` invariant lacks the evidence needed for the claim being made;
- a baseline-reachable instruction reference becomes unreachable or a required moved rule lacks an operational load condition;
- progressive loading is replaced by orphaned or always-loaded branch detail;
- token reduction is the only positive evidence;
- tokenizer identities/surfaces are mixed into an invalid comparison;
- touched scripts/tests/package validation fail;
- the final candidate differs from the frozen identity or receipt.

## Commands

Baseline:

```text
<PYTHON> -S <skill-root>/scripts/refactor_audit.py --target <BASELINE> --tokenizer estimator-v1 --token-scope instructions --output <REPORT_DIR>/baseline.json
```

Optional independent cross-tokenizer measurement:

```text
<PYTHON> -S <skill-root>/scripts/refactor_audit.py --target <BASELINE> --tokenizer estimator-v1 --compare-tokenizer tiktoken:<encoding> --token-scope instructions --output <REPORT_DIR>/baseline-tokenizers.json
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

Keep token efficiency and preservation evidence separate:

- mode, target, baseline/candidate identities;
- primary tokenizer identity plus every comparison tokenizer identity;
- per-surface and selected-scope counts/deltas, never cross-tokenizer mixed;
- total/file/section token deltas;
- semantic-invariant results by category and verification type;
- protected-surface results by category;
- activation/scope/authority/workflow/output regression evidence and whether it was structural, reviewed, executed behavioral, or runtime;
- deterministic local-reference/progressive-loading/load-condition status;
- changed files/sections and accepted trade-offs;
- exact commands/status;
- manual/scenario evidence still required;
- rollback/last-good path;
- final frozen identity;
- package and receipt hashes/paths only after validation;
- residual risks/irreducible judgment.

## Optional runtime economics

Use only when an explicit profile exists:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --profile <PROFILE.json> --json <REPORT.json>
```

or for a pair:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --before <BASELINE_PROFILE.json> --after <CANDIDATE_PROFILE.json> --json <REPORT.json>
```

Report uncached input, cache write, cache read, output, total tokens, cost components, currency/rate-profile identity, latency, and `estimated|observed` provenance separately. `runtime-comparable` requires observed profiles with matching non-empty environment identity; cost comparison additionally requires compatible rate/currency identity. The calculator never declares overall improvement.
