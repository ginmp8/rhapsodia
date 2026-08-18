from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".template", ".txt"}


def test_no_retired_governance_name_or_obsolete_cycle_key():
    retired = "magi" + "arca"
    obsolete = "cycle" + "_version"
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8-sig").lower()
            assert retired not in text, path
            assert obsolete not in text, path


def test_no_external_skill_runtime_coupling():
    forbidden = ("skills://" + "mago", "skills://" + "nomia", ".github/skills/" + "mago", ".github/skills/" + "nomia")
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8-sig").lower()
            assert not any(item in text for item in forbidden), path
