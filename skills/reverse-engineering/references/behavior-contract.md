# Behavioral observation contract: V1 / V2

**Purpose:** define finite, reproducible behavior evidence with typed values, action-aligned observations, explicit effects and stable comparison semantics.
**Load when:** capturing or comparing original/candidate behavior, generating tests, modeling stateful traces or diagnosing a mismatch.
**Decision impact:** sets accepted NDJSON shapes, provenance status, strict comparison, schemas/limits, serialization behavior and all unverified boundaries.

## Freeze evidence before code changes

Record input/reference/candidate hashes, observation corpus hash, command/executable/dependency identifiers, runtime, initial state/reset policy, compiler/runtime versions, timezone/locale, seed, side effect scope, time/byte budgets, authority and comparison exceptions. `runner_status:"ok"` contained in user-provided JSON is a **claim**, not an authenticated execution record; a trusted captured run requires its independent provenance receipt.

## V1 (default): backward compatible

UTF-8 NDJSON, exactly one object per line: unique non-empty string `id`, any JSON `input`, object `observation` containing at least one of `output|error|state|status|events`. `null` differs from absent. Optional `kind`; optional `runner_status` (`ok|timeout|error|exit|invalid-output`). Unknown properties remain explicit compare data. Reject duplicate keys/IDs, unpaired surrogate characters and nonfinite raw JSON numbers.

```json
{"id":"n1","input":{"n":1},"observation":{"output":2}}
{"id":"bad","input":{"n":"oops"},"observation":{"error":{"kind":"validation","code":"BAD_INPUT"}}}
```

## V2 (`"schema_version":"2.0"` on a row)

Retains V1 records but permits `observation.steps`, `observation.effects`, or both as valid observations. `input.actions` must be a list of objects for `steps`; one step for every action, `action_index` exactly `0..n-1`. Each step must contain an observable `output|error|state|events|status|effects`. Each `effects` array (at observation or step level) contains objects with `kind` in `file|http|database|event|process|other` and a nonempty `operation`. Extra fields are compared without implicit normalization. Effects marked as supplied are *not* proof the runner captured them; an opt-in trusted filesystem/HTTP instrumentation adds only its documented observation scope.

Typed envelopes are opt-in and strictly checked by the v2 validator (only the following exact reserved `$type` variants):

| Typed value | Required shape | Semantics |
|---|---|---|
| bytes | `{"$type":"bytes","base64":"AAE="}` | Strict RFC 4648 canonical padded bytes |
| undefined | `{"$type":"undefined"}` | Distinct from JSON `null` or absent property |
| bigint | `{"$type":"bigint","decimal":"1234567890123456789"}` | Canonical signed decimal integer string |
| decimal | `{"$type":"decimal","value":"-1.2300"}` | Decimal textual representation preserved exactly |
| float-special | `{"$type":"float-special","value":"-0"}` | One of `NaN|Infinity|-Infinity|-0` |
| datetime-offset | `{"$type":"datetime-offset","iso8601":"2026-10-12T00:00:00-03:00"}` | Explicit ISO datetime with timezone offset |

V2 tagged envelopes are representations; **they do not automatically preserve an original language's numeric, date or serialization semantics**. Domain adapters must define those rules. Unknown `$type` variants fail v2 validation rather than being silently accepted.

```json
{"schema_version":"2.0","id":"sequence","input":{"actions":[{"action":"add","value":1},{"action":"read"}]},"observation":{"steps":[{"action_index":0,"state":{"count":1}},{"action_index":1,"output":1}],"effects":[{"kind":"event","operation":"publish"}]}}
```

## Comparison and diagnosis

The comparator joins exact IDs and checks exact input types/values, even if numeric tolerance is requested. Every observation field is significant by default: array ordering, object missing keys, typed values, errors, state and effect order. Justified numeric tolerance and ignored JSON pointers may affect `/observation/...` only. Distinct runner failures or missing cases block `PASS_OBSERVED_CASES`; finite supplied PASS does not assert that the original ran or that unseen cases agree.

`behavior_lab.py suggest` and `probe_engine.py` emit input-only unobserved hypotheses, **never** expected outputs. Test proposed cases on a trusted, explicitly authorized original and record results separately. `behavioral_pipeline.py --shrink-trials N` replays both trusted oracles and preserves the original first difference pointer+kind by default; state/external effects must be independently reset before reduction.

## Coverage and privacy

Partition tests across positive, invalid, missing/null, Unicode, numeric and overflow boundaries, ordering, duplicates, serialization/errors, time and environment, state transitions, concurrency/retries and controlled external failures. Report partitions actually executed, not an invented percentage of all possible behaviors. Avoid production secrets; case input, raw traces, screenshots and working directories remain sensitive even when diff reports omit raw values.
