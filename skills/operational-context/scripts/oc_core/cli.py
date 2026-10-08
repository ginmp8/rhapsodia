"""One JSON request/result per explicit invocation; no implicit mutation on reads."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from .common import RuntimeFault, canonical, read_bytes, strict_json
from .store import Cache

COMMANDS=('describe','output-card','pack','pack-save','pack-verify','pack-use','prefix','index','query','action-key','action-store','action-lookup',
          'usage','metric-record','metric-summary','metrics-compare','delegate','retrieval','lease','federation-export','federation-import','graph-export')

class Parser(argparse.ArgumentParser):
    def error(self,message):raise RuntimeFault('INVALID_INPUT',message)


def dispatch(cache, command: str, data: dict) -> dict:
    if command=='describe':
        from .describe import describe
        return describe(data)
    if command=='output-card':
        from .output import card
        return card(cache,data)
    if command in {'pack','pack-save','pack-verify','pack-use','prefix'}:
        from .context import build, verify, prefix
        if command=='prefix':return prefix(cache,data)
        if command=='pack-verify':return verify(cache,data)
        if command=='pack-use':
            from .common import fields
            fields(data,{'id'})
            pack=cache.get('pack',data['id']);check=verify(cache,pack)
            if check['status']!='current':raise RuntimeFault('STALE_PACK','Pack source pins changed; rebuild from live sources.')
            return pack
        result=build(cache,data)
        if command=='pack-save':return {'status':'stored','id':cache.put('pack',result),'pack_id':result['pack_id']}
        return result
    if command in {'index','query'}:
        from .registry import publish, query
        return publish(cache,data) if command=='index' else query(cache,data)
    if command.startswith('action-'):
        from .actions import action_key, store_result, lookup
        return {'action-key':action_key,'action-store':store_result,'action-lookup':lookup}[command](cache,data)
    if command in {'usage','metric-record','metric-summary','metrics-compare'}:
        from .metrics import normalize_usage, record, compare, summary
        if command=='usage':
            from .common import fields
            fields(data,{'provider','usage'})
            return normalize_usage(data['provider'],data['usage'])
        if command=='metric-record':return record(cache,data)
        if command=='metric-summary':return summary(cache,data)
        return compare(data)
    if command in {'delegate','retrieval'}:
        from .policy import decide, retrieval
        return decide(data) if command=='delegate' else retrieval(data)
    if command in {'lease','federation-export','federation-import','graph-export'}:
        from .sharing import lease, export_refs, import_refs, graph
        return {'lease':lease,'federation-export':export_refs,'federation-import':import_refs,'graph-export':graph}[command](cache,data)
    raise RuntimeFault('INVALID_INPUT','Unknown operational command.')


def main(argv=None):
    try:
        parser=Parser(description=__doc__)
        parser.add_argument('--workspace',type=Path,default=Path.cwd())
        parser.add_argument('command',choices=COMMANDS)
        parser.add_argument('--input',type=Path)
        args=parser.parse_args(argv)
        if args.input is not None and args.input.is_symlink():raise RuntimeFault('UNSAFE_PATH','Input cannot be a symbolic link.')
        raw=read_bytes(args.input,4*1024*1024) if args.input else sys.stdin.buffer.read(4*1024*1024+1)
        data=strict_json(raw,4*1024*1024)
        result=dispatch(Cache(args.workspace),args.command,data)
        output=canonical(result)
        if len(output)>4*1024*1024:raise RuntimeFault('OUTPUT_TOO_LARGE','Request a narrower bounded result.')
        sys.stdout.buffer.write(output)
        return 0
    except RuntimeFault as exc:
        sys.stdout.buffer.write(canonical(exc.result()));return exc.exit_code
    except (OSError,UnicodeError):
        fault=RuntimeFault('IO_ERROR','Selected local data could not be accessed; no automatic retry or remote action.',3)
        sys.stdout.buffer.write(canonical(fault.result()));return fault.exit_code

if __name__=='__main__':raise SystemExit(main())
