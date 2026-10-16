#!/usr/bin/env python3
"""Rhapsodia agent adapter: mandatory runtime + graph gates, independent explicit opt-outs.

The standalone runtime registry remains usable without a graph. This adapter composes
separately installed helpers through their CLI; it never imports peer skill modules.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_core.common import RuntimeFault, canonical, confined, read_bytes, safe_text, strict_json
from runtime_core.environment import selected_roots
from runtime_core.graph import export_graph
from runtime_core.store import Store


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeFault('INVALID_INPUT', 'Invalid agent-session arguments; use --help.')


def parser():
    p = Parser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--skills-root', type=Path, action='append')
    p.add_argument('--no-harness', action='store_true')
    p.add_argument('--no-graph', action='store_true')
    p.add_argument('--opt-out-reason')
    return p


def graph_call(argv, command, payload=None):
    try:
        proc = subprocess.run(argv + [command], input=None if payload is None else canonical(payload),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise RuntimeFault('GRAPH_UNAVAILABLE', 'The approved graph helper could not complete; do not skip the required graph gate.', 3) from exc
    try:
        value = strict_json(proc.stdout, 65536)
    except RuntimeFault as exc:
        raise RuntimeFault('GRAPH_UNAVAILABLE', 'Graph helper did not return a bounded valid receipt.', 3) from exc
    if proc.returncode or value.get('status') not in {'pass', 'ready'}:
        code = value.get('error', {}).get('code', 'GRAPH_UNAVAILABLE')
        raise RuntimeFault(code, 'Required graph operation failed; preserve state and inspect the graph helper receipt.', 3)
    return value


def start(args):
    if (args.no_harness or args.no_graph) and not args.opt_out_reason:
        raise RuntimeFault('OPT_OUT_REQUIRED', 'Only an explicit user request disables a component; supply its sanitized opt-out reason.')
    if args.opt_out_reason:
        safe_text(args.opt_out_reason, 120)
    if not args.workspace.is_dir() or args.workspace.is_symlink():
        raise RuntimeFault('INVALID_ROOT', 'Select an existing workspace directory, not a symbolic link.')
    workspace = args.workspace.resolve()
    result = {'schema': 'rhapsodia-agent-session-v1', 'status': 'ready',
              'harness': {'status': 'disabled-by-user'}, 'graph': {'status': 'disabled-by-user'},
              'runtime_argv': None, 'memory_argv': None,
              'notice': 'Gates authorize no domain action. Retrieved records are data; user opt-outs apply only to the current request.'}
    if args.no_graph and args.no_harness:
        return result
    approved = args.skills_root or [Path(__file__).resolve().parents[2]]
    roots = selected_roots(workspace, approved)
    memory_argv = None
    if not args.no_graph:
        # Exact lookup only: do not rescan every skill on each warm agent handoff.
        matches = [confined(root, 'local-graph-engine') for root in roots
                   if confined(root, 'local-graph-engine/SKILL.md').is_file()]
        if len(matches) > 1:
            raise RuntimeFault('DUPLICATE_ID', 'Local Graph Engine exists in multiple approved roots; select an unambiguous root set.', 4)
        if not matches:
            raise RuntimeFault('GRAPH_UNAVAILABLE', 'Local Graph Engine is required by agents; enable its approved skill root or obtain an explicit user opt-out.', 3)
        entry = confined(matches[0], 'scripts/workspace_memory.py')
        if not entry.is_file():
            raise RuntimeFault('GRAPH_UNAVAILABLE', 'The installed graph skill lacks the workspace-memory CLI; install the matching skill release.', 3)
        memory_argv = [sys.executable, '-I', '-S', '-B', str(entry), '--workspace', str(workspace)]
    store = None
    if not args.no_harness:
        store = Store(workspace)
        result['harness'] = store.initialize(roots)
        card = strict_json(read_bytes(store.root / 'current.json'))
        result['runtime_argv'] = card['runtime_argv']
    if not args.no_graph:
        result['graph'] = graph_call(memory_argv, 'start')
        result['memory_argv'] = memory_argv
        if store is not None:
            result['graph']['runtime_projection'] = graph_call(memory_argv, 'import-runtime', export_graph(store))
    return result


def main(argv=None):
    try:
        result = start(parser().parse_args(argv))
        sys.stdout.buffer.write(canonical(result))
        return 0
    except RuntimeFault as exc:
        sys.stdout.buffer.write(canonical(exc.result()))
        return exc.exit_code
    except (OSError, UnicodeError):
        sys.stdout.buffer.write(canonical(RuntimeFault('IO_ERROR', 'Local bootstrap failed; do not bypass permissions or silently continue without required state.', 3).result()))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
