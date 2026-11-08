# Source and licensing

- **Original project:** [Archify by tt-a1i](https://github.com/tt-a1i/archify).
- **Fork used to pin the source:** [ginmp8/archify](https://github.com/ginmp8/archify).
- **Immutable source commit:** `a4065941f12be7967436261d9934784e381d423c` (2026-10-31).
- **Lineage:** Archify originated from [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator).
- **Rights:** Apache License 2.0 for the pinned work, with historical MIT grants and third-party requirements retained. Exact original texts are stored at `licenses/third-party/archify-apache-2.0.txt`, `licenses/third-party/archify-historical-MIT.txt`, and the package-specific entries in `licenses/notices/`; `licenses/skill-assets.json` maps every original path. Standalone ZIP builds restore the source-relative `LICENSE`, `LICENSE-MIT`, `NOTICE` and other notices.
- **Maintainer:** RhapsodIA integration by ginmp8; independently maintained, not an official upstream distribution or endorsement.

## Adaptations

- Packages the complete upstream Archify 3.2.0 runtime and examples from the successful CI build associated with the pinned fork revision.
- Shortens the discovery description for ChatGPT's 500-character limit; adds version/changelog tracking and conditional context-loading reference previews; makes minor example/link and Spanish wording corrections.
- Does not claim behavioral changes to the upstream runtime; the package ships the original browser/runtime/tooling logic.
- Preserves the original Apache/MIT/third-party notices in the repository's central legal registry; independent builds restore the notices. Some embedded marks have separate usage restrictions, including non-commercial licensing; review marks before commercial redistribution or display.
