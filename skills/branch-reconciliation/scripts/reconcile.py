#!/usr/bin/env python3
"""Plan or apply a single-parent integration using Git's three-way tree engine.

Only local Git objects and explicit local refs are used. No fetch, reset, merge
commit, checkout, force push, arbitrary project commands, or network writes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

OID = re.compile(r"^[0-9a-f]{40,64}$")


class Blocked(Exception):
    pass


def git(repo: Path, *args: str, stdin: str | None = None, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(command, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if check and result.returncode:
        raise Blocked(f"git {args[0]} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result


def commit_oid(repo: Path, ref: str) -> str:
    if not ref or ref.startswith("-") or "\x00" in ref:
        raise Blocked("Invalid revision")
    result = git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}")
    oid = result.stdout.strip()
    if not OID.fullmatch(oid):
        raise Blocked("Revision did not resolve to a commit")
    return oid


def target_ref(repo: Path, branch: str) -> str:
    if not branch or branch.startswith("-") or branch.startswith("refs/"):
        raise Blocked("Target must be a local branch name")
    git(repo, "check-ref-format", "--branch", branch)
    ref = "refs/heads/" + branch
    if git(repo, "show-ref", "--verify", "--quiet", ref, check=False).returncode:
        raise Blocked("Destination local branch does not exist")
    return ref


def merge_base(repo: Path, source: str, target: str, explicit: str | None) -> str:
    if explicit:
        base = commit_oid(repo, explicit)
        for tip in (source, target):
            if git(repo, "merge-base", "--is-ancestor", base, tip, check=False).returncode:
                raise Blocked("Explicit merge base is not an ancestor of both tips")
        return base
    result = git(repo, "merge-base", "--all", source, target, check=False)
    if result.returncode:
        raise Blocked("No common history; refusing unrelated branches")
    bases = result.stdout.splitlines()
    if len(bases) != 1:
        raise Blocked("Ambiguous merge base; supply a reviewed --base")
    return bases[0]


def entries(repo: Path, revision: str) -> dict[str, tuple[str, str, str]]:
    raw = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--full-tree", revision], capture_output=True)
    if raw.returncode:
        raise Blocked("Cannot inventory complete recursive tree")
    result: dict[str, tuple[str, str, str]] = {}
    for record in raw.stdout.split(b"\x00"):
        if not record:
            continue
        try:
            header, name = record.split(b"\t", 1)
            mode, kind, oid = header.decode("ascii").split(" ")
            path = os.fsdecode(name)
        except (ValueError, UnicodeError) as exc:
            raise Blocked("Unsupported Git tree entry") from exc
        if path in result:
            raise Blocked("Duplicate tree entry")
        result[path] = (mode, kind, oid)
    return result


def classify(base: dict, source: dict, target: dict, candidate: dict | None) -> dict:
    groups: dict[str, list[str]] = {key: [] for key in ("source_only", "target_only", "both_same", "both_changed", "unchanged")}
    for path in sorted(base.keys() | source.keys() | target.keys()):
        b, s, t = base.get(path), source.get(path), target.get(path)
        if s == t:
            group = "unchanged" if s == b else "both_same"
        elif b == t:
            group = "source_only"
        elif b == s:
            group = "target_only"
        else:
            group = "both_changed"
        groups[group].append(path)
        if candidate is not None:
            actual = candidate.get(path)
            if group in ("source_only", "both_same", "unchanged") and actual != s:
                raise Blocked(f"Integration lost source content or mode: {path}")
            if group == "target_only" and actual != t:
                raise Blocked(f"Integration lost destination content or mode: {path}")
            if group == "both_changed" and actual is None and s is not None and t is not None:
                raise Blocked(f"Integration dropped both versions of {path}")
    if candidate is not None and (candidate.keys() - (base.keys() | source.keys() | target.keys())):
        raise Blocked("Integration introduced an unrecognized path")
    return groups


def resolved_tree(repo: Path, preliminary: str, conflicts: list[str], manifest_path: Path, root: Path) -> str:
    if manifest_path.is_symlink() or not manifest_path.is_file() or root.is_symlink():
        raise Blocked("Unsafe resolution manifest or root")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        root = root.resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise Blocked("Cannot read resolutions") from exc
    paths = manifest.get("paths") if isinstance(manifest, dict) and manifest.get("schema") == "branch-reconciliation-resolutions/v1" else None
    if not isinstance(paths, dict) or set(paths) != set(conflicts):
        raise Blocked("Resolution paths must exactly match unresolved conflict paths")
    with tempfile.TemporaryDirectory(prefix="branch-reconciliation-") as folder:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(folder) / "index"))
        git(repo, "read-tree", preliminary, env=env)
        for path in conflicts:
            entry = paths[path]
            if not isinstance(entry, dict) or not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
                raise Blocked(f"Reviewed resolution reason required: {path}")
            if entry.get("delete") is True and set(entry) == {"delete", "reason"}:
                git(repo, "update-index", "--force-remove", "--", path, env=env)
                continue
            if set(entry) != {"file", "mode", "reason"} or entry["mode"] not in {"100644", "100755", "120000"}:
                raise Blocked(f"Unsupported resolution mode or fields: {path}")
            relative = entry["file"]
            if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise Blocked(f"Resolution file must be a safe relative path: {path}")
            selected = root / relative
            if selected.is_symlink() or not selected.is_file() or not selected.resolve().is_relative_to(root):
                raise Blocked(f"Unsafe resolution file: {path}")
            data = selected.read_bytes()
            digest = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=data, capture_output=True)
            if digest.returncode or not OID.fullmatch(digest.stdout.decode("ascii", errors="replace").strip()):
                raise Blocked(f"Unable to store resolution: {path}")
            oid = digest.stdout.decode("ascii").strip()
            git(repo, "update-index", "--add", "--cacheinfo", f"{entry['mode']},{oid},{path}", env=env)
        result = git(repo, "write-tree", env=env).stdout.strip()
        if not OID.fullmatch(result):
            raise Blocked("Resolved tree is not a valid object")
        return result


def build_plan(repo: Path, source_ref: str, branch: str, base_ref: str | None,
               resolutions: Path | None = None, resolution_root: Path | None = None) -> dict:
    ref = target_ref(repo, branch)
    source = commit_oid(repo, source_ref)
    target = commit_oid(repo, ref)
    base = merge_base(repo, source, target, base_ref)
    b, s, t = (entries(repo, oid) for oid in (base, source, target))
    if len(b | s | t) > 100000:
        raise Blocked("Tree inventory exceeds the 100000-path safety ceiling")
    # Attributes can select custom external merge drivers from Git configuration.
    # Never invoke an unreviewed command supplied by a repository or host config.
    drivers = git(repo, "config", "--get-regexp", r"^merge\..*\.driver$", check=False)
    if drivers.returncode == 0 and drivers.stdout.strip():
        raise Blocked("Custom external Git merge drivers require a separately reviewed environment")
    if drivers.returncode not in (0, 1):
        raise Blocked("Cannot inspect Git merge drivers")
    command = ["git", "-C", str(repo), "merge-tree", "--write-tree", "--name-only", "-z",
               "--merge-base=" + base, target, source]
    merge = subprocess.run(command, capture_output=True)
    if merge.returncode not in (0, 1):
        raise Blocked("Git merge-tree failed: " + (merge.stderr or merge.stdout).decode("utf-8", errors="replace")[:800])
    items = merge.stdout.split(b"\x00\x00", 1)[0].split(b"\x00")
    first = items[0].decode("ascii", errors="replace") if items else ""
    if not OID.fullmatch(first):
        raise Blocked("Git merge-tree did not return a valid tree object")
    conflicted = merge.returncode == 1
    conflict_paths = [os.fsdecode(p) for p in items[1:] if p] if conflicted else []
    if len(conflict_paths) != len(set(conflict_paths)):
        raise Blocked("Duplicate conflict paths from merge-tree")
    if conflicted and not conflict_paths:
        raise Blocked("Unreported conflict paths")
    if conflicted and resolutions is not None:
        if resolution_root is None:
            raise Blocked("--resolution-root is required with --resolutions")
        candidate_oid = resolved_tree(repo, first, conflict_paths, resolutions, resolution_root)
    elif not conflicted and resolutions is not None:
        raise Blocked("Resolutions supplied but merge-tree reports no conflicts")
    else:
        candidate_oid = None if conflicted else first
    candidate = entries(repo, candidate_oid) if candidate_oid is not None else None
    groups = classify(b, s, t, candidate)
    return {
        "schema": "branch-reconciliation-plan/v1",
        "source_ref": source_ref,
        "target_branch": branch,
        "source_sha": source,
        "target_sha": target,
        "base_sha": base,
        "candidate_tree": candidate_oid,
        "status": "conflicts" if candidate_oid is None else ("no_change" if candidate == t else "ready"),
        "groups": groups,
        "counts": {k: len(v) for k, v in groups.items()},
        "conflict_paths": conflict_paths,
        "resolution_required": conflicted,
    }


def load_plan(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise Blocked("Plan file missing or symbolic link")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Blocked("Cannot read plan JSON") from exc
    if not isinstance(value, dict) or value.get("schema") != "branch-reconciliation-plan/v1":
        raise Blocked("Unsupported plan format")
    return value


def apply(repo: Path, saved: dict, message: str, reviewed: bool,
          resolutions: Path | None = None, resolution_root: Path | None = None) -> dict:
    if not message.strip() or "\x00" in message:
        raise Blocked("Nonempty commit message required")
    expected = build_plan(repo, str(saved.get("source_ref", "")), str(saved.get("target_branch", "")),
                          str(saved["base_sha"]) if isinstance(saved.get("base_sha"), str) else None, resolutions, resolution_root)
    keys = ("schema", "source_ref", "target_branch", "source_sha", "target_sha", "base_sha",
            "candidate_tree", "status", "groups", "counts", "conflict_paths", "resolution_required")
    if any(expected[k] != saved.get(k) for k in keys):
        raise Blocked("Plan or branch tip changed; regenerate and review")
    if expected["status"] != "ready":
        raise Blocked("Only a conflict-free, changing tree can be applied")
    if expected["counts"]["both_changed"] and not reviewed:
        raise Blocked("Overlapping paths need explicit human/agent semantic review (--reviewed)")
    if git(repo, "status", "--porcelain", check=False).stdout.strip():
        raise Blocked("Worktree contains local changes; refusing to update a branch")
    branch = target_ref(repo, expected["target_branch"])
    checked = git(repo, "worktree", "list", "--porcelain").stdout.splitlines()
    if any(row == "branch " + branch for row in checked):
        raise Blocked("Destination branch is checked out in a worktree; switch to a detached worktree")
    if git(repo, "diff", "--check", expected["target_sha"], expected["candidate_tree"], check=False).returncode:
        raise Blocked("git diff --check rejected candidate")
    new_commit = git(repo, "commit-tree", expected["candidate_tree"], "-p", expected["target_sha"], stdin=message.rstrip() + "\n").stdout.strip()
    parent = git(repo, "rev-list", "--parents", "-n", "1", new_commit).stdout.strip().split()
    if parent != [new_commit, expected["target_sha"]]:
        raise Blocked("Candidate commit is not single-parent linear")
    if commit_oid(repo, expected["source_ref"]) != expected["source_sha"]:
        raise Blocked("Source moved during integration; regenerate the plan")
    git(repo, "update-ref", branch, new_commit, expected["target_sha"])
    return {"status": "applied", "new_commit": new_commit, "parent": expected["target_sha"],
            "source_sha": expected["source_sha"], "tree": expected["candidate_tree"],
            "target_ref": branch, "remote_pushed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    subs = parser.add_subparsers(dest="command", required=True)
    plan = subs.add_parser("plan", help="compute a full-tree integration candidate; no ref mutation")
    plan.add_argument("--source", required=True)
    plan.add_argument("--target", required=True, help="existing local branch name")
    plan.add_argument("--base", help="optional reviewed common ancestor")
    plan.add_argument("--output", type=Path, help="new JSON plan file (never overwrite)")
    plan.add_argument("--resolutions", type=Path, help="reviewed per-conflict resolution manifest")
    plan.add_argument("--resolution-root", type=Path, help="approved directory containing resolved files")
    change = subs.add_parser("apply", help="create exactly one single-parent commit and CAS local target ref")
    change.add_argument("--plan", required=True, type=Path)
    change.add_argument("--message", required=True)
    change.add_argument("--reviewed", action="store_true", help="acknowledge review of concurrent edits")
    change.add_argument("--resolutions", type=Path, help="same resolution manifest as the frozen plan")
    change.add_argument("--resolution-root", type=Path, help="same approved resolution root as the plan")
    change.add_argument("--confirm", action="store_true", help="explicit authorization for local branch ref update")
    args = parser.parse_args()
    try:
        repo = args.repo.resolve(strict=True)
        if args.command == "plan":
            result = build_plan(repo, args.source, args.target, args.base, args.resolutions, args.resolution_root)
            if args.output:
                if args.output.is_symlink() or args.output.exists():
                    raise Blocked("Plan output already exists or is a symbolic link")
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                    json.dump(result, stream, sort_keys=True, indent=2)
                    stream.write("\n")
            print(json.dumps(result, indent=2))
            return 3 if result["status"] == "conflicts" else 0
        if not args.confirm:
            raise Blocked("Apply requires --confirm")
        result = apply(repo, load_plan(args.plan), args.message, args.reviewed, args.resolutions, args.resolution_root)
        print(json.dumps(result, indent=2))
        return 0
    except (Blocked, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
