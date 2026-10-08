"""Compact tool-output cards with an exact local recovery reference."""
from __future__ import annotations
import hashlib
from .common import RuntimeFault, bounded, confined, fields, number, read_bytes


def card(cache, request):
    fields(request, {'path', 'observed_status'}, {'budget_bytes', 'include_excerpt', 'approved_content', 'tail_lines'})
    if request['observed_status'] not in ('passed', 'failed', 'blocked', 'not-run', 'unknown'):
        raise RuntimeFault('INVALID_INPUT', 'Output cards report a caller-observed status, not a verdict.')
    include = request.get('include_excerpt', False)
    if type(include) is not bool or include and request.get('approved_content') is not True:
        raise RuntimeFault('CONTENT_APPROVAL_REQUIRED', 'Log excerpts require explicit content approval after source-side redaction.')
    raw = read_bytes(confined(cache.workspace, request['path']), 8 * 1024 * 1024)
    result = {'schema': 'tool-output-card/v1', 'path': request['path'], 'sha256': hashlib.sha256(raw).hexdigest(),
              'bytes': len(raw), 'observed_status': request['observed_status'], 'content_omitted': True,
              'source_mutated': False, 'domain_approval': False}
    budget = number(request.get('budget_bytes', 4096), 256, 65536)
    if include:
        count = number(request.get('tail_lines', 20), 1, 200)
        try:
            lines = raw.decode('utf-8').splitlines(keepends=True)
        except UnicodeError as exc:
            raise RuntimeFault('INVALID_INPUT', 'Select a UTF-8 log or keep a reference-only card.') from exc
        selected = lines[-count:]
        result.update(excerpt=''.join(selected), start_line=max(1, len(lines)-len(selected)+1), end_line=len(lines),
                      content_omitted=len(selected)<len(lines))
        while selected:
            try:
                return bounded(result, budget)
            except RuntimeFault as exc:
                if exc.code != 'BUDGET_EXCEEDED':
                    raise
            selected = selected[1:]
            result.update(excerpt=''.join(selected), start_line=len(lines)-len(selected)+1, content_omitted=True)
        result.pop('excerpt', None); result.pop('start_line', None); result.pop('end_line', None)
    return bounded(result, budget)
