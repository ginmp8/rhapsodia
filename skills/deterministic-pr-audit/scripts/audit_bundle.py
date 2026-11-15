#!/usr/bin/env python3
"""Always produce an honest, replayable PR-audit artifact, even without a checkout.

This command does not treat an absent verification plan as passed or failed.
It never executes code from the candidate pull request.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

from audit_core import (
    AuditError, canonical, digest, extract_requirements, init_checks, inspect,
    markdown_report, normalize_source, read_json, score, validate_checks,
    write_immutable,
)
from pr_audit import collect_github


OUTPUT_FILES = ("source.json", "requirements.json", "checks.json", "evidence.json",
                "report.json", "report.md", "manifest.json", "README.txt")


def build_bundle(*, source_input: dict, output: str | Path,
                 checks: dict | None = None, repo_path: str | None = None,
                 executions: dict | None = None) -> dict:
    """Produce deterministic audit inputs, report and ZIP from source evidence.

    The input is always treated as offline/manual unless it was collected by
    our live, paginated gh API capture in the same invocation.
    """
    source = normalize_source(source_input)
    requirements = extract_requirements(source)
    plan = checks if checks is not None else init_checks(requirements)
    validate_checks(requirements, plan)
    evidence = inspect(source, requirements, plan, repo_path, executions)
    report = score(source, requirements, plan, evidence)
    out = Path(output)
    payloads = {
        "source.json": canonical(source),
        "requirements.json": canonical(requirements),
        "checks.json": canonical(plan),
        "evidence.json": canonical(evidence),
        "report.json": canonical(report),
        "report.md": markdown_report(report).encode("utf-8"),
    }
    assessed = report["overall"]["assessment_state"]
    readme = (
        "DETERMINISTIC PR AUDIT - REPLAYABLE OUTPUT\n"
        f"State: {assessed}\n"
        f"Pinned head: {source['pull_request']['head_sha']}\n"
        f"Capture: {source['capture']['method']}\n"
        "An absent verification plan or checkout is NOT ASSESSED, not 0% implemented.\n"
        "This bundle is not independent evidence of end-to-end correctness.\n"
        "For a defensible numeric evidence floor, review and fill checks.json,\n"
        "obtain pinned source/test evidence, then regenerate in a new directory.\n"
        "Offline/manual capture completeness must be independently confirmed.\n"
    ).encode("utf-8")
    payloads["README.txt"] = readme
    manifest = {
        "schema": "pr-audit/bundle/v1",
        "head_sha": source["pull_request"]["head_sha"],
        "assessment_state": assessed,
        "capture_completeness": source["capture"]["issue_completeness"],
        "files_sha256": {name: hashlib.sha256(content).hexdigest()
                         for name, content in sorted(payloads.items())},
    }
    payloads["manifest.json"] = canonical(manifest)
    for name, content in sorted(payloads.items()):
        write_immutable(out / name, content)
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as archive:
        for name, content in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=6)
    write_immutable(out / "audit-bundle.zip", zip_bytes.getvalue())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Always generate a deterministic audit evidence bundle (N/A when unverified)")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--from-json", help="Offline complete source snapshot (scope unverified)")
    input_group.add_argument("--repo", help="GitHub owner/name; requires gh CLI")
    parser.add_argument("--pr", type=int, help="PR number with --repo")
    parser.add_argument("--issue", type=int, help="Issue number with --repo")
    parser.add_argument("--checks", help="Reviewed frozen checks.json, optional")
    parser.add_argument("--repo-path", help="Local Git repository with exact HEAD, optional")
    parser.add_argument("--executions", help="Frozen runtime receipts, optional")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args(argv)
    try:
        if args.from_json:
            raw = read_json(args.from_json)
            raw["capture"] = {"method": "offline_input", "issue_completeness": "not_verified"}
        else:
            if not args.pr or not args.issue:
                parser.error("--repo requires --pr and --issue")
            raw = collect_github(args.repo, args.pr, args.issue)
        report = build_bundle(source_input=raw, output=args.out,
                              checks=read_json(args.checks) if args.checks else None,
                              repo_path=args.repo_path,
                              executions=read_json(args.executions) if args.executions else None)
    except (AuditError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Generated {Path(args.out) / 'audit-bundle.zip'}")
    print(f"State: {report['overall']['assessment_state']}; verified evidence floor: {report['overall']['completion_verified_pct'] or 'N/A'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
