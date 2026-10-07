"""Budgeted, evidence-addressed context. No model, network, cache or DB writes.

The UTF-8 limit covers canonical JSON plus one LF (the CLI representation), not
transport envelopes. Token estimates are explicitly heuristic, not billing data.
"""
from __future__ import annotations

from collections import Counter, deque
import json
import re
from typing import Any

from graph_common import canonical, digest, integer
from graph_store import logical_hash

CONTEXT_FIELDS = {'detail', 'budget_bytes', 'token_budget', 'properties', 'previous', 'max_edges'}
RECEIPT_VERSION = 'graph-context-receipt-v1'


def validate_context(request: dict) -> dict:
    out = dict(request)
    out.setdefault('detail', 'compact')
    if out['detail'] not in ('compact', 'evidence'):
        raise ValueError('detail must be compact or evidence')
    out.setdefault('budget_bytes', 12000)
    integer(out['budget_bytes'], 'budget_bytes', 2048, 1048576)
    if 'token_budget' in out:
        integer(out['token_budget'], 'token_budget', 512, 262144)
    integer(out['max_nodes'], 'context max_nodes', 1, 500)
    out.setdefault('max_edges', 100)
    integer(out['max_edges'], 'max_edges', 0, 2000)
    props = out.setdefault('properties', [])
    if not isinstance(props, list) or len(props) > 32 or any(
        not isinstance(p, str) or not p.strip() or len(p) > 256 for p in props
    ):
        raise ValueError('properties must be at most 32 bounded property names')
    out['properties'] = sorted(set(props))
    if out.get('query') and (out.get('seed') or out.get('node')):
        raise ValueError('choose either a context seed/node or a text query')
    previous = out.get('previous')
    if 'previous' in out:
        keys = {'schema_version', 'graph_sha256', 'profile_sha256', 'items'}
        if not isinstance(previous, dict) or set(previous) != keys or previous.get('schema_version') != RECEIPT_VERSION:
            raise ValueError('invalid previous context receipt')
        for key in ('graph_sha256', 'profile_sha256'):
            if not isinstance(previous[key], str) or not re.fullmatch(r'[0-9a-f]{64}', previous[key]):
                raise ValueError('invalid context receipt digest')
        items = previous['items']
        if not isinstance(items, dict) or len(items) > 2500 or any(
            not isinstance(k, str) or len(k) > 8192 or not k.startswith(('n:', 'e:'))
            or not isinstance(v, str) or not re.fullmatch(r'[0-9a-f]{64}', v)
            for k, v in items.items()
        ):
            raise ValueError('invalid context receipt items')
    return out


def _select(con, request, nodes, rows):
    from graph_query import adjacency, resolve
    limit = request['max_nodes']
    token = request.get('seed') or request.get('node')
    degree = Counter(n for row in rows for n in (row['source_node_id'], row['target_node_id']))
    if token:
        seeds = [resolve(nodes, token, con)]
    elif request.get('query'):
        term = request['query'].casefold()
        aliases = {}
        for row in con.execute('SELECT alias,node_id FROM node_aliases ORDER BY node_id,alias'):
            aliases.setdefault(row['node_id'], []).append(row['alias'].casefold())
        seeds = [nid for nid, n in nodes.items() if term in n['label'].casefold() or term in nid.casefold()
                 or any(term in a for a in aliases.get(nid, []))]
        seeds.sort(key=lambda nid: (nodes[nid]['label'].casefold() != term, -degree[nid], nid))
    else:
        ids = sorted(nodes, key=lambda nid: (-degree[nid], nid))
        return ids[:limit], {'matched_seeds': 0, 'depth_boundary': False, 'node_boundary': len(ids) > limit}
    matched = len(seeds)
    chosen = seeds[:min(limit, 5)]
    seen = set(chosen)
    queue = deque((nid, 0) for nid in chosen)
    adj = adjacency(rows, request.get('direction', 'both'))
    depth_boundary = False
    node_boundary = len(seeds) > len(chosen)
    while queue:
        nid, depth = queue.popleft()
        for other, _ in adj.get(nid, []):
            if other in seen:
                continue
            if depth >= request['depth']:
                depth_boundary = True
                continue
            if len(chosen) >= limit:
                node_boundary = True
                continue
            seen.add(other)
            chosen.append(other)
            queue.append((other, depth + 1))
    return chosen, {'matched_seeds': matched, 'depth_boundary': depth_boundary, 'node_boundary': node_boundary}


