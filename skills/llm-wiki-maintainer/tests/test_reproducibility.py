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

from _wiki_common import canonical_page_id, render_frontmatter, sha256_file  # noqa: E402
from wiki_transaction import commit_transaction, rollback_receipt  # noqa: E402
from wiki_validate import validate as validate_wiki  # noqa: E402


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], text=True, capture_output=True)


class WikiReproTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        (self.ws / "raw").mkdir()
        for d in ["sources", "entities", "concepts", "syntheses"]:
            (self.ws / "wiki" / d).mkdir(parents=True, exist_ok=True)
        (self.ws / "WIKI_SCHEMA.md").write_text("# Schema\n\nschema_version: llm-wiki/2\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
        (self.ws / "wiki" / "log.md").write_text("## [2026-09-19] initialize | test\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def capture(self, source: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        args = ["capture", "--workspace", str(self.ws), "--source", str(source)]
        if extra:
            args.extend(extra)
        return run_script("source_identity.py", *args)

    def test_source_identity_reingest_duplicate_and_snapshot(self) -> None:
        a = self.ws / "raw" / "a.md"
        b = self.ws / "raw" / "copy.md"
        a.write_text("same bytes\n", encoding="utf-8")
        b.write_bytes(a.read_bytes())

        first = self.capture(a)
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        first_data = json.loads(first.stdout)
        second = self.capture(a)
        self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
        second_data = json.loads(second.stdout)
        duplicate = self.capture(b)
        self.assertEqual(duplicate.returncode, 0, duplicate.stderr + duplicate.stdout)
        duplicate_data = json.loads(duplicate.stdout)

        self.assertEqual(first_data["source_id"], second_data["source_id"])
        self.assertEqual(first_data["source_id"], duplicate_data["source_id"])
        self.assertEqual(second_data["classification"], "already-ingested")
        self.assertEqual(duplicate_data["classification"], "duplicate-content-alias")
        snapshot = self.ws / first_data["snapshot_path"]
        self.assertEqual(sha256_file(snapshot), first_data["sha256"])
        manifest = json.loads((self.ws / ".llm-wiki" / "source-manifest.json").read_text())
        self.assertEqual(len(manifest["sources"]), 1)
        self.assertEqual(sorted(manifest["sources"][first_data["source_id"]]["aliases"]), ["raw/a.md", "raw/copy.md"])

    def test_source_modification_blocks_and_old_snapshot_survives(self) -> None:
        a = self.ws / "raw" / "a.md"
        a.write_text("v1\n", encoding="utf-8")
        first = self.capture(a)
        self.assertEqual(first.returncode, 0)
        first_data = json.loads(first.stdout)
        snapshot = self.ws / first_data["snapshot_path"]
        old_bytes = snapshot.read_bytes()

        a.write_text("v2\n", encoding="utf-8")
        blocked = self.capture(a)
        self.assertEqual(blocked.returncode, 2)
        blocked_data = json.loads(blocked.stdout)
        self.assertEqual(blocked_data["classification"], "source-modified")
        self.assertEqual(snapshot.read_bytes(), old_bytes)
        manifest = json.loads((self.ws / ".llm-wiki" / "source-manifest.json").read_text())
        self.assertEqual(manifest["paths"]["raw/a.md"]["source_id"], first_data["source_id"])

        accepted = self.capture(a, ["--accept-external-replacement"])
        self.assertEqual(accepted.returncode, 0, accepted.stderr + accepted.stdout)
        accepted_data = json.loads(accepted.stdout)
        self.assertEqual(accepted_data["classification"], "external-replacement-accepted")
        self.assertEqual(accepted_data["previous_source_id"], first_data["source_id"])
        self.assertTrue(snapshot.exists())

    def test_source_removal_is_warning_not_history_deletion(self) -> None:
        a = self.ws / "raw" / "a.md"
        a.write_text("evidence\n", encoding="utf-8")
        first = self.capture(a)
        self.assertEqual(first.returncode, 0)
        sid = json.loads(first.stdout)["source_id"]
        a.unlink()
        checked = run_script("source_identity.py", "verify", "--workspace", str(self.ws))
        self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
        report = json.loads(checked.stdout)
        self.assertEqual(report["status"], "warn")
        self.assertTrue(any(c["code"] == "source/path-missing" for c in report["checks"]))
        manifest = json.loads((self.ws / ".llm-wiki" / "source-manifest.json").read_text())
        self.assertIn(sid, manifest["sources"])

    def test_page_identity_and_frontmatter_are_canonical(self) -> None:
        a = canonical_page_id("entity", "  Example   Entity ")
        b = canonical_page_id("entity", "example entity")
        self.assertEqual(a, b)
        meta = {
            "page_type": "entity",
            "wiki_schema_version": "llm-wiki/2",
            "page_id": a,
            "title": "Example Entity",
            "canonical_key": "example entity",
            "source_ids": ["sha256:" + "b" * 64, "sha256:" + "a" * 64, "sha256:" + "a" * 64],
            "reviewed_source_ids": ["sha256:" + "a" * 64],
            "status": "current",
        }
        rendered1 = render_frontmatter(meta)
        rendered2 = render_frontmatter(dict(reversed(list(meta.items()))))
        self.assertEqual(rendered1, rendered2)
        self.assertLess(rendered1.index("wiki_schema_version"), rendered1.index("page_id"))
        self.assertEqual(rendered1.count("sha256:" + "a" * 64), 2)  # once in source_ids, once reviewed

    def test_transaction_commit_rerun_and_rollback(self) -> None:
        target = self.ws / "wiki" / "entities" / "x.md"
        target.write_text("before\n", encoding="utf-8")
        before = sha256_file(target)
        staging = self.ws / "stage"
        (staging / "wiki" / "entities").mkdir(parents=True)
        (staging / "wiki" / "entities" / "x.md").write_text("after\n", encoding="utf-8")
        plan = {
            "transaction_version": 1,
            "operation": "ingest",
            "schema_version": "llm-wiki/2",
            "source_ids": [],
            "writes": [{"path": "wiki/entities/x.md", "expected_before_sha256": before}],
            "deletes": [],
        }
        receipt_path = self.ws / "mutation.json"
        code, receipt = commit_transaction(self.ws, staging, plan, receipt_path)
        self.assertEqual(code, 0)
        self.assertEqual(receipt["classification"], "committed")
        self.assertEqual(target.read_text(), "after\n")

        code2, receipt2 = commit_transaction(self.ws, staging, plan, self.ws / "mutation-rerun.json")
        self.assertEqual(code2, 0)
        self.assertEqual(receipt2["classification"], "already-applied")

        rb_code, rb = rollback_receipt(self.ws, receipt, self.ws / "rollback.json")
        self.assertEqual(rb_code, 0, json.dumps(rb, indent=2))
        self.assertEqual(target.read_text(), "before\n")

    def test_transaction_blocks_manual_drift(self) -> None:
        target = self.ws / "wiki" / "entities" / "x.md"
        target.write_text("v1\n", encoding="utf-8")
        expected = sha256_file(target)
        staging = self.ws / "stage"
        (staging / "wiki" / "entities").mkdir(parents=True)
        (staging / "wiki" / "entities" / "x.md").write_text("candidate\n", encoding="utf-8")
        target.write_text("manual\n", encoding="utf-8")
        plan = {"transaction_version": 1, "operation": "ingest", "schema_version": "llm-wiki/2", "source_ids": [], "writes": [{"path": "wiki/entities/x.md", "expected_before_sha256": expected}], "deletes": []}
        code, receipt = commit_transaction(self.ws, staging, plan, self.ws / "drift.json")
        self.assertEqual(code, 2)
        self.assertEqual(receipt["classification"], "precondition-failed")
        self.assertEqual(target.read_text(), "manual\n")

    def test_transaction_injected_failure_rolls_back_touched_files(self) -> None:
        a = self.ws / "wiki" / "entities" / "a.md"
        b = self.ws / "wiki" / "entities" / "b.md"
        a.write_text("a0\n", encoding="utf-8")
        b.write_text("b0\n", encoding="utf-8")
        staging = self.ws / "stage"
        (staging / "wiki" / "entities").mkdir(parents=True)
        (staging / "wiki" / "entities" / "a.md").write_text("a1\n", encoding="utf-8")
        (staging / "wiki" / "entities" / "b.md").write_text("b1\n", encoding="utf-8")
        plan = {
            "transaction_version": 1,
            "operation": "ingest",
            "schema_version": "llm-wiki/2",
            "source_ids": [],
            "writes": [
                {"path": "wiki/entities/a.md", "expected_before_sha256": sha256_file(a)},
                {"path": "wiki/entities/b.md", "expected_before_sha256": sha256_file(b)},
            ],
            "deletes": [],
        }
        code, receipt = commit_transaction(self.ws, staging, plan, self.ws / "fail.json", fail_after=1)
        self.assertEqual(code, 1)
        self.assertEqual(receipt["classification"], "commit-failed-rolled-back")
        self.assertEqual(a.read_text(), "a0\n")
        self.assertEqual(b.read_text(), "b0\n")

    def test_transaction_refuses_raw_target(self) -> None:
        staging = self.ws / "stage"
        (staging / "raw").mkdir(parents=True)
        (staging / "raw" / "a.md").write_text("nope\n", encoding="utf-8")
        plan = {"transaction_version": 1, "operation": "ingest", "schema_version": "llm-wiki/2", "source_ids": [], "writes": [{"path": "raw/a.md", "expected_before_sha256": None}], "deletes": []}
        with self.assertRaises(ValueError):
            commit_transaction(self.ws, staging, plan, self.ws / "raw.json")


    def test_receipts_cannot_alias_raw_or_maintained_wiki_content(self) -> None:
        src = self.ws / "raw" / "a.md"
        src.write_text("evidence\n", encoding="utf-8")
        bad_capture = run_script("source_identity.py", "capture", "--workspace", str(self.ws), "--source", str(src), "--json", str(self.ws / "raw" / "receipt.json"))
        self.assertNotEqual(bad_capture.returncode, 0)
        self.assertEqual(src.read_text(), "evidence\n")

        staging = self.ws / "stage"
        (staging / "wiki" / "entities").mkdir(parents=True)
        (staging / "wiki" / "entities" / "x.md").write_text("x\n", encoding="utf-8")
        plan = {"transaction_version": 1, "operation": "ingest", "schema_version": "llm-wiki/2", "source_ids": [], "writes": [{"path": "wiki/entities/x.md", "expected_before_sha256": None}], "deletes": []}
        with self.assertRaises(ValueError):
            commit_transaction(self.ws, staging, plan, self.ws / "wiki" / "receipt.json")

    def test_mutation_receipt_contains_bidirectional_provenance(self) -> None:
        sid = "sha256:" + "a" * 64
        page_id = canonical_page_id("entity", "provenance thing")
        meta = {
            "wiki_schema_version": "llm-wiki/2",
            "page_id": page_id,
            "page_type": "entity",
            "title": "Provenance Thing",
            "canonical_key": "provenance thing",
            "source_ids": [sid],
            "reviewed_source_ids": [sid],
            "status": "current",
        }
        staging = self.ws / "stage"
        (staging / "wiki" / "entities").mkdir(parents=True)
        (staging / "wiki" / "entities" / "p.md").write_text(render_frontmatter(meta) + "# Provenance Thing\n", encoding="utf-8")
        plan = {"transaction_version": 1, "operation": "ingest", "schema_version": "llm-wiki/2", "source_ids": [sid], "writes": [{"path": "wiki/entities/p.md", "expected_before_sha256": None}], "deletes": []}
        code, receipt = commit_transaction(self.ws, staging, plan, self.ws / "mutation-provenance.json")
        self.assertEqual(code, 0, json.dumps(receipt, indent=2))
        self.assertEqual(receipt["page_provenance"][0]["page_id"], page_id)
        self.assertEqual(receipt["page_provenance"][0]["source_ids"], [sid])
        self.assertEqual(receipt["source_to_pages"][sid], [page_id])

    def test_validator_separates_structural_and_semantic_findings(self) -> None:
        src = self.ws / "raw" / "a.md"
        src.write_text("evidence\n", encoding="utf-8")
        cap = self.capture(src)
        self.assertEqual(cap.returncode, 0)
        sid = json.loads(cap.stdout)["source_id"]

        source_meta = {
            "wiki_schema_version": "llm-wiki/2",
            "page_id": canonical_page_id("source", sid),
            "page_type": "source",
            "title": "Source A",
            "canonical_key": sid,
            "source_ids": [sid],
            "source_paths": ["raw/a.md"],
            "reviewed_source_ids": [sid],
            "status": "current",
        }
        entity_meta = {
            "wiki_schema_version": "llm-wiki/2",
            "page_id": canonical_page_id("entity", "thing"),
            "page_type": "entity",
            "title": "Thing",
            "canonical_key": "thing",
            "source_ids": [sid],
            "reviewed_source_ids": [],
            "status": "current",
        }
        sp = self.ws / "wiki" / "sources" / "source-a.md"
        ep = self.ws / "wiki" / "entities" / "thing.md"
        sp.write_text(render_frontmatter(source_meta) + "# Source A\n", encoding="utf-8")
        ep.write_text(render_frontmatter(entity_meta) + "# Thing\n", encoding="utf-8")
        (self.ws / "wiki" / "index.md").write_text("# Index\n\n- [[sources/source-a]]\n- [[entities/thing]]\n", encoding="utf-8")

        code, report = validate_wiki(self.ws, strict=True)
        self.assertEqual(code, 0, json.dumps(report, indent=2))
        self.assertTrue(any(f["code"] == "semantic/stale-candidate" for f in report["semantic_editorial_judgment"]))
        self.assertFalse(any(f["status"] == "fail" for f in report["structural_evidence"]))

        ep.write_text(ep.read_text() + "\n[[missing-page]]\n", encoding="utf-8")
        code2, report2 = validate_wiki(self.ws, strict=True)
        self.assertEqual(code2, 1)
        self.assertTrue(any(f["code"] == "link/broken-wikilink" for f in report2["structural_evidence"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
