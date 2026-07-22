# Changelog

## [1.7.0] - 2026-07-22

### Added
- Add the distributed ecosystem routing contract, shared cross-skill corpus, lifecycle map, provenance validation, and negative ecosystem harness.
- Add coordinated development requirements and release gates for routing, provenance, full local validation, and positive/negative ecosystem flows.

### Changed
- Canonicalize activation terminology to `cycle_id` and strengthen multi-intent handoff guidance while preserving Mago planning ownership.

### Compatibility
- Coordinated exact release `1.7.0` for Mago, Magia, and Nomia. Mixed versions remain rejected before mutation.


## [1.6.0] - 2026-07-22

- Adopt exact ecosystem compatibility with Nomia and Magia `1.6.0`.
- Add local strict handoff v2 producer/consumer tooling for `nomia_to_mago`, `magia_to_mago`, `mago_to_magia`, and `mago_to_nomia`.
- Require byte-equivalent priority, handoff, and compatibility contracts; reject mixed versions, unsupported envelope schemas, `priority`, and `order_hint`.
- Separate Nomia-owned `business_priority`, Mago-owned `technical_criticality`, and Mago-owned `execution_sequence`.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Keep planning-compass and execution-wave outputs non-authoritative and disposable.
- Require security contract v2 for new governed security work before handoff.
- Keep external adapters bounded to declared file conventions and explicit schema versions.
- Add semantic contract linting so current prose cannot re-enable legacy handoffs, mixed versions, or generic priority aliases.
- Strengthen negative handoff tests for fake compatibility switches and recursive `order_hint` aliases.
- Clarify shared registry ownership for `business_priority`, `technical_criticality`, and `execution_sequence`.

### Compatibility

- Coordinated exact ecosystem release: Mago, Magia, and Nomia must all be `1.6.0`.
- Unsupported handoff schemas and generic `priority`/`order_hint` inputs are rejected rather than translated.
- Rollback requires restoring a complete package set declared by an explicit compatibility manifest.

All notable package changes are recorded here. Versions follow semantic versioning for the distributed skill package only; cycle and spec filesystem identities never use semantic versioning.
