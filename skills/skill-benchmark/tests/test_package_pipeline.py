from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'package_skill.py'


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_deterministic_package_and_receipt() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        a = base / 'a.zip'
        b = base / 'b.zip'
        ra = base / 'a.json'
        rb = base / 'b.json'
        first = run('--target', str(ROOT), '--output', str(a), '--json-output', str(ra), '--hosts', 'all')
        second = run('--target', str(ROOT), '--output', str(b), '--json-output', str(rb), '--hosts', 'all')
        assert first.returncode == 0, first.stderr or first.stdout
        assert second.returncode == 0, second.stderr or second.stdout
        assert sha(a) == sha(b)
        receipt = json.loads(ra.read_text(encoding='utf-8'))
        assert receipt['archive_sha256'] == sha(a)
        assert receipt['portability']['status'] == 'pass'


def test_output_receipt_alias_fails_and_preserves_last_good() -> None:
    if not hasattr(os, 'link'):
        return
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        output = base / 'skill.zip'
        receipt = base / 'receipt.json'
        output.write_bytes(b'last-good')
        try:
            os.link(output, receipt)
        except OSError:
            return
        before = output.read_bytes()
        result = run('--target', str(ROOT), '--output', str(output), '--json-output', str(receipt), '--hosts', 'all')
        assert result.returncode == 1
        assert output.read_bytes() == before
        assert receipt.read_bytes() == before


if __name__ == '__main__':
    test_deterministic_package_and_receipt()
    test_output_receipt_alias_fails_and_preserves_last_good()
    print('ok')
