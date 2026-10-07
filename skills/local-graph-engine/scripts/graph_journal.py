"""Portable rollback by default; opt-in WAL requires an upstream fixed version.

Policy source: https://www.sqlite.org/wal.html#the_wal_reset_bug, checked
2026-10-07. This checks release ranges, not all SQLite vulnerabilities.
"""
from pathlib import Path
import sqlite3


def wal_reset_fixed(version=None):
    v=tuple(sqlite3.sqlite_version_info if version is None else version)
    return v >= (3,51,3) or ((3,50,7) <= v < (3,51,0)) or ((3,44,6) <= v < (3,45,0))


def guard_writer(con):
    if con.execute('PRAGMA journal_mode').fetchone()[0].lower() == 'wal' and not wal_reset_fixed():
        raise ValueError('SQLite WAL-reset fix not established for this runtime. Stop other connections, back up, then run journal --mode delete; or use a fixed SQLite build.')


def set_journal(path:Path, mode:str):
    if mode not in ('delete','wal'):raise ValueError('unsupported journal mode')
    if mode=='wal' and not wal_reset_fixed():raise ValueError('WAL requires SQLite 3.51.3+, 3.50.7+, or 3.44.6+ in the documented fixed release branches')
    path=Path(path).resolve()
    if not path.is_file():raise FileNotFoundError(str(path))
    con=sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,timeout=5)
    try:
        from graph_store import check_schema
        check_schema(con)
        actual=con.execute('PRAGMA journal_mode='+mode.upper()).fetchone()[0].lower()
        if actual!=mode:raise ValueError('journal mode could not change; stop other connections')
        return {'status':'pass','journal_mode':actual,'sqlite':sqlite3.sqlite_version,'scope':'local filesystem; stop concurrent use before mode changes'}
    finally:con.close()
