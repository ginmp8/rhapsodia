#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "graph_explorer.py"
EXAMPLE = ROOT / "examples" / "basic-view.json"
TEMPLATE = ROOT / "assets" / "graph-viewer.html"

spec = importlib.util.spec_from_file_location("graph_explorer", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


def run(*args: str, expect: int = 0) -> dict:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)
    if proc.returncode != expect:
        raise AssertionError(f"command failed rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return json.loads(proc.stdout)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


class ExplorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_validate_and_layout_policy(self) -> None:
        result = run("validate", str(EXAMPLE))
        self.assertEqual(result["status"], "pass")
        focused = run("layout", str(EXAMPLE))
        self.assertEqual(focused["layout"], "radial")

        dag = json.loads(json.dumps(self.base))
        dag["query"]["seed"] = None
        dag_path = self.dir / "dag.json"
        write_json(dag_path, dag)
        self.assertEqual(run("layout", str(dag_path))["layout"], "dagre")

        cycle = json.loads(json.dumps(dag))
        cycle["edges"].append({
            "id": "edge:cycle", "source": "component:repository", "target": "component:controller",
            "relation": "cycles", "directed": True, "properties": {}, "evidence_summary": {}
        })
        cycle_path = self.dir / "cycle.json"
        write_json(cycle_path, cycle)
        self.assertEqual(run("layout", str(cycle_path))["layout"], "circular")
        self.assertEqual(run("layout", str(cycle_path), "--layout", "force")["layout"], "force")

    def test_invalid_endpoint_and_duplicate_node_rejected(self) -> None:
        bad = json.loads(json.dumps(self.base))
        bad["nodes"].append(json.loads(json.dumps(bad["nodes"][0])))
        bad["edges"][0]["target"] = "missing:node"
        path = self.dir / "bad.json"
        write_json(path, bad)
        result = run("validate", str(path), expect=1)
        joined = "\n".join(result["errors"])
        self.assertIn("duplicate node id", joined)
        self.assertIn("unknown node", joined)

    def test_render_is_byte_deterministic_and_pins_g6(self) -> None:
        a, b = self.dir / "a.html", self.dir / "b.html"
        ra = run("render", str(EXAMPLE), "--output", str(a), "--backend", "auto")
        rb = run("render", str(EXAMPLE), "--output", str(b), "--backend", "auto")
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(ra["sha256"], rb["sha256"])
        html = a.read_text(encoding="utf-8")
        self.assertIn("@antv/g6@5.1.1/dist/g6.min.js", html)
        self.assertIn("prefers-reduced-motion", html)
        for marker in ["kind-filters", "relation-filters", "inspector", "path-button", "theme", "search"]:
            self.assertIn(f'id="{marker}"', html)

    def test_builtin_is_offline_and_script_payload_is_escaped(self) -> None:
        malicious = json.loads(json.dumps(self.base))
        malicious["nodes"][0]["label"] = "</script><script>alert(1)</script>"
        source = self.dir / "malicious.json"
        out = self.dir / "offline.html"
        write_json(source, malicious)
        result = run("render", str(source), "--output", str(out), "--backend", "builtin", "--layout", "circular")
        self.assertTrue(result["offline"])
        html = out.read_text(encoding="utf-8")
        self.assertNotIn("unpkg.com", html)
        self.assertNotIn("</script><script>alert(1)</script>", html)
        self.assertIn("<\\/script><script>alert(1)<\\/script>", html)

    def test_local_g6_bundle_can_be_inlined(self) -> None:
        fake = self.dir / "g6.min.js"
        fake.write_text("window.G6={Graph:function(){}};", encoding="utf-8")
        out = self.dir / "inlined.html"
        result = run("render", str(EXAMPLE), "--output", str(out), "--backend", "g6", "--g6-js", str(fake))
        self.assertTrue(result["offline"])
        html = out.read_text(encoding="utf-8")
        self.assertIn("window.G6={Graph:function(){}};", html)
        self.assertNotIn("unpkg.com", html)


if __name__ == "__main__":
    unittest.main()
