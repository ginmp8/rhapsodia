import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MarketplaceManifestTests(unittest.TestCase):
    def load_json(self, relative_path: str):
        with (ROOT / relative_path).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_required_multiplatform_marketplace_surfaces_exist(self):
        required = [
            "marketplace/catalog.json",
            ".github/plugin/marketplace.json",
            ".github/plugin/plugin.json",
            ".agents/plugins/marketplace.json",
            ".codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".claude-plugin/plugin.json",
            ".cursor-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
            "scripts/generate_marketplace_manifests.py",
            "scripts/build_portable_agent_plugin.py",
            "docs/marketplace.md",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual([], missing, f"missing marketplace files: {missing}")

    def test_source_tree_has_only_one_canonical_agent_directory(self):
        canonical = sorted((ROOT / "agents").glob("*.agent.md"))
        self.assertGreater(len(canonical), 0)
        self.assertFalse(
            (ROOT / "com.github.copilot" / "agents").exists(),
            "Copilot agent copies must not be committed; agents/ is canonical",
        )

    def test_root_is_not_agent_plugins_package(self):
        self.assertFalse(
            (ROOT / "plugin.json").exists(),
            "root plugin.json would force Copilot into Agent Plugins semantics and require duplicated agent adapters",
        )

    def test_copilot_legacy_manifest_reuses_canonical_agents_and_skills(self):
        manifest = self.load_json(".github/plugin/plugin.json")
        self.assertEqual("rhapsodia", manifest["name"])
        self.assertNotIn("$schema", manifest)
        self.assertEqual("agents/", manifest["agents"])
        self.assertEqual("skills/", manifest["skills"])

    def test_cursor_manifest_reuses_canonical_agents_and_skills(self):
        manifest = self.load_json(".cursor-plugin/plugin.json")
        self.assertEqual("rhapsodia", manifest["name"])
        self.assertEqual("agents/", manifest["agents"])
        self.assertEqual("skills/", manifest["skills"])

    def test_codex_manifest_reuses_canonical_skills(self):
        manifest = self.load_json(".codex-plugin/plugin.json")
        self.assertEqual("rhapsodia", manifest["name"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertNotIn("agents", manifest)

    def test_host_marketplaces_expose_the_same_plugin(self):
        github = self.load_json(".github/plugin/marketplace.json")
        cursor = self.load_json(".cursor-plugin/marketplace.json")
        claude = self.load_json(".claude-plugin/marketplace.json")
        openai = self.load_json(".agents/plugins/marketplace.json")

        for manifest in (github, cursor, claude, openai):
            self.assertEqual("rhapsodia", manifest["name"])
            self.assertEqual(["rhapsodia"], [p["name"] for p in manifest["plugins"]])

        self.assertEqual(".", github["plugins"][0]["source"])
        self.assertEqual(".", cursor["plugins"][0]["source"])
        self.assertEqual("./", claude["plugins"][0]["source"])

        openai_plugin = openai["plugins"][0]
        self.assertEqual("url", openai_plugin["source"]["source"])
        self.assertEqual(
            "https://github.com/ginmp8/rhapsodia.git",
            openai_plugin["source"]["url"],
        )
        self.assertEqual("AVAILABLE", openai_plugin["policy"]["installation"])

    def test_portable_agent_plugin_is_generated_without_agents(self):
        script = ROOT / "scripts" / "build_portable_agent_plugin.py"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "rhapsodia"
            result = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            manifest = json.loads((output / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                manifest["$schema"],
            )
            self.assertTrue((output / "skills").is_dir())
            self.assertFalse((output / "agents").exists())
            self.assertFalse((output / "com.github.copilot").exists())

    def test_generated_marketplace_files_are_in_sync(self):
        script = ROOT / "scripts" / "generate_marketplace_manifests.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
