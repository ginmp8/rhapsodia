# Routing Evidence Profile

Evidence contract version: `2`.

Use this profile only when a review attempts to compare observed activation or routing behavior. Static review does not need a fabricated runtime profile.

## Purpose

Bind host-routing evidence to the material environment that can change discovery and selection:

`frozen suite + frozen evaluator + invocation mode + host/model + competing catalog + trial policy + observed trials`.

A result remains useful historical evidence after the environment changes, but it is not comparable to a different routing fingerprint.

## Evidence shape

```json
{
  "evidence_version": 2,
  "suite_sha256": "<64-hex>",
  "evaluator_sha256": "<64-hex>",
  "execution_kind": "host-routing",
  "evidence_status": "executed",
  "executed_at": "2026-10-04T16:00:00-03:00",
  "evaluator_visibility": "hidden",
  "candidate_saw_evaluator_only_assets": false,
  "routing_profile": {
    "host": "<host identity>",
    "host_version": "<stable value or unknown>",
    "model_provider": "<provider or not-applicable>",
    "model_name": "<model or not-applicable>",
    "model_snapshot": "<snapshot or unknown>",
    "discovery_mode": "automatic",
    "skill_catalog_sha256": "<64-hex>",
    "skill_catalog_size": 12,
    "metadata_extensions": []
  },
  "routing_fingerprint_sha256": "<derived 64-hex>",
  "trial_policy": {
    "mode": "fixed-trials",
    "trials_per_case": 3
  },
  "cases": [
    {
      "id": "act-002",
      "invocation_mode": "implicit",
      "trials": [
        {"activated": true, "observed_route": "activate", "evidence": "<optional trace ref>"}
      ]
    }
  ]
}
```

## Routing profile rules

- `host`, host version, model provider/name/snapshot, discovery mode, catalog identity, catalog size, and material metadata extensions form the routing fingerprint.
- Hash the exact catalog representation used by the runner when possible: at minimum stable skill identifiers plus discovery descriptions in deterministic order. Do not substitute only the target skill hash when neighboring skills were available.
- Use `unknown` only when the host does not expose a material version/snapshot. Do not invent one. If an unavailable identity could change routing, downgrade the comparison to `not-proven` rather than claiming equivalence.
- `metadata_extensions` records host-specific discovery inputs that may alter routing, such as path filters or invocation-policy metadata. Host extensions remain adapters; the portable core never requires a particular extension.
- `executed_at` preserves freshness/history. A newer run is not automatically better evidence; comparability still depends on identity.

## Invocation modes

- `explicit`: the user or caller names/selects the skill directly. Treat as direct-usage evidence, not automatic discovery evidence.
- `implicit`: the user intent should cause automatic selection from discovery metadata.
- `contextual`: the same routing decision is embedded in realistic surrounding context, noise, or multiple intents.

Never mix `explicit` cases into automatic activation precision/recall.

## Trial rules

Routing is stochastic when a model decides among skills. Use a predeclared fixed trial count when a repeatability claim matters.

- One trial per case is a measured observation only.
- Two or more fixed trials may support repeated-run descriptive evidence; report raw outcomes and uncertainty rather than hiding variance behind one mean.
- Use the same trial count and isolation policy for baseline and candidate.
- Strong reliability/superiority claims require a stronger repeated-trial protocol and independent replication outside this focused reviewer.

## Negative routing semantics

Keep two negative classes distinct:

- `alternative-owner`: another skill/workflow should own the request. Report target-skill false activation separately from generic abstention.
- `abstain`: no skill in the relevant catalog should own the request. Measure abstention accuracy.

A near-miss failure and a generic abstention failure are operationally different and must not be collapsed into one aggregate.

## Validation

Validate evidence with:

```text
<PYTHON> scripts/validate_activation_evidence.py --input <RESULT.json> --suite <FROZEN_SUITE.json> --json <OUT.json>
```

The validator derives the routing fingerprint and per-case trigger rates. It does not execute routing.

Paired comparison additionally requires identical suite, evaluator, routing fingerprint, and trial policy:

```text
<PYTHON> scripts/compare_activation_evidence.py --suite <FROZEN_SUITE.json> --baseline <BASELINE.json> --candidate <CANDIDATE.json> --json <OUT.json>
```

## Versioning and migration

`evidence_version=2` and scenario suite major `3` are intentionally incompatible with the previous single-observation evidence shape. Do not silently reinterpret v1 evidence as v2 repeated-trial evidence. Preserve old evidence as historical material or convert it explicitly as one-trial, non-reliability evidence with traceable provenance.
