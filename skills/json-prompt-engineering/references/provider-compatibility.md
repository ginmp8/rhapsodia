# Provider Compatibility and Projection

## Principle

Provider Structured Output and tool-calling surfaces commonly support different JSON Schema subsets, root-shape rules, limits, and failure semantics. Treat these as versioned capabilities discovered from current official documentation, not as permanent assumptions in `SKILL.md`.

## Capability profile

Represent the evidence needed for one provider/API surface in a small runtime profile. Start from `assets/templates/provider-capability-profile.json`.

Minimum fields:

- `profile_version`;
- stable `id` for this snapshot;
- provider and API surface;
- `verified_at` date;
- official source URLs;
- declared/assumed schema dialect;
- unsupported keywords or constructions;
- provider-required object rules;
- complexity/size limits when material;
- incompatible feature combinations;
- failure/refusal behavior notes.

A profile is evidence, not a universal truth. Re-verify when the provider, API surface, model family, or material date/version changes.

## Canonical to provider projection

Never mutate the canonical schema in place. Produce a separate projection and a loss ledger:

```json
{
  "canonical_schema": "contract-v3",
  "provider_profile": "provider-surface-2026-10-04",
  "projection": "contract-v3-provider",
  "lossy": true,
  "unsupported_constraints": [
    {
      "path": "$.properties.name.minLength",
      "keyword": "minLength",
      "application_side_enforcement": "validate after model output"
    }
  ]
}
```

If a provider-required transformation changes semantics and the application cannot restore the canonical constraint, classify compatibility as `incompatible` unless the user explicitly accepts the trade-off.

## Compatibility verdicts

- `compatible`: projection preserves the canonical contract for the intended path.
- `compatible-with-application-validation`: provider projection is weaker but every lost constraint is restored deterministically outside the model.
- `incompatible`: a required canonical behavior cannot be represented or restored safely.
- `not-proven`: current provider capability evidence or runtime validation is missing.

## Current-source examples

As of the research snapshot dated 2026-10-04:

- OpenAI Structured Outputs documents a supported subset with strict object requirements on relevant surfaces.
- Anthropic Structured Outputs documents `output_config.format`, strict tool use, a supported subset, and explicit schema-complexity limits; older `output_format` syntax is deprecated.
- Gemini Structured Outputs documents a provider-specific JSON Schema subset.

These examples are intentionally not encoded as timeless validator rules. Verify the current official documentation before making provider guarantees.

## Deterministic support

`scripts/plan_schema_projection.py` can compare schema keyword paths with a supplied capability profile. It returns unsupported-keyword findings and an application-side enforcement ledger. It does not rewrite the canonical schema or claim semantic equivalence.
