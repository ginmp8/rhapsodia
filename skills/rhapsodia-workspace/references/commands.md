# Commands

Use Python 3.11 or later. The runtime is standard-library-only. Set the working directory freely; every command takes an explicit repository root and uses package-relative resources.

| Command | Result | Writes |
|---|---|---|
| `discover` | discovered descriptor paths printed as JSON | none |
| `validate` | integrity summary and diagnostics | none |
| `index` | canonical-shape derived catalog | `.rhapsodia/catalog/catalog.json` |
| `project --view portfolio --output .rhapsodia/catalog/portfolio.json` | correlated work-item records | `.rhapsodia/catalog/portfolio.json` |
| `project --view timeline --output .rhapsodia/catalog/timeline.json` | metadata update chronology | `.rhapsodia/catalog/timeline.json` |
| `project --view relations --output .rhapsodia/catalog/relations.json` | typed nodes/relations | `.rhapsodia/catalog/relations.json` |
| `project --view skills --output .rhapsodia/catalog/skills.json` | counts by producer and exact state | `.rhapsodia/catalog/skills.json` |
| `render` | self-contained local HTML | `.rhapsodia/views/index.html` |

Repeat `--source-root docs/product --source-root docs/specs --source-root docs/implementation` to narrow discovery. Use `--destination public` only after all records authorize external sharing; private records are not silently omitted. `--output` is repository-relative and cannot escape the relevant derived subtree.

A manifest lock is not a document watcher. If a producer is changing sources, rerun after publication; source drift never becomes a successful partial snapshot. A last-good view may be stale after a failed refresh, so retain its fingerprint and inspect diagnostics rather than treating it as current truth.

The HTML can be opened directly in a browser. JSON import is an explicit local snapshot operation. Export returns the currently loaded catalog, not new filesystem evidence. All UI controls are local and offline.
