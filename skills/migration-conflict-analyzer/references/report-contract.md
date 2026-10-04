# Report Contract v3

The canonical result is JSON conforming to `schemas/analysis-report.schema.json`. Markdown is a human rendering of the same evidence.

## Required identity

A report binds:

- analyzer version `3.0.0`;
- heuristic-set name/version/hash;
- provider-profile version/hash and selected profile;
- migration/support file identities;
- generated/reviewed/deployment/rollback SQL identities;
- runtime-code and semantic-evidence identities;
- Git base/head/merge-base/history identities when applicable;
- normalized context: EF Core version, provider, DbContext, migrations assembly, deployment instances/method.

`analysis_id` is deterministic over the analysis contract, input digest, context, semantic evidence, heuristics, and provider profiles.

## Findings

Every finding must include:

- stable `id` and `rule_id`;
- `severity`, `confidence`, `evidence_status`, `gate`, `hazard_type`;
- exact files/operation IDs;
- evidence summary;
- why it matters;
- smallest safe recommendation;
- validation step;
- explicit uncertainty.

Severity/gate are contract data from `heuristic-set.json`; prose cannot override them.

## Decisions

- any `block` gate -> `block`;
- otherwise any high finding -> `changes-required`;
- otherwise any medium finding -> `review-required`;
- otherwise -> `no-static-blocker`.

`no-static-blocker` means no critical/high/medium finding from the supplied static/optional evidence. It is not production-safety proof.

## Receipts

`analysis_receipt` version 2 binds the report core to input, heuristic, provider-profile, and finding identities. File delivery receipts additionally bind the exact emitted artifact bytes and preserve recovery evidence if atomic replacement fails.

## Evidence-layer claims

Keep these distinct:

- static/structural evidence — source operations, hashes, Git relationships;
- semantic evidence — supplied output of EF-aware tooling;
- generated-SQL evidence — exact provider SQL bytes, not execution;
- runtime/database evidence — actual provider/database/deployment execution, which this analyzer does not perform.

Do not promote one evidence layer into another.
