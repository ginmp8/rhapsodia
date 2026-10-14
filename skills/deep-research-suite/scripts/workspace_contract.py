#!/usr/bin/env python3
"""Dependency-free, fail-closed parser for Deep Research Suite's documented YAML subset.

This is intentionally NOT a general YAML loader: unrecognized nested structures,
anchors and multiline values are rejected rather than silently truncated.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

KEY = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*)|\s*)$")
INLINE = re.compile(r"^-\s*\{(.*)\}$")
ITEM_ID = re.compile(r"^[a-zA-Z0-9][\w.-]{0,127}$", flags=re.ASCII)


def _strip_comment(value: str) -> str:
    quote = None
    escaped = False
    for i, ch in enumerate(value):
        if escaped:
            escaped = False
        elif quote == '"' and ch == "\\":
            escaped = True
        elif ch in ("'", '"'):
            if quote is None:
                quote = ch
            elif quote == ch:
                quote = None
        elif ch == '#' and quote is None and (i == 0 or value[i - 1].isspace()):
            return value[:i].rstrip()
    return value


def clean_scalar(value: str) -> str:
    value = _strip_comment(value.strip()).strip()
    if value in {'|', '>', '|-', '>-', '---', '...'} or value.startswith(('&', '*', '!')):
        raise ValueError('unsupported YAML construct; use documented scalar subset')
    if not value:
        return ''
    if value[0] in ('"', "'"):
        if len(value) < 2 or value[-1] != value[0]:
            raise ValueError('unbalanced quoted scalar')
        if value[0] == "'":
            return value[1:-1].replace("''", "'")
        # Support the useful, safe subset of YAML double-quoted escapes.
        import json
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f'invalid quoted scalar: {exc}') from exc
    if value[0] in '[{' and value not in ('[]', '{}'):
        raise ValueError('nested YAML collections are not supported')
    return value


def parse_bool(value: str) -> bool | None:
    value = clean_scalar(value)
    return {'true': True, 'false': False}.get(value.lower())


def parse_int(value: str) -> int | None:
    try:
        return int(clean_scalar(value))
    except ValueError:
        return None


def _lines(path: Path):
    for no, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        if '\t' in raw[:len(raw) - len(raw.lstrip())]:
            raise ValueError(f'{path.name}:{no}: tabs cannot indent YAML')
        stripped = raw.strip()
        if not stripped or stripped.startswith('#'):
            continue
        level = len(raw) - len(raw.lstrip(' '))
        yield no, level, _strip_comment(raw[level:]).rstrip()


def _kv(text: str, context: str) -> tuple[str, str]:
    m = KEY.match(text)
    if not m:
        raise ValueError(f'{context}: expected a key: scalar')
    return m.group(1), clean_scalar(m.group(2) or '')


def _inline_pairs(body: str) -> dict[str, Any]:
    parts: list[str] = []
    start = 0
    quote = None
    escaped = False
    for index, ch in enumerate(body):
        if escaped:
            escaped = False
        elif ch == '\\' and quote == '"':
            escaped = True
        elif ch in ('"', "'"):
            if quote is None:
                quote = ch
            elif quote == ch:
                quote = None
        elif ch == ',' and quote is None:
            parts.append(body[start:index].strip())
            start = index + 1
    if quote is not None:
        raise ValueError('unclosed quote in inline field')
    parts.append(body[start:].strip())
    result: dict[str, Any] = {}
    for part in parts:
        key, value = _kv(part, 'inline field')
        if key in result:
            raise ValueError(f'duplicate inline key: {key}')
        result[key] = value
    return result


def load_outline(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {'topic': None, 'output_language': None,
                            'items': [], 'execution': {}, 'research': {}, 'schema_version': None}
    section = None
    current_item: dict[str, Any] | None = None
    for no, level, content in _lines(path):
        context = f'{path.name}:{no}'
        if level == 0:
            key, value = _kv(content, context)
            if key in {'items', 'execution', 'research'}:
                if value:
                    raise ValueError(f'{context}: {key} requires a mapping/list block')
                section = key
                current_item = None
            elif key in {'topic', 'output_language', 'schema_version'}:
                data[key] = value
                section = None
            else:
                # Preserve simple legacy metadata rather than dropping it.
                data[key] = value
                section = None
            continue
        if section == 'items':
            if level == 2 and content.startswith('- '):
                key, value = _kv(content[2:], context)
                if key != 'name':
                    raise ValueError(f'{context}: each item must begin with - name:')
                current_item = {'name': value}
                data['items'].append(current_item)
            elif level == 4 and current_item is not None:
                key, value = _kv(content, context)
                if key in current_item:
                    raise ValueError(f'{context}: duplicate item property {key}')
                current_item[key] = value
            else:
                raise ValueError(f'{context}: unsupported items indentation/structure')
        elif section in ('execution', 'research') and level == 2:
            key, value = _kv(content, context)
            dest = data[section]
            if key in dest:
                raise ValueError(f'{context}: duplicate {section}.{key}')
            if section == 'execution' and key in ('batch_size', 'items_per_agent'):
                value = parse_int(value) if parse_int(value) is not None else value
            dest[key] = value
        else:
            raise ValueError(f'{context}: unsupported indentation/section')
    return data


def load_fields(path: Path) -> dict[str, Any]:
    categories: list[dict[str, Any]] = []
    by_category: dict[str, list[dict[str, Any]]] = {}
    current_category: str | None = None
    current_field: dict[str, Any] | None = None
    in_fields = False
    for no, level, content in _lines(path):
        context = f'{path.name}:{no}'
        if level == 0:
            key, value = _kv(content, context)
            if key == 'fields':
                if value:
                    raise ValueError(f'{context}: fields must contain category blocks')
                in_fields = True
            elif key == 'uncertain':
                if value != '[]':
                    raise ValueError(f'{context}: fields.uncertain must be []')
                in_fields = False
            else:
                raise ValueError(f'{context}: unsupported top-level key {key}')
            continue
        if not in_fields:
            raise ValueError(f'{context}: unexpected nested content')
        if level == 2:
            if not content.endswith(':'):
                raise ValueError(f'{context}: expected category name:')
            current_category = content[:-1].strip()
            if not current_category or current_category in by_category:
                raise ValueError(f'{context}: missing or duplicate category')
            by_category[current_category] = []
            categories.append({'name': current_category, 'fields': by_category[current_category]})
            current_field = None
        elif level == 4 and content.startswith('- '):
            if current_category is None:
                raise ValueError(f'{context}: field without category')
            match = INLINE.match(content)
            if match:
                current_field = _inline_pairs(match.group(1))
            else:
                key, value = _kv(content[2:], context)
                if key != 'name':
                    raise ValueError(f'{context}: field must start with - name:')
                current_field = {'name': value}
            by_category[current_category].append(current_field)
        elif level == 6 and current_field is not None:
            key, value = _kv(content, context)
            if key in current_field:
                raise ValueError(f'{context}: duplicate field property {key}')
            current_field[key] = value
        else:
            raise ValueError(f'{context}: unsupported fields indentation/structure')
    fields = [field for category in categories for field in category['fields']]
    if not fields:
        raise ValueError('fields.yaml contains no field definitions')
    names = [str(field.get('name', '')).strip() for field in fields]
    if any(not name for name in names):
        raise ValueError('fields.yaml contains empty field name')
    if len(set(names)) != len(names):
        raise ValueError('fields.yaml contains duplicate field names')
    for field in fields:
        if 'required' in field:
            required = parse_bool(str(field['required']))
            if required is None:
                raise ValueError(f'invalid required for field {field["name"]}')
            field['required'] = required
    # New files default to required=True unless explicitly false; previously
    # an unrelated required:false silently made other fields optional.
    required = {field['name'] for field in fields if field.get('required', True)}
    return {'categories': categories, 'fields': fields, 'names': set(names),
            'required': required, 'explicit_required': any('required' in f for f in fields)}


def filesystem_slug(name: str) -> str:
    value = re.sub(r'[^\w\s-]', '', str(name), flags=re.UNICODE)
    value = re.sub(r'[\s-]+', '_', value).strip('_')
    return value or 'item'


def item_slug(item: dict[str, Any]) -> str:
    identifier = item.get('id')
    if identifier:
        if not isinstance(identifier, str) or not ITEM_ID.fullmatch(identifier):
            raise ValueError('item.id must be an ASCII alphanumeric/underscore/dash/dot identifier')
        return identifier
    name = str(item.get('name', ''))
    return filesystem_slug(name)[:80] + '_' + hashlib.sha256(name.casefold().encode('utf-8')).hexdigest()[:10]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
