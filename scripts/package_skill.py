#!/usr/bin/env python3
"""Build a deterministic, license-complete standalone archive for any RhapsodIA Skill."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import package_policy
import skill_licenses

ROOT = Path(__file__).resolve().parents[1]


def _put(archive: ZipFile, path: str, data: bytes, executable: bool) -> None:
    entry = ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.compress_type = ZIP_DEFLATED
    entry.external_attr = (0o755 if executable else 0o644) << 16
    archive.writestr(entry, data)


def build(skill: str, output: Path) -> dict:
    doc = skill_licenses.registry(ROOT)
    expected = {item["name"] for item in doc["skills"]}
    if skill not in expected:
        raise ValueError("unknown registered RhapsodIA skill: " + skill)
    package = ROOT / "skills" / skill
    if not package.is_dir() or package.is_symlink() or not (package / "SKILL.md").is_file():
        raise ValueError("missing or unsafe canonical skill: " + skill)
    if output.suffix.lower() != ".zip" or output.is_symlink():
        raise ValueError("expected ordinary ZIP destination")
    resolved = output.resolve()
    if resolved == ROOT or resolved.is_relative_to(package.resolve()):
        raise ValueError("output cannot overwrite the skill package")
    files = sorted(package_policy.files(package), key=lambda p: p.relative_to(package).as_posix())
    legal = skill_licenses.restore(skill, ROOT, doc)
    if any((package / name).exists() for name in legal):
        raise ValueError("legal asset collides with ordinary skill source")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".rhapsodia-skill-", suffix=".zip", dir=output.parent)
    os.close(fd)
    temporary = Path(temp)
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for file in files:
                relative = file.relative_to(package).as_posix()
                _put(archive, f"{skill}/{relative}", file.read_bytes(), file.suffix in {".py", ".sh"})
            for relative, content in legal.items():
                _put(archive, f"{skill}/{relative}", content, False)
        with ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity failed")
            if len(archive.namelist()) != len(set(archive.namelist())):
                raise ValueError("duplicate ZIP entry")
            for relative, content in legal.items():
                if archive.read(f"{skill}/{relative}") != content:
                    raise ValueError("license notice mismatch: " + relative)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return {"skill": skill, "archive": str(output), "files": len(files) + len(legal),
            "legal_files": len(legal),
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.skill, args.output), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
