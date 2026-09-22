from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "static_change_gate.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def write_skill(root: Path, *, description: str | None = None, body: str = "# Demo\n") -> None:
    root.mkdir(parents=True, exist_ok=True)
    desc = description or "review candidate Agent Skill changes before acceptance using portable structural evidence, explicit regression gates, immutable identities, and delivery checks across multiple compatible agent hosts"
    (root / "SKILL.md").write_text(
        f"---\nname: {root.name}\ndescription: {desc}\n---\n\n{body}",
        encoding="utf-8",
    )


def parse(proc: subprocess.CompletedProcess[str]) -> dict:
    assert proc.stdout.strip(), proc.stderr
    return json.loads(proc.stdout)


def test_self_check_emits_stable_tree_hash() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill)
        a = run("--target", str(skill))
        b = run("--target", str(skill))
        assert a.returncode == b.returncode == 0
        ra, rb = parse(a), parse(b)
        assert ra["status"] == "pass"
        assert ra["target_tree_sha256"] == rb["target_tree_sha256"]


def test_invalid_unquoted_yaml_mapping_separator_is_blocking() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: review prompt surfaces: frontmatter descriptions and activation boundaries across compatible agent hosts with explicit evidence, immutable candidate identities, regression checks, portability review, and safe delivery acceptance\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        result = run("--target", str(skill), "--policy", "strict")
        report = parse(result)
        assert result.returncode == 1
        assert report["status"] == "fail"
        assert any(f["code"] == "frontmatter/yaml-invalid" for f in report["findings"])


def test_quoted_yaml_scalar_with_colon_is_valid() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            '---\nname: demo-skill\ndescription: "review prompt surfaces: frontmatter descriptions and activation boundaries across compatible agent hosts with explicit evidence, immutable candidate identities, regression checks, portability review, and safe delivery acceptance"\n---\n\n# Demo\n',
            encoding="utf-8",
        )
        result = run("--target", str(skill), "--policy", "strict")
        report = parse(result)
        assert result.returncode == 0, report
        assert report["status"] == "pass"


def test_block_scalar_description_and_optional_adapter_are_portable() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: >\n  review proposed skill changes before acceptance across multiple compatible agent hosts using portable evidence and explicit regression gates\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        (skill / "agents").mkdir()
        (skill / "agents" / "openai.yaml").write_text("interface:\n  display_name: Demo Skill\n", encoding="utf-8")
        result = run("--target", str(skill), "--profile", "portable")
        report = parse(result)
        assert result.returncode == 0, report
        assert report["portability"]["host_adapters"] == ["openai"]
        assert not report["portability"]["private_core_hits"]


def test_protected_path_change_is_blocking() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        before = base / "before"
        after = base / "after"
        write_skill(before)
        write_skill(after)
        (before / "evals").mkdir(); (after / "evals").mkdir()
        (before / "evals" / "golden.json").write_text('{"v":1}\n', encoding="utf-8")
        (after / "evals" / "golden.json").write_text('{"v":2}\n', encoding="utf-8")
        # Directory names intentionally differ from skill names, so copy through canonical roots.
        for root in (before, after):
            text = (root / "SKILL.md").read_text(encoding="utf-8").replace(f"name: {root.name}", "name: demo-skill")
            (root / "SKILL.md").write_text(text, encoding="utf-8")
        # Portable spec requires root-name match; use normal profile semantics by renaming roots.
        before2 = base / "b" / "demo-skill"; after2 = base / "a" / "demo-skill"
        before2.parent.mkdir(); after2.parent.mkdir()
        before.rename(before2); after.rename(after2)
        result = run("--target", str(after2), "--before", str(before2), "--protected-path", "evals/**")
        report = parse(result)
        assert result.returncode == 1
        assert "evals/golden.json" in report["protected_path_changes"]
        assert any(f["code"] == "evidence/protected-path-changed" for f in report["findings"])


def test_expected_hash_mismatch_is_blocking() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill)
        result = run("--target", str(skill), "--expected-target-sha256", "0" * 64)
        report = parse(result)
        assert result.returncode == 1
        assert any(f["code"] == "evidence/target-identity-mismatch" for f in report["findings"])


def test_artifact_receipt_must_match_candidate() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = base / "demo-skill"
        write_skill(skill)
        receipt = base / "receipt.json"
        receipt.write_text(json.dumps({"status": "pass", "source_tree_sha256": "f" * 64}), encoding="utf-8")
        result = run("--target", str(skill), "--artifact-receipt", str(receipt))
        report = parse(result)
        assert result.returncode == 1
        assert any(f["code"] == "delivery/receipt-candidate-mismatch" for f in report["findings"])


def test_report_inside_target_is_rejected_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill)
        before = hashlib.sha256((skill / "SKILL.md").read_bytes()).hexdigest()
        report_path = skill / "gate.json"
        result = run("--target", str(skill), "--json", str(report_path))
        report = parse(result)
        assert result.returncode == 1
        assert report["findings"][0]["code"] == "report/inside-target"
        assert not report_path.exists()
        assert hashlib.sha256((skill / "SKILL.md").read_bytes()).hexdigest() == before


def test_host_private_core_dependency_warns_normal_and_fails_strict() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill, body="# Demo\nUse `skills://private-runtime` as the required execution primitive.\n")
        normal = run("--target", str(skill), "--profile", "portable", "--policy", "normal")
        strict = run("--target", str(skill), "--profile", "portable", "--policy", "strict")
        assert parse(normal)["status"] == "pass-with-warnings"
        assert normal.returncode == 0
        assert parse(strict)["status"] == "fail"
        assert strict.returncode == 1


def test_receipt_with_matching_candidate_identity_passes() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = base / "demo-skill"
        write_skill(skill)
        first = run("--target", str(skill))
        first_report = parse(first)
        assert first.returncode == 0
        receipt = base / "receipt.json"
        receipt.write_text(json.dumps({"status": "pass", "source_tree_sha256": first_report["target_tree_sha256"]}), encoding="utf-8")
        second = run("--target", str(skill), "--artifact-receipt", str(receipt))
        second_report = parse(second)
        assert second.returncode == 0, second_report
        assert second_report["artifact_receipt"]["identity"] == second_report["target_tree_sha256"]


def test_token_efficiency_filename_is_not_treated_as_secret() -> None:
    with tempfile.TemporaryDirectory() as td:
        skill = Path(td) / "demo-skill"
        write_skill(skill)
        (skill / "references").mkdir()
        (skill / "references" / "token-efficiency.md").write_text("# Token efficiency\n", encoding="utf-8")
        result = run("--target", str(skill))
        report = parse(result)
        assert result.returncode == 0, report
        assert not any(f["code"] == "safety/sensitive-path" for f in report["findings"])


if __name__ == "__main__":
    tests = [
        test_self_check_emits_stable_tree_hash,
        test_invalid_unquoted_yaml_mapping_separator_is_blocking,
        test_quoted_yaml_scalar_with_colon_is_valid,
        test_block_scalar_description_and_optional_adapter_are_portable,
        test_protected_path_change_is_blocking,
        test_expected_hash_mismatch_is_blocking,
        test_artifact_receipt_must_match_candidate,
        test_receipt_with_matching_candidate_identity_passes,
        test_token_efficiency_filename_is_not_treated_as_secret,
        test_report_inside_target_is_rejected_without_mutation,
        test_host_private_core_dependency_warns_normal_and_fails_strict,
    ]
    for test in tests:
        test()
    print(f"ok: {len(tests)} tests")
