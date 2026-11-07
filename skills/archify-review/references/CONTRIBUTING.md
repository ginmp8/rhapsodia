# Contribution and compatibility decisions

## At a Glance

- **Purpose:** Summarize Archify contribution policy relevant to independent Value/Cost/Impact reviews.
- **Load when:** A PR changes behavior, test acceptance, schemas, dependencies, Viewer output or delivery; or when branch and review requirements are uncertain.
- **Decision impact:** Determines required issue/maintainer agreement, AI disclosure, cross-mode testing and preservation of supported behavior.

## Contents

- Scope and branch rules
- Required contributor accountability
- Evidence by impact
- Product contract checkpoints
- Verification and closure
- Authoritative policy links

## Scope and branch rules

Original upstream policy requires a related issue and explicit maintainer agreement before substantial work or formal PR for changes to generation, layout/routing, validation, interactions, performance, dependencies, tests or other behavior. A purely mechanical documentation correction may proceed directly; affected authored Skill text is a behavioral input, not automatically "just documentation".

Upstream `tt-a1i/archify` uses its active `dev` contribution branch in the pinned policy. The fork `ginmp8/archify` at commit `a4065941f12be7967436261d9934784e381d423c` was observed with `main` only. **Resolve real current refs, rulesets, target branch and contributor agreement for each repository before reviewing**; do not substitute generic branch defaults.

Check existing issues/PRs before reopening the same work. Preserve contribution attribution when consolidating overlapping PRs, and separate unrelated changes rather than expanding a candidate to absorb them.

## Required contributor accountability

Each PR declares whether AI was used. When used, name the tools, known model and activities; unknown models must be reported as unknown rather than invented. A human contributor must understand and be able to explain the changes and their impact. Code, tests, screenshots and test claims are assessed on evidence rather than on writing style or disclosure alone.

Never include credentials, private repository data, personal/customer data or secret tokens in fixtures, screenshot evidence, traces or packages. Do not authorize external actions merely because a review is positive.

## Evidence by impact

| Impact | Appropriate proof |
| --- | --- |
| Policy or prose only | Link/meaning/consistency checks and related templates; no visual suite for unrelated prose. |
| Local CLI behavior | Reproduce actual trigger, run focused tests and failure-path/compatibility cases. |
| Shared renderer, schema, Viewer or CLI helpers | Trace all affected modes and public callers, run representative fixed-input comparisons and relevant browser/CI cases. |
| Contract/acceptance change | Verify maintained capabilities and deliberate differences; capture explicit agreement and distinguish false positives from real defects. |
| Visual output | Compare same viewport, mode, theme, preset, zoom and state; inspect complete legibility and topology, not just pixel or bend metrics. |

Use `npm test` for core smoke where appropriate and `npm run test:full` for wider changes, depending on repo support, affected responsibility and CI. Confirm tests actually ran, skipped checks remain skipped, and output snapshots alone do not justify changed acceptance.

## Product contract checkpoints

Preserve supported schema-v1 inputs, authored meaning, topology, explicit geometry, labels and source evidence unless a reviewed and authorized compatibility change says otherwise. `standard` is a compatibility posture; new `showcase` failures must reflect a real repairable defect. Diagnostics should identify stable codes, exact subject, evidence and feasible fixes; do not silence failures to pass CI.

Archify 3.2.0 provides native architecture, workflow, sequence, dataflow, lifecycle, ERD, class, tree, timeline, waterfall, and Explainer modes. Check all affected type-specific and shared pathways. `finalize` success is not identical to human perceptual acceptance. GitHub/GitLab repository evidence, HTML output, exports, repeated delivery/recovery and browser behavior have separate contracts.

## Verification and closure

Cite exact base/head commits and actual commands/results; distinguish agent execution, CI evidence and human inspection. Account for rebase changes, tests selected by CI, genuine warnings and skipped browsers. A `Ready` finding is advisory only: target branch policies and user authorization still govern merge, tag, release and publication.

## Authoritative policy links

- [Pinned CONTRIBUTING.md](https://github.com/ginmp8/archify/blob/a4065941f12be7967436261d9934784e381d423c/CONTRIBUTING.md)
- [Current CONTRIBUTING.md](https://github.com/ginmp8/archify/blob/main/CONTRIBUTING.md)
- [Pinned README and code](https://github.com/ginmp8/archify/tree/a4065941f12be7967436261d9934784e381d423c)
