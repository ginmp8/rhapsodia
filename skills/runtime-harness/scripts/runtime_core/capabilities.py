"""Observed capabilities and bounded discovery outcomes; never execute probes.

A capability is a pin to an existing tool and an explicit caller-produced receipt.
Neither a caller assertion nor a content hash grants execution or gate authority.
"""
from __future__ import annotations
import math
from pathlib import Path
import statistics
import time
from .common import HASH_RE, ID_RE, RuntimeFault, fields, file_hash, number, safe_text, sha, strict_json, read_bytes, bounded
from .environment import search_fingerprint

OUTCOMES = {'available', 'missing', 'denied', 'incompatible', 'transient', 'broken', 'stale'}
STRATEGIES = {'path', 'explicit', 'registered-root'}
TTL = {'available': 3600, 'missing': 600, 'denied': 60, 'incompatible': 600,
       'transient': 30, 'broken': 120, 'stale': 1}


def capability_name(uri):
    if not isinstance(uri, str) or not uri.startswith('capability://') or not ID_RE.fullmatch(uri[13:]):
        raise RuntimeFault('INVALID_INPUT', 'Expected one canonical capability:// ID.')
    return uri[13:]


def validate_catalogs(snapshot):
    """Validate additive catalogs even when state has a valid content hash."""
    for key in ('capabilities', 'attempts'):
        catalog = snapshot.get(key, {})
        if not isinstance(catalog, dict) or len(catalog) > 4096:
            raise ValueError('invalid operational observation catalog')
        for name, record in catalog.items():
            if not isinstance(name, str) or not isinstance(record, dict):
                raise ValueError('invalid observation record')
            if key == 'capabilities':
                fields(record, {'uri', 'kind', 'tool_uri', 'tool_identity', 'proof_uri', 'proof_sha256',
                                'features', 'observed_at', 'ttl_seconds', 'identity'})
                if capability_name(record['uri']) != name or record['kind'] != 'capability':
                    raise ValueError('invalid capability')
                if sha({k:v for k,v in record.items() if k != 'identity'}) != record['identity']:
                    raise ValueError('invalid capability identity')
                for field in ('tool_identity', 'proof_sha256'):
                    if not isinstance(record[field], str) or not HASH_RE.fullmatch(record[field]):
                        raise ValueError('invalid pin')
                if not isinstance(record['tool_uri'], str) or not record['tool_uri'].startswith('tool://'):
                    raise ValueError('invalid tool URI')
                if not ID_RE.fullmatch(record['tool_uri'][7:]):
                    raise ValueError('invalid tool URI')
                if not isinstance(record['proof_uri'], str) or not record['proof_uri'].startswith(('repo://', 'skill://', 'resource://')):
                    raise ValueError('invalid proof URI')
                _features(record['features'])
            else:
                fields(record, {'target', 'outcome', 'strategy', 'duration_ms', 'observed_at', 'ttl_seconds',
                                'search_fingerprint', 'scope', 'target_identity'})
                if sha(record) != name or record['outcome'] not in OUTCOMES or record['strategy'] not in STRATEGIES:
                    raise ValueError('invalid attempt')
                _target(record['target'])
                for field in ('scope', 'search_fingerprint'):
                    if not isinstance(record[field], str) or not HASH_RE.fullmatch(record[field]):
                        raise ValueError('invalid observation identity')
                identity = record['target_identity']
                if identity is not None and (not isinstance(identity, str) or not HASH_RE.fullmatch(identity)):
                    raise ValueError('invalid target identity')
                _duration(record['duration_ms'])
            observed = record['observed_at']
            if isinstance(observed, bool) or not isinstance(observed, (int, float)) or not math.isfinite(observed):
                raise ValueError('invalid observation timestamp')
            number(record['ttl_seconds'], 1, 86400)


def _features(value):
    if not isinstance(value, list) or len(value) > 32 or any(not isinstance(x, str) or not ID_RE.fullmatch(x) for x in value) or len(set(value)) != len(value):
        raise RuntimeFault('INVALID_INPUT', 'Features must be 0..32 unique lowercase capability labels.')
    return sorted(value)


