from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "snapshot_sources.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)


def test_source_change_after_snapshot_is_detected() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / "source"
        work = base / "work"
        source.mkdir()
        work.mkdir()
        (source / "input.txt").write_text("alpha\n", encoding="utf-8")
        manifest = work / "source-manifest.json"
        snapshot = work / "bytes"

        captured = run(
            "capture",
            "--root", str(source),
            "--path", "input.txt",
            "--snapshot-dir", str(snapshot),
            "--out", str(manifest),
        )
        assert captured.returncode == 0, captured.stderr or captured.stdout
        assert (snapshot / "input.txt").read_text(encoding="utf-8") == "alpha\n"

        (source / "input.txt").write_text("beta\n", encoding="utf-8")
        verified = run("verify", "--manifest", str(manifest))
        assert verified.returncode == 1
        report = json.loads(verified.stdout)
        assert report["snapshot_changed"] == []
        assert report["source_changed"][0]["reason"] == "source-bytes-changed"

        frozen_only = run("verify", "--manifest", str(manifest), "--snapshot-only")
        assert frozen_only.returncode == 0
        assert json.loads(frozen_only.stdout)["status"] == "pass"


def test_symlink_escape_is_rejected() -> None:
    if not hasattr(os, "symlink"):
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        source = base / "source"
        work = base / "work"
        source.mkdir()
        work.mkdir()
        outside = base / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        link = source / "escape.txt"
        try:
            link.symlink_to(outside)
        except OSError:
            return

        result = run(
            "capture",
            "--root", str(source),
            "--path", "escape.txt",
            "--snapshot-dir", str(work / "bytes"),
            "--out", str(work / "manifest.json"),
        )
        assert result.returncode == 1
        failure = json.loads(result.stdout)
        assert "symlink escapes root" in failure["error"]


if __name__ == "__main__":
    test_source_change_after_snapshot_is_detected()
    test_symlink_escape_is_rejected()
    print("ok")
