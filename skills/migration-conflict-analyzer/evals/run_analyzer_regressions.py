#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def write_files(root: Path, mapping):
    for rel, content in mapping.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def invoke(analyzer: Path, root: Path, scenario):
    runtime_paths = []
    for rel, content in scenario.get("runtime_files", {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        runtime_paths.extend(["--runtime-code", str(path)])
    args = [sys.executable, str(analyzer), str(root), "--format", "json"]
    if scenario.get("include_support_files"):
        args.append("--include-support-files")
    args.extend(runtime_paths)
    args.extend(scenario.get("args", []))
    proc = run(args, cwd=root)
    if proc.returncode not in (0, 2):
        raise AssertionError(f"analyzer failed rc={proc.returncode}: {proc.stderr}")
    return json.loads(proc.stdout)


def invoke_git(analyzer: Path, scenario):
    with tempfile.TemporaryDirectory(prefix="mca-git-") as td:
        root = Path(td)
        run(["git", "init", "-q"], cwd=root)
        run(["git", "config", "user.email", "eval@example.invalid"], cwd=root)
        run(["git", "config", "user.name", "Eval"], cwd=root)
        write_files(root, scenario["git_base_files"])
        run(["git", "add", "."], cwd=root)
        run(["git", "commit", "-qm", "base"], cwd=root)
        base_sha = run(["git", "rev-parse", "HEAD"], cwd=root).stdout.strip()
        write_files(root, scenario["git_head_files"])
        run(["git", "add", "."], cwd=root)
        run(["git", "commit", "-qm", "head"], cwd=root)
        proc = run([sys.executable, str(analyzer), ".", "--git-base", base_sha, "--format", "json"], cwd=root)
        if proc.returncode not in (0, 2):
            raise AssertionError(f"git analyzer failed rc={proc.returncode}: {proc.stderr}")
        return json.loads(proc.stdout)


def select(report, rule_id):
    return [f for f in report.get("findings", []) if f.get("rule_id") == rule_id]


def identity_view(report):
    return {
        "analysis_id": report.get("analysis_id"),
        "heuristic_set.sha256": report.get("heuristic_set", {}).get("sha256"),
        "input_identity.digest": report.get("input_identity", {}).get("digest"),
        "finding_ids": sorted(f.get("id") for f in report.get("findings", [])),
    }


def validate_report(report, scenario):
    errors = []
    required_top = ["analysis_version", "analysis_id", "heuristic_set", "input_identity", "operations", "findings", "summary", "analysis_receipt"]
    for key in required_top:
        if key not in report:
            errors.append(f"missing top-level field {key}")
    for rule in scenario.get("expected_rules", []):
        matches = select(report, rule)
        if not matches:
            errors.append(f"missing rule {rule}")
            continue
        expected = scenario.get("expected_severity", {}).get(rule)
        if expected and any(x.get("severity") != expected for x in matches):
            errors.append(f"rule {rule} severity mismatch")
        for finding in matches:
            for field in ("id", "confidence", "evidence_status", "gate", "uncertainty"):
                if field not in finding:
                    errors.append(f"rule {rule} missing {field}")
    forbidden = set(scenario.get("forbidden_severities", []))
    if forbidden:
        bad = [f for f in report.get("findings", []) if f.get("severity") in forbidden]
        if bad:
            errors.append(f"forbidden severities present: {[f.get('severity') for f in bad]}")
    if scenario.get("require_git_identity"):
        git_id = report.get("git_identity", {})
        for field in ("base_requested", "base_sha", "head_sha", "merge_base_sha"):
            if not git_id.get(field):
                errors.append(f"git identity missing {field}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyzer", required=True)
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--expected-heuristics", required=True)
    ap.add_argument("--json-out")
    ns = ap.parse_args()
    analyzer = Path(ns.analyzer).resolve()
    scenarios_doc = json.loads(Path(ns.scenarios).read_text(encoding="utf-8"))
    expected = json.loads(Path(ns.expected_heuristics).read_text(encoding="utf-8"))
    results = []
    failures = 0
    for scenario in scenarios_doc["scenarios"]:
        sid = scenario["id"]
        try:
            if "git_base_files" in scenario:
                report = invoke_git(analyzer, scenario)
                rerun = None
            else:
                with tempfile.TemporaryDirectory(prefix=f"mca-{sid}-") as td:
                    root = Path(td)
                    write_files(root, scenario.get("files", {}))
                    report = invoke(analyzer, root, scenario)
                    rerun = invoke(analyzer, root, scenario) if scenario.get("rerun_equal") else None
            errs = validate_report(report, scenario)
            if report.get("heuristic_set", {}).get("version") != expected["heuristic_version"]:
                errs.append("heuristic version mismatch")
            if rerun is not None and identity_view(report) != identity_view(rerun):
                errs.append(f"rerun identity mismatch: {identity_view(report)} != {identity_view(rerun)}")
            status = "pass" if not errs else "fail"
            if errs:
                failures += 1
            results.append({"id": sid, "status": status, "errors": errs})
        except Exception as exc:
            failures += 1
            results.append({"id": sid, "status": "error", "errors": [str(exc)]})
    payload = {
        "suite_version": "2.0",
        "status": "pass" if failures == 0 else "fail",
        "total": len(results),
        "failed": failures,
        "results": results,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if ns.json_out:
        Path(ns.json_out).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if failures == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
