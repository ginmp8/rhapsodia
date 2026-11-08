"""Ensure consolidated MIT notices remain present in full and standalone distributions."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("code-review", "domain-modeling", "grill-me", "grill-with-docs",
         "grilling", "retro", "wayfinder")
NOTICE = ROOT / "licenses" / "third-party" / "mattpocock-skills-MIT.txt"


class CentralLicenseTests(unittest.TestCase):
    def test_first_party_premortem_and_root_owner_notice(self):
        root_license = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Apache License", root_license)
        self.assertIn("Copyright (c) 2026 ginmp8", root_license)
        owned = ROOT / "licenses/first-party/premortem-analysis-MIT.txt"
        self.assertTrue(owned.is_file())
        self.assertTrue(owned.read_bytes().startswith(b"MIT License\n\nCopyright (c) 2026 ginmp8"))
        self.assertFalse((ROOT / "licenses/third-party/premortem-analysis-MIT.txt").exists())
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import skill_licenses
        self.assertEqual(skill_licenses.restore("premortem-analysis")["LICENSE"], owned.read_bytes())

    def test_repository_has_one_verbatim_mit_notice(self):
        raw = NOTICE.read_bytes()
        self.assertTrue(raw.startswith(b"MIT License\n\nCopyright (c) 2026 Matt Pocock"))
        self.assertIn(b"The above copyright notice and this permission notice", raw)
        self.assertIn(b"THE SOFTWARE IS PROVIDED", raw)
        self.assertEqual(raw.count(b"Copyright (c) 2026 Matt Pocock"), 1)
        import runpy
        include = runpy.run_path(str(ROOT / "scripts/package_policy.py"))["include"]
        self.assertTrue(include(NOTICE, ROOT))
        for name in NAMES:
            with self.subTest(skill=name):
                root = ROOT / "skills" / name
                self.assertFalse((root / "LICENSE-MIT").exists())
                source = (root / "SOURCE.md").read_text(encoding="utf-8")
                self.assertIn("licenses/third-party/mattpocock-skills-MIT.txt", source)
                self.assertIn("Reference Git blob SHA", source)
                self.assertIn("Copyright (c) 2026 Matt Pocock", source)
                self.assertEqual((root / "VERSION").read_text().strip(), "0.1.2")
                self.assertIn("## [0.1.2]", (root / "CHANGELOG.md").read_text())
        self.assertTrue((ROOT / "licenses" / "README.md").is_file())

    def test_all_standalone_archives_restore_full_notice(self):
        expected = NOTICE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            for name in NAMES:
                with self.subTest(skill=name):
                    output = Path(td) / (name + ".zip")
                    cmd = [sys.executable, "-B",
                           str(ROOT / "scripts/package_attributed_skill.py"),
                           "--skill", name, "--output", str(output)]
                    completed = subprocess.run(cmd, cwd=ROOT,
                                               capture_output=True, text=True,
                                               timeout=30, check=False)
                    self.assertEqual(completed.returncode, 0,
                                     completed.stderr + completed.stdout)
                    receipt = json.loads(completed.stdout)
                    self.assertEqual(receipt["skill"], name)
                    with ZipFile(output) as archive:
                        self.assertIsNone(archive.testzip())
                        self.assertEqual(archive.read(f"{name}/LICENSE-MIT"), expected)
                        self.assertIn(f"{name}/SKILL.md", archive.namelist())
                        self.assertIn(f"{name}/SOURCE.md", archive.namelist())
                        self.assertIn(f"{name}/agents/openai.yaml", archive.namelist())
                        self.assertIn(f"{name}/assets/icon.svg", archive.namelist())

    def test_all_76_skills_use_only_central_legal_notices(self):
        import hashlib
        doc = json.loads((ROOT / "licenses/skill-assets.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["schema"], "rhapsodia-skill-legal-assets/v1")
        registered = {entry["name"]: entry["notices"] for entry in doc["skills"]}
        self.assertEqual(len(registered), 76)
        self.assertEqual(sorted(registered), sorted(
            path.name for path in (ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        ))
        observed = {}
        for name, notices in registered.items():
            root = ROOT / "skills" / name
            for item in notices:
                path = root / item["path"]
                self.assertFalse(path.exists(), f"Legal text still inside source skill: {path}")
                canonical = ROOT / item["canonical"]
                self.assertTrue(canonical.is_file(), item["canonical"])
                raw = canonical.read_bytes()
                blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii")
                                    + b"\0" + raw).hexdigest()
                self.assertEqual(blob, item["blob_sha"], f"License byte drift: {name}/{item['path']}")
                self.assertEqual(len(raw), item["size"])
                key = (name, item["path"])
                self.assertNotIn(key, observed)
                observed[key] = item
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.name in {"LICENSE", "LICENSE-MIT", "LICENSE.txt", "NOTICE", "NOTICE.txt",
                                 "THIRD_PARTY_NOTICES.md", "JetBrainsMono-OFL.txt"}:
                    self.fail(f"Unmigrated legal asset: {path}")
        plan = json.loads((ROOT / "licenses/cleanup-plan-0.17.0.json").read_text())
        self.assertEqual(len(plan["original_files"]), 22)
        self.assertEqual(sum(len(entries) for entries in registered.values()), 29)
        amendments = {row["canonical"]: row for row in plan.get("post_cleanup_amendments", [])}
        self.assertEqual(set(amendments), {"LICENSE"})
        for item in plan["original_files"]:
            source = item["path"].split("/")
            name, original = source[1], "/".join(source[2:])
            current = observed[(name, original)]
            self.assertEqual(current["canonical"], item["canonical"])
            if current["blob_sha"] != item["git_blob_sha"]:
                amendment = amendments.get(item["canonical"])
                self.assertIsNotNone(amendment, item["path"])
                self.assertEqual(amendment["original_blob_sha"], item["git_blob_sha"])
                self.assertEqual(amendment["current_blob_sha"], current["blob_sha"])
        self.assertTrue((ROOT / "skills/streamlit/references/source-and-license.md").is_file())
        self.assertTrue((ROOT / "skills/archify/renderers/shared/software-notices.mjs").is_file())

    def test_complete_independent_exports_restore_all_legacy_notice_types(self):
        doc = json.loads((ROOT / "licenses/skill-assets.json").read_text(encoding="utf-8"))
        selected = (
            "archify", "archify-review", "archify-tuning",
            "local-graph-engine", "local-graph-explorer",
            "deep-research-suite", "premortem-analysis",
            "runtime-harness", "operational-context",
            "skill-creator", "visual-code-intelligence",
        )
        indexed = {entry["name"]: entry["notices"] for entry in doc["skills"]}
        with tempfile.TemporaryDirectory() as td:
            for name in selected:
                with self.subTest(skill=name):
                    target = Path(td) / (name + ".zip")
                    proc = subprocess.run([
                        sys.executable, "-B", str(ROOT / "scripts/package_skill.py"),
                        "--skill", name, "--output", str(target),
                    ], cwd=ROOT, capture_output=True, text=True, timeout=90)
                    self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
                    details = json.loads(proc.stdout)
                    self.assertEqual(details["skill"], name)
                    with ZipFile(target) as archive:
                        self.assertIsNone(archive.testzip())
                        paths = archive.namelist()
                        self.assertEqual(len(paths), len(set(paths)))
                        self.assertIn(name + "/SKILL.md", paths)
                        for item in indexed[name]:
                            self.assertEqual(
                                archive.read(name + "/" + item["path"]),
                                (ROOT / item["canonical"]).read_bytes(),
                                "Exported legal content differs from original"
                            )
                        if not any(x["path"] == "LICENSE" for x in indexed[name]):
                            self.assertEqual(archive.read(name + "/LICENSE"),
                                             (ROOT / "LICENSE").read_bytes())

    def test_archives_are_bitwise_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "one.zip", Path(td) / "two.zip"
            cmd = [sys.executable, "-B", str(ROOT / "scripts/package_attributed_skill.py"),
                   "--skill", "wayfinder", "--output"]
            for out in (a, b):
                proc = subprocess.run(cmd + [str(out)], cwd=ROOT,
                                      capture_output=True, text=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
