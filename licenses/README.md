# RhapsodIA legal texts and source attribution

## Source tree policy

All **76** skills keep their operational instructions, references, icons, scripts, and independent package metadata in `skills/`; original first-party license grants, third-party license grants, copyright notices, historical notices, vendored-component licenses and font OFL notices are centralized under `licenses/` or the repository's root `LICENSE`.

[skill-assets.json](skill-assets.json) records each skill's exact **original path, canonical file, Git blob identity and byte count**. This includes **22** previously local legal texts/notices in the established skills plus the already-centralized Matt Pocock MIT notice used by seven new skills. Byte-identical grants share one canonical file; unique copyright holders and package-specific notices remain distinct. No legal terms were rewritten by the relocation. An owner-requested follow-up identifies `ginmp8` as the copyright holder for original RhapsodIA work in the root Apache-2.0 `LICENSE` without changing Apache terms. The historical root LICENSE blob is preserved in the cleanup plan.

## Distribution contracts

- **Full-repository release:** `scripts/build_release_archive.py` includes root `LICENSE` and every canonical file under `licenses/`.
- **Portable Agent Plugins package:** `scripts/build_portable_agent_plugin.py` copies the source `skills/` as-is and includes root `LICENSE` and `licenses/`, keeping license texts outside individual skill folders.
- **Standalone skill ZIP:** `python scripts/package_skill.py --skill archify --output dist/archify.zip` works for any one of the 76 skills. It restores each original legal filename at its historical location inside the ZIP and includes a root Apache license for packages without their own `LICENSE`. The original exporter `scripts/package_attributed_skill.py` is a backwards-compatible alias.
- **Bare directory copy:** copying only `skills/<name>/` from this source tree is **not** a complete standalone redistribution unless the applicable original legal notices are included separately. Do not claim legal completeness for unvalidated host installers or copying workflows.

Archify's `renderers/shared/software-notices.mjs` is live executable code, not a standalone legal text, and continues to embed the exact original notices in generated artifacts by resolving the central files in source/plugin mode or the restored files in standalone mode.

## Canonical notice families

| Family | Canonical location |
|---|---|
| RhapsodIA Apache-2.0 license and ginmp8 copyright notice | `../LICENSE` |
| Apache-2.0 byte variant reused by Archify and Skill Creator | `third-party/archify-apache-2.0.txt` |
| Historical Archify/Cocoon AI MIT grant | `third-party/archify-historical-MIT.txt` |
| Distinct Archify package notices | `notices/archify.txt`, `notices/archify-review.txt`, `notices/archify-tuning.txt` |
| Archify third-party brands, vendor Pele and JetBrains Mono OFL | `notices/archify-third-party.md`, `third-party/pele-MIT.txt`, `third-party/JetBrainsMono-OFL.txt` |
| Local Graph MIT and shared third-party notices | `third-party/local-graph-MIT.txt`, `notices/local-graph-third-party.md` |
| Deep Research Suite MIT | `third-party/deep-research-suite-MIT.txt` |
| Original ginmp8 Premortem Analysis MIT | `first-party/premortem-analysis-MIT.txt` |
| Visual Code Intelligence distinct notice | `notices/visual-code-intelligence.txt` |
| Seven Matt Pocock-derived skills MIT | `third-party/mattpocock-skills-MIT.txt` |

The central registry is the exhaustive per-skill mapping, not this illustrative family table.

## Deliberately retained inside skills

- `skills/streamlit/references/source-and-license.md`: an **operational source policy and workflow reference**, not a full license grant. It is consumed by Streamlit's skill and validator.
- `skills/archify/renderers/shared/software-notices.mjs`: **executable JavaScript** that embeds licensing content into rendered output; moving it would change code loading.
- Other unrelated repeated Mago/Magia/Nomia scripts, tests, icons and contracts: they are not legal texts and are outside this cleanup's scope.

**Context distinction:** a license file is not automatically loaded as model context merely by being present in a skill folder. This cleanup reduces duplicate source-tree bytes and improves attribution ownership, but does not claim a measured input-token reduction or a legal opinion.

## Verification and rollback

The move is pinned to the Git baseline and original blobs in `licenses/cleanup-plan-0.17.0.json`. The owner-requested LICENSE notice amendment is recorded separately; the Premortem Analysis MIT notice was moved without changing its bytes. Test scripts validate all 76 catalog identities, original notice bytes, restored standalone ZIP notices, portable-plugin legal content, deterministic archives and Archify distribution contracts. Rollback is the previous Git commit from the unchanged release branch, not deleting the central record without restoration.
