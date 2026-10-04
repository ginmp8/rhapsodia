from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_review_evidence_manifest import build_manifest, hash_path  # noqa: E402


def _make_skill(root: Path, body: str = "A") -> Path:
    root.mkdir()
    (root / "SKILL.md").write_text(
        "---\nname: demo\ndescription: demo skill\n---\n\n" + body + "\n",
        encoding="utf-8",
    )
    return root


def test_manifest_is_deterministic_and_order_independent(tmp_path):
    target = _make_skill(tmp_path / "target")
    reviewer = _make_skill(tmp_path / "reviewer", "Reviewer")
    evaluator = tmp_path / "eval.json"
    evaluator.write_text('{"a":1}\n', encoding="utf-8")

    a = build_manifest(
        target,
        reviewer,
        ["cursor", "portable", "cursor"],
        "spec@1",
        [("eval", evaluator)],
        [("z", "https://z.example", "v2"), ("a", "https://a.example", "v1")],
    )
    b = build_manifest(
        target,
        reviewer,
        ["portable", "cursor"],
        "spec@1",
        [("eval", evaluator)],
        [("a", "https://a.example", "v1"), ("z", "https://z.example", "v2")],
    )
    assert a == b
    assert a["host_profiles"] == ["cursor", "portable"]
    assert str(tmp_path) not in str(a)


def test_target_identity_changes_when_target_bytes_change(tmp_path):
    target = _make_skill(tmp_path / "target")
    kind_before, before = hash_path(target)
    (target / "SKILL.md").write_text(
        "---\nname: demo\ndescription: demo skill\n---\n\nB\n",
        encoding="utf-8",
    )
    kind_after, after = hash_path(target)
    assert kind_before == kind_after == "directory-tree-sha256"
    assert before != after
