"""Bounded delta transport over immutable complete v1 handoffs.

No domain state or permission is patched. Complete receipts are retained locally;
missing acknowledged parents fall back to full transport at the sender.
"""
from __future__ import annotations
from .common import HASH_RE, RuntimeFault, canonical, confined, fields, number, read_bytes, sha, strict_json
from .handoff import validate_receipt


def _load(store, key):
    if not isinstance(key, str) or not HASH_RE.fullmatch(key):
        raise RuntimeFault('INVALID_INPUT', 'Expected a content-addressed handoff ID.')
    receipt = validate_receipt(strict_json(read_bytes(confined(store.root, 'handoffs/' + key + '.json'), 65536)))
    if receipt['handoff_id'] != key:
        raise RuntimeFault('INVALID_RECEIPT', 'Stored receipt identity differs from its path.', 3)
    return receipt


def _seal(value):
    return {**value, 'transport_id': sha(value)}


def make(store, request):
    fields(request, {'target_id'}, {'parent_id', 'receiver_parent_id', 'parent_depth'})
    target = _load(store, request['target_id'])
    depth = number(request.get('parent_depth', 0), 0, 8)
    full = _seal({'schema': 'runtime-handoff-transport/v1', 'mode': 'full', 'depth': 0, 'receipt': target})
    if depth >= 8 or request.get('receiver_parent_id') != request.get('parent_id') or not request.get('parent_id'):
        return full
    try:
        parent = _load(store, request['parent_id'])
    except (OSError, RuntimeFault):
        return full
    if parent['scope'] != target['scope'] or parent['task_id'] != target['task_id']:
        return full
    changed = {k: v for k, v in target.items() if k != 'handoff_id' and parent.get(k) != v}
    removed = sorted(k for k in parent if k != 'handoff_id' and k not in target)
    transport = _seal({'schema': 'runtime-handoff-transport/v1', 'mode': 'delta', 'depth': depth + 1,
                       'parent_id': parent['handoff_id'], 'target_id': target['handoff_id'],
                       'changed': changed, 'removed': removed})
    return transport if len(canonical(transport)) < len(canonical(full)) else full


def apply(store, request):
    fields(request, {'transport'}, {'parent_id'})
    transport = request['transport']
    if not isinstance(transport, dict):
        raise RuntimeFault('INVALID_INPUT', 'Expected a handoff transport object.')
    common = {'schema', 'mode', 'depth', 'transport_id'}
    if transport.get('mode') == 'full':
        fields(transport, common | {'receipt'})
    elif transport.get('mode') == 'delta':
        fields(transport, common | {'parent_id', 'target_id', 'changed', 'removed'})
    else:
        raise RuntimeFault('INVALID_RECEIPT', 'Unknown handoff transport mode.', 3)
    if transport['schema'] != 'runtime-handoff-transport/v1' or sha({k:v for k,v in transport.items() if k != 'transport_id'}) != transport['transport_id']:
        raise RuntimeFault('INVALID_RECEIPT', 'Transport identity does not match its content.', 3)
    if transport['mode'] == 'full':
        if transport['depth'] != 0:
            raise RuntimeFault('INVALID_RECEIPT', 'Full receipts must reset the chain.', 3)
        receipt = validate_receipt(transport['receipt'])
    else:
        number(transport['depth'], 1, 8)
        if request.get('parent_id') != transport['parent_id']:
            raise RuntimeFault('PARENT_REQUIRED', 'Fetch the exact acknowledged parent or request a full handoff.', 3)
        parent = _load(store, transport['parent_id'])
        allowed = {'next_action', 'snapshot_id', 'pins', 'summary'}
        changed, removed = transport['changed'], transport['removed']
        if not isinstance(changed, dict) or set(changed) - allowed or not isinstance(removed, list) or any(x != 'summary' for x in removed) or len(removed) > 1 or set(removed) & changed.keys():
            raise RuntimeFault('INVALID_RECEIPT', 'Delta cannot change scope, task identity or required contract fields.', 3)
        receipt = {k:v for k,v in parent.items() if k not in removed}
        receipt.update(changed)
        receipt['handoff_id'] = transport['target_id']
        receipt = validate_receipt(receipt)
    if receipt['scope'] != store.current()[1]['scope']:
        raise RuntimeFault('REBIND_REQUIRED', 'Foreign handoffs require the explicit v1 rebind workflow.', 3)
    # Decoding is read-only. Call handoff-resume to check current pins before use.
    return receipt
