#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _wiki_common import canonical_page_id, render_frontmatter  # noqa: E402
from wiki_validate import validate as validate_wiki  # noqa: E402


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], text=True, capture_output=True)


class WikiSchemaV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        (self.ws / "raw").mkdir()
        for d in ["sources", "entities", "concepts", "syntheses", "claims"]:
            (self.ws / "wiki" / d).mkdir(parents=True, exist_ok=True)
        (self.ws / "WIKI_SCHEMA.md").write_text("# Schema\n\nschema_version: llm-wiki/3\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
        (self.ws / "wiki" / "log.md").write_text("## [2026-10-04] initialize | test\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def capture(self, source: Path) -> subprocess.CompletedProcess[str]:
        return run_script("source_identity.py", "capture", "--workspace", str(self.ws), "--source", str(source))

    def test_source_capture_uses_active_schema_for_v2_compatibility(self) -> None:
        (self.ws / "WIKI_SCHEMA.md").write_text("# Schema\n\nschema_version: llm-wiki/2\n", encoding="utf-8")
        src = self.ws / "raw" / "v2.md"
        src.write_text("v2 evidence\n", encoding="utf-8")
        result = self.capture(src)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)["schema_version"], "llm-wiki/2")

    def test_claim_identity_temporal_frontmatter_and_v3_metrics(self) -> None:
        src = self.ws / "raw" / "claim.md"
        src.write_text("claim evidence\n", encoding="utf-8")
        cap = self.capture(src)
        self.assertEqual(cap.returncode, 0, cap.stderr + cap.stdout)
        sid = json.loads(cap.stdout)["source_id"]
        claim_id = canonical_page_id("claim", "acme status")
        meta = {
            "wiki_schema_version": "llm-wiki/3",
            "page_id": claim_id,
            "page_type": "claim",
            "title": "Acme status",
            "canonical_key": "acme status",
            "source_ids": [sid],
            "reviewed_source_ids": [sid],
            "subject_page_ids": [],
            "depends_on_claim_ids": [],
            "value_state": "known",
            "point_in_time": "2026-10-04",
            "status": "current",
        }
        out = self.ws / "wiki" / "claims" / "acme-status.md"
        out.write_text(render_frontmatter(meta) + "# Acme status\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n\n- [[claims/acme-status]]\n", encoding="utf-8")
        code, report = validate_wiki(self.ws, strict=True)
        self.assertEqual(code, 0, json.dumps(report, indent=2))
        self.assertEqual(report["metrics"]["claim_pages"], 1)
        self.assertEqual(report["metrics"]["temporal_qualified_claims"], 1)
        self.assertEqual(report["metrics"]["provenance_coverage"], 1.0)
        for finding in report["structural_evidence"] + report["semantic_editorial_judgment"]:
            for field in ("rule_id", "severity", "focus", "repairability"):
                self.assertIn(field, finding)

    def test_unknown_source_lineage_is_localizable_failure(self) -> None:
        src = self.ws / "raw" / "source.md"
        src.write_text("source evidence\n", encoding="utf-8")
        cap = self.capture(src)
        self.assertEqual(cap.returncode, 0)
        sid = json.loads(cap.stdout)["source_id"]
        unknown = "sha256:" + "f" * 64
        meta = {
            "wiki_schema_version": "llm-wiki/3",
            "page_id": canonical_page_id("source", sid),
            "page_type": "source",
            "title": "Source",
            "canonical_key": sid,
            "source_ids": [sid],
            "source_paths": ["raw/source.md"],
            "reviewed_source_ids": [sid],
            "derived_from_source_ids": [unknown],
            "status": "current",
        }
        out = self.ws / "wiki" / "sources" / "source.md"
        out.write_text(render_frontmatter(meta) + "# Source\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n\n- [[sources/source]]\n", encoding="utf-8")
        code, report = validate_wiki(self.ws, strict=True)
        self.assertEqual(code, 1)
        finding = next(f for f in report["structural_evidence"] if f["code"] == "source-lineage/unknown-source-id")
        self.assertEqual(finding["severity"], "error")
        self.assertEqual(finding["focus"], "wiki/sources/source.md")
        self.assertEqual(report["metrics"]["lineage_relations"], 1)

    def test_claim_value_state_and_temporal_shape_are_validated(self) -> None:
        src = self.ws / "raw" / "invalid.md"
        src.write_text("evidence\n", encoding="utf-8")
        cap = self.capture(src)
        self.assertEqual(cap.returncode, 0)
        sid = json.loads(cap.stdout)["source_id"]
        meta = {
            "wiki_schema_version": "llm-wiki/3",
            "page_id": canonical_page_id("claim", "invalid temporal"),
            "page_type": "claim",
            "title": "Invalid temporal",
            "canonical_key": "invalid temporal",
            "source_ids": [sid],
            "reviewed_source_ids": [sid],
            "value_state": "maybe",
            "point_in_time": "2026-10-04",
            "valid_from": "2026-01-01",
            "status": "current",
        }
        out = self.ws / "wiki" / "claims" / "invalid.md"
        out.write_text(render_frontmatter(meta) + "# Invalid\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n\n- [[claims/invalid]]\n", encoding="utf-8")
        code, report = validate_wiki(self.ws, strict=True)
        self.assertEqual(code, 1)
        codes = {f["code"] for f in report["structural_evidence"]}
        self.assertIn("claim/value-state-invalid", codes)
        self.assertIn("claim/temporal-shape-invalid", codes)

    def test_entity_reconciliation_references_require_existing_entities(self) -> None:
        a_id = canonical_page_id("entity", "entity a")
        b_id = canonical_page_id("entity", "entity b")
        a = {
            "wiki_schema_version": "llm-wiki/3", "page_id": a_id, "page_type": "entity",
            "title": "Entity A", "canonical_key": "entity a", "source_ids": [], "reviewed_source_ids": [],
            "possible_same_entity_page_ids": [b_id], "status": "current",
        }
        b = {
            "wiki_schema_version": "llm-wiki/3", "page_id": b_id, "page_type": "entity",
            "title": "Entity B", "canonical_key": "entity b", "source_ids": [], "reviewed_source_ids": [],
            "status": "current",
        }
        (self.ws / "wiki" / "entities" / "a.md").write_text(render_frontmatter(a) + "# A\n", encoding="utf-8")
        (self.ws / "wiki" / "entities" / "b.md").write_text(render_frontmatter(b) + "# B\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n\n- [[entities/a]]\n- [[entities/b]]\n", encoding="utf-8")
        code, report = validate_wiki(self.ws, strict=True)
        self.assertEqual(code, 0, json.dumps(report, indent=2))
        (self.ws / "wiki" / "entities" / "b.md").unlink()
        code2, report2 = validate_wiki(self.ws, strict=True)
        self.assertEqual(code2, 1)
        self.assertTrue(any(f["code"] == "entity/unknown-related-page-id" for f in report2["structural_evidence"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
