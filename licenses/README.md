# Third-party license notices

## Purpose

Keep license texts and attribution traceable while avoiding repeated copies inside RhapsodIA's source skill directories. This folder is **distribution metadata** and is not a required runtime input for any skill.

## Matt Pocock-derived skills (0.17.0)

The seven independently maintained adaptations `code-review`, `domain-modeling`, `grill-me`, `grill-with-docs`, `grilling`, `retro` and `wayfinder` share one **byte-identical** MIT grant and copyright notice:

- Canonical notice: [mattpocock-skills-MIT.txt](third-party/mattpocock-skills-MIT.txt).
- Original author: Matt Pocock, Copyright (c) 2026 Matt Pocock.
- Immutable source: [ginmp8/mattpocock-skills at 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d](https://github.com/ginmp8/mattpocock-skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d), derived from [mattpocock/skills](https://github.com/mattpocock/skills).
- Each skill retains a small `SOURCE.md` with its own pinned original path, Git blob and adaptation statement.
- Full-repository release archives include the canonical notice through the ordinary release packaging policy.
- **Standalone redistributions:** a standalone skill ZIP or copied folder must carry the full MIT copyright and permission notice. Use `python scripts/package_attributed_skill.py --skill wayfinder --output dist/wayfinder.zip` (or copy the canonical notice as `LICENSE-MIT` alongside the skill when distributing manually). A bare folder copied without that notice does not constitute a license-complete standalone distribution.

The canonical MIT license text is **not** replaced by an SPDX string or a URL alone; one full notice remains in the root repository, and a full notice is restored when independently packaging a skill.

## Other license and duplicate audit (0.17.0)

| Existing skills/files | Finding | Decision |
|---|---|---|
| `archify`, `archify-review`, `archify-tuning` | Exactly identical Apache-2.0 and historical MIT texts; `NOTICE` files differ and describe package-specific attribution. | **Retain** per-skill notices for standalone Archify distributions, historical grants and third-party provenance. No automatic replacement. |
| `local-graph-engine`, `local-graph-explorer` | Identical MIT text with Local Graph contributor attribution. | **Retain** for separately distributed runnable packages. |
| `runtime-harness`, `operational-context`, root `LICENSE` | Repeated Apache-2.0 text. | **Retain** for standalone distributions and independent package rights; root notice remains authoritative for the overall repository. |
| `skill-creator/LICENSE.txt` | Apache-2.0 text identical to Archify's license text, but independently distributed as a plugin/skill. | **Retain**; do not collapse independent package notices solely because bytes match. |
| `deep-research-suite`, `premortem-analysis`, vendored Archify components | Different copyright holders or vendor notices. | **Retain** as distinct rights statements. |
| `magia`, `mago`, `nomia`, `rhapsodia-workspace` | Several byte-identical scripts, schemas and integration tests, some larger than licenses. | **Retain pending dedicated consumer/contract audit**; these are not dead resources, and cross-skill deduplication could break standalone workflows. |
| Shared `assets/icon.svg` files | Intentional identical icons across some skills. | **Retain** local paths required by the host UI and standalone skill installation. |

**Token note:** license files are not injected automatically into model context merely because they exist beside `SKILL.md`. Moving them reduces duplicated repository/package files; it does not prove any reduction in model input tokens.

This is a scoped cleanup, not a license change, a removal of attribution, or a claim of legal compliance for arbitrary third-party redistribution. The existing license and notice files of all other skills remain unchanged.
