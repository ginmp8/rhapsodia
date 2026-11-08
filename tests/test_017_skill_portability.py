"""Skill Booster structural, OpenAI metadata and multi-host compatibility regression gates for 0.17.0."""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("grilling", "grill-me", "grill-with-docs", "domain-modeling", "wayfinder", "retro", "code-review")
HOSTS = "portable-core,openai,codex,claude,copilot,cursor"
VALIDATORS = (
    ("skills/skill-booster/scripts/validate_skill_booster.py", ("--target",)),
    ("skills/skill-booster/scripts/validate_portability.py", ("--target",)),
    ("skills/skill-testing-and-validation/scripts/validate_skill_package.py", ()),
)

class SkillPortability017Tests(unittest.TestCase):
    def test_openai_metadata_and_icon_paths(self):
        digests = set()
        for name in SKILLS:
            with self.subTest(skill=name):
                folder = ROOT / "skills" / name
                yaml = (folder / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertIn("interface:", yaml)
                for key in ("display_name", "short_description", "default_prompt"):
                    self.assertRegex(yaml, rf'(?m)^  {key}: "[^"\n]+"$')
                self.assertIn(f"$" + name, yaml)
                self.assertRegex(yaml, r'(?m)^  brand_color: "#[0-9A-Fa-f]{6}"$')
                for key in ("icon_small", "icon_large"):
                    m = re.search(rf'(?m)^  {key}: "(\./assets/[^"\n]+\.svg)"$', yaml)
                    self.assertIsNotNone(m, f"{name} missing {key} SVG path")
                    relative = m.group(1)
                    target = (folder / relative).resolve()
                    self.assertTrue(target.is_relative_to(folder.resolve()))
                    self.assertTrue(target.is_file() and not target.is_symlink())
                self.assertRegex(yaml, r'(?m)^    - "CHAT"$')
                self.assertRegex(yaml, r'(?m)^    - "CODEX"$')
                self.assertRegex(yaml, r'(?m)^  allow_implicit_invocation: (true|false)$')
                if name in ("grill-me", "grill-with-docs", "retro"):
                    self.assertIn("allow_implicit_invocation: false", yaml)
                else:
                    self.assertIn("allow_implicit_invocation: true", yaml)

                raw = (folder / "assets/icon.svg").read_bytes()
                digests.add(hashlib.sha256(raw).hexdigest())
                root = ET.fromstring(raw)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertEqual(root.attrib.get("viewBox"), "0 0 64 64")
                self.assertLess(len(raw), 8192)
                permitted = {"svg", "rect", "path", "circle", "line", "polyline", "polygon", "ellipse"}
                for node in root.iter():
                    self.assertIn(node.tag.rsplit("}", 1)[-1], permitted)
                    for attribute, value in node.attrib.items():
                        self.assertNotIn("href", attribute.casefold())
                        self.assertNotIn("url(", value.casefold())
                        self.assertNotIn("<", value)
        self.assertEqual(len(digests), len(SKILLS), "Each new skill should have its own icon")

    def test_dependency_fallback_and_authority_boundaries(self):
        text = {n:(ROOT / "skills" / n / "SKILL.md").read_text(encoding="utf-8") for n in SKILLS}
        self.assertIn("Inline semantic fallback", text["grill-me"])
        self.assertIn("otherwise", text["grill-with-docs"].lower())
        self.assertIn("inline", text["wayfinder"].lower())
        self.assertIn("named-skill invocation", text["grill-with-docs"])
        for n in SKILLS:
            compatibility_markers = {
                "grilling": "Host portability",
                "grill-me": "Inline semantic fallback",
                "grill-with-docs": "inline",
                "domain-modeling": "Host portability",
                "wayfinder": "Host portability",
                "retro": "Host portability",
                "code-review": "Host portability",
            }
            self.assertIn(compatibility_markers[n].lower(), text[n].lower())
            self.assertLessEqual(len(text[n].splitlines()), 100)
            self.assertTrue((ROOT / "skills" / n / "VERSION").is_file())
            self.assertEqual((ROOT / "skills" / n / "VERSION").read_text().strip(), "0.1.1")
            self.assertIn("## [0.1.1]", (ROOT / "skills" / n / "CHANGELOG.md").read_text())
        for n in ("grill-with-docs", "domain-modeling", "wayfinder"):
            self.assertIn("Mago", text[n])

    def test_skill_booster_and_agent_skills_portability_validators(self):
        for n in SKILLS:
            folder = "skills/" + n
            for script, arguments in VALIDATORS:
                with self.subTest(skill=n, validator=script):
                    cmd = [sys.executable, "-B", str(ROOT / script), *arguments, folder]
                    if "validate_portability" in script:
                        cmd += ["--hosts", HOSTS]
                    if "validate_skill_package" in script:
                        cmd += ["--format", "json"]
                    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=45)
                    self.assertEqual(result.returncode, 0,
                                     f"{n} failed {script}: {result.stdout[-1800:]}\n{result.stderr[-1500:]}")

if __name__ == "__main__":
    unittest.main()
