"""MCP 2026-07-28 stateless stdio adapter; no legacy session mutation."""
from __future__ import annotations
from . import VERSION
from .common import RuntimeFault, canonical
from .query import execute_query

PROTOCOL = '2026-07-28'
VERSION_KEY = 'io.modelcontextprotocol/protocolVersion'
CAPS_KEY = 'io.modelcontextprotocol/clientCapabilities'


def selected(method, params):
    meta = params.get('_meta')
    return method == 'server/discover' or isinstance(meta, dict) and VERSION_KEY in meta


def handle(store, id, method, params, tool, legacy_protocols):
    from .mcp import failure
    meta = params.get('_meta')
    if not isinstance(meta, dict) or not isinstance(meta.get(VERSION_KEY), str) or not isinstance(meta.get(CAPS_KEY), dict):
        return failure(id, -32602, 'Modern requests require protocolVersion and clientCapabilities in _meta')
    version = meta[VERSION_KEY]
    if version != PROTOCOL:
        result = failure(id, -32022, 'Unsupported protocol version')
        result['error']['data'] = {'supported': [PROTOCOL, *legacy_protocols], 'requested': version}
        return result
    if method in {'server/discover', 'ping'}:
        if set(params) - {'_meta'}:
            return failure(id, -32602, 'Unexpected body parameters')
        if method == 'ping':
            result = {'resultType': 'complete'}
        else:
            result = {'resultType': 'complete', 'supportedVersions': [PROTOCOL, *legacy_protocols],
                      'capabilities': {'tools': {}},
                      '_meta': {'io.modelcontextprotocol/serverInfo': {'name': 'rhapsodia-runtime', 'version': VERSION}},
                      'ttlMs': 60000, 'cacheScope': 'private'}
    elif method == 'tools/list':
        if set(params) - {'_meta', 'cursor'} or params.get('cursor') not in (None, ''):
            return failure(id, -32602, 'The fixed tool catalog has no continuation cursor')
        result = {'resultType': 'complete', 'tools': [tool], 'ttlMs': 60000, 'cacheScope': 'private'}
    elif method == 'tools/call':
        if set(params) - {'_meta', 'name', 'arguments'} or params.get('name') != 'runtime_query' or not isinstance(params.get('arguments'), dict):
            return failure(id, -32602, 'Unknown tool or invalid arguments')
        try:
            data, is_error = execute_query(store, params['arguments']), False
        except RuntimeFault as exc:
            data, is_error = exc.result(), True
        except (OSError, UnicodeError):
            data, is_error = RuntimeFault('IO_ERROR', 'Local resource unavailable.', 3).result(), True
        result = {'resultType': 'complete', 'content': [{'type': 'text', 'text': canonical(data).decode('utf-8').rstrip('\n')}],
                  'structuredContent': data, 'isError': is_error}
    else:
        return failure(id, -32601, 'Method not found')
    return {'jsonrpc': '2.0', 'id': id, 'result': result}
