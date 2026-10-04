#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ALLOWED = {"used", "integrable", "duplicate", "obsolete", "generated", "blocked", "unknown"}


def write(path: Path, text: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")


def base_skill(root: Path, body: str = "") -> None:
    name = root.name
    write(
        root / "SKILL.md",
        f"---\nname: {name}\ndescription: Fixture used by cleanup regression evaluation for deterministic package mechanics.\n---\n\n# Fixture\n\n{body}\n",
    )


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted((item for item in root.rglob("*") if item.is_file() and not item.is_symlink()), key=lambda item: item.relative_to(root).as_posix()):
        h.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
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


def inventory(skill_root: Path, fixture: Path, roots: list[str] | None = None) -> dict:
    suffix = hashlib.sha256("|".join(roots or []).encode()).hexdigest()[:8]
    out = fixture.parent / (fixture.name + f"-inventory-{suffix}.json")
    cmd = [sys.executable, "-S", str(skill_root / "scripts/cleanup_inventory.py"), "--target", str(fixture), "--output", str(out)]
    for root_spec in roots or []:
        cmd.extend(["--root", root_spec])
    rc, payload, msg = run_json(cmd, out)
    if rc != 0 or payload is None:
        raise AssertionError(f"inventory failed rc={rc}: {msg}")
    return payload


def by_path(inv: dict) -> dict[str, dict]:
    return {entry["path"]: entry for entry in inv.get("entries", [])}


def apply_plan(skill_root: Path, fixture: Path, plan: dict, work: Path, *, do_apply: bool) -> tuple[int, dict | None, str]:
    plan_path = work / "plan.json"
    receipt = work / ("receipt-apply.json" if do_apply else "receipt-dry.json")
    write(plan_path, json.dumps(plan, indent=2, sort_keys=True) + "\n")
    cmd = [
        sys.executable,
        "-S",
        str(skill_root / "scripts/cleanup_apply.py"),
        "--target",
        str(fixture),
        "--plan",
        str(plan_path),
        "--work-dir",
        str(work / "recovery"),
        "--receipt",
        str(receipt),
    ]
    if do_apply:
        cmd.append("--apply")
    return run_json(cmd, receipt)


def plan_delete(
    rel: str,
    classification: str,
    expected_sha256: str | None,
    kind: str = "inventory",
    *,
    approval: str | None = None,
    checkpoint: str | None = None,
) -> dict:
    action = {
        "action": "delete",
        "path": rel,
        "classification": classification,
        "evidence": [{"kind": kind, "value": f"frozen-eval:{rel}"}],
    }
    if expected_sha256 is not None:
        action["expected_sha256"] = expected_sha256
    if approval is not None:
        action["approval"] = approval
    if checkpoint is not None:
        action["checkpoint"] = checkpoint
    return {"plan_version": 2, "actions": [action]}


def scenario_indirect(skill_root: Path, td: Path) -> None:
    root = td / "indirect-reference"
    index_rel = "references/index.md"
    deep_rel = "references/deep.md"
    base_skill(root, f"See [index]({index_rel}).")
    write(root / index_rel, "# Index\n\nSee [deep](deep.md).\n")
    write(root / deep_rel, "# Deep\n\nMaterial branch guidance.\n")
    inv = by_path(inventory(skill_root, root))
    assert inv[index_rel]["status"] == "used", inv[index_rel]
    assert inv[deep_rel]["status"] == "used", inv[deep_rel]


def scenario_partial_duplicate(skill_root: Path, td: Path) -> None:
    root = td / "partial-duplicate"
    base_skill(root)
    write(root / "references/a.md", "# Rules\nKeep behavior.\nValidate links.\nAlpha only.\n")
    write(root / "references/b.md", "# Rules\nKeep behavior.\nValidate links.\nBeta only.\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["references/a.md"]["status"] != "duplicate", inv["references/a.md"]
    assert inv["references/b.md"]["status"] != "duplicate", inv["references/b.md"]


def scenario_legitimate_scaffold(skill_root: Path, td: Path) -> None:
    root = td / "legitimate-scaffold"
    template_rel = "assets/templates/legit.md.template"
    base_skill(root, f"Use `{template_rel}` when producing a plan.")
    fill_marker = "TO" + "DO"
    write(root / template_rel, f"# Template\n\n{fill_marker}: {{{{filled_by_user}}}}\n")
    inv = by_path(inventory(skill_root, root))
    assert inv[template_rel]["status"] == "used", inv[template_rel]


def scenario_generated(skill_root: Path, td: Path) -> None:
    root = td / "generated-artifact"
    base_skill(root)
    junk = root / "__pycache__/junk.pyc"
    write(junk, b"generated-residue\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["__pycache__/junk.pyc"]["status"] == "generated", inv["__pycache__/junk.pyc"]
    before = tree_hash(root)
    work = td / "generated-work"
    work.mkdir()
    rc, receipt, msg = apply_plan(skill_root, root, plan_delete("__pycache__/junk.pyc", "generated", sha(junk)), work, do_apply=False)
    assert rc == 0, msg
    assert receipt and receipt.get("status") == "dry-run", receipt
    assert tree_hash(root) == before and junk.exists(), "dry-run mutated target"


def scenario_weak_generated_namespace(skill_root: Path, td: Path) -> None:
    root = td / "weak-generated-namespace"
    base_skill(root)
    artifact = root / "dist/manual-reference.md"
    write(artifact, "human-authored material\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["dist/manual-reference.md"]["status"] != "generated", inv["dist/manual-reference.md"]
    assert any(signal.get("strength") == "weak" for signal in inv["dist/manual-reference.md"]["generated_signals"])
    work1 = td / "weak-generated-reject"; work1.mkdir()
    rc1, receipt1, _ = apply_plan(skill_root, root, plan_delete("dist/manual-reference.md", "generated", sha(artifact)), work1, do_apply=False)
    assert rc1 != 0 and receipt1 and receipt1.get("status") == "rejected", receipt1
    work2 = td / "weak-generated-approved"; work2.mkdir()
    approved = plan_delete("dist/manual-reference.md", "generated", sha(artifact), kind="target-doc", approval="explicit")
    rc2, receipt2, msg2 = apply_plan(skill_root, root, approved, work2, do_apply=False)
    assert rc2 == 0, msg2
    assert receipt2 and receipt2.get("status") == "dry-run", receipt2


def scenario_declared_root(skill_root: Path, td: Path) -> None:
    root = td / "declared-root"
    base_skill(root)
    write(root / "runtime/entry.txt", "references/dynamic.md\n")
    write(root / "runtime/references/dynamic.md", "dynamic consumer target\n")
    without = by_path(inventory(skill_root, root))
    assert without["runtime/references/dynamic.md"]["status"] == "unknown", without["runtime/references/dynamic.md"]
    inv = inventory(skill_root, root, roots=["runtime-root:runtime/entry.txt"])
    entries = by_path(inv)
    assert entries["runtime/entry.txt"]["status"] == "used", entries["runtime/entry.txt"]
    assert entries["runtime/references/dynamic.md"]["status"] == "used", entries["runtime/references/dynamic.md"]
    assert any(item["kind"] == "runtime-root" and item["path"] == "runtime/entry.txt" for item in inv["root_registry"])


def scenario_typed_edges(skill_root: Path, td: Path) -> None:
    root = td / "typed-edges"
    base_skill(root, "See [rules](references/rules.md).")
    write(root / "references/rules.md", "# Rules\n")
    inv = inventory(skill_root, root)
    assert any(edge["source"] == "SKILL.md" and edge["target"] == "references/rules.md" and edge["kind"] == "markdown-link" for edge in inv["reference_edges"]), inv["reference_edges"]


def scenario_markdown_image(skill_root: Path, td: Path) -> None:
    root = td / "markdown-image"
    base_skill(root, "![icon](assets/icon.svg)")
    write(root / "assets/icon.svg", "<svg></svg>\n")
    inv = inventory(skill_root, root)
    entries = by_path(inv)
    assert entries["assets/icon.svg"]["status"] == "used", entries["assets/icon.svg"]
    assert any(edge["kind"] == "markdown-image" and edge["target"] == "assets/icon.svg" for edge in inv["reference_edges"])


def scenario_protected(skill_root: Path, td: Path) -> None:
    root = td / "protected-evidence"
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


def scenario_eval_protected(skill_root: Path, td: Path) -> None:
    root = td / "eval-protected"
    base_skill(root)
    write(root / "evals/scenarios.json", "{}\n")
    inv = by_path(inventory(skill_root, root))
    assert inv["evals/scenarios.json"]["status"] == "blocked", inv["evals/scenarios.json"]


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
    rc, receipt, _ = apply_plan(skill_root, root, plan_delete("references/outside-link.md", "obsolete", None, kind="target-doc", approval="explicit"), work, do_apply=True)
    assert rc != 0, receipt
    assert link.is_symlink() and outside.exists(), "symlink cleanup escaped or mutated"


def scenario_rerun(skill_root: Path, td: Path) -> None:
    root = td / "rerun"
    base_skill(root)
    junk = root / "__pycache__/junk.pyc"
    write(junk, b"generated residue\n")
    expected = sha(junk)
    plan = plan_delete("__pycache__/junk.pyc", "generated", expected)
    work1 = td / "rerun-work1"; work1.mkdir()
    rc1, receipt1, msg1 = apply_plan(skill_root, root, plan, work1, do_apply=True)
    assert rc1 == 0, msg1
    assert not junk.exists(), "first apply did not remove generated file"
    assert receipt1 and receipt1.get("status") == "pass", receipt1
    assert receipt1.get("checkpoints") and receipt1["checkpoints"][0]["name"] == "default", receipt1
    after1 = tree_hash(root)
    work2 = td / "rerun-work2"; work2.mkdir()
    rc2, receipt2, msg2 = apply_plan(skill_root, root, plan, work2, do_apply=True)
    assert rc2 == 0, msg2
    assert receipt2 and receipt2.get("status") == "pass", receipt2
    assert "already_absent" in [action.get("result") for action in receipt2.get("actions", [])], receipt2
    assert tree_hash(root) == after1, "rerun changed target"


def scenario_failure_rollback(skill_root: Path, td: Path) -> None:
    root = td / "cleanup-failure-rollback"
    base_skill(root)
    junk = root / "__pycache__/junk.pyc"
    write(junk, b"generated residue\n")
    write(root / "blocked.zip", "not-a-real-zip\n")
    before = tree_hash(root)
    expected = sha(junk)
    work = td / "rollback-work"; work.mkdir()
    rc, receipt, _ = apply_plan(skill_root, root, plan_delete("__pycache__/junk.pyc", "generated", expected), work, do_apply=True)
    assert rc != 0, receipt
    assert receipt and receipt.get("status") == "rolled-back", receipt
    assert junk.exists() and sha(junk) == expected, "last-known-good file was not restored"
    assert tree_hash(root) == before, "rollback did not restore target tree"


def scenario_external_validation_rollback(skill_root: Path, td: Path) -> None:
    root = td / "external-validation-rollback"
    base_skill(root)
    junk = root / "__pycache__/junk.pyc"
    write(junk, b"generated residue\n")
    failer = root / "scripts/fail_validation.py"
    write(failer, "raise SystemExit(7)\n")
    before = tree_hash(root)
    plan = plan_delete("__pycache__/junk.pyc", "generated", sha(junk))
    plan["validation_commands"] = [{"name": "fixture-failure", "approved": True, "argv": [sys.executable, "scripts/fail_validation.py"], "timeout_seconds": 30}]
    work = td / "external-validation-work"; work.mkdir()
    rc, receipt, _ = apply_plan(skill_root, root, plan, work, do_apply=True)
    assert rc != 0, receipt
    assert receipt and receipt.get("status") == "rolled-back", receipt
    assert receipt.get("validations") and receipt["validations"][0]["exit_code"] == 7, receipt
    assert tree_hash(root) == before and junk.exists(), "external validation failure did not restore baseline"


def scenario_noncanonical(skill_root: Path, td: Path) -> None:
    root = td / "noncanonical-path"
    base_skill(root)
    junk = root / "__pycache__/junk.pyc"
    write(junk, b"generated residue\n")
    work = td / "noncanonical-work"; work.mkdir()
    plan = plan_delete("__pycache__/../__pycache__/junk.pyc", "generated", sha(junk))
    rc, receipt, _ = apply_plan(skill_root, root, plan, work, do_apply=True)
    assert rc != 0, receipt
    assert junk.exists(), "noncanonical path mutated target"
    assert receipt and receipt.get("status") == "rejected", receipt


def scenario_status_vocabulary(skill_root: Path, td: Path) -> None:
    root = td / "status-vocabulary"
    used_rel = "references/used.md"
    base_skill(root, f"Use `{used_rel}`.")
    write(root / used_rel, "used\n")
    write(root / "references/free.md", "free\n")
    write(root / "__pycache__/generated.pyc", b"generated\n")
    write(root / "evidence/protected.txt", "protected\n")
    write(root / "references/dup-a.txt", "duplicate\n")
    write(root / "references/dup-b.txt", "duplicate\n")
    inv = inventory(skill_root, root)
    statuses = {entry.get("status") for entry in inv.get("entries", [])}
    assert statuses <= ALLOWED, statuses - ALLOWED


SCENARIOS = [
    ("indirect-reference", scenario_indirect),
    ("partial-duplicate", scenario_partial_duplicate),
    ("legitimate-scaffold", scenario_legitimate_scaffold),
    ("generated-artifact", scenario_generated),
    ("weak-generated-namespace", scenario_weak_generated_namespace),
    ("declared-root", scenario_declared_root),
    ("typed-edges", scenario_typed_edges),
    ("markdown-image", scenario_markdown_image),
    ("protected-evidence", scenario_protected),
    ("eval-protected", scenario_eval_protected),
    ("symlink", scenario_symlink),
    ("rerun", scenario_rerun),
    ("cleanup-failure-rollback", scenario_failure_rollback),
    ("external-validation-rollback", scenario_external_validation_rollback),
    ("noncanonical-path", scenario_noncanonical),
    ("status-vocabulary", scenario_status_vocabulary),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    skill_root = Path(args.skill_root).resolve()
    results = []
    with tempfile.TemporaryDirectory(prefix="cleanup-regression-") as tmp:
        td = Path(tmp)
        for scenario_id, function in SCENARIOS:
            try:
                function(skill_root, td)
                results.append({"id": scenario_id, "status": "pass"})
            except Exception as exc:
                results.append({"id": scenario_id, "status": "fail", "error": f"{type(exc).__name__}: {exc}"})
    failed = [result for result in results if result["status"] == "fail"]
    report = {
        "suite_version": 2,
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
