from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'validate_portability.py'


def load_module():
    spec = importlib.util.spec_from_file_location('validate_portability', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_all_structural_host_profiles_pass() -> None:
    import sys
    sys.path.insert(0, str(ROOT / 'scripts'))
    module = load_module()
    report = module.validate(ROOT, module.normalize_hosts('all'))
    assert report['status'] == 'pass', report
    assert report['portable_core'] is True
    for host in ('openai', 'claude', 'copilot', 'cursor'):
        assert report['host_results'][host]['status'] == 'pass', report['host_results'][host]


if __name__ == '__main__':
    test_all_structural_host_profiles_pass()
    print('ok')
