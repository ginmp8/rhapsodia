#!/usr/bin/env python3
"""Structural and safety tests for the bounded directory; not model/host behavior tests."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPOSITORY = SKILL.parents[1]
SCRIPT = SKILL / "scripts/capability_directory.py"
spec = importlib.util.spec_from_file_location("capability_directory", SCRIPT)
assert spec and spec.loader
DIRECTORY = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DIRECTORY)


def write_skill(where: Path, name: str, description: str = "Technical planning, not implementation") -> Path:
    path = where / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {name}\ndescription: {description}\n---\n# Skill\n", encoding="utf-8")
    return path


def run(*args):
    result = subprocess.run([sys.executable, "-I", "-S", "-B", str(SCRIPT), *map(str, args)],
                            capture_output=True, text=True, check=False)
    return result.returncode, json.loads(result.stdout) if result.stdout else {}


class DirectoryTests(unittest.TestCase):
    def test_skill_is_self_contained_and_top_100(self):
        lines = (SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines()
        front = DIRECTORY.metadata(SKILL / "SKILL.md")
        self.assertEqual(front["name"], "capability-discovery")
        self.assertLessEqual(len(front["description"]), 500)
        self.assertLessEqual(len(lines), 100)
        first = "\n".join(lines[:100]).lower()
        for term in ("host", "bootstrap", "authority", "source", "non-use", "not", "references/routing.md"):
            self.assertIn(term, first)
        self.assertNotIn("docs/agents/capability-discovery.md", first)
        self.assertTrue((SKILL / "scripts/capability_directory.py").is_file())
        self.assertTrue((SKILL / "references/routing.md").is_file())

    def test_local_repository_contains_agents_and_skills_with_digests(self):
        rc, data = run("list", "--root", REPOSITORY, "--limit", 150)
        self.assertEqual(rc, 0, data.get("errors"))
        self.assertEqual(data["status"], "candidates")
        names = {(x["kind"], x["id"]) for x in data["matches"]}
        self.assertIn(("agent", "magia"), names)
        self.assertIn(("skill", "magia"), names)
        self.assertIn(("skill", "capability-discovery"), names)
        for item in data["matches"]:
            if not item["path"].startswith("/"):
                self.assertEqual(item["sha256"], hashlib.sha256((REPOSITORY / item["path"]).read_bytes()).hexdigest())

    def test_project_installed_skill_root_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root / ".github/skills", "example", "Organize architecture diagrams")
            rc, data = run("find", "architecture", "--root", root, "--kind", "skill")
            self.assertEqual(rc, 0, data)
            self.assertEqual([m["id"] for m in data["matches"]], ["example"])
            self.assertIn(".github/skills", data["inspected_roots"])

    def test_explicit_external_root_is_bounded_and_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            target = Path(temp) / "external-skills"
            root.mkdir()
            write_skill(target, "other-provider", "Inspect performance regressions")
            rc, data = run("find", "performance", "--root", root, "--skill-root", target, "--kind", "skill")
            self.assertEqual(rc, 0, data)
            self.assertEqual(data["matches"][0]["id"], "other-provider")
            self.assertTrue(data["matches"][0]["path"].endswith("external-skills/other-provider/SKILL.md"))

    def test_unmatched_does_not_claim_absence(self):
        rc, data = run("find", "zzrarezznamezz", "--root", REPOSITORY)
        self.assertEqual(rc, 0)
        self.assertEqual(data["status"], "unresolved")
        self.assertEqual(data["unmatched_meaning"], "unknown-outside-inspected-roots")
        self.assertNotIn("unavailable", json.dumps(data))

    def test_partial_when_no_roots_accessible(self):
        with tempfile.TemporaryDirectory() as temp:
            rc, data = run("list", "--root", temp)
            self.assertEqual(rc, 2)
            self.assertEqual(data["status"], "partial")
            self.assertTrue(data["errors"])

    def test_malformed_entrypoint_causes_partial(self):
        with tempfile.TemporaryDirectory() as temp:
            p = write_skill(Path(temp) / "skills", "x")
            p.write_text("---\nname: x\n---\n", encoding="utf-8")
            rc, data = run("list", "--root", temp)
            self.assertEqual(rc, 2)
            self.assertEqual(data["source_completeness"], "partial")
            self.assertTrue(any("unreadable entrypoint" in s for s in data["errors"]))

    def test_duplicate_skill_identity_is_partial(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_skill(root / "skills", "duplicate")
            write_skill(root / ".github/skills", "duplicate")
            rc, data = run("list", "--root", root)
            self.assertEqual(rc, 2)
            self.assertTrue(any("duplicate" in s for s in data["errors"]))

    def test_symlinked_external_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"; root.mkdir()
            external = Path(temp) / "external"; external.mkdir()
            alias = Path(temp) / "alias"
            try:
                alias.symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            rc, data = run("list", "--root", root, "--skill-root", alias)
            self.assertEqual(rc, 2)
            self.assertEqual(data["status"], "partial")
            self.assertTrue(any("symlinked" in s for s in data["errors"]))

    def test_root_with_symlinked_ancestor_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / "target"
            root = target / "workspace"
            root.mkdir(parents=True)
            alias = base / "alias"
            try:
                alias.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            approved_root = alias / "workspace"
            write_skill(approved_root / ".github/skills", "example", "Organize architecture diagrams")
            rc, data = run("find", "architecture", "--root", approved_root, "--kind", "skill")
            self.assertEqual(rc, 0, data)
            self.assertEqual([m["id"] for m in data["matches"]], ["example"])

    def test_linked_skill_child_is_partial_not_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            normal = root / "skills"; normal.mkdir()
            external = root / "outside"; write_skill(external, "linked")
            alias = normal / "linked"
            try:
                alias.symlink_to(external / "linked", target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unavailable")
            rc, data = run("list", "--root", root)
            self.assertEqual(rc, 2)
            self.assertEqual(data["status"], "partial")
            self.assertTrue(any("linked" in error for error in data["errors"]))

    def test_score_is_advisory_and_never_dispatches(self):
        rc, data = run("find", "technical planning", "--root", REPOSITORY, "--limit", 3)
        self.assertEqual(rc, 0)
        self.assertEqual(data["decision"], "native-availability-and-semantic-review-required")
        for forbidden in ("permission_granted", "agent_invoked", "skill_executed"):
            self.assertNotIn(forbidden, data)

    def test_folded_yaml_parsing_is_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            p = write_skill(Path(temp), "multiline")
            p.write_text("---\nname: multiline\ndescription: >\n  My first line\n  and second line\n---\n", encoding="utf-8")
            self.assertEqual(DIRECTORY.metadata(p)["description"], "My first line and second line")

    def test_skill_files_are_never_executed_as_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = write_skill(root / "skills", "never-execute")
            marker = root / "bad-marker"
            path.write_text("---\nname: x\ndescription: harmless\n---\n" +
                            f"# Never run\nimport pathlib; pathlib.Path({str(marker)!r}).write_text('bad')\n", encoding="utf-8")
            rc, _ = run("list", "--root", root)
            self.assertEqual(rc, 0)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
