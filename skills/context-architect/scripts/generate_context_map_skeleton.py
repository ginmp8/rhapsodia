#!/usr/bin/env python3
"""Generate a context-map/2.0 markdown skeleton for a repository task."""

from __future__ import annotations

import argparse
from pathlib import Path

CONTRACT_VERSION = "2.0"

TEMPLATE = """## Context Map for: {task}

### Evidence identity
- Contract: context-map/{contract_version}
- Repository: {repository}
- Revision/worktree: {revision}
- Evidence freshness: blocked

### Scope classification
- Change type: {change_type}
- Evidence tier: {evidence_tier}
- Scope confidence: low - repository evidence has not been inspected yet
- Repository evidence inspected: none yet

### Primary files / owners
| File | Evidence | Why primary | Expected action |
|---|---|---|---|
| `<unresolved>` | blocked | owner not established | inspect |

### Secondary files and dependencies
| File | Relation | Evidence | Action |
|---|---|---|---|
| `<unresolved>` | unresolved | blocked | inspect |

### Test coverage and validation
| Test or command | Evidence | Purpose | Confidence |
|---|---|---|---|
| `<unresolved>` | planned | establish nearest validation path | low |

### Patterns to follow
- blocked: inspect an analogous implementation only after ownership and direct consumers are known.

### Conflicts / unresolved consumers
- blocked: repository evidence is required before conflicts or consumer closure can be assessed.

### Ripple effects and risks
| Severity | Risk | Evidence | Mitigation |
|---|---|---|---|
| high | incomplete repository context may hide affected consumers | blocked | inspect owner, consumers, runtime wiring, tests, and boundaries before editing |

### Coverage and closure
- Closure: blocked
- Owners/definitions: unresolved
- Direct consumers: unresolved
- Runtime/config: unresolved
- Tests/validation: unresolved
- External/dynamic consumers: unresolved

### Suggested sequence
1. Establish repository identity and find the owning source.
2. Trace direct consumers, runtime wiring, and tests in canonical order.
3. Update this map with evidence and close the selected tier before editing.

### Open questions or blockers
- Repository evidence is required before implementation.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a context-map/2.0 skeleton.")
    parser.add_argument("task", help="Task description for the context map.")
    parser.add_argument(
        "--change-type",
        default="investigation",
        choices=["bugfix", "feature", "refactor", "migration", "config", "test", "investigation"],
    )
    parser.add_argument(
        "--evidence-tier",
        default="standard",
        choices=["focused", "standard", "extended"],
        help="Initial evidence tier; standard is the default for multi-file work.",
    )
    parser.add_argument("--repository", default="<unknown>", help="Repository root or supplied-file boundary label.")
    parser.add_argument("--revision", default="<unknown>", help="Revision/worktree identity when known.")
    parser.add_argument("--output", help="Optional output markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    content = TEMPLATE.format(
        task=args.task.strip(),
        contract_version=CONTRACT_VERSION,
        change_type=args.change_type,
        evidence_tier=args.evidence_tier,
        repository=args.repository,
        revision=args.revision,
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
