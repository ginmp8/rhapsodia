#!/usr/bin/env python3
"""Explicit opt-in, bounded NDJSON subprocess adapter for trusted programs.

NOT a sandbox. A target can still use the network, spawn children or access
files permitted by its OS account. Never execute an untrusted upload here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from behavior_lab import DataError, MAX_LINE, strict_json, save_output
from json_writer import write_exclusive
from effect_capture import snapshot, changes, CaptureError


def json_lines(path: Path, cap: int) -> list[dict[str, Any]]:
    if not path.is_file():
        raise DataError('case input file not found')
    found: list[dict[str, Any]] = []
    unique: set[str] = set()
    with path.open('rb') as fh:
        for line_no, raw in enumerate(fh, 1):
            if len(raw) > MAX_LINE:
                raise DataError(f'oversized line {line_no}')
            if not raw.strip():
                continue
            if len(found) >= cap:
                raise DataError(f'case count exceeds --max-cases={cap}')
            row = strict_json(raw.decode('utf-8'))
            if not isinstance(row, dict) or 'input' not in row or not isinstance(row.get('id'), str):
                raise DataError(f'case {line_no} needs id and input')
            if not row['id'] or len(row['id']) > 200 or row['id'] in unique:
                raise DataError(f'invalid/duplicate id at line {line_no}')
            unique.add(row['id'])
            found.append({'id': row['id'], 'input': row['input'], 'kind': row.get('kind', 'reference')})
    if not found:
        raise DataError('no inputs supplied')
    return found


def check_command(argv_file: Path) -> list[str]:
    command = strict_json(argv_file.read_text('utf-8'))
    if not isinstance(command, list) or not 1 <= len(command) <= 30:
        raise DataError('command file must contain an argv JSON array (1..30)')
    if any(not isinstance(token, str) or not token or '\x00' in token or len(token) > 4096 for token in command):
        raise DataError('invalid argv entry')
    # Avoid ambiguity with cwd or PATH injection for the executable.
    if not Path(command[0]).is_absolute():
        raise DataError('argv[0] must be an absolute executable path')
    if not Path(command[0]).is_file():
        raise DataError('argv[0] executable not found')
    return command


def run_one(command: list[str], value: Any, cwd: Path, timeout: float, output_cap: int, memory_mb: int,
            capture_fs: bool = False) -> tuple[str,dict[str,Any]]:
    payload = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8') + b'\n'
    if len(payload) > MAX_LINE:
        return 'invalid-output', {'error': {'kind': 'input_too_large'}}
    environment = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
                   'HOME': str(cwd), 'TZ':'UTC', 'TMPDIR': str(cwd), 'PYTHONDONTWRITEBYTECODE':'1'}
    def cap_resources() -> None:
        if os.name != 'posix':
            return
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(timeout)+1, math.ceil(timeout)+2))
        resource.setrlimit(resource.RLIMIT_FSIZE, (output_cap, output_cap))
        if memory_mb:
            bound=memory_mb*1024*1024
            resource.setrlimit(resource.RLIMIT_AS, (bound,bound))
    try:
        initial_files = snapshot(cwd) if capture_fs else None
    except (CaptureError, OSError) as exc:
        return 'error', {'error': {'kind': 'capture_before_failed', 'code': type(exc).__name__}}
    with tempfile.TemporaryDirectory(prefix='re-oracle-') as scratch:
        with open(Path(scratch)/'out.txt','wb') as out, open(Path(scratch)/'err.txt','wb') as err:
            try:
                proc=subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                      cwd=cwd, env=environment, shell=False, start_new_session=(os.name=='posix'),
                                      preexec_fn=cap_resources if os.name=='posix' else None)
                try:
                    proc.communicate(input=payload, timeout=timeout)
                except subprocess.TimeoutExpired:
                    if os.name=='posix':
                        os.killpg(proc.pid, signal.SIGKILL)
                    else:
                        proc.kill()
                    proc.communicate()
                    return 'timeout', {'error': {'kind':'timeout'}}
            except OSError as exc:
                return 'error', {'error': {'kind':'process_start', 'code': type(exc).__name__}}
        if proc.returncode != 0:
            return 'exit', {'error': {'kind':'nonzero_exit','code':proc.returncode}}
        stdout=Path(scratch)/'out.txt'
        if stdout.stat().st_size>output_cap:
            return 'invalid-output', {'error': {'kind':'oversized_stdout'}}
        try:
            raw=stdout.read_text('utf-8')
            if len(raw.splitlines()) != 1:
                raise DataError('expected exactly one JSON result line')
            parsed=strict_json(raw.strip())
            if not isinstance(parsed, dict) or not any(k in parsed for k in ('output','error','status','state','events','steps','effects')):
                raise DataError('protocol requires an observation object')
        except (UnicodeDecodeError, DataError, json.JSONDecodeError):
            return 'invalid-output', {'error': {'kind':'invalid_json_protocol'}}
        if capture_fs:
            try:
                final_files = snapshot(cwd)
                if not isinstance(parsed.get('effects',[]),list):
                    return 'invalid-output', {'error': {'kind': 'invalid_effects_protocol'}}
                parsed['effects'] = parsed.get('effects', []) + changes(initial_files, final_files)
            except (CaptureError, OSError) as exc:
                return 'error', {'error': {'kind': 'capture_after_failed', 'code': type(exc).__name__}}
        return 'ok', parsed


def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description='Run a preapproved trusted JSON-line oracle; NOT a sandbox')
    ap.add_argument('--cases',required=True,type=Path)
    ap.add_argument('--argv-file',required=True,type=Path)
    ap.add_argument('--cwd',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--timeout',type=float,default=3.0)
    ap.add_argument('--max-cases',type=int,default=100)
    ap.add_argument('--max-output-kb',type=int,default=256)
    ap.add_argument('--memory-mb',type=int,default=512)
    ap.add_argument('--execute-authorized',action='store_true')
    ap.add_argument('--capture-fs', action='store_true', help='Trusted-only hash/diff of cwd regular files; NOT isolation')
    args=ap.parse_args(argv)
    try:
        if not args.execute_authorized:
            raise DataError('Refusing execution: user must authorize target execution and --execute-authorized must be set')
        if not 0.1<=args.timeout<=30 or not 1<=args.max_cases<=500 or not 1<=args.max_output_kb<=1024 or not 0<=args.memory_mb<=8192:
            raise DataError('unsupported execution budget')
        if args.cwd.is_symlink():
            raise DataError('cwd must be a non-symlink directory')
        cwd=args.cwd.resolve()
        if not cwd.is_dir():
            raise DataError('cwd must be existing regular directory')
        cases=json_lines(args.cases,args.max_cases)
        command=check_command(args.argv_file)
        protected={args.cases.resolve(),args.argv_file.resolve(),Path(__file__).resolve()}
        if args.output.resolve() in protected:
            raise DataError('output cannot overwrite case inputs, command or script')
        observations=[]
        for case in cases:
            state,obs=run_one(command,case['input'],cwd,args.timeout,args.max_output_kb*1024,args.memory_mb, capture_fs=args.capture_fs)
            observations.append({'id':case['id'],'input':case['input'],'kind':case['kind'],
                                 'observation':obs, 'runner_status':state})
        payload=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in observations)
        write_exclusive(args.output,payload,protected)
        summary={'case_count':len(observations),'completed':sum(r['runner_status']=='ok' for r in observations),
                 'failed':sum(r['runner_status']!='ok' for r in observations),
                 'observations_sha256':hashlib.sha256(payload.encode()).hexdigest(),
                 'external_processes_executed':len(observations),
                 'security':'User-authorized trusted code only. No network or OS filesystem sandbox is provided.',
                 'filesystem_capture': args.capture_fs,
                 'filesystem_capture_scope':'only regular files within cwd; no outside/network/process effects'}
        save_output(summary,None)
        return 0 if not summary['failed'] else 1
    except (DataError,OSError,ValueError,json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
