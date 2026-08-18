# Changelog


## [1.9.4] - 2026-08-18

- Make the live-routing harness unit tests self-contained so the complete Mago test suite passes from the standalone skill package without sibling Magia/Nomia checkouts.
- Preserve the runtime harness contract: real prepare/evaluate commands still require explicit Mago, Magia, and Nomia roots and verify byte-equivalent routing corpora.
- Compatibility impact: compatible coordinated patch; no ownership, lifecycle, activation, handoff schema `3.0.0`, priority schema `2.0.0`, or routing-oracle semantic change. Live-model routing remains unmeasured.

## [1.9.3] - 2026-08-18

- Normalize native activation oracles with explicit `expected_owner`, tri-state `expected_activation`, and `diagnostic_entry_allowed`; unresolved ownership no longer uses the legacy `"ambiguous"` activation value.
- Repair the stale `order` eval so registry records are authoritative and `spec-catalog.yaml` / `define-queue.yaml` remain external read-only projections.
- Clarify that canonical planning intent may activate read-only blocker diagnosis before `BOARD_ROOT` is resolved, while writes still require canonical inputs.
- Broaden the agent entry prompt to planning from governance intake, repository evidence, or existing canonical planning artifacts.
- Add a shared adversarial routing case that rejects a forced Magia owner while lifecycle/current owner is unresolved.
- Compatibility impact: compatible coordinated patch; ownership, lifecycle, handoff schema `3.0.0`, priority schema `2.0.0`, and exact-version policy are unchanged. Live-model routing remains unmeasured.

## [1.9.2] - 2026-08-17

- Fix `current_owner` routing so a current Nomia phase plus implementation intent inserts the mandatory Mago bridge instead of failing on a forbidden direct handoff.
- Clarify same-owner phase semantics: consecutive intents coalesce into one owner phase while ordered intents and non-consecutive repeated owner phases remain preserved.
- Make the 365-day durable-artifact cap explicitly stricter than the 3650-day handoff limit; persistence remains fail-closed when inherited retention exceeds the durable-artifact policy.
- Strengthen artifact privacy lineage with canonical handoff references, source-handoff integrity verification when source evidence is supplied, and exact-inheritance checks. Structural lineage alone no longer implies source authenticity.
- Keep routing activation evidence explicitly structural; live-model precision and recall remain unmeasured.
- Compatibility impact: compatible coordinated patch; handoff schema `3.0.0`, priority schema `2.0.0`, ownership, and payload contracts are unchanged. Exact-version policy still requires upgrading or rolling back all three skills together.

## [1.9.1] - 2026-07-23

- Preserve ordered and repeated lifecycle phases with a corpus-backed executable routing oracle.
- Reject legacy Nomia ops schema v1 outside explicit governance adaptation.
- Verify privacy declarations against content and propagate compact privacy lineage to durable artifacts.
- Define conditional `execution_sequence.rank` semantics for draft/blocked versus ready handoffs.
- Add deterministic privacy, routing, compatibility, and regression gates without changing domain authority.

## [1.9.0] - 2026-07-23

- Added privacy-minimized contract-v3 handoffs with workflow lineage.
- Added deterministic read-only routing and persistent handoff ledger contracts.
- Preserved independent Nomia, Mago, and Magia ownership.
- Compatibility impact: breaking coordinated release; contract-v2 envelopes and mixed package versions are rejected before mutation.

## [1.8.0] - 2026-07-23

- Harden strict handoff v2 consumption with closed direction payloads, bounded freshness, future-timestamp rejection, non-empty evidence references, stable reason codes, and non-actionable draft exit semantics.
- Add exact negative-harness assertions that isolate each failure cause instead of passing through a stale handoff id.
- Add one release-time coordinated attestation ledger that validates and packages the same Mago, Magia, and Nomia candidates without introducing runtime peer coupling.
- Add an external live-routing evidence contract and immutable result schema while retaining `live-model-routing-not-measured` until attributed model execution exists.
- Preserve Mago planning authority, strict exact-version compatibility, current identities, and migration-only adapt behavior.

### Compatibility

- Coordinated exact ecosystem release `1.8.0`; all three packages must move together.
- Handoff schema remains `2.0.0`; draft consumption now fails process control by default and requires explicit inspection allowance.

## [1.7.0] - 2026-07-22
- Document coordinated staging, exact-version preflight, and three-package rollback while preserving Mago as an independent planning skill.
- Clarify one-owner context loading so distributed routing does not require concatenating Nomia, Mago, and Magia control planes.

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
