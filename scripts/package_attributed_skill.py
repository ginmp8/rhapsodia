#!/usr/bin/env python3
"""Package an attributed RhapsodIA Skill with its complete MIT notice."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import package_policy

ROOT = Path(__file__).resolve().parents[1]
SKILLS = frozenset({
    "code-review", "domain-modeling", "grill-me", "grill-with-docs",
    "grilling", "retro", "wayfinder",
})
NOTICE = ROOT / "licenses" / "third-party" / "mattpocock-skills-MIT.txt"


def _put(archive: ZipFile, name: str, data: bytes, executable: bool = False) -> None:
    entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.compress_type = ZIP_DEFLATED
    entry.external_attr = (0o755 if executable else 0o644) << 16
    archive.writestr(entry, data)


def build(skill: str, output: Path) -> dict:
    if skill not in SKILLS:
        raise ValueError("not an attributed 0.17.0 skill: " + skill)
    package = ROOT / "skills" / skill
    if not (package / "SKILL.md").is_file() or not (package / "SOURCE.md").is_file():
        raise ValueError("incomplete package: " + skill)
    if (package / "LICENSE-MIT").exists():
        raise ValueError("license copy must be centralized in the source tree")
    notice = NOTICE.read_bytes()
    if b"Copyright (c) 2026 Matt Pocock" not in notice or b"MIT License" not in notice:
        raise ValueError("missing or unrecognized original license notice")
    if output.suffix.lower() != ".zip" or output.is_symlink():
        raise ValueError("output must be a normal .zip destination")
    if package.resolve() in output.resolve().parents:
        raise ValueError("output cannot be written inside the skill source")
    files = sorted(package_policy.files(package), key=lambda p: p.relative_to(package).as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".skill-archive-", suffix=".zip", dir=output.parent)
    os.close(fd)
    tmp = Path(temporary)
    try:
        with ZipFile(tmp, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for file in files:
                relative = file.relative_to(package).as_posix()
                _put(archive, f"{skill}/{relative}", file.read_bytes(), file.suffix in {".py", ".sh"})
            _put(archive, f"{skill}/LICENSE-MIT", notice)
        with ZipFile(tmp) as archive:
            if archive.testzip() is not None or archive.read(f"{skill}/LICENSE-MIT") != notice:
                raise ValueError("standalone archive license/integrity check failed")
        os.replace(tmp, output)
    finally:
        tmp.unlink(missing_ok=True)
    return {
        "skill": skill,
        "archive": str(output),
        "files": len(files) + 1,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, choices=sorted(SKILLS))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.skill, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