def _evidence(con, kind, identifier, request):
    # Use evidence rows, not every stored claim: excluded status/provenance must
    # never re-enter the response through a rich-detail helper.
    condition = 'e.status IN (' + ','.join('?' for _ in request['statuses']) + ') AND e.confidence>=?'
    args = [identifier, *request['statuses'], request.get('min_confidence', 0)]
    if request.get('provenance'):
        condition += ' AND e.provenance IN (' + ','.join('?' for _ in request['provenance']) + ')'
        args += request['provenance']
    cap = 1 if request['detail'] == 'compact' else 5
    raw = con.execute(
        f'SELECT e.*,s.uri,s.content_hash FROM {kind}_evidence e JOIN sources s ON s.id=e.source_id '
        f'WHERE e.{kind}_id=? AND {condition} ORDER BY s.uri,e.locator,e.id LIMIT ?', [*args, cap + 1]
    ).fetchall()
    evidence, sources = [], {}
    for row in raw[:cap]:
        entry = {'source': row['source_id'], 'locator': row['locator'], 'status': row['status'],
                 'provenance': row['provenance'], 'confidence': row['confidence']}
        if request['detail'] == 'evidence':
            entry['details'] = json.loads(row['details_json'])
        evidence.append(entry)
        sources[row['source_id']] = {'uri': row['uri'], 'content_hash': row['content_hash']}
    return evidence, sources, len(raw) > cap


def _item(con, kind, raw, request, has_claims):
    identifier = raw['id']
    if kind == 'node':
        value = {k: raw[k] for k in ('id', 'kind', 'label')}
    else:
        value = {'id': identifier, 'source': raw['source_node_id'], 'target': raw['target_node_id'],
                 'relation': raw['relation'], 'directed': bool(raw['directed'])}
    if request['properties']:
        props = json.loads(raw['properties_json'])
        value['properties'] = {k: props[k] for k in request['properties'] if k in props}
    evidence, sources, truncated = _evidence(con, kind, identifier, request)
    value['evidence'] = evidence
    if truncated:
        value['evidence_truncated'] = True
    if not evidence:
        value['evidence_missing'] = True  # eligible endpoint, not an evidenced attribute assertion
    if has_claims:
        # Conflict flag is an inspection cue, not a disclosure of excluded claims.
        rows = con.execute(f'SELECT payload_json FROM {kind}_claims WHERE {kind}_id=? ORDER BY source_id LIMIT 101', (identifier,)).fetchall()
        variants = {canonical({k: v for k, v in json.loads(r[0]).items() if k not in ('evidence', 'aliases')}) for r in rows}
        if len(variants) > 1:
            value['attribute_conflict'] = True
        if len(rows) > 100:
            value['claim_check_truncated'] = True
    return value, sources


def _account(value: dict) -> int:
    # Decimal length changes can alter the accounting object itself. Converge
    # mechanically, then verify the exact wire representation before returning.
    for _ in range(12):
        size = len((canonical(value) + '\n').encode('utf-8'))
        estimate = (size + 3) // 4
        if value['budget']['output_bytes'] == size and value['budget']['estimated_tokens'] == estimate:
            return size
        value['budget']['output_bytes'] = size
        value['budget']['estimated_tokens'] = estimate
    raise ValueError('context byte accounting did not converge')


