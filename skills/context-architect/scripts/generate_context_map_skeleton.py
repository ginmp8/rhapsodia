#!/usr/bin/env python3
"""Generate a context-map/2.1 Markdown skeleton from bounded inputs."""
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_REL = Path("assets/templates/context-map.md.template")

DEFAULTS = {
    "TASK": "[task]", "REPOSITORY": "[repository or supplied-file boundary]", "REVISION": "[revision/worktree]",
    "CHANGE_ANCHOR": "[base...head | changed paths | not-applicable]", "FRESHNESS": "[observed|measured|supplied|blocked]",
    "CHANGE_TYPE": "[bugfix|feature|refactor|migration|config|test|investigation]", "EVIDENCE_TIER": "standard",
    "CONFIDENCE": "[high|medium|low]", "CONFIDENCE_REASON": "[evidence reason]", "EVIDENCE": "[paths/searches/commands]",
    "PRIMARY_FILE": "path/to/owner", "PRIMARY_EVIDENCE_LABEL": "observed", "PRIMARY_SOURCE_CLASS": "[semantic index|build graph|syntax|lexical|other]",
    "WHY_PRIMARY": "owns changed behavior", "EXPECTED_CHANGE": "inspect/edit", "SECONDARY_FILE": "path/to/consumer",
    "RELATIONSHIP": "[called-by|implements|runtime-registers|tested-by|...]", "DIRECTION_HOP": "owner -> consumer / 1",
    "SECONDARY_EVIDENCE_LABEL": "observed", "SECONDARY_SOURCE_CLASS": "[source class]", "SELECTION_ROLE": "direct consumer", "ACTION": "inspect/update",
    "COMMAND_OR_TEST": "[command/test]", "VALIDATION_EVIDENCE_LABEL": "planned", "PURPOSE": "validate changed behavior", "TEST_CONFIDENCE": "medium",
    "PATTERN_REFERENCE": "[analogous path and convention]", "CONFLICT_OR_UNRESOLVED": "[none or unresolved evidence]",
    "RISK_SEVERITY": "medium", "RISK": "[risk]", "RISK_EVIDENCE": "inferred", "MITIGATION": "[mitigation]",
    "CLOSURE": "provisional", "OWNER_COVERAGE": "covered", "CONSUMER_COVERAGE": "unresolved", "RUNTIME_COVERAGE": "unresolved",
    "VALIDATION_COVERAGE": "unresolved", "EXTERNAL_COVERAGE": "not-applicable", "TRAVERSAL_COVERAGE": "[max hop/depth and stop reason]",
    "SELECTION_QUALITY": "no gold/reference set", "STEP_1": "[first dependency-safe change]", "STEP_2": "[next change]", "STEP_3": "[validation]",
    "BLOCKER": "[none or blocking question]",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default=str(Path(__file__).resolve().parents[1]), help="skill root containing the template")
    ap.add_argument("--task")
    ap.add_argument("--repository")
    ap.add_argument("--revision")
    ap.add_argument("--change-anchor")
    ap.add_argument("--tier", choices=["focused", "standard", "extended"])
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    root = Path(args.target).resolve()
    template = (root / TEMPLATE_REL).read_text(encoding="utf-8")
    values = dict(DEFAULTS)
    if args.task: values["TASK"] = args.task
    if args.repository: values["REPOSITORY"] = args.repository
    if args.revision: values["REVISION"] = args.revision
    if args.change_anchor: values["CHANGE_ANCHOR"] = args.change_anchor
    if args.tier: values["EVIDENCE_TIER"] = args.tier
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
