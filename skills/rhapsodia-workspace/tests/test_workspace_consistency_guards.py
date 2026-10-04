from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from workspace import build_catalog, main
from artifact_protocol import ContractError

class WorkspaceConsistencyGuards(unittest.TestCase):
    def test_project_rechecks_snapshot_before_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp);first=build_catalog(repo);changed=copy.deepcopy(first);changed['source_fingerprint']='f'*64
            dest=repo/'.rhapsodia/catalog/portfolio.json';dest.parent.mkdir(parents=True);dest.write_bytes(b'last-good')
            with patch('workspace.build_catalog',side_effect=[first,changed]):
                result=main(['project','--repo-root',str(repo),'--output','.rhapsodia/catalog/portfolio.json'])
            self.assertEqual(result,1);self.assertEqual(dest.read_bytes(),b'last-good')
    def test_repository_root_symlink_is_not_normalized_away(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);repo=base/'repo';repo.mkdir();link=base/'link';link.symlink_to(repo,target_is_directory=True)
            self.assertEqual(main(['index','--repo-root',str(link)]),1)
            self.assertFalse((repo/'.rhapsodia').exists())
    def test_unknown_destination_rejected_even_for_empty_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ContractError):build_catalog(Path(tmp),destination='arbitrary')

if __name__=='__main__':unittest.main()
