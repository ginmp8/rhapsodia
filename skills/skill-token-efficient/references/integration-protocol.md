# Token Efficiency Provider Integration Contract v1

## Purpose and ownership

`skill-token-efficient` is the **sole owner** of format eligibility, token measurement interpretation, compression semantics, and preservation/acceptance guards. It exports `skill-opt.token-efficiency` v1 via `contracts/integration-manifest.json`. Callers keep their own lifecycle/approval/testing authority; they **do not copy** the selection rules.

Read this reference when an orchestration/creation/benchmark consumer delegates a format question, efficiency change, or before/after comparison. This contract **does not automatically install or enable peer imports**: the caller must discover/invoke the provider through its native skill mechanism and import the contract version, or report `provider-unavailable` and proceed only with its own declared fallback (never with fabricated format evidence).

## Consumer boundaries

| Consumer | Call | Ownership |
|---|---|---|
| `skill-booster` | `format-advice` (read-only); `optimize-existing` (staged mutation) | Orchestrates; authorizes one isolated token-efficiency transformation batch; performs independent promotion/change gates |
| `skill-creator-juiced` | `format-advice` (read-only) on an existing staged draft | Owns new skill creation and writes its own draft; provider does not redefine skill architecture |
| `skill-benchmark` | `compare-existing` (read-only) | Owns evaluation scenarios/statistics and capability claims; provider supplies same-tokenizer/surface measurement and preservation diagnostics, not behavioral outcome |

Unknown/future consumers may request read-only `format-advice` after contract negotiation. `optimize-existing` v1 requires explicit Booster delegation; Benchmark/Creator requests cannot authorize provider writes.

## Request and execution

JSON request schema: [`contracts/token-efficiency-request.schema.json`](../contracts/token-efficiency-request.schema.json), request examples: [Creator](../assets/templates/token-efficiency-request.json), [Booster](../assets/templates/token-efficiency-booster-request.json), and [Benchmark](../assets/templates/token-efficiency-benchmark-request.json). Request keys: `contract_id`, `contract_version=1`, `consumer`, `operation`, `mode`, `target_skill`, `mutation_authorized`; operation-specific `format_context`, `staged_candidate`, `baseline_path`, `candidate_path`, `tokenization`.

- `format-advice` (`plan` or `audit`, read-only): caller supplies material role, supported formats, parsing/typing/schema/codec capabilities. Invoke `<PYTHON> -S <skill-root>/scripts/validate_integration.py --json-input request.json` then `<PYTHON> -S <skill-root>/scripts/recommend_format.py --json-input request.json`. Response is `advice-only`/`blocked`, not a measured optimization.
- `optimize-existing` (`apply`, only Booster, staged/write authorization): validate request, then use existing [refactor contract](../assets/templates/refactor-contract.json) and documented [refactor audit](../scripts/refactor_audit.py) -> staged mutation -> preservation gates. The request/validator **does not execute** those operations. In v1, validation rejects an identical/nested staged path but does not inspect the filesystem or prove the candidate is isolated; the executor must check source trust and byte-for-byte rollback. Do not edit installed or baseline skill in place.
- `compare-existing` (`validate`, read-only): validate request, then invoke existing `refactor_audit.py --before <baseline> --after <candidate> --tokenizer <pinned> --token-scope <same>`. Provider reports counts/evidence only; Skill Benchmark runs its own frozen scenario evaluation and gates.

`<skill-root>` is resolved by host capability/discovery; no absolute installation path is part of the contract. CLI `--json-input -` accepts stdin. No optional dependency is required for `estimator-v1`; `tiktoken:<encoding>` must be explicitly available or the exact token measurement is blocked, never silently downgraded.

## Response / evidence contract

Format advice fields: `contract_id`, `contract_version`, `consumer`, `operation`, `status`, `recommended_format`, `candidates_to_measure`, `conditional_formats`, `decision_basis`, `evidence`, `required_checks`, `mutation_performed=false`. A `blocked` result requires escalation; it is not permission to substitute a lossy encoding.

For compare/apply, the response is the existing target-owned audit/comparison and validation receipts tied to exact baseline/candidate identity, tokenizer, scope, source/evaluator identity and hard gates. Caller must label evidence as `measured`, `estimated`, `semantic-review`, `behavioral`, `runtime`, or `not-run` according to actual checks. Integration validation or eligibility advice is never proof of a token win, agent equivalence, or package readiness.

## Version, fallback and change control

- Contract ID/version are independent of the package release version. v1 rejects unknown major/contract versions; negotiate or stop instead of guessing.
- Compatible optional fields can be added without changing v1 mandatory semantics. Breaking response shape, trust boundaries, permissions, or operations requires contract v2 plus consumer migration checks.
- Consumer imports/pointers must cite only `skill-opt.token-efficiency` v1 and link to this provider. Do not duplicate matrix/thresholds/tokenizers in Booster, Creator or Benchmark.
- If no provider is discoverable: report it unavailable and skip delegated pass with explicit status; never claim a caller-performed optimization was the canonical Golden Source pass. Consumers retain their own independent acceptance/safety gates.
