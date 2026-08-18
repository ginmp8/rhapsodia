from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_resource_integration import validate  # noqa: E402


def test_current_resource_routes_are_complete():
    result = validate(ROOT)
    assert result["status"] == "pass", result
    assert result["route_count"] >= 7


def test_missing_resource_map_route_fails_closed():
    with tempfile.TemporaryDirectory(prefix="magia-resource-route-") as raw:
        candidate = Path(raw) / "magia"
        shutil.copytree(ROOT, candidate)
        path = candidate / "references" / "resource-map.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("scripts/validate_convergence.py", "scripts/unmapped_convergence.py"),
            encoding="utf-8",
        )
        result = validate(candidate)
        assert result["status"] == "fail"
        assert any("scripts/validate_convergence.py" in error for error in result["errors"])
