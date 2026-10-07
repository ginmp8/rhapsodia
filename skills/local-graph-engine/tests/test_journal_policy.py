"""Version-aware policy for the upstream SQLite WAL-reset defect."""
from pathlib import Path
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import graph_engine as ge

class JournalPolicy(unittest.TestCase):
    def test_default_journal_is_portable_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ge.init_db(Path(d)/'graph.db')['journal_mode'],'delete')
    def test_exact_upstream_fixed_ranges(self):
        from graph_journal import wal_reset_fixed
        for v in [(3,51,3),(3,52,0),(3,50,7),(3,44,6)]:self.assertTrue(wal_reset_fixed(v),v)
        for v in [(3,51,2),(3,50,6),(3,44,5),(3,46,1)]:self.assertFalse(wal_reset_fixed(v),v)
    def test_unpatched_wal_writer_blocked_and_explicit_conversion(self):
        from graph_journal import set_journal
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'graph.db';ge.init_db(db)
            con=sqlite3.connect(db);con.execute('PRAGMA journal_mode=WAL');con.close()
            with patch('sqlite3.sqlite_version_info',(3,46,1)):
                with self.assertRaises(ValueError):ge.connect(db)
                self.assertEqual(set_journal(db,'delete')['journal_mode'],'delete')
                with self.assertRaises(ValueError):set_journal(db,'wal')
            with closing(ge.connect(db)) as con:self.assertEqual(con.execute('PRAGMA journal_mode').fetchone()[0],'delete')

if __name__=='__main__':unittest.main()
