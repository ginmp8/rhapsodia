#!/usr/bin/env python3
"""Original, stdlib-only behavioral evidence and differential testing utility.

This script never runs target code. Inputs are NDJSON observations from already
captured, explicitly authorized experiments. Comparison is exact by default.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import math
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

MAX_LINE = 2 * 1024 * 1024
MAX_CORPUS_BYTES = 32 * 1024 * 1024
MAX_DEPTH = 128
MAX_CASES = 20_000
MAX_DIFFS = 200
MAX_PROBES = 300


class DataError(ValueError):
    pass


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DataError(f'duplicate JSON key: {key!r}')
        obj[key] = value
    return obj


def _json_value_check(value: Any, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise DataError(f'JSON nesting depth exceeds {MAX_DEPTH}')
    if isinstance(value, float) and not math.isfinite(value):
        raise DataError('nonfinite JSON number is unsupported')
    if isinstance(value, str) and any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise DataError('unpaired Unicode surrogate is unsupported')
    if isinstance(value, dict):
        for key, item in value.items():
            _json_value_check(key, depth + 1)
            _json_value_check(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _json_value_check(item, depth + 1)


def strict_json(text: str) -> Any:
    if len(text.encode('utf-8')) > MAX_LINE:
        raise DataError(f'JSON exceeds {MAX_LINE} byte limit')
    try:
        value = json.loads(text, object_pairs_hook=_no_duplicate_keys,
                           parse_constant=lambda constant: (_ for _ in ()).throw(DataError(f'nonfinite JSON constant: {constant}')))
        _json_value_check(value)
        return value
    except RecursionError as exc:
        raise DataError('JSON nesting exceeds available parser depth') from exc



def _validate_v2_bytes(value: Any, where: str, depth: int = 0) -> None:
    """Validate only the opted-in bytes tag; ordinary user dictionaries remain data."""
    if depth > MAX_DEPTH:
        raise DataError(f'{where}: typed value depth exceeded')
    if isinstance(value, dict):
        if value.get('$type') == 'bytes':
            if set(value) != {'$type', 'base64'} or not isinstance(value.get('base64'), str):
                raise DataError(f'{where}: bytes requires exactly $type and base64')
            encoded = value['base64']
            try:
                decoded = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise DataError(f'{where}: invalid base64') from exc
            if base64.b64encode(decoded).decode('ascii') != encoded:
                raise DataError(f'{where}: noncanonical base64')
        elif '$type' in value:
            kind=value['$type']
            if kind=='undefined':
                if set(value)!={'$type'}:raise DataError(f'{where}: undefined must have no payload')
            elif kind=='bigint':
                val=value.get('decimal')
                if set(value)!={'$type','decimal'} or not isinstance(val,str) or not re.fullmatch(r'-?(?:0|[1-9][0-9]{0,1023})',val) or val=='-0':
                    raise DataError(f'{where}: noncanonical bigint')
            elif kind=='decimal':
                val=value.get('value')
                if (set(value)!={'$type','value'} or not isinstance(val,str) or len(val)>1024 or
                    not re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]{1,4})?',val)):
                    raise DataError(f'{where}: invalid decimal')
                try:
                    if not Decimal(val).is_finite():raise DataError(f'{where}: nonfinite decimal')
                except InvalidOperation as exc:raise DataError(f'{where}: invalid decimal') from exc
            elif kind=='float-special':
                if set(value)!={'$type','value'} or value.get('value') not in ('NaN','Infinity','-Infinity','-0'):
                    raise DataError(f'{where}: invalid float-special')
            elif kind=='datetime-offset':
                val=value.get('iso8601')
                if set(value)!={'$type','iso8601'} or not isinstance(val,str) or len(val)>128:
                    raise DataError(f'{where}: datetime-offset requires ISO string')
                try:
                    d=datetime.fromisoformat(val)
                    if d.utcoffset() is None:raise ValueError('offset missing')
                except ValueError as exc:raise DataError(f'{where}: ISO datetime requires offset') from exc
            else:raise DataError(f'{where}: unknown reserved typed value')
        else:
            for key, item in value.items():
                _validate_v2_bytes(item, f'{where}/{key}', depth + 1)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_v2_bytes(item, f'{where}/{index}', depth + 1)


def _validate_v2_record(row: dict[str, Any], location: str) -> None:
    """Opt-in version-2 observation shape, preserving v1 corpus compatibility."""
    version = row.get('schema_version', '1.0')
    if version not in ('1.0', '2.0'):
        raise DataError(f'{location}: unsupported schema_version {version!r}')
    if version != '2.0':
        return
    observation = row['observation']
    input_data = row['input']
    actions = input_data.get('actions') if isinstance(input_data, dict) else None
    if actions is not None and (not isinstance(actions, list) or
                                any(not isinstance(item, dict) for item in actions)):
        raise DataError(f'{location}: input.actions must be a list of objects')
    if 'steps' in observation:
        steps = observation['steps']
        if not isinstance(actions, list) or not isinstance(steps, list) or len(steps) != len(actions):
            raise DataError(f'{location}: steps require one record per input action')
        for index, step in enumerate(steps):
            if (not isinstance(step, dict) or type(step.get('action_index')) is not int or
                    step['action_index'] != index or
                    not any(k in step for k in ('output', 'error', 'state', 'events', 'status', 'effects'))):
                raise DataError(f'{location}: step {index} must match action_index and record behavior')
    groups = [observation]
    if 'steps' in observation:
        groups.extend(observation['steps'])
    for index, group in enumerate(groups):
        if 'effects' not in group:
            continue
        effects = group['effects']
        if not isinstance(effects, list):
            raise DataError(f'{location}: effects at group {index} must be a list')
        for effect in effects:
            if (not isinstance(effect, dict) or
                    effect.get('kind') not in ('file', 'http', 'database', 'event', 'process', 'other') or
                    not isinstance(effect.get('operation'), str) or not 1 <= len(effect['operation']) <= 128):
                raise DataError(f'{location}: effects require recognized kind and operation')
    _validate_v2_bytes(input_data, f'{location}/input')
    _validate_v2_bytes(observation, f'{location}/observation')


def load_corpus(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        raise DataError(f'not a regular file: {path}')
    if path.stat().st_size > MAX_CORPUS_BYTES:
        raise DataError(f'corpus exceeds {MAX_CORPUS_BYTES} byte limit')
    result: dict[str, dict[str, Any]] = {}
    with path.open('rb') as fh:
        for line_no, raw in enumerate(fh, 1):
            if len(raw) > MAX_LINE:
                raise DataError(f'{path.name}:{line_no}: line exceeds limit')
            if not raw.strip():
                continue
            if len(result) >= MAX_CASES:
                raise DataError('case count exceeds limit')
            try:
                row = strict_json(raw.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError, DataError) as exc:
                raise DataError(f'{path.name}:{line_no}: invalid NDJSON: {exc}') from exc
            if not isinstance(row, dict):
                raise DataError(f'{path.name}:{line_no}: record must be object')
            case_id = row.get('id')
            if not isinstance(case_id, str) or not 1 <= len(case_id) <= 200 or '\x00' in case_id:
                raise DataError(f'{path.name}:{line_no}: id must be nonempty string <=200 characters')
            if case_id in result:
                raise DataError(f'{path.name}:{line_no}: duplicate case id {case_id!r}')
            if 'input' not in row or 'observation' not in row:
                raise DataError(f'{path.name}:{line_no}: input and observation are required')
            obs = row['observation']
            accepted_fields = ('output', 'error', 'status', 'state', 'events')
            if row.get('schema_version') == '2.0':
                accepted_fields += ('steps', 'effects')
            if not isinstance(obs, dict) or not any(x in obs for x in accepted_fields):
                raise DataError(f'{path.name}:{line_no}: observation must declare supported behavior fields')
            if 'runner_status' in row and row['runner_status'] not in ('ok', 'timeout', 'error', 'exit', 'invalid-output'):
                raise DataError(f'{path.name}:{line_no}: unknown runner_status')
            _validate_v2_record(row, f'{path.name}:{line_no}')
            result[case_id] = row
    if not result:
        raise DataError(f'{path.name}: no test cases')
    return result


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(128 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def pointer(path: tuple[str, ...]) -> str:
    return ''.join('/' + str(piece).replace('~', '~0').replace('/', '~1') for piece in path)


def differ(a: Any, b: Any, path: tuple[str, ...], output: list[dict[str, Any]],
           ignore: frozenset[str], tol: float, limit: int) -> None:
    if len(output) >= limit or pointer(path) in ignore:
        return
    if len(path) > MAX_DEPTH:
        output.append({'pointer': pointer(path), 'kind': 'depth_limit_unverified'})
        return
    # JSON true and 1 must never match simply because Python bool is int.
    if type(a) is not type(b):
        # JSON numerics may change int/float representation across runtimes.
        if not (tol > 0 and type(a) in (float, int) and type(b) in (float, int) and
                math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol):
            output.append({'pointer': pointer(path), 'kind': 'type_mismatch',
                           'reference_type': type(a).__name__, 'candidate_type': type(b).__name__})
        return
    if isinstance(a, dict):
        for key in sorted(a.keys() | b.keys()):
            p = path + (key,)
            if pointer(p) in ignore:
                continue
            if key not in a or key not in b:
                output.append({'pointer': pointer(p), 'kind': 'missing_in_reference' if key not in a else 'missing_in_candidate'})
            else:
                differ(a[key], b[key], p, output, ignore, tol, limit)
            if len(output) >= limit:
                return
    elif isinstance(a, list):
        if len(a) != len(b):
            output.append({'pointer': pointer(path), 'kind': 'array_length', 'reference_length': len(a), 'candidate_length': len(b)})
        for index in range(min(len(a), len(b))):
            differ(a[index], b[index], path + (str(index),), output, ignore, tol, limit)
            if len(output) >= limit:
                return
    elif (isinstance(a, float) and tol > 0 and math.isfinite(a) and math.isfinite(b)
          and abs(a - b) <= tol):
        return
    elif a != b:
        output.append({'pointer': pointer(path), 'kind': 'value_mismatch'})


def compare(ref_file: Path, cand_file: Path, *, ignore: frozenset[str] = frozenset(),
            tolerance: float = 0., limit: int = MAX_DIFFS) -> dict[str, Any]:
    if tolerance < 0 or not math.isfinite(tolerance):
        raise DataError('tolerance must be finite and nonnegative')
    if any(not p.startswith('/observation/') for p in ignore):
        raise DataError('ignores must be exact JSON pointers below /observation/ only')
    if ref_file.resolve() == cand_file.resolve():
        raise DataError('reference and candidate must be distinct files')
    ref = load_corpus(ref_file)
    cand = load_corpus(cand_file)
    failures: list[dict[str, Any]] = []
    counts = {'matched': 0, 'mismatched': 0, 'missing_reference': 0, 'missing_candidate': 0, 'unverified': 0}
    allids = sorted(ref.keys() | cand.keys())
    for cid in allids:
        if cid not in ref:
            counts['missing_reference'] += 1
            failures.append({'id': cid, 'class': 'missing_reference'})
        elif cid not in cand:
            counts['missing_candidate'] += 1
            failures.append({'id': cid, 'class': 'missing_candidate'})
        elif ref[cid].get('runner_status', 'ok') != 'ok' or cand[cid].get('runner_status', 'ok') != 'ok':
            counts['unverified'] += 1
            failures.append({'id': cid, 'class': 'unverified_runner_failure'})
        else:
            changes: list[dict[str, Any]] = []
            differ(ref[cid]['input'], cand[cid]['input'], ('input',), changes, ignore, 0.0, limit)
            differ(ref[cid]['observation'], cand[cid]['observation'], ('observation',), changes, ignore, tolerance, limit)
            if changes:
                counts['mismatched'] += 1
                failures.append({'id': cid, 'class': 'differential_mismatch', 'diffs': changes[:limit],
                                 'truncated': len(changes) >= limit})
            else:
                counts['matched'] += 1
    return {'schema_version': '1.0', 'verdict': 'PASS_OBSERVED_CASES' if counts['matched'] == len(allids) else 'DIVERGENCE_OR_INCOMPLETE',
            'reference': {'sha256': digest(ref_file), 'cases': len(ref)},
            'candidate': {'sha256': digest(cand_file), 'cases': len(cand)},
            'comparisons': {'exact_pointer_exclusions': sorted(ignore), 'numeric_absolute_tolerance': tolerance,
                            'array_order_matters': True, 'json_type_matters': True, 'inputs_exact': True},
            'counts': counts, 'total_ids': len(allids), 'findings': failures[:limit],
            'findings_truncated': len(failures) > limit,
            'conclusion_scope': 'Only supplied finite observations; not universal semantic equivalence.'}


def study(path: Path) -> dict[str, Any]:
    rows = load_corpus(path)
    probes = []
    features: dict[str, int] = {'has_error': 0, 'has_state': 0, 'has_events': 0, 'has_output': 0, 'has_status': 0, 'has_steps': 0, 'has_effects': 0}
    for cid, row in sorted(rows.items()):
        obs = row['observation']
        for key in ('error', 'state', 'events', 'output', 'status', 'steps', 'effects'):
            features['has_' + key] += int(key in obs)
        declared_status = row.get('runner_status')
        # A value in a file, even runner_status=ok, is a claim, not proof of replay.
        provenance = ('supplied' if declared_status is None else
                      'claimed_runtime' if declared_status == 'ok' else 'unverified')
        probes.append({'id': cid, 'kind': row.get('kind', 'recorded'), 'oracle': 'recorded',
                       'behavior_fields': sorted(obs), 'evidence': f'{path.name}#id={cid}',
                       'status': provenance, 'schema_version': row.get('schema_version', '1.0')})
    return {'schema_version': '1.0', 'corpus_sha256': digest(path), 'count': len(rows),
            'features': features, 'obligations': probes,
            'unobserved': ['unsampled inputs', 'unobserved state transitions', 'environment-specific behavior',
                           'concurrency/scheduling', 'non-JSON boundary semantics'],
            'note': 'Captures supplied observations and claimed runtime status, not authenticated execution or functional correctness.'}


def proposals(path: Path, max_probes: int = 60) -> dict[str, Any]:
    rows = load_corpus(path)
    proposals_out = []
    # Never propose an input already present in the trusted/supplied source corpus.
    seen = {hashlib.sha256(json.dumps(row['input'], sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()
            for row in rows.values()}
    def add(base: str, key: str, input_data: Any, hypothesis: str):
        if len(proposals_out) >= max_probes:
            return
        serialized = json.dumps(input_data,sort_keys=True,separators=(',', ':'), ensure_ascii=False)
        ident = hashlib.sha256(serialized.encode()).hexdigest()
        if ident in seen:
            return
        seen.add(ident)
        proposals_out.append({'based_on': base, 'field': key, 'input': input_data,
                              'hypothesis': hypothesis, 'status': 'not_observed'})
    for cid, row in sorted(rows.items()):
        value = row['input']
        if isinstance(value, dict):
            actions = value.get('actions')
            if isinstance(actions, list) and all(isinstance(a, dict) for a in actions):
                def sequence_probe(new_actions: list[dict[str, Any]], why: str) -> None:
                    edited = dict(value)
                    edited['actions'] = new_actions
                    add(cid, 'actions', edited, why)
                sequence_probe([], 'sequence empty actions')
                if len(actions) >= 2:
                    sequence_probe(actions[:max(1, len(actions)//2)], 'sequence prefix truncation')
                    sequence_probe(actions[1:], 'sequence remove first action')
                    sequence_probe(actions + [actions[-1]], 'sequence replay last action')
                    sequence_probe(actions[:1] + actions, 'sequence duplicate first action')
                    sequence_probe([actions[1],actions[0]] + actions[2:], 'sequence swap adjacent actions')
                elif actions:
                    sequence_probe(actions + actions, 'sequence duplicate single action')
            for key in sorted(value):
                current = value[key]
                choices: list[tuple[Any,str]] = [(None,'nullable/absent value boundary')]
                if isinstance(current, bool):
                    choices.append((not current, 'boolean alternative'))
                elif type(current) in (int, float):
                    choices += [(0,'numeric zero'),(-1,'negative boundary'),(1,'positive boundary')]
                elif isinstance(current, str):
                    choices += [('', 'empty string'), (current + ' ', 'trailing whitespace')]
                elif isinstance(current, list):
                    choices += [([], 'empty list')]
                elif isinstance(current, dict):
                    choices += [({},'empty object')]
                for replacement, why in choices:
                    modified = dict(value); modified[key] = replacement
                    add(cid, key, modified, why)
                modified = dict(value); modified.pop(key)
                add(cid,key,modified,'missing property')
        if len(proposals_out) >= max_probes:
            break
    return {'schema_version': '1.0', 'source_sha256': digest(path), 'proposals': proposals_out,
            'notice': 'Generated hypotheses only. They are not observations and must not be used as an oracle.'}


def save_output(data: Any, output: Path | None) -> None:
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if output is None:
        print(content, end='')
        return
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.re-', dir=output.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, output)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Original offline behavioral evidence comparison (no target execution)')
    commands = ap.add_subparsers(dest='mode', required=True)
    diff = commands.add_parser('compare')
    diff.add_argument('reference', type=Path)
    diff.add_argument('candidate', type=Path)
    diff.add_argument('--ignore-pointer', action='append', default=[])
    diff.add_argument('--numeric-absolute-tolerance', type=float, default=0.)
    diff.add_argument('--limit', type=int, default=MAX_DIFFS)
    ch = commands.add_parser('characterize')
    ch.add_argument('corpus', type=Path)
    sug = commands.add_parser('suggest')
    sug.add_argument('corpus', type=Path)
    sug.add_argument('--max-probes', type=int, default=60)
    for command in (diff, ch, sug):
        command.add_argument('-o', '--output', type=Path)
    args = ap.parse_args(argv)
    try:
        if args.mode == 'compare':
            if not 1 <= args.limit <= 5000:
                raise DataError('--limit must be 1..5000')
            result = compare(args.reference, args.candidate,
                             ignore=frozenset(args.ignore_pointer),
                             tolerance=args.numeric_absolute_tolerance, limit=args.limit)
        elif args.mode == 'characterize':
            result = study(args.corpus)
        else:
            if not 1 <= args.max_probes <= MAX_PROBES:
                raise DataError('--max-probes out of bounds')
            result = proposals(args.corpus, args.max_probes)
        if args.output is not None:
            protected = ([args.reference, args.candidate] if args.mode == 'compare' else [args.corpus])
            if args.output.resolve() in {p.resolve() for p in protected}:
                raise DataError('output cannot overwrite a source corpus')
        save_output(result, args.output)
        return 0 if args.mode != 'compare' or result['verdict'] == 'PASS_OBSERVED_CASES' else 1
    except (DataError, OSError, ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