def publish(store, request):
    from .query import resolve
    fields(request, {'uri', 'tool', 'proof'}, {'ttl_seconds'})
    name = capability_name(request['uri'])
    ttl = number(request.get('ttl_seconds', 3600), 1, 86400)
    for key in ('tool', 'proof'):
        safe_text(request[key], 1024)
    if not request['tool'].startswith('tool://') or not request['proof'].startswith(('repo://', 'skill://', 'resource://')):
        raise RuntimeFault('INVALID_INPUT', 'Bind a tool:// and one existing local file receipt.')
    # Resolve and publish under the same catalog lock. File mutations remain detectable on read.
    with store.writer():
        _, snapshot = store.current()
        tool, proof = resolve(snapshot, request['tool']), resolve(snapshot, request['proof'])
        if tool['status'] != 'available' or proof['status'] != 'available' or 'sha256' not in proof:
            raise RuntimeFault('UNAVAILABLE_RESOURCE', 'The tool or its observation receipt is unavailable.', 3)
        receipt = strict_json(read_bytes(Path(proof['path']), 65536))
        fields(receipt, {'schema', 'capability_uri', 'tool_identity', 'available', 'features'})
        if receipt['schema'] != 'capability-observation/v1' or receipt['capability_uri'] != request['uri'] or receipt['tool_identity'] != tool['identity'] or receipt['available'] is not True:
            raise RuntimeFault('INVALID_RECEIPT', 'Capability observation does not match the current tool identity.', 3)
        if file_hash(Path(proof['path'])) != proof['sha256']:
            raise RuntimeFault('STALE_OBSERVATION', 'Observation changed during publication.', 3)
        record = {'uri': request['uri'], 'kind': 'capability', 'tool_uri': request['tool'],
                  'tool_identity': tool['identity'], 'proof_uri': request['proof'], 'proof_sha256': proof['sha256'],
                  'features': _features(receipt['features']), 'observed_at': time.time(), 'ttl_seconds': ttl}
        record['identity'] = sha(record)
        data = dict(snapshot)
        data['capabilities'] = {**snapshot.get('capabilities', {}), name: record}
        data['updated_at'] = time.time()
        from . import VERSION
        data['runtime_version'] = VERSION
        key, _ = store._publish(data)
    return {'status': 'stored', 'snapshot_id': key, 'uri': request['uri'], 'execution_authority': False,
            'notice': 'Caller-produced observation pinned, not authenticated or independently re-executed.'}


def resolve_capability(snapshot, uri):
    from .query import resolve
    name = capability_name(uri)
    record = snapshot.get('capabilities', {}).get(name)
    base = {'uri': uri, 'kind': 'capability', 'status': 'missing', 'execution_authority': False}
    if record is None:
        return base
    age = time.time() - record['observed_at']
    if age < -5 or age > record['ttl_seconds']:
        return {**base, 'status': 'stale'}
    try:
        tool = resolve(snapshot, record['tool_uri'])
        proof = resolve(snapshot, record['proof_uri'])
        current = tool['status'] == 'available' and proof['status'] == 'available' and tool.get('identity') == record['tool_identity'] and proof.get('sha256') == record['proof_sha256']
    except (OSError, RuntimeFault):
        current = False
    return {**base, 'status': 'available' if current else 'stale', 'identity': record['identity'],
            'tool_uri': record['tool_uri'], 'features': record['features'], 'proof_uri': record['proof_uri'],
            'producer_authenticated': False}


def _target(value):
    safe_text(value, 1024)
    if not value.startswith(('tool://', 'capability://', 'resource://')):
        raise RuntimeFault('INVALID_INPUT', 'Attempts describe tool, capability or resource discovery only.')
    from .common import relative_parts
    parts = relative_parts(value.split('://', 1)[1])
    if any(not ID_RE.fullmatch(p) for p in parts):
        raise RuntimeFault('INVALID_INPUT', 'Noncanonical observation target.')
    return value


def _duration(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 86400000):
        raise RuntimeFault('INVALID_INPUT', 'Duration must be a finite measured number or null.')
    return value


