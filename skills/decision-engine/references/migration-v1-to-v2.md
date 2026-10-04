# Migration from decision-engine/1 to decision-engine/2

Version 2 is intentionally breaking. Do not reinterpret a v1 envelope as v2 without explicit migration.

## Required changes

| v1 | v2 | Migration |
|---|---|---|
| `decision.type: "noul"` with boolean `value` | `decision.type: "binary"` | rename the boolean type; preserve `value` semantics |
| Choice has `options` + `selected` | Choice also requires `options_exhaustive` | declare whether supplied options cover the decision surface |
| Choice has no option criteria field | optional `option_criteria` | add only when caller-supplied option descriptions reduce ambiguity |
| Score uses `{min,max,meaning}` | Score scale is tagged `ordinal` or `numeric` | choose the correct scale semantics explicitly |
| non-decided result still carries qualitative confidence | non-decided result uses `confidence: null` | move uncertainty explanation to status/rationale/next_action |
| `contract_version: decision-engine/1` | `contract_version: decision-engine/2` | update consumer validation and schemas |

## Why `noul` was renamed

In v1, `noul` meant a boolean proposition. The name is also used by external typed-decision ecosystems for a probability that a proposition is true. Version 2 removes that semantic collision by naming the boolean contract `binary`. The Decision Engine still permits numeric probability only through the separate `calibration` object when it comes from an identified calibrated external source.

## Choice migration

For every v1 Choice, decide explicitly:

- `options_exhaustive: true` when all acceptable outcomes are represented;
- `options_exhaustive: false` when other real outcomes may exist.

Do not let the engine invent an `other` option. If a fallback is required, the caller must include it as a real supplied option.

## Score migration

Use `ordinal` when values represent ordered categories and the distance between adjacent levels is not assumed equal:

```json
{
  "kind": "ordinal",
  "levels": ["Low impact", "Material impact", "Critical impact"]
}
```

The result score is the zero-based integer index of the selected level.

Use `numeric` for a real bounded numeric quantity:

```json
{
  "kind": "numeric",
  "min": 0,
  "max": 100,
  "meaning": "Percentage of capacity budget",
  "unit": "percent"
}
```

## No compatibility shim

This package validates v2 only. A workflow that must accept both versions should perform explicit version dispatch outside the Decision Engine so the two contracts remain distinguishable and testable.
