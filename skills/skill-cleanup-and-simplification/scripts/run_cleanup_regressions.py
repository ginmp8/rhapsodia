#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
import tempfile
from pathlib import Path

ALLOWED = {"used", "integrable", "duplicate", "obsolete", "generated", "blocked", "unknown"}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def base_skill(root: Path, body: str = "") -> None:
    write(root / "SKILL.md", "---\nname: fixture-skill\ndescription: fixture used by cleanup regression evaluation.\n---\n\n# Fixture\n\n" + body + "\n")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted((x for x in root.rglob("*") if x.is_file() and not x.is_symlink()), key=lambda x: x.relative_to(root).as_posix()):
        rel = p.relative_to(root).as_posix().encode()
        h.update(rel + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def run_json(cmd: list[str], output: Path | None = None) -> tuple[int, dict | None, str]:
    cp = subprocess.run(cmd, text=True, capture_output=True)
    payload = None
    if output and output.exists():
        try:
            payload = json.loads(output.read_text(encoding="utf-8"))
        except Exception:
            payload = None
    return cp.returncode, payload, (cp.stdout + cp.stderr).strip()


def inventory(skill_root: Path, fixture: Path) -> dict:
    out = fixture.parent / (fixture.name + "-inventory.json")
    rc, payload, msg = run_json([sys.executable, "-S", str(skill_root / "scripts/cleanup_inventory.py"), "--target", str(fixture), "--output", str(out)], out)
    if rc != 0 or payload is None:
        raise AssertionError(f"inventory failed rc={rc}: {msg}")
    return payload


def by_path(inv: dict) -> dict[str, dict]:
    return {e["path"]: e for e in inv.get("entries", [])}


def apply_plan(skill_root: Path, fixture: Path, plan: dict, work: Path, *, do_apply: bool) -> tuple[int, dict | None, str]:
    plan_path = work / "plan.json"
    receipt = work / ("receipt-apply.json" if do_apply else "receipt-dry.json")
    write(plan_path, json.dumps(plan, indent=2, sort_keys=True) + "\n")
    cmd = [sys.executable, "-S", str(skill_root / "scripts/cleanup_apply.py"), "--target", str(fixture), "--plan", str(plan_path), "--work-dir", str(work / "recovery"), "--receipt", str(receipt)]
    if do_apply:
        cmd.append("--apply")
    return run_json(cmd, receipt)


def plan_delete(rel: str, classification: str, expected_sha256: str | None, kind: str = "inventory") -> dict:
    action = {
        "action": "delete",
        "path": rel,
        "classification": classification,
        "evidence": [{"kind": kind, "value": f"frozen-eval:{rel}"}],
    }
    if expected_sha256 is not None:
        action["expected_sha256"] = expected_sha256
    return {"plan_version": 1, "actions": [action]}


def scenario_indirect(skill_root: Path, td: Path) -> None:
    root = td / "indirect"
    base_skill(root, "See [index](references/index.md).")
    write(root / "references/index.md", "# Index\n\nSee [deep](deep.md).\n")
    write(root / "references/deep.md", "# Deep\n\nMaterial branch guidance.\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["references/index.md"]["status"] == "used", inv["references/index.md"]
    assert inv["references/deep.md"]["status"] == "used", inv["references/deep.md"]


def scenario_partial_duplicate(skill_root: Path, td: Path) -> None:
    root = td / "partial"
    base_skill(root)
    write(root / "references/a.md", "# Rules\nKeep behavior.\nValidate links.\nAlpha only.\n")
    write(root / "references/b.md", "# Rules\nKeep behavior.\nValidate links.\nBeta only.\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["references/a.md"]["status"] != "duplicate", inv["references/a.md"]
    assert inv["references/b.md"]["status"] != "duplicate", inv["references/b.md"]


def scenario_legitimate_scaffold(skill_root: Path, td: Path) -> None:
    root = td / "scaffold"
    base_skill(root, "Use `assets/templates/legit.md.template` when producing a plan.")
    write(root / "assets/templates/legit.md.template", "# Template\n\nTODO: {{filled_by_user}}\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["assets/templates/legit.md.template"]["status"] == "used", inv["assets/templates/legit.md.template"]


def scenario_generated(skill_root: Path, td: Path) -> None:
    root = td / "generated"
    base_skill(root)
    junk = root / "dist/junk.txt"
    write(junk, "generated residue\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["dist/junk.txt"]["status"] == "generated", inv["dist/junk.txt"]
    before = tree_hash(root)
    work = td / "generated-work"
    work.mkdir()
    rc, receipt, msg = apply_plan(skill_root, root, plan_delete("dist/junk.txt", "generated", sha(junk)), work, do_apply=False)
    assert rc == 0, msg
    assert receipt and receipt.get("status") == "dry-run", receipt
    assert tree_hash(root) == before and junk.exists(), "dry-run mutated target"


def scenario_protected(skill_root: Path, td: Path) -> None:
    root = td / "protected"
    base_skill(root)
    protected = root / "evidence/run.json"
    write(protected, "{}\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["evidence/run.json"]["status"] == "blocked", inv["evidence/run.json"]
    work = td / "protected-work"
    work.mkdir()
    rc, receipt, _ = apply_plan(skill_root, root, plan_delete("evidence/run.json", "generated", sha(protected)), work, do_apply=True)
    assert rc != 0, receipt
    assert protected.exists(), "protected evidence was removed"
    assert receipt and receipt.get("status") == "rejected", receipt


def scenario_symlink(skill_root: Path, td: Path) -> None:
    root = td / "symlink"
    base_skill(root)
    outside = td / "outside.txt"
    write(outside, "outside\n")
    link = root / "references/outside-link.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        return
    inv = by_path(inventory(skill_root, root))
    assert inv["references/outside-link.md"]["status"] == "blocked", inv["references/outside-link.md"]
    work = td / "symlink-work"
    work.mkdir()
    rc, receipt, _ = apply_plan(skill_root, root, plan_delete("references/outside-link.md", "obsolete", None, kind="explicit-obsolete"), work, do_apply=True)
    assert rc != 0, receipt
    assert link.is_symlink() and outside.exists(), "symlink cleanup escaped or mutated"


def scenario_rerun(skill_root: Path, td: Path) -> None:
    root = td / "rerun"
    base_skill(root)
    junk = root / "dist/junk.txt"
    write(junk, "generated residue\n")
    expected = sha(junk)
    plan = plan_delete("dist/junk.txt", "generated", expected)
    work1 = td / "rerun-work1"; work1.mkdir()
    rc1, receipt1, msg1 = apply_plan(skill_root, root, plan, work1, do_apply=True)
    assert rc1 == 0, msg1
    assert not junk.exists(), "first apply did not remove generated file"
    assert receipt1 and receipt1.get("status") == "pass", receipt1
    after1 = tree_hash(root)
    work2 = td / "rerun-work2"; work2.mkdir()
    rc2, receipt2, msg2 = apply_plan(skill_root, root, plan, work2, do_apply=True)
    assert rc2 == 0, msg2
    assert receipt2 and receipt2.get("status") == "pass", receipt2
    action_states = [a.get("result") for a in receipt2.get("actions", [])]
    assert "already_absent" in action_states, receipt2
    assert tree_hash(root) == after1, "rerun changed target"


def scenario_failure_rollback(skill_root: Path, td: Path) -> None:
    root = td / "rollback"
    base_skill(root)
    junk = root / "dist/junk.txt"
    write(junk, "generated residue\n")
    # Leave a separate blocked archive so post-cleanup package validation fails.
    write(root / "blocked.zip", "not-a-real-zip\n")
    before = tree_hash(root)
    expected = sha(junk)
    work = td / "rollback-work"; work.mkdir()
    rc, receipt, _ = apply_plan(skill_root, root, plan_delete("dist/junk.txt", "generated", expected), work, do_apply=True)
    assert rc != 0, receipt
    assert receipt and receipt.get("status") == "rolled-back", receipt
    assert junk.exists() and sha(junk) == expected, "last-known-good file was not restored"
    assert tree_hash(root) == before, "rollback did not restore target tree"
    recovery = receipt.get("recovery", {})
    assert recovery.get("last_known_good"), receipt


def scenario_noncanonical(skill_root: Path, td: Path) -> None:
    root = td / "noncanonical"
    base_skill(root)
    junk = root / "dist/junk.txt"
    write(junk, "generated residue\n")
    work = td / "noncanonical-work"; work.mkdir()
    plan = plan_delete("dist/../dist/junk.txt", "generated", sha(junk))
    rc, receipt, _ = apply_plan(skill_root, root, plan, work, do_apply=True)
    assert rc != 0, receipt
    assert junk.exists(), "noncanonical path mutated target"
    assert receipt and receipt.get("status") == "rejected", receipt


def scenario_status_vocabulary(skill_root: Path, td: Path) -> None:
    root = td / "states"
    base_skill(root, "Use `references/used.md`.")
    write(root / "references/used.md", "used\n")
    write(root / "references/free.md", "free\n")
    write(root / "dist/generated.txt", "generated\n")
    write(root / "evidence/protected.txt", "protected\n")
    write(root / "references/dup-a.txt", "duplicate\n")
    write(root / "references/dup-b.txt", "duplicate\n")
    inv = inventory(skill_root, root)
    statuses = {e.get("status") for e in inv.get("entries", [])}
    assert statuses <= ALLOWED, statuses - ALLOWED


SCENARIOS = [
    ("indirect-reference", scenario_indirect),
    ("partial-duplicate", scenario_partial_duplicate),
    ("legitimate-scaffold", scenario_legitimate_scaffold),
    ("generated-artifact", scenario_generated),
    ("protected-evidence", scenario_protected),
    ("symlink", scenario_symlink),
    ("rerun", scenario_rerun),
    ("cleanup-failure-rollback", scenario_failure_rollback),
    ("noncanonical-path", scenario_noncanonical),
    ("status-vocabulary", scenario_status_vocabulary),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", required=True)
    ap.add_argument("--json", required=True)
    args = ap.parse_args()
    skill_root = Path(args.skill_root).resolve()
    results = []
    with tempfile.TemporaryDirectory(prefix="cleanup-regression-") as tmp:
        td = Path(tmp)
        for sid, fn in SCENARIOS:
            try:
                fn(skill_root, td)
                results.append({"id": sid, "status": "pass"})
            except Exception as exc:
                results.append({"id": sid, "status": "fail", "error": f"{type(exc).__name__}: {exc}"})
    failed = [r for r in results if r["status"] == "fail"]
    report = {
        "suite_version": 1,
        "skill_root": str(skill_root),
        "status": "pass" if not failed else "fail",
        "summary": {"pass": len(results) - len(failed), "fail": len(failed), "total": len(results)},
        "results": results,
    }
    out = Path(args.json).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
