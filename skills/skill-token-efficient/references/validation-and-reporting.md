# Validation and Reporting

## At a Glance

- **Purpose:** Define comparable token metrics, preservation gates, canonical commands, report requirements, and runtime-claim boundaries.
- **Load when:** Measuring or comparing candidates, running final gates/packaging, or producing the result report.
- **Decision impact:** Determines whether counts are comparable, what blocks acceptance, and which token/runtime claims the evidence supports. Token reduction alone never establishes overall improvement.

## Contents

- Token metrics
- Preservation gates
- Commands
- Report contract
- Optional runtime economics

## Token metrics

Report the primary tokenizer identity before counts: `method`, `kind`, comparison `scope`, implementation/version when available, before/after count, delta, reduction percentage, per-file deltas, and local section regressions. Use the same primary method/scope for both arms.

Report available surfaces separately: `catalog`, `entrypoint`, `activated`, `instructions`, `all-text`. Legacy scopes `entrypoint|instructions|all-text` remain valid. Surface counts describe where text lives/loads, not expected cost unless an explicit observed/declared load profile exists.

`estimator-v1` is deterministic but approximate. `tiktoken:<encoding>` is exact only for that encoding/version and must not silently fall back. Measure optional `--compare-tokenizer` methods independently; never mix their counts/deltas with the primary tokenizer. Machine diagnostics must separate token reduction from preservation failures. Legacy `comparison.improved` is only a deprecated alias for `token_reduced`.

## Preservation gates

Fail when any applicable condition holds:

- activation, authority, scope, workflow/tool protocol, safety, validation, compatibility, output/stop, or evidence/citation duties weaken;
- a required protected literal is lost without authorized equivalence;
- a mechanical invariant fails, or required `manual`/`scenario` evidence is missing for the claim;
- a baseline-reachable instruction reference becomes unreachable, or a moved required rule lacks an operational load condition;
- progressive loading becomes orphaned/always-loaded branch detail;
- token reduction is the only positive evidence;
- tokenizer identities/surfaces are mixed into an invalid comparison;
- touched scripts/tests/package validation fail;
- the candidate differs from the final frozen identity/receipt.

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

Keep token efficiency and preservation evidence separate. Report mode/target; baseline/candidate identities; primary/comparison tokenizer identities; per-surface and selected-scope counts/deltas; file/section deltas; invariant/protected-surface status; activation/scope/authority/workflow/output evidence with its structural, reviewed, executed-behavioral, or runtime level; reference/load-condition status; changed surfaces/trade-offs; exact commands/status; remaining manual/scenario evidence; rollback/last-good; final frozen identity; package/receipt hashes only after validation; residual risk.

## Optional runtime economics

Use only with an explicit profile:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --profile <PROFILE.json> --json <REPORT.json>
```

or pair:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --before <BASELINE_PROFILE.json> --after <CANDIDATE_PROFILE.json> --json <REPORT.json>
```

Report uncached input, cache write/read, output, total tokens, cost components, currency/rate-profile identity, latency, and `estimated|observed` provenance separately. `runtime-comparable` requires observed profiles with matching non-empty environment identity; cost comparison also requires compatible rate/currency identity. The calculator never declares overall improvement.
