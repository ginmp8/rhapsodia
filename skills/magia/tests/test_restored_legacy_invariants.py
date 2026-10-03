from pathlib import Path
from board_contract import validate_board
from test_board_contract import build_board

def test_created_at_cycle_mismatch(tmp_path:Path):
 root,spec=build_board(tmp_path);p=root/'cycle.yaml';p.write_text(p.read_text().replace('2026-04-20T00:00:00Z','2026-04-21T00:00:00Z'))
 assert any('created_at date must match' in e for e in validate_board(root))

def test_created_at_spec_and_manifest_mismatch(tmp_path:Path):
 root,spec=build_board(tmp_path);p=root/'registry'/f'{spec}.yaml';p.write_text(p.read_text().replace('2026-04-20T00:00:00Z','2026-04-21T00:00:00Z'))
 errors=validate_board(root);assert any('created_at date must match' in e for e in errors);assert any('manifest created_at must match' in e for e in errors)

def test_invalid_dependency_is_rejected_as_identity(tmp_path:Path):
 root,spec=build_board(tmp_path);p=root/'registry'/f'{spec}.yaml';p.write_text(p.read_text().replace('depends_on_specs: []','depends_on_specs: [spec-2026-02-30-invalid]'))
 assert any('invalid depends_on_specs entry' in e for e in validate_board(root))