def context(con, request: dict, nodes: dict, rows: list) -> dict[str, Any]:
    request = validate_context(request)
    graph_hash = logical_hash(con)
    profile = {k: request.get(k) for k in ('detail', 'properties', 'statuses', 'provenance', 'min_confidence')}
    profile_hash = digest(profile)
    previous = request.get('previous')
    can_reuse = bool(previous and previous['graph_sha256'] == graph_hash and previous['profile_sha256'] == profile_hash)
    known = previous['items'] if can_reuse else {}
    order, bounds = _select(con, request, nodes, rows)
    selected = set(order)
    candidates = [r for r in rows if r['source_node_id'] in selected and r['target_node_id'] in selected]
    candidates.sort(key=lambda r: r['id'])
    limited_edges = candidates[:request['max_edges']]
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    nitems = {nid: _item(con, 'node', nodes[nid], request, 'node_claims' in tables) for nid in order}
    eitems = {r['id']: _item(con, 'edge', r, request, 'edge_claims' in tables) for r in limited_edges}
    hashes = {'n:' + k: digest(v[0]) for k, v in nitems.items()}
    hashes.update({'e:' + k: digest(v[0]) for k, v in eitems.items()})
    cap = min(request['budget_bytes'], request.get('token_budget', 262144) * 4)
    original_count = len(order)
    original_edge_count = len(limited_edges)

    def pack(ids, edges, reuse=False):
        ns, es, reused, sources, manifest = [], [], [], {}, {}
        for kind, keys, items, output in [('n', ids, nitems, ns), ('e', [e['id'] for e in edges], eitems, es)]:
            for key in keys:
                record, source_map = items[key]
                ref = kind + ':' + key
                manifest[ref] = hashes[ref]
                if reuse and known.get(ref) == hashes[ref]:
                    reused.append(ref)
                else:
                    output.append(record)
                    sources.update(source_map)
        byte_boundary = len(ids) < original_count or len(edges) < original_edge_count
        truncated = byte_boundary or bounds['depth_boundary'] or bounds['node_boundary'] or len(edges) < len(candidates)
        return {
            'status': 'pass', 'schema_version': 'graph-context-v1',
            'scope': {**bounds, 'eligible_nodes': len(nodes), 'eligible_edges': len(rows),
                      'selected_nodes': len(ids), 'selected_edges': len(edges),
                      'omitted_nodes': original_count - len(ids), 'omitted_edges': len(candidates) - len(edges),
                      'edge_boundary': len(candidates) > request['max_edges'], 'byte_boundary': byte_boundary,
                      'truncated': truncated, 'complete_database': False, 'statuses': request['statuses']},
            'nodes': ns, 'edges': es, 'sources': sources, 'reused': reused,
            'reuse_status': ('reused' if can_reuse else 'invalidated') if previous else 'not_requested',
            'receipt': {'schema_version': RECEIPT_VERSION, 'graph_sha256': graph_hash,
                        'profile_sha256': profile_hash, 'items': manifest},
            'budget': {'max_bytes': cap, 'output_bytes': 0, 'estimated_tokens': 0,
                       'estimator': 'ceil(UTF-8 bytes / 4); heuristic, not model tokens',
                       'transport_overhead_included': False},
        }

    # Select against full records first. A reuse receipt saves transmission; it
    # must not silently broaden the selected graph or change the chosen answer.
    ids = list(order)
    while True:
        included = set(ids)
        edges = [r for r in limited_edges if r['source_node_id'] in included and r['target_node_id'] in included]
        value = pack(ids, edges)
        if _account(value) <= cap:
            break
        if len(ids) > 1:
            ids.pop()
        elif edges:
            limited_edges.pop()
        else:
            raise ValueError('context budget cannot fit the required seed/item and evidence; increase budget_bytes or narrow properties/detail')
    if previous:
        value = pack(ids, edges, reuse=True)
        if _account(value) > cap:
            raise ValueError('context receipt exceeds the byte budget')
    return value
