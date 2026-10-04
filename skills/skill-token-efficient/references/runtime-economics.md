# Runtime Economics

Raw instruction tokens and realized runtime economics are different measurements. Use runtime economics only when an explicit profile exists; never embed provider pricing or require a vendor SDK in the portable core.

## Profile contract

Use `assets/templates/runtime-profile.json` as the portable shape. A profile records:

- `profile_version`;
- `evidence_kind`: `estimated` or `observed`;
- `rate_profile_id`: caller-defined identity for the rate schedule;
- optional `environment_id` when runtime comparability matters;
- separate usage for uncached input, cache write, cache read, and output tokens;
- optional latency;
- optional per-million-token rates and currency.

Rates are user/source inputs. The skill never fetches current pricing or assumes one provider's cache model.

## Evidence rules

- `estimated` profiles are planning evidence only.
- `observed` profiles may support realized-usage claims when provenance is retained.
- Pairwise runtime claims require comparable profiles. For strong runtime comparison, keep environment identity stable and use the same `rate_profile_id`/currency when comparing cost.
- A raw input-token decrease cannot establish lower total tokens, cost, or latency.
- A cache or output change may invert the result; always report components separately.
- Do not invent cache hit rates, execution frequency, prices, or latency.

## Deterministic calculator

Single profile:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --profile <PROFILE.json> --json <REPORT.json>
```

Paired comparison:

```text
<PYTHON> <skill-root>/scripts/runtime_economics.py --before <BASELINE.json> --after <CANDIDATE.json> --json <REPORT.json>
```

The calculator reports arithmetic and comparability. It does not decide overall semantic/behavioral improvement.
