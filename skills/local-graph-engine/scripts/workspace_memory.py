#!/usr/bin/env python3
"""Private per-workspace memory using the Local Graph Engine's public GraphPatch format."""
from __future__ import annotations
import argparse
from pathlib import Path
import sqlite3
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_common import canonical, parse_json
from workspace_memory_contract import MAX_INPUT, MemoryFault, pin, workspace_path
from workspace_memory_core import WorkspaceMemory


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise MemoryFault('INVALID_INPUT', 'Invalid command arguments; use --help for supported operations.')


def parser():
    p = Parser(description=__doc__)
    p.add_argument('--workspace', required=True, type=Path)
    subs = p.add_subparsers(dest='command', required=True)
    for name in ('start', 'status'):
        subs.add_parser(name)
    subs.add_parser('pin').add_argument('paths', nargs='+')
    lookup = subs.add_parser('lookup')
    lookup.add_argument('query')
    lookup.add_argument('--key')
    lookup.add_argument('--budget-bytes', type=int, default=8192)
    subs.add_parser('review-lessons')
    for name in ('learn', 'import-runtime'):
        subs.add_parser(name).add_argument('--input', type=Path)
    reconcile = subs.add_parser('reconcile')
    reconcile.add_argument('--paths', nargs='+')
    reconcile.add_argument('--prune-missing', action='store_true')
    reconcile.add_argument('--confirm-complete-scope', action='store_true')
    return p


def input_value(path, limit):
    if path is None:
        data = sys.stdin.buffer.read(limit + 1)
    else:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            raise MemoryFault('INVALID_INPUT', 'Select a bounded regular input file.')
        with path.open('rb') as stream:
            data = stream.read(limit + 1)
    if len(data) > limit:
        raise MemoryFault('INPUT_TOO_LARGE', 'Request exceeds its byte limit.')
    return parse_json(data.decode('utf-8'))


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        if args.command == 'pin':
            if len(args.paths) > 16:
                raise MemoryFault('INVALID_INPUT', 'Pin at most sixteen exact files per call.')
            root = workspace_path(args.workspace)
            result = {'status': 'pass', 'sources': [pin(root, path) for path in args.paths]}
        else:
            memory = WorkspaceMemory(args.workspace)
            if args.command == 'start':
                result = memory.start()
            elif args.command == 'status':
                memory.check(integrity=True)
                result = {'status': 'ready', 'db': str(memory.db), 'scope': memory.scope}
            elif args.command == 'lookup':
                result = memory.lookup(args.query, budget=args.budget_bytes, key=args.key)
            elif args.command == 'review-lessons':
                result = memory.review_lessons()
            elif args.command == 'learn':
                result = memory.learn(input_value(args.input, MAX_INPUT))
            elif args.command == 'import-runtime':
                result = memory.import_runtime(input_value(args.input, 4 * 1024 * 1024))
            else:
                result = memory.reconcile(args.paths, prune=args.prune_missing, complete=args.confirm_complete_scope)
        print(canonical(result))
        return 0
    except MemoryFault as exc:
        print(canonical(exc.result()))
        return 2
    except (ValueError, TypeError, KeyError, OSError, UnicodeError, RecursionError, sqlite3.Error):
        print(canonical(MemoryFault('INVALID_OR_UNAVAILABLE', 'Input or local state could not be validated; no command, installation or automatic recovery was attempted.').result()))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
