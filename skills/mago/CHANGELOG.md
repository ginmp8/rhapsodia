# Changelog

The version line was normalized with Nomia and Magia. Historical Mago releases `2.1.0` through `3.0.0` are grouped below without removing capabilities.

## [1.6.0] - 2026-07-22

- Adopt exact ecosystem compatibility with Nomia and Magia `1.6.0`.
- Add local strict handoff v2 producer/consumer tooling for `nomia_to_mago`, `magia_to_mago`, `mago_to_magia`, and `mago_to_nomia`.
- Require byte-equivalent priority, handoff, and compatibility contracts; reject mixed versions, legacy envelopes, `priority`, and `order_hint`.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.

### Compatibility

- Coordinated exact ecosystem release: Mago, Magia, and Nomia must all be `1.6.0`.
- Handoff v1 and generic `priority`/`order_hint` inputs are rejected rather than silently migrated.
- Rollback requires restoring all three packages to the same previously supported ecosystem release.

## [1.5.0] - 2026-07-22

- Separate Nomia-owned `business_priority`, Mago-owned `technical_criticality`, and Mago-owned `execution_sequence`.
- Remove generic priority and ordering aliases from active planning records and generated views.

## [1.4.0] - 2026-07-21

- Add planning compass, execution-wave projections, bounded aggregate runners, lifecycle evidence suites, distribution validation, and progressive onboarding.

## [1.3.0] - 2026-07-21

- Add governed plan-quality v2, clarification readiness, runtime dependency metadata, adapter round trips, and bounded parallel validation.

## [1.2.0] - 2026-07-20

- Add mutation transactions, drift detection, resume/rollback, relational security-risk contract v2, interoperability adapters, and release metadata.

## [1.1.0] - 2026-07-20

- Establish canonical identity, registry, requirements, design, task, validation, traceability, and planning-to-execution boundaries.

## Preserved pre-normalization controls

The following statements are retained as historical compatibility and safety records. They do not override the strict `1.6.0` ecosystem contracts.

- Preserve legacy Mago registry records as read-only migration inputs while rejecting mixed canonical and legacy forms.

All notable package changes are recorded here. Versions follow semantic versioning for the distributed skill package only; cycle and spec filesystem identities never use semantic versioning.

- Planning compass and execution-wave outputs are disposable external projections and never become canonical planning or runtime evidence.
- The new distribution and lifecycle gates are additive. Existing 2.3 planning packages remain readable and require no artifact migration.
- Existing version 1 security artifacts remain readable for legacy compatibility; new governed security work requires contract version 2 before handoff.
- External adapters are bounded file-convention mappings and do not claim complete compatibility with unspecified external schema versions.
