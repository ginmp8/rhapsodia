"""Measure serialized bytes for identical selected entity/relationship IDs.

This is a representation comparison, not an answer-quality or LLM billing test.
All three arms share one read-only SQLite snapshot. No network/tokenizer download.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from graph_common import canonical, parse_json
from graph_query import query, validate_request, filtered_graph, node_view, edge_view
from graph_store import readonly


def wire_size(value: dict) -> int:
    return len((canonical(value) + '\n').encode('utf-8'))


def measure_context(db: Path, request: dict) -> dict:
    if request.get('operation') != 'context' or 'previous' in request:
        raise ValueError('measurement requires a context request without previous')
    con = readonly(db)
    try:
        con.execute('BEGIN')
        normalized = validate_request(request)
        first = query(con, normalized)
        nodes, edges = filtered_graph(con, normalized)
        node_ids = {n['id'] for n in first['nodes']}
        edge_ids = {e['id'] for e in first['edges']}
        rich = {'nodes': [node_view(con, n) for n in sorted(node_ids)],
                'edges': [edge_view(con, e) for e in edges if e['id'] in edge_ids]}
        reused = query(con, dict(normalized, previous=first['receipt']))
        if reused['receipt'] != first['receipt']:
            raise ValueError('measurement selection changed across receipt reuse')
        baseline, compact, repeat = map(wire_size, (rich, first, reused))
        return {
            'status': 'pass', 'schema_version': 'graph-context-byte-measurement-v1',
            'graph_sha256': first['receipt']['graph_sha256'],
            'comparison': 'Same selected node/edge IDs and DB snapshot; rich properties/claims versus requested context. Not lossless compression.',
            'selected_nodes': len(node_ids), 'selected_edges': len(edge_ids),
            'eligible_nodes': len(nodes), 'eligible_edges': first['scope']['eligible_edges'],
            'rich_records_bytes': baseline, 'compact_envelope_bytes': compact,
            'repeat_envelope_bytes': repeat,
            'compact_reduction_percent': round(100 * (baseline - compact) / baseline, 2),
            'repeat_vs_compact_reduction_percent': round(100 * (compact - repeat) / compact, 2),
            'wire_format': 'canonical UTF-8 JSON plus LF',
            'scope': first['scope'],
            'limits': ['Not measured model tokens or billing.',
                       'No prompt, tool/MCP envelope or tokenizer overhead included.',
                       'No answer-quality or retrieval-recall evaluation.',
                       'Reuse requires the caller to retain the previous records and source dictionary.',
                       'Rich records include attributes/claims not requested by compact mode.'],
        }
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, type=Path)
    parser.add_argument('--request', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = measure_context(args.db, parse_json(args.request.read_text(encoding='utf-8')))
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        print(canonical({'status': 'fail', 'error': str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
