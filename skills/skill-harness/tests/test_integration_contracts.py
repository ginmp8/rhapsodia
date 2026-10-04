from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "contracts" / "integration-manifest.json"


def test_public_contract_ids_are_unique_and_surfaces_exist():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ids = [row["contract_id"] for row in data["exports"]]
    assert len(ids) == len(set(ids))
    for row in data["exports"]:
        assert row["surface_paths"]
        for rel in row["surface_paths"]:
            assert (ROOT / rel).exists(), f"missing contract surface: {rel}"


def test_existing_multi_candidate_contract_versions_are_preserved():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    versions = {row["contract_id"]: row["version"] for row in data["exports"]}
    assert versions["skill-opt.harness-multi-candidate-evidence"] == 4
    assert versions["skill-opt.harness-multi-candidate-evidence-strict"] == 2
