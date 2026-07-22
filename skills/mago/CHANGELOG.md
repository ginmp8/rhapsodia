# Changelog

## [1.6.0] - 2026-07-22

- Adopt exact ecosystem compatibility with Nomia and Magia `1.6.0`.
- Add local strict handoff v2 producer/consumer tooling for `nomia_to_mago`, `magia_to_mago`, `mago_to_magia`, and `mago_to_nomia`.
- Require byte-equivalent priority, handoff, and compatibility contracts; reject mixed versions, unsupported envelope schemas, `priority`, and `order_hint`.
- Separate Nomia-owned `business_priority`, Mago-owned `technical_criticality`, and Mago-owned `execution_sequence`.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Keep planning-compass and execution-wave outputs non-authoritative and disposable.
- Require security contract v2 for new governed security work before handoff.
- Keep external adapters bounded to declared file conventions and explicit schema versions.

### Compatibility

- Coordinated exact ecosystem release: Mago, Magia, and Nomia must all be `1.6.0`.
- Unsupported handoff schemas and generic `priority`/`order_hint` inputs are rejected rather than translated.
- Rollback requires restoring a complete package set declared by an explicit compatibility manifest.

All notable package changes are recorded here. Versions follow semantic versioning for the distributed skill package only; cycle and spec filesystem identities never use semantic versioning.
