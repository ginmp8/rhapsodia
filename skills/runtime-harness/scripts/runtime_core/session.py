"""Optional host entry adapters. No host configuration or process is auto-started."""
from __future__ import annotations
from .common import bounded, canonical, read_bytes, strict_json
from .store import Store


def session_start(store: Store, roots, output_format: str) -> dict:
    summary = store.initialize(roots)
    card = strict_json(read_bytes(store.root / 'current.json'))
    result = bounded(dict(summary, schema='runtime-session-v1', runtime_argv=card['runtime_argv'],
                          python_argv=card['python_argv'], notice='Local observations only; not authorization or test evidence.'), 4096)
    if output_format == 'vscode-local':
        # VS Code Local SessionStart protocol; not a claim about other hook hosts.
        return {'hookSpecificOutput': {'hookEventName': 'SessionStart',
                'additionalContext': canonical(result).decode('utf-8').rstrip()}}
    return result


def mcp_config(store: Store) -> dict:
    store.current()
    card = strict_json(read_bytes(store.root / 'current.json'))
    argv = card['runtime_argv']
    return {'command': argv[0], 'args': argv[1:] + ['mcp']}
