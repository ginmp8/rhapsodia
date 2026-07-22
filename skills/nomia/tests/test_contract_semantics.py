from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_contract_semantics.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_contract_semantics", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_current_contract_semantics_pass():
    module = load_module()
    assert module.collect_errors(ROOT) == []


def test_legacy_handoff_acceptance_is_rejected(tmp_path: Path):
    module = load_module()
    root = tmp_path / "nomia"
    path = root / "references" / "state-risk-and-handoffs.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "Legacy Nomia envelope fields are accepted only by explicit compatibility mode and are normalized before validation.\n",
        encoding="utf-8",
    )
    errors = module.collect_errors(root)
    assert any("legacy handoff compatibility" in error for error in errors)


def test_migration_only_language_does_not_enable_handoff_compatibility(tmp_path: Path):
    module = load_module()
    root = tmp_path / "nomia"
    path = root / "references" / "state-risk-and-handoffs.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "Legacy envelope fields are not accepted as ecosystem handoff compatibility. "
        "Normal producers require strict handoff v2. Historical input is isolated to governance-adapt "
        "and requires externally supplied current identities.\n",
        encoding="utf-8",
    )
    assert module.collect_errors(root) == []
