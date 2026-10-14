#!/usr/bin/env python3
"""Fail-closed workspace validation with stable item identity and scope checks."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from workspace_contract import ITEM_ID, item_slug, load_fields, load_outline


def validate(outline_path: Path, fields_path: Path) -> dict:
    spec = load_outline(outline_path)
    schema = load_fields(fields_path)
    errors, warnings = [], []
    if not spec['topic'] or not str(spec['topic']).strip():
        errors.append('outline.topic must be nonempty')
    if not spec['items']:
        errors.append('outline.items must contain at least one item')
    names = [str(x.get('name', '')).strip() for x in spec['items']]
    if any(not x for x in names):
        errors.append('every item requires a nonempty name')
    if len(set(x.casefold() for x in names)) != len(names):
        errors.append('duplicate item names (case-insensitive)')
    identifiers = []
    for item in spec['items']:
        try:
            identifiers.append(item_slug(item))
        except ValueError as exc:
            errors.append(str(exc))
    if len(set(x.casefold() for x in identifiers)) != len(identifiers):
        errors.append('duplicate item file identities')
    execution = spec['execution']
    for key, default in (('batch_size', 4), ('items_per_agent', 1)):
        value = execution.get(key, default)
        if not isinstance(value, int) or not 1 <= value <= 1024:
            errors.append(f'execution.{key} must be an integer 1..1024')
    directory = execution.get('output_dir', './results')
    if not isinstance(directory, str) or not directory.strip():
        errors.append('execution.output_dir must be a nonempty path')
    else:
        output = Path(directory)
        if not output.is_absolute():
            base = outline_path.resolve().parent
            effective = (base / output).resolve()
            if not effective.is_relative_to(base):
                errors.append('relative execution.output_dir cannot escape the workspace')
        else:
            warnings.append('absolute output_dir requires explicit user authorization')
    for field in schema['fields']:
        if field.get('detail_level') not in ('brief', 'moderate', 'detailed'):
            errors.append(f'field {field["name"]} needs detail_level brief/moderate/detailed')
        if not str(field.get('description') or '').strip():
            warnings.append(f'field {field["name"]} lacks description')
    return {'valid': not errors, 'topic': spec['topic'], 'items': len(spec['items']),
            'fields': len(schema['fields']), 'required_fields': len(schema['required']),
            'errors': errors, 'warnings': warnings}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--outline', required=True)
    p.add_argument('--fields', required=True)
    a = p.parse_args()
    try:
        result = validate(Path(a.outline), Path(a.fields))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['valid'] else 1
    except Exception as exc:
        print(json.dumps({'valid': False, 'errors': [str(exc)], 'warnings': []}, ensure_ascii=False, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
