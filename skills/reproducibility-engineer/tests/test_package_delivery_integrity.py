from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'package_target.py'


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_skill(base: Path) -> Path:
    skill = base / 'demo-skill'
    skill.mkdir()
    (skill / 'SKILL.md').write_text(
        '---\nname: demo-skill\ndescription: Deterministic demo skill used to test package delivery integrity.\n---\n\n# Demo\n\nDo the deterministic thing.\n',
        encoding='utf-8',
    )
    return skill


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_package_and_receipt_alias_is_rejected_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / 'skill.zip'
        receipt = base / 'receipt.json'
        output.write_bytes(b'last-good')
        try:
            os.link(output, receipt)
        except OSError:
            return
        before = output.read_bytes()
        result = run('--target', str(skill), '--output', str(output), '--json', str(receipt))
        assert result.returncode == 1
        report = json.loads(result.stdout)
        assert report['code'] == 'output/target-alias'
        assert output.read_bytes() == before
        assert receipt.read_bytes() == before


def test_symlink_output_resolving_to_non_zip_is_rejected() -> None:
    if not hasattr(os, 'symlink'):
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        marker = base / 'marker.env'
        marker.write_bytes(b'keep-me')
        output = base / 'skill.zip'
        try:
            output.symlink_to(marker)
        except OSError:
            return
        result = run('--target', str(skill), '--output', str(output))
        assert result.returncode == 1
        report = json.loads(result.stdout)
        assert report['code'] == 'output/resolved-extension'
        assert marker.read_bytes() == b'keep-me'
        assert output.is_symlink()


def test_success_receipt_matches_committed_package() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = make_skill(base)
        output = base / 'skill.zip'
        receipt = base / 'receipt.json'
        result = run('--target', str(skill), '--output', str(output), '--json', str(receipt))
        assert result.returncode == 0, result.stderr or result.stdout
        assert output.is_file()
        assert receipt.is_file()
        report = json.loads(receipt.read_text(encoding='utf-8'))
        assert report['status'] == 'pass'
        assert report['stage'] == 'committed'
        assert report['package_sha256'] == sha256(output)
        assert report['output_preserved_on_failure'] is True
        with zipfile.ZipFile(output, 'r') as zf:
            assert zf.testzip() is None
            assert 'demo-skill/SKILL.md' in zf.namelist()



def test_validation_failure_preserves_existing_package_and_receipt() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        skill = base / 'demo-skill'
        skill.mkdir()
        (skill / 'SKILL.md').write_text(
            '---\nname: demo-skill\ndescription: TODO\n---\n\n# Demo\n',
            encoding='utf-8',
        )
        output = base / 'skill.zip'
        receipt = base / 'receipt.json'
        output.write_bytes(b'old-package')
        receipt.write_text('{"status":"pass","old":true}\n', encoding='utf-8')
        old_output = output.read_bytes()
        old_receipt = receipt.read_bytes()
        result = run('--target', str(skill), '--output', str(output), '--json', str(receipt))
        assert result.returncode == 1
        assert output.read_bytes() == old_output
        assert receipt.read_bytes() == old_receipt
        failure = json.loads(result.stdout)
        assert failure['stage'] == 'validation'


if __name__ == '__main__':
    test_package_and_receipt_alias_is_rejected_without_mutation()
    test_symlink_output_resolving_to_non_zip_is_rejected()
    test_success_receipt_matches_committed_package()
    test_validation_failure_preserves_existing_package_and_receipt()
    print('ok')
