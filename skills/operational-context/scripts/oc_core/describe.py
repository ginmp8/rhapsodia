"""Progressive discovery of this package's static command contracts."""
from pathlib import Path
from .common import RuntimeFault, fields, read_bytes, strict_json


def describe(request):
    fields(request, set(), {'command'})
    path = Path(__file__).resolve().parents[2] / 'contracts' / 'commands.json'
    catalog = strict_json(read_bytes(path, 1024 * 1024), 1024 * 1024)
    if 'command' not in request:
        return {'schema': catalog['schema'], 'commands': {k: v['effect'] for k, v in catalog['commands'].items()}}
    name = request['command']
    if not isinstance(name, str) or name not in catalog['commands']:
        raise RuntimeFault('INVALID_INPUT', 'Select one known command from the inventory.')
    return {'schema': catalog['schema'], 'command': name, **catalog['commands'][name]}
