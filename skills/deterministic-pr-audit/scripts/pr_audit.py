#!/usr/bin/env python3
"""Frozen, evidence-backed PR/issue scoring. No network for replay/score.

External commands: gh for read-only capture; git for read-only inspection;
explicit local tests only with --execute.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import quote

from implementation_review import (
    MAX_FILES, MAX_FILE_BYTES, SNAPSHOTS_SCHEMA, blob_sha, compare_grades,
    grade, init_review, markdown_grade, validate_review,
)
from audit_core import (
    AuditError, SOURCE_SCHEMA, EXECUTIONS_SCHEMA, REPORT_SCHEMA, canonical,
    compare_reports, digest, extract_requirements, git_bytes, init_checks,
    inspect, markdown_report, normalize_source, read_json, require_schema,
    spec_material,
    score, suggest_paths, validate_checks, verify_commit_available, write_immutable,
)


def gh_api(endpoint: str) -> dict | list:
    gh = shutil.which("gh")
    if gh is None:
        raise AuditError("GitHub CLI `gh` not found. Install/authenticate gh, or use --from-json fixture.")
    try:
        r = subprocess.run([gh, "api", endpoint], capture_output=True, text=True, timeout=60)
    except FileNotFoundError as exc:
        raise AuditError("GitHub CLI `gh` not found. Install/authenticate gh, or use --from-json fixture.") from exc
    except subprocess.TimeoutExpired as exc:
        raise AuditError("GitHub API request timed out") from exc
    if r.returncode:
        raise AuditError(f"GitHub API request failed ({endpoint}): {r.stderr.strip()[:400]}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as exc:
        raise AuditError(f"Invalid JSON from gh API for {endpoint}") from exc


def gh_paginated(endpoint: str, max_items: int = 5000) -> list:
    items = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        response = gh_api(f"{endpoint}{separator}per_page=100&page={page}")
        if not isinstance(response, list):
            raise AuditError(f"Paginated endpoint returned non-array: {endpoint}")
        items.extend(response)
        if len(items) > max_items:
            raise AuditError(f"Unbounded API content: more than {max_items} items at {endpoint}")
        if len(response) < 100:
            break
        page += 1
    return items


def collect_github(repo: str, pr_number: int, issue_number: int) -> dict:
    pr = gh_api(f"repos/{repo}/pulls/{pr_number}")
    issue = gh_api(f"repos/{repo}/issues/{issue_number}")
    comments = gh_paginated(f"repos/{repo}/issues/{issue_number}/comments")
    files = gh_paginated(f"repos/{repo}/pulls/{pr_number}/files")
    # To avoid inconsistency during capture, verify that the PR did not advance
    # while its files and issue comments were being fetched.
    pr_second = gh_api(f"repos/{repo}/pulls/{pr_number}")
    issue_second = gh_api(f"repos/{repo}/issues/{issue_number}")
    if pr["head"]["sha"] != pr_second["head"]["sha"] or pr["base"]["sha"] != pr_second["base"]["sha"]:
        raise AuditError("PR advanced during capture; retry with a new frozen snapshot")
    if issue.get("updated_at") != issue_second.get("updated_at") or issue.get("comments") != issue_second.get("comments"):
        raise AuditError("Issue changed during capture; retry")
    if len(comments) != issue.get("comments", len(comments)):
        raise AuditError("Incomplete issue comments; cannot certify complete capture")
    if len(files) != pr.get("changed_files", len(files)):
        raise AuditError("Incomplete PR file listing; GitHub limits file endpoints for very large PRs")
    return {
        "repository": repo,
        "capture": {"method": "gh_api_live", "issue_completeness": "verified_by_pagination"},
        "pull_request": {
            "number": pr["number"], "title": pr.get("title"), "body": pr.get("body"),
            "url": pr.get("html_url"), "head_sha": pr["head"]["sha"],
            "base_sha": pr["base"]["sha"], "files": files,
        },
        "issue": {
            "number": issue["number"], "title": issue.get("title"),
            "body": issue.get("body"), "url": issue.get("html_url"),
            "comments": comments,
        },
    }


def source_input_args(args: argparse.Namespace) -> dict:
    if args.from_json:
        raw = read_json(args.from_json)
        # This route can contain hand-picked excerpts rather than the full issue.
        # Never silently upgrade it to a fully captured normative issue.
        raw["capture"] = {"method": "offline_input", "issue_completeness": "not_verified"}
        return raw
    if args.pr_url:
        m = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)/?", args.pr_url)
        if not m:
            raise AuditError("--pr-url must be https://github.com/owner/repo/pull/NUMBER")
        repo, num = f"{m.group(1)}/{m.group(2)}", int(m.group(3))
    else:
        if not args.repo or not args.pr:
            raise AuditError("Supply --pr-url, or --repo owner/repo --pr NUMBER")
        repo, num = args.repo, args.pr
    if not args.issue:
        raise AuditError("--issue is required. Never infer normative issue from PR description alone.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise AuditError("Invalid owner/repo")
    return collect_github(repo, num, args.issue)


def capture(args: argparse.Namespace) -> None:
    raw = source_input_args(args)
    specs = raw.get("spec_files", [])
    for path in args.spec_file or []:
        content = Path(path).read_text(encoding="utf-8")
        specs.append({"name": Path(path).name, "body": content})
    source = normalize_source(raw, specs)
    requirements = extract_requirements(source)
    out = Path(args.out)
    write_immutable(out / "source.json", canonical(source))
    write_immutable(out / "requirements.json", canonical(requirements))
    print(f"Captured: PR #{source['pull_request']['number']} at {source['pull_request']['head_sha']}")
    print(f"Extracted: {len(requirements['criteria'])} criteria; {len(requirements['warnings'])} warnings")
    print(f"Spec SHA-256: {requirements['spec_digest']}")
    print(f"Output: {out}")


def init_command(args: argparse.Namespace) -> None:
    req = read_json(args.requirements)
    plan = init_checks(req)
    write_immutable(args.out, canonical(plan))
    print(f"Initialized {len(plan['requirements'])} requirements in {args.out}")
    print("IMPORTANT: Empty plans are UNVERIFIED, never automatically PASS.")


def inspect_command(args: argparse.Namespace) -> None:
    source, req, plan = read_json(args.source), read_json(args.requirements), read_json(args.checks)
    executions = read_json(args.executions) if args.executions else None
    evidence = inspect(source, req, plan, args.repo_path, executions)
    write_immutable(args.out, canonical(evidence))
    statuses = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0}
    for rec in evidence["results"].values():
        for check in rec.values():
            statuses[check["status"]] += 1
    print(f"Evidence captured: {statuses}; SHA-256 {digest(evidence)}")


def preflight_command(args: argparse.Namespace) -> None:
    """Fail early rather than convert absent inspection into a progress score."""
    source = read_json(args.source)
    requirements = read_json(args.requirements)
    checks = read_json(args.checks)
    require_schema(source, SOURCE_SCHEMA)
    validate_checks(requirements, checks)
    if requirements["spec_digest"] != digest(spec_material(source)):
        raise AuditError("The criteria do not match the frozen issue/spec source")
    declared = sum(len(x["checks"]) for x in checks["requirements"].values() if not x.get("not_applicable"))
    if not declared:
        raise AuditError("NO_VERIFICATION_PLAN: no checks declared. Build and review criterion-specific assertions before inspecting or scoring.")
    applicable = [x for x in checks["requirements"].values() if not x.get("not_applicable")]
    mapped = sum(bool(x["checks"]) for x in applicable)
    if mapped < len(applicable) and not args.allow_partial:
        raise AuditError(f"INCOMPLETE_VERIFICATION_PLAN: {mapped}/{len(applicable)} applicable criteria have checks. Map every applicable criterion or use --allow-partial for an explicitly incomplete diagnostic (never full issue completion).")
    available = []
    if args.repo_path:
        verify_commit_available(args.repo_path, source["pull_request"]["head_sha"])
        available.append("pinned Git commit")
    if args.executions:
        executions = read_json(args.executions)
        require_schema(executions, EXECUTIONS_SCHEMA)
        expected = {
            "source_digest": digest(source), "requirements_digest": digest(requirements),
            "checks_digest": digest(checks), "head_sha": source["pull_request"]["head_sha"],
        }
        if any(executions.get(k) != v for k, v in expected.items()):
            raise AuditError("Execution receipts belong to a different source, plan, or HEAD")
        if not any(r.get("status") in ("PASS", "FAIL") for r in executions.get("results", {}).values()):
            raise AuditError("NO_EXECUTED_TESTS: execution file has no evaluated test receipts")
        available.append("frozen execution receipts")
    if not available:
        raise AuditError("NO_AUDIT_EVIDENCE: no local repository containing the pinned HEAD and no executed test receipts. Try a read-only Git fetch. If unavailable, inspect GitHub source and CI using an authorized connector and report a QUALITATIVE evidence-backed analysis; do not report a completion percentage.")
    print(f"READY: {mapped}/{len(applicable)} criteria mapped, {declared} checks declared; evidence inputs: {', '.join(available)}")
    if mapped < len(applicable):
        print("WARNING: PARTIAL PLAN; output cannot claim full issue completion or implementation progress")
    if source.get("capture", {}).get("method") == "offline_input":
        print("WARNING: offline issue body/comments may be partial; confirm the full normative issue before claiming complete scope")


def suggest_command(args: argparse.Namespace) -> None:
    source, req = read_json(args.source), read_json(args.requirements)
    hints = suggest_paths(source, req, args.repo_path)
    write_immutable(args.out, canonical(hints))
    print(f"Generated non-scoring lexical hints for {len(hints['candidates'])} criteria: {args.out}")


def verify_evidence_command(args: argparse.Namespace) -> None:
    source, req, plan = read_json(args.source), read_json(args.requirements), read_json(args.checks)
    frozen = read_json(args.evidence)
    executions = read_json(args.executions) if args.executions else None
    actual = inspect(source, req, plan, args.repo_path, executions)
    if canonical(actual) != canonical(frozen):
        raise AuditError("Frozen evidence differs from pinned Git inspection and/or test receipts")
    print(f"VERIFIED: evidence reinspection is byte-identical: {digest(actual)}")


def score_command(args: argparse.Namespace) -> None:
    source, req, plan, evidence = (read_json(x) for x in (args.source, args.requirements, args.checks, args.evidence))
    report = score(source, req, plan, evidence)
    out = Path(args.out)
    write_immutable(out / "report.json", canonical(report))
    write_immutable(out / "report.md", markdown_report(report).encode("utf-8"))
    value = report['overall']['completion_verified_pct']
    print(f"Verified evidence floor (NOT implementation progress): {value}%" if value is not None else "NOT ASSESSED: N/A; zero observed checks is not 0% implementation")
    print(f"Verdict: {report['verdict']}; report: {out / 'report.md'}")


def verify_command(args: argparse.Namespace) -> None:
    report = score(*[read_json(x) for x in (args.source, args.requirements, args.checks, args.evidence)])
    json_bytes = Path(args.report_json).read_bytes()
    md_bytes = Path(args.report_md).read_bytes()
    if json_bytes != canonical(report) or md_bytes != markdown_report(report).encode("utf-8"):
        raise AuditError("Report does not match canonical recomputation. Possible input/report drift or tampering.")
    print(f"VERIFIED: byte-identical report; report SHA-256 {hashlib.sha256(json_bytes).hexdigest()}")


def compare_command(args: argparse.Namespace) -> None:
    left, right = read_json(args.left), read_json(args.right)
    result = compare_reports(left, right)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


def run_tests_command(args: argparse.Namespace) -> None:
    if not args.execute:
        raise AuditError("Executing repo commands requires explicit --execute (untrusted code may run).")
    source, req, plan = read_json(args.source), read_json(args.requirements), read_json(args.checks)
    validate_checks(req, plan)
    require_schema(source, SOURCE_SCHEMA)
    head = source["pull_request"]["head_sha"]
    verify_commit_available(args.repo_path, head)
    current_head = git_bytes(args.repo_path, "rev-parse", "HEAD").decode().strip()
    if current_head != head:
        raise AuditError(f"Checkout HEAD {current_head} differs from pinned candidate {head}")
    dirty = git_bytes(args.repo_path, "status", "--porcelain")
    if dirty.strip():
        raise AuditError("Checkout is not clean. Run tests in a clean disposable clone/worktree.")
    tests = []
    for ident, binding in plan["requirements"].items():
        for check in binding["checks"]:
            if check["kind"] == "test":
                tests.append((ident, check))
    if not tests:
        raise AuditError("No test checks are defined in the evidence plan")
    print(f"Executing {len(tests)} explicitly declared test command(s) at {head}", file=sys.stderr)
    results = {}
    for ident, check in tests:
        key = f"{ident}/{check['id']}"
        command = check["argv"]
        limit = check.get("timeout_seconds", 120)
        try:
            # Drain output directly into SHA-256, never onto disk or into RAM.
            # This avoids accumulating Playwright/build/test logs in the audit.
            h = hashlib.sha256()
            size = [0]
            proc = subprocess.Popen(command, cwd=args.repo_path, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    shell=False, start_new_session=(os.name != "nt"))
            def drain():
                assert proc.stdout is not None
                while True:
                    chunk = proc.stdout.read(65536)
                    if not chunk:
                        break
                    size[0] += len(chunk)
                    h.update(chunk)
                proc.stdout.close()
            drain_thread = threading.Thread(target=drain, daemon=True)
            drain_thread.start()
            try:
                exit_code = proc.wait(timeout=limit)
                status = "PASS" if exit_code == 0 else "FAIL"
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                proc.wait()
                exit_code, status = None, "TIMEOUT"
            drain_thread.join(timeout=5)
            if drain_thread.is_alive():
                # A child process kept stdout open; incomplete evidence is not proof.
                status, exit_code = "ERROR", None
            results[key] = {"argv": command, "status": status, "exit_code": exit_code,
                            "output_sha256": h.hexdigest(), "output_size_bytes": size[0]}
        except OSError as exc:
            results[key] = {"argv": command, "status": "ERROR", "exit_code": None,
                            "error": f"{type(exc).__name__}: {str(exc)[:200]}"}
        print(f"{key}: {results[key]['status']}", file=sys.stderr)
    if git_bytes(args.repo_path, "rev-parse", "HEAD").decode().strip() != head:
        raise AuditError("Test execution changed HEAD; cannot certify receipts")
    if git_bytes(args.repo_path, "status", "--porcelain").strip():
        raise AuditError("Test execution left checkout dirty; use a disposable clean worktree and rerun")
    executions = {
        "schema": EXECUTIONS_SCHEMA, "source_digest": digest(source),
        "requirements_digest": digest(req), "checks_digest": digest(plan),
        "head_sha": head, "runtime": {"platform": platform.platform(),
                                       "python": platform.python_version()},
        "results": results,
    }
    write_immutable(args.out, canonical(executions))
    print(f"Test receipts written to {args.out}")


def init_code_review_command(args: argparse.Namespace) -> None:
    source, requirements = read_json(args.source), read_json(args.requirements)
    review = init_review(source, requirements)
    write_immutable(args.out, canonical(review))
    print(f"Code-review rubric created for {len(review['criteria'])} frozen criteria: {args.out}")



def collect_code_snapshots(source: dict, requirements: dict, review: dict, fetch=gh_api) -> dict:
    """Fetch cited full files at the pinned commit, without cloning or executing PR code."""
    validate_review(source, requirements, review)
    expected = {}
    for entry in review["criteria"].values():
        if entry["status"] == "UNVERIFIED":
            continue
        for citation in entry["evidence"]:
            path, sha = citation["path"], citation["blob_sha"]
            if path in expected and expected[path] != sha:
                raise AuditError(f"Conflicting blob identities for source path: {path}")
            expected[path] = sha
    if not expected:
        raise AuditError("NO_SUBSTANTIVE_REVIEW: capture-code-snapshots needs assessed source references")
    if len(expected) > MAX_FILES:
        raise AuditError(f"Too many cited files: {len(expected)} > {MAX_FILES}")
    head, repo = source["pull_request"]["head_sha"], source["repository"]
    files = []
    for path, expected_sha in sorted(expected.items()):
        item = fetch(f"repos/{repo}/contents/{quote(path, safe='/')}?ref={head}")
        if not isinstance(item, dict) or item.get("type") != "file" or item.get("encoding") != "base64":
            raise AuditError(f"Missing or unsupported pinned GitHub file: {path}")
        encoded = item.get("content")
        if not isinstance(encoded, str):
            raise AuditError(f"Invalid GitHub file payload: {path}")
        try:
            raw = base64.b64decode("".join(encoded.split()), validate=True)
            content = raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuditError(f"Invalid UTF-8/base64 from GitHub for {path}") from exc
        if len(raw) > MAX_FILE_BYTES:
            raise AuditError(f"Pinned source file exceeds maximum size: {path}")
        actual_sha = blob_sha(raw)
        if actual_sha != item.get("sha") or actual_sha != expected_sha:
            raise AuditError(f"Pinned GitHub blob SHA mismatch: {head}:{path}")
        files.append({"path": path, "blob_sha": actual_sha, "content": content})
    return {"schema": SNAPSHOTS_SCHEMA, "source_digest": digest(source),
            "head_sha": head, "files": files}


def capture_code_snapshots_command(args: argparse.Namespace) -> None:
    source, requirements, review = (read_json(p) for p in (args.source, args.requirements, args.review))
    snapshots = collect_code_snapshots(source, requirements, review)
    write_immutable(args.out, canonical(snapshots))
    print(f"Captured {len(snapshots['files'])} full source blobs at pinned HEAD: {args.out}")


def code_grade_command(args: argparse.Namespace) -> None:
    source, requirements, review = (read_json(p) for p in (args.source, args.requirements, args.review))
    snapshots = read_json(args.snapshots) if args.snapshots else None
    result = grade(source, requirements, review, repo_path=args.repo_path, snapshots=snapshots,
                   allow_provisional=args.allow_provisional)
    if args.require_review and not result["summary"]["assessed"]:
        raise AuditError("NO_SUBSTANTIVE_REVIEW: final graded audit needs at least one source-adjudicated AC")
    output = Path(args.out)
    write_immutable(output / "implementation-grade.json", canonical(result))
    write_immutable(output / "implementation-grade.md", markdown_grade(result).encode("utf-8"))
    print(f"Numeric delivery grade (conservative floor, CI-independent): {result['summary']['numeric_delivery_grade_pct']}/100; "
          f"reviewed: {result['summary']['assessed']}/{result['summary']['total']}; "
          f"provenance: {result['code_provenance']}")
    print(f"Frozen code-grade: {output / 'implementation-grade.md'}")


def verify_code_grade_command(args: argparse.Namespace) -> None:
    source, requirements, review = (read_json(p) for p in (args.source, args.requirements, args.review))
    snapshots = read_json(args.snapshots) if args.snapshots else None
    result = grade(source, requirements, review, repo_path=args.repo_path, snapshots=snapshots,
                   allow_provisional=args.allow_provisional)
    if args.require_review and not result["summary"]["assessed"]:
        raise AuditError("NO_SUBSTANTIVE_REVIEW: final graded audit needs at least one source-adjudicated AC")
    if Path(args.report_json).read_bytes() != canonical(result) or Path(args.report_md).read_bytes() != markdown_grade(result).encode("utf-8"):
        raise AuditError("Code-delivery report differs from reproducible frozen review")
    print(f"VERIFIED: deterministic code-delivery grade {digest(result)}")


def compare_code_grade_command(args: argparse.Namespace) -> None:
    left, right = read_json(args.left), read_json(args.right)
    result = compare_grades(left, right)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic PR-vs-issue scoring with frozen checks and evidence")
    sub = p.add_subparsers(dest="action", required=True)
    cap = sub.add_parser("capture", help="Freeze PR+issue+comments; fetch with gh or import JSON")
    cap.add_argument("--from-json", help="Offline source input")
    cap.add_argument("--pr-url")
    cap.add_argument("--repo")
    cap.add_argument("--pr", type=int)
    cap.add_argument("--issue", type=int)
    cap.add_argument("--spec-file", action="append", help="Additional normative Markdown; may repeat")
    cap.add_argument("--out", required=True, help="New directory for source.json and requirements.json")
    cap.set_defaults(handler=capture)
    init = sub.add_parser("init-checks", help="Create evidence contract with one entry per criterion")
    init.add_argument("--requirements", required=True)
    init.add_argument("--out", required=True)
    init.set_defaults(handler=init_command)
    sugg = sub.add_parser("suggest", help="Lexical file candidates, never counted as proof")
    sugg.add_argument("--source", required=True)
    sugg.add_argument("--requirements", required=True)
    sugg.add_argument("--repo-path", required=True)
    sugg.add_argument("--out", required=True)
    sugg.set_defaults(handler=suggest_command)
    ready = sub.add_parser("preflight", help="Require usable exact-SHA evidence inputs before numeric audit")
    ready.add_argument("--source", required=True)
    ready.add_argument("--requirements", required=True)
    ready.add_argument("--checks", required=True)
    ready.add_argument("--repo-path", help="Local Git repository containing the captured HEAD")
    ready.add_argument("--executions", help="Exact-SHA frozen test receipts")
    ready.add_argument("--allow-partial", action="store_true", help="Permit an explicitly incomplete diagnostic; not a final compliance assessment")
    ready.set_defaults(handler=preflight_command)
    for name, handler in (("inspect", inspect_command), ("score", score_command), ("verify", verify_command),
                          ("verify-evidence", verify_evidence_command), ("run-tests", run_tests_command)):
        cmd = sub.add_parser(name)
        cmd.add_argument("--source", required=True)
        cmd.add_argument("--requirements", required=True)
        cmd.add_argument("--checks", required=True)
        if name == "inspect":
            cmd.add_argument("--repo-path", help="Local Git repository containing exact PR HEAD commit")
            cmd.add_argument("--executions", help="Frozen test receipts (optional)")
            cmd.add_argument("--out", required=True)
        elif name == "score":
            cmd.add_argument("--evidence", required=True)
            cmd.add_argument("--out", required=True, help="Report output directory")
        elif name == "verify":
            cmd.add_argument("--evidence", required=True)
            cmd.add_argument("--report-json", required=True)
            cmd.add_argument("--report-md", required=True)
        elif name == "verify-evidence":
            cmd.add_argument("--evidence", required=True)
            cmd.add_argument("--repo-path", required=True)
            cmd.add_argument("--executions")
        else:
            cmd.add_argument("--repo-path", required=True)
            cmd.add_argument("--execute", action="store_true")
            cmd.add_argument("--out", required=True)
        cmd.set_defaults(handler=handler)
    initial = sub.add_parser("init-code-review", help="Scaffold every AC/REQ for CI-independent code analysis")
    initial.add_argument("--source", required=True)
    initial.add_argument("--requirements", required=True)
    initial.add_argument("--out", required=True)
    initial.set_defaults(handler=init_code_review_command)
    code_cap = sub.add_parser("capture-code-snapshots", help="Fetch referenced HEAD blobs via gh (no checkout)")
    for required in ("source", "requirements", "review", "out"):
        code_cap.add_argument(f"--{required}", required=True)
    code_cap.set_defaults(handler=capture_code_snapshots_command)
    for action, handler in (("code-grade", code_grade_command), ("verify-code-grade", verify_code_grade_command)):
        cmd = sub.add_parser(action, help="Score validated source-code implementation without CI inputs")
        cmd.add_argument("--source", required=True)
        cmd.add_argument("--requirements", required=True)
        cmd.add_argument("--review", required=True)
        cmd.add_argument("--repo-path", help="Local Git checkout with candidate commit")
        cmd.add_argument("--snapshots", help="Frozen code-file contents collected at candidate HEAD")
        cmd.add_argument("--allow-provisional", action="store_true", help="Explicitly grade source-traced citations without Git object verification; marked provisional")
        cmd.add_argument("--require-review", action="store_true", help="Reject all-UNVERIFIED diagnostics as final audits")
        if action == "code-grade":
            cmd.add_argument("--out", required=True)
        else:
            cmd.add_argument("--report-json", required=True)
            cmd.add_argument("--report-md", required=True)
        cmd.set_defaults(handler=handler)
    comp_code = sub.add_parser("compare-code-grade", help="Compare common reviewed AC scope without using CI")
    comp_code.add_argument("--left", required=True)
    comp_code.add_argument("--right", required=True)
    comp_code.set_defaults(handler=compare_code_grade_command)
    comp = sub.add_parser("compare", help="Compare only reports with the same spec/plan/algorithm")
    comp.add_argument("--left", required=True)
    comp.add_argument("--right", required=True)
    comp.set_defaults(handler=compare_command)
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
        return 0
    except (AuditError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
