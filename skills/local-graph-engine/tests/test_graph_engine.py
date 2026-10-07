#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "graph_engine.py"
EXAMPLE = ROOT / "examples" / "basic-patch.json"


def run(*args: str, expect: int = 0) -> dict:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)
    if proc.returncode != expect:
        raise AssertionError(f"command failed rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return json.loads(proc.stdout)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = self.dir / "graph.db"
        run("--db", str(self.db), "init")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_init_apply_validate_queries_and_deterministic_export(self) -> None:
        first = run("--db", str(self.db), "apply-patch", str(EXAMPLE))
        self.assertEqual(first["counts"]["active_nodes"], 3)
        self.assertEqual(first["counts"]["active_edges"], 2)

        second = run("--db", str(self.db), "apply-patch", str(EXAMPLE))
        self.assertEqual(first["counts"], second["counts"])

        valid = run("--db", str(self.db), "validate-db")
        self.assertEqual(valid["status"], "pass")

        found = run("--db", str(self.db), "find", "repository")
        self.assertEqual(found["results"][0]["id"], "component:repository")

        path = run("--db", str(self.db), "path", "component:controller", "component:repository")
        self.assertEqual(path["path"]["nodes"], ["component:controller", "component:handler", "component:repository"])

        deps = run("--db", str(self.db), "impact", "component:controller", "--direction", "dependencies")
        self.assertEqual(deps["impact"]["steps"], [["component:handler"], ["component:repository"]])

        dependents = run("--db", str(self.db), "impact", "component:repository", "--direction", "dependents")
        self.assertEqual(dependents["impact"]["steps"], [["component:handler"], ["component:controller"]])

        a = self.dir / "a.json"
        b = self.dir / "b.json"
        run("--db", str(self.db), "export-view", str(a), "--seed", "component:handler", "--depth", "2")
        run("--db", str(self.db), "export-view", str(b), "--seed", "component:handler", "--depth", "2")
        self.assertEqual(a.read_bytes(), b.read_bytes())
        view = json.loads(a.read_text(encoding="utf-8"))
        self.assertEqual(view["schema_version"], "graph-view-v1")
        self.assertEqual(view["metadata"]["truncated"], False)

    def test_invalid_patch_does_not_mutate(self) -> None:
        before = run("--db", str(self.db), "stats")["stats"]
        bad = {
            "schema_version": "graph-patch-v1",
            "source": {"uri": "example://bad", "kind": "example"},
            "nodes": [],
            "edges": [{
                "source": "missing:a", "target": "missing:b", "relation": "uses", "directed": True,
                "properties": {},
                "evidence": [{"provenance": "MANUAL", "confidence": 1.0, "status": "accepted", "locator": "fixture", "details": {}}]
            }]
        }
        p = self.dir / "bad.json"
        write_json(p, bad)
        result = run("--db", str(self.db), "apply-patch", str(p), expect=1)
        self.assertEqual(result["mutated"], False)
        after = run("--db", str(self.db), "stats")["stats"]
        self.assertEqual(before, after)

    def test_source_scoped_replacement_preserves_other_evidence(self) -> None:
        base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        p1 = self.dir / "p1.json"
        p2 = self.dir / "p2.json"
        p1r = self.dir / "p1-replace.json"
        write_json(p1, base)
        other = json.loads(json.dumps(base))
        other["source"]["uri"] = "example://second-source"
        other["source"]["content_hash"] = "sha256:second"
        write_json(p2, other)
        run("--db", str(self.db), "apply-patch", str(p1))
        run("--db", str(self.db), "apply-patch", str(p2))

        replacement = json.loads(json.dumps(base))
        replacement["edges"] = []
        replacement["source"]["content_hash"] = "sha256:replacement"
        write_json(p1r, replacement)
        result = run("--db", str(self.db), "apply-patch", str(p1r))
        self.assertEqual(result["counts"]["active_edges"], 2)
        self.assertEqual(result["counts"]["edge_evidence"], 2)

    def test_full_export_refuses_unbounded_large_graph(self) -> None:
        run("--db", str(self.db), "apply-patch", str(EXAMPLE))
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(self.db), "export-view", str(self.dir / "x.json"), "--max-nodes", "2"],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("specify --seed", payload["error"])


if __name__ == "__main__":
    unittest.main()
