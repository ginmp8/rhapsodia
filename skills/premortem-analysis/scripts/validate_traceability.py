#!/usr/bin/env python3
"""Research-corpus bounded S/F/R/C/E bidirectional trace verification.

This catches missing IDs and inconsistent reverse links, not citation truth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DISPOSITIONS = {"implement", "already-covered", "rejected", "not-applicable", "uncertain", "conflict"}
KINDS = {"deterministic", "scenario", "review", "runtime"}
STATUSES = {"pass", "fail", "not-run", "planned", "pass-with-limitations"}


def validate_traceability(doc: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    blocks = ("sources", "findings", "requirements", "changes", "evaluations")
    if not isinstance(doc, dict) or any(not isinstance(doc.get(k), list) for k in blocks):
        return ["missing or malformed S/F/R/C/E arrays"]
    schema = doc.get("trace_version")
    if schema != "1.0.0":
        errors.append("unsupported trace_version")
    sections: dict[str, dict[str, dict]] = {}
    for block, prefix in (("sources", "S-"), ("findings", "F-"), ("requirements", "R-"), ("changes", "C-"), ("evaluations", "E-")):
        coll: dict[str, dict] = {}
        for row in doc[block]:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                errors.append(f"{block} contains malformed entry")
                continue
            if not row["id"].startswith(prefix):
                errors.append(f"{block} ID lacks expected {prefix} prefix: {row['id']}")
            if row["id"] in coll:
                errors.append(f"duplicate ID {row['id']}")
            coll[row["id"]] = row
        sections[block] = coll
    for source in doc["sources"]:
        for f in source.get("finding_ids", []):
            if f not in sections["findings"] or source["id"] not in sections["findings"][f].get("source_ids", []):
                errors.append(f"source/finding asymmetric: {source['id']} -> {f}")
        for field in ("title", "locator", "access_level", "accessed_on"):
            if not source.get(field):
                errors.append(f"source {source['id']} missing {field}")
    for finding in doc["findings"]:
        f_id = finding["id"]
        if finding.get("disposition") not in DISPOSITIONS:
            errors.append(f"{f_id}: bad disposition")
        if not finding.get("rationale"):
            errors.append(f"{f_id}: missing disposition rationale")
        if not finding.get("claim"):
            errors.append(f"{f_id}: missing atomic claim")
        for s in finding.get("source_ids", []):
            if s not in sections["sources"] or f_id not in sections["sources"][s].get("finding_ids", []):
                errors.append(f"finding/source asymmetric: {f_id} -> {s}")
        if not finding.get("source_ids"):
            errors.append(f"{f_id}: no source IDs")
        for r in finding.get("requirement_ids", []):
            if r not in sections["requirements"] or f_id not in sections["requirements"][r].get("finding_ids", []):
                errors.append(f"finding/requirement asymmetric: {f_id} -> {r}")
        if finding.get("disposition") == "implement" and not finding.get("requirement_ids"):
            errors.append(f"{f_id}: implemented finding with no requirement")
        if finding.get("disposition") in ("rejected", "not-applicable", "uncertain", "conflict") and finding.get("requirement_ids"):
            errors.append(f"{f_id}: excluded finding unexpectedly mapped to implementation")
    for req in doc["requirements"]:
        r_id = req["id"]
        if req.get("priority") not in ("must", "should", "may"):
            errors.append(f"{r_id}: unknown priority")
        if not req.get("text"):
            errors.append(f"{r_id}: missing requirement text")
        for f in req.get("finding_ids", []):
            if f not in sections["findings"] or r_id not in sections["findings"][f].get("requirement_ids", []):
                errors.append(f"requirement/finding asymmetric: {r_id} -> {f}")
        for c in req.get("change_ids", []):
            if c not in sections["changes"] or r_id not in sections["changes"][c].get("requirement_ids", []):
                errors.append(f"requirement/change asymmetric: {r_id} -> {c}")
        for e in req.get("evaluation_ids", []):
            if e not in sections["evaluations"] or r_id not in sections["evaluations"][e].get("requirement_ids", []):
                errors.append(f"requirement/evaluation asymmetric: {r_id} -> {e}")
        if not all(req.get(k) for k in ("finding_ids", "change_ids", "evaluation_ids")):
            errors.append(f"{r_id}: incomplete S/F/R/C/E coverage")
    for change in doc["changes"]:
        c_id = change["id"]
        if not change.get("files") or not change.get("requirement_ids"):
            errors.append(f"{c_id}: no files or justification")
        if root is not None:
            for file in change.get("files", []):
                if not isinstance(file, str) or not (root / file).is_file() or not (root / file).resolve().is_relative_to(root.resolve()):
                    errors.append(f"{c_id}: missing or escaping implementation file {file!r}")
        for r in change.get("requirement_ids", []):
            if r not in sections["requirements"] or c_id not in sections["requirements"][r].get("change_ids", []):
                errors.append(f"change/requirement asymmetric: {c_id} -> {r}")
    for evaluation in doc["evaluations"]:
        e_id = evaluation["id"]
        if evaluation.get("kind") not in KINDS or evaluation.get("status") not in STATUSES:
            errors.append(f"{e_id}: invalid kind or status")
        if not evaluation.get("artifact") or not evaluation.get("requirement_ids"):
            errors.append(f"{e_id}: no evidence artifact or requirements")
        if root is not None:
            for file in evaluation.get("artifacts", []):
                if not isinstance(file, str) or not (root / file).is_file() or not (root / file).resolve().is_relative_to(root.resolve()):
                    errors.append(f"{e_id}: missing or escaping evaluation artifact {file!r}")
        for r in evaluation.get("requirement_ids", []):
            if r not in sections["requirements"] or e_id not in sections["requirements"][r].get("evaluation_ids", []):
                errors.append(f"evaluation/requirement asymmetric: {e_id} -> {r}")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("trace", type=Path)
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--root", type=Path, help="also verify the referenced implementation/evaluation files")
    args = p.parse_args(argv)
    try:
        errors = validate_traceability(json.loads(args.trace.read_text(encoding="utf-8")), args.root)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    outcome = {"status": "pass" if not errors else "fail", "errors": errors, "claim_boundary": "bidirectional corpus mapping only; not scientific proof"}
    print(json.dumps(outcome, indent=2) if args.as_json else (outcome["status"].upper() + (": " + "; ".join(errors) if errors else ": trace relationships valid")))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
