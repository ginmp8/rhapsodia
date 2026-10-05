# Changelog

## 1.0.1 - 2026-10-05

Reworked the `SKILL.md` control plane so selection, authority, privacy, safety bounds, snapshot semantics, workflow, evidence limits, and stop conditions are self-contained within the first 100 physical lines. References are now branch-specific depth rather than mandatory startup reading; no producer ownership or runtime behavior changed.

## 1.0.0 - 2026-10-03

Initial source-owned artifact catalog and offline Workspace. Includes closed envelopes/actions, deterministic projections, privacy enforcement, source drift detection, safe publication boundaries, four local views, and package/behavior tests.

Compatibility: optional independent capability. Existing producers are not required to install it. New compatible producers need only the public data envelope, not a runtime import.
