#!/usr/bin/env python3
"""Generate a context-map markdown skeleton for a repository task."""

from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE = """## Context Map for: {task}

### Scope classification
- Change type: {change_type}
- Scope confidence: low - repository evidence has not been inspected yet
- Repository evidence inspected: none yet

### Primary files
| File | Why it is primary | Expected change |
|---|---|---|
| `TODO` | TODO | inspect |

### Secondary files and dependencies
| File | Relationship | Action |
|---|---|---|
| `TODO` | TODO | inspect |

### Test coverage and validation
| Test or command | Purpose | Confidence |
|---|---|---|
| `TODO` | TODO | low |

### Patterns to follow
- TODO

### Ripple effects and risks
| Risk | Evidence | Mitigation |
|---|---|---|
| incomplete repository evidence | no searches run yet | inspect primary files, usages, tests, and patterns before editing |

### Suggested sequence
1. Search for primary files, symbols, usages, and tests.
2. Read primary and analogous files.
3. Update this map with evidence before editing.

### Open questions or blockers
- Repository evidence is required before implementation.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a context-map skeleton.")
    parser.add_argument("task", help="Task description for the context map.")
    parser.add_argument(
        "--change-type",
        default="investigation",
        choices=["bugfix", "feature", "refactor", "migration", "config", "test", "investigation"],
        help="Initial change classification.",
    )
    parser.add_argument("--output", help="Optional output markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    content = TEMPLATE.format(task=args.task.strip(), change_type=args.change_type)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