def attempt(store, request):
    from .query import resolve
    fields(request, {'target', 'outcome', 'strategy'}, {'duration_ms', 'ttl_seconds'})
    target = _target(request['target'])
    if not isinstance(request['outcome'], str) or request['outcome'] not in OUTCOMES or not isinstance(request['strategy'], str) or request['strategy'] not in STRATEGIES:
        raise RuntimeFault('INVALID_INPUT', 'Unknown typed outcome or discovery strategy.')
    duration = _duration(request.get('duration_ms'))
    ttl = number(request.get('ttl_seconds', TTL[request['outcome']]), 1, TTL[request['outcome']])
    with store.writer():
        _, snapshot = store.current()
        live = resolve(snapshot, target)
        if request['outcome'] == 'available' and live['status'] != 'available':
            raise RuntimeFault('UNAVAILABLE_RESOURCE', 'Publish the observed tool/resource before recording an available outcome.', 3)
        value = {'target': target, 'outcome': request['outcome'], 'strategy': request['strategy'],
                 'duration_ms': duration, 'observed_at': time.time(), 'ttl_seconds': ttl,
                 'search_fingerprint': search_fingerprint(), 'scope': snapshot['scope'],
                 'target_identity': live.get('identity', live.get('sha256'))}
        key = sha(value)
        records = dict(snapshot.get('attempts', {}))
        # A bounded rolling observation log is not canonical workflow or execution evidence.
        if len(records) >= 512:
            oldest = min(records, key=lambda k: (records[k]['observed_at'], k))
            del records[oldest]
        records[key] = value
        data = {**snapshot, 'attempts': records, 'updated_at': time.time()}
        from . import VERSION
        data['runtime_version'] = VERSION
        snapshot_id, _ = store._publish(data)
    return {'status': 'stored', 'id': key, 'snapshot_id': snapshot_id, 'execution_authority': False}


def history(store, request):
    from .query import resolve
    fields(request, {'target'}, {'budget_bytes'})
    target = _target(request['target'])
    budget = number(request.get('budget_bytes', 8192), 512, 65536)
    _, snapshot = store.current()
    live = resolve(snapshot, target)
    identity = live.get('identity', live.get('sha256'))
    now, fingerprint = time.time(), search_fingerprint()
    rows = []
    for key, row in snapshot.get('attempts', {}).items():
        if row['target'] != target:
            continue
        fresh = -5 <= now - row['observed_at'] <= row['ttl_seconds'] and row['scope'] == snapshot['scope'] and row['search_fingerprint'] == fingerprint and row['target_identity'] == identity
        if fresh:
            rows.append({'id': key, **row})
    rows.sort(key=lambda row: (row['observed_at'], row['id']), reverse=True)
    stats = []
    for strategy in sorted(STRATEGIES):
        subset = [r for r in rows if r['strategy'] == strategy]
        if not subset:
            continue
        successes = sum(r['outcome'] == 'available' for r in subset)
        durations = [r['duration_ms'] for r in subset if r['duration_ms'] is not None]
        stats.append({'strategy': strategy, 'observations': len(subset), 'successes': successes,
                      'smoothed_success_rate': (successes + 1) / (len(subset) + 2),
                      'median_duration_ms': statistics.median(durations) if durations else None})
    stats.sort(key=lambda row: (-row['smoothed_success_rate'], row['median_duration_ms'] if row['median_duration_ms'] is not None else float('inf'), row['strategy']))
    result = {'schema': 'runtime-discovery-history/v1', 'target': target, 'observations': [],
              'strategy_statistics': stats, 'omitted': len(rows), 'execution_authority': False,
              'notice': 'Scoped observations only. A denied or incompatible result never authorizes bypass; transient results expire quickly.'}
    for row in rows:
        proposed = {**result, 'observations': result['observations'] + [row], 'omitted': result['omitted'] - 1}
        try:
            bounded(proposed, budget)
        except RuntimeFault as exc:
            if exc.code != 'BUDGET_EXCEEDED':
                raise
            break
        result = proposed
    return bounded(result, budget)
