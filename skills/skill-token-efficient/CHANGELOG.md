# Changelog — Skill Token Efficient

## 0.1.0 — 2026-10-14 (first explicitly versioned candidate)

- Established the provider-owned format-selection knowledge, with source evidence and counterexamples (including flat vs mixed TOON results).
- Added host-neutral `skill-opt.token-efficiency` integration contract v1 and schema, with distinct Booster/Creator/Benchmark authority boundaries.
- Added deterministic, read-only format eligibility guidance; requires explicit schema/codec capabilities and rejects unsafe fallback.
- Preserved existing optimization, preservation, evaluation, and packaging logic without claiming empirical behavioral improvement.

Previous published version: **unknown**. Version `0.1.0` is the first explicit package identity in this candidate, not an asserted increment from a known release.

## [0.1.1] - 2026-10-14

- Removed legacy OpenAI-only `policy.products` metadata while retaining the optional adapter and implicit invocation policy.
- Aligned root SemVer `VERSION` with the mandatory versioning policy and existing `release.json` identity.
- Preserved `skill-opt.token-efficiency` v1 schema, CLI behavior, format-selection policy, and existing optimization workflows without modification.
- This is a compatible packaging/version-identity correction; no runtime or cross-model behavioral improvement is claimed.
