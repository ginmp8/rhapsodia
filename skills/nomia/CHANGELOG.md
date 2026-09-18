# Changelog


## [1.9.4] - 2026-08-18

- Make the live-routing harness unit tests self-contained so the complete Nomia test suite passes from the standalone skill package without sibling Mago/Magia checkouts.
- Preserve the runtime harness contract: real prepare/evaluate commands still require explicit Mago, Magia, and Nomia roots and verify byte-equivalent routing corpora.
- Advance the current release contract to `1.9.4` without changing the protected `agents/openai.yaml` bytes or historical migration chain.
- Compatibility impact: compatible coordinated patch; no ownership, lifecycle, governance-validation boundary, handoff schema `3.0.0`, priority schema `2.0.0`, or routing-oracle semantic change. Live-model routing remains unmeasured.

## [1.9.3] - 2026-08-18

- Clarify that Nomia may validate Nomia-owned governance artifacts and ecosystem contracts while never owning technical/runtime validation.
- Broaden public activation metadata to cover portfolio, governance decisions, reporting, release communication, and handoffs.
- Normalize native activation oracles with explicit owner, tri-state activation, and diagnostic-entry semantics; implementation-plan regression now routes deterministically to Mago.
- Add positive governance-validation and negative runtime-validation scenarios.
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

## 1.9.0 - 2026-07-23

- Added privacy-minimized contract-v3 handoffs with workflow lineage.
- Added deterministic read-only routing and persistent handoff ledger contracts.
- Preserved independent Nomia, Mago, and Magia ownership.
- Compatibility impact: breaking coordinated release; contract-v2 envelopes and mixed package versions are rejected before mutation.

## [1.8.0] - 2026-07-23

- Harden strict handoff v2 consumption with closed direction payloads, bounded freshness, future-timestamp rejection, non-empty evidence references, stable reason codes, and non-actionable draft exit semantics.
- Add exact fail-closed harness assertions and a coordinated three-package release ledger bound to candidate roots, hashes, suites, archives, and ecosystem gates.
- Add an external live-routing evidence contract and immutable result schema while preserving structural-versus-measured evidence separation.
- Preserve Nomia governance ownership, closure authority, protected-file history, current identifiers, and migration-only governance adaptation.

### Compatibility

- Coordinated exact ecosystem release `1.8.0`; all three packages must move together.
- Handoff schema remains `2.0.0`; draft consumption now fails process control by default and requires explicit inspection allowance.

## [1.7.0] - 2026-07-22
- Repair protected `agents/openai.yaml` release continuity with an explicit two-step, user-authorized migration chain while keeping the immutable historical contract unchanged.
- Group correlated validation failures under deterministic root-cause identifiers while preserving every individual gate result.
- Clarify independent one-owner context loading and coordinated three-package rollback without transferring governance authority.

- Replace retired cycle-version vocabulary in current activation scenarios with canonical `cycle_id` terminology.
- Add distributed routing, lifecycle, shared provenance, negative ecosystem harness, coordinated release metadata, and declared development requirements.
- Standardize the display name as `Nomia` while preserving the technical id `nomia`.
- Preserve Nomia governance ownership and coordinated exact compatibility with Mago and Magia `1.7.0`.

### Compatibility

- Coordinated exact ecosystem release `1.7.0`; mixed versions remain rejected before mutation or closure.


## 1.6.0 - 2026-07-22

- Maintenance correction: align handoff prose with the strict breaking-no-legacy contract; legacy governance input remains isolated to `governance-adapt` and is never accepted as ecosystem handoff compatibility.
- Maintenance correction: add a contract-semantic gate to package, ledger, unit-test, and packaging assurance.

- Adopt exact ecosystem compatibility with Mago and Magia `1.6.0`.
- Upgrade ecosystem handoffs to strict schema v2 with deterministic ids, exact package versions, no unsupported aliases, and explicit state projections.
- Make `business_priority` the only governance priority field; reject generic priority aliases.
- Add a Nomia-owned closure gate that requires an explicit governance decision and external release evidence after technical completion.
- Add the integrated Nomia-to-Mago-to-Magia reconciliation and closure harness.
- Preserve fail-closed package security, atomic governance writes, canonical schema v2, documentation validation, and machine-readable assurance gates.
- Keep validation and packaging read-only with respect to source caches; reject symlinks, credential files, private-key material, and unsafe archive paths.
