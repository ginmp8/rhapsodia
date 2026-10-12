#!/usr/bin/env python3
"""Bounded side-by-side behavioral replay with optional counterexample reduction.

Only for two explicitly approved TRUSTED local executables. Not an OS sandbox.
Each stimulus is passed on stdin as JSON and each program returns a one-line
JSON observation. Offline observations can also be compared without running.
"""
from __future__ import annotations
import argparse
import hashlib
from itertools import islice
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from oracle_runner import json_lines,check_command,run_one
from behavior_lab import DataError,compare,differ,strict_json,save_output


def equivalent(ref_status:str, ref_obs:dict, cand_status:str, cand_obs:dict):
    if ref_status!='ok' or cand_status!='ok':return None
    changes=[]
    differ(ref_obs,cand_obs,('observation',),changes,frozenset(),0.0,20)
    return not changes


def candidates(v:Any,depth:int=0):
    """Generate bounded, deterministic shrink candidates; no output is guessed."""
    if depth >= 12:
        return
    if isinstance(v,dict):
        for k in sorted(v):
            x=dict(v);x.pop(k);yield x
            for smaller in islice(candidates(v[k],depth+1),16):
                y=dict(v);y[k]=smaller;yield y
    elif isinstance(v,list):
        if v:
            yield []
            for size in (max(1,len(v)//2),1):
                for i in range(0,len(v),size):
                    yield v[:i]+v[i+size:]
            for i in range(min(8,len(v))):
                for smaller in islice(candidates(v[i],depth+1),8):
                    y=list(v);y[i]=smaller;yield y
    elif isinstance(v,str):
        if v:yield ''
        if len(v)>1:yield v[:len(v)//2]
    elif isinstance(v,bool):
        yield not v
    elif isinstance(v,(float,int)) and not isinstance(v,bool):
        for a in (0,1,-1):
            if a!=v:yield a
    elif v is not None:yield None


def mismatch_signature(ref_status: str, ref_obs: dict, cand_status: str, cand_obs: dict):
    """First deterministic, value-free difference; statuses must be usable."""
    if ref_status != 'ok' or cand_status != 'ok':
        return None
    changes: list[dict[str, Any]] = []
    differ(ref_obs, cand_obs, ('observation',), changes, frozenset(), 0.0, 1)
    return {'pointer': changes[0]['pointer'], 'kind': changes[0]['kind']} if changes else None


def shrink_one(original: Any, ref_cmd, cand_cmd, ref_cwd: Path, cand_cwd: Path,
               timeout, output_bytes, memory_mb, max_trials=40,
               preserve_signature=True, baseline_reference=None, baseline_candidate=None):
    """Deterministically reduce an observed difference, preserving failure identity by default.

    Only use with explicitly approved trusted programs. Each trial re-executes
    both programs and may mutate external state: no sandbox or reset guarantee.
    """
    if baseline_reference is None or baseline_candidate is None:
        baseline_reference = run_one(ref_cmd, original, ref_cwd, timeout, output_bytes, memory_mb)
        baseline_candidate = run_one(cand_cmd, original, cand_cwd, timeout, output_bytes, memory_mb)
    signature = mismatch_signature(*baseline_reference, *baseline_candidate)
    if signature is None:
        return {'input': original, 'attempted_trials': 0, 'reduced': False,
                'failure_signature': None, 'preserved_signature': False,
                'note': 'No verified initial difference; no reduction attempted.'}
    value = original
    trials = 0
    visited = set()
    while trials < max_trials:
        improved = False
        for attempt in candidates(value):
            fingerprint = json.dumps(attempt, sort_keys=True, ensure_ascii=False, allow_nan=False)
            if fingerprint in visited:
                continue
            visited.add(fingerprint)
            if len(fingerprint) >= len(json.dumps(value, sort_keys=True, ensure_ascii=False)):
                continue
            trials += 1
            astatus, aobs = run_one(ref_cmd, attempt, ref_cwd, timeout, output_bytes, memory_mb)
            bstatus, bobs = run_one(cand_cmd, attempt, cand_cwd, timeout, output_bytes, memory_mb)
            candidate_signature = mismatch_signature(astatus, aobs, bstatus, bobs)
            if candidate_signature is not None and (not preserve_signature or candidate_signature == signature):
                value = attempt
                improved = True
                break
            if trials >= max_trials:
                break
        if not improved:
            break
    return {'input': value, 'attempted_trials': trials, 'reduced': value != original,
            'failure_signature': signature, 'preserved_signature': preserve_signature,
            'note': 'Preserves first difference pointer/kind if enabled; not globally minimal, stable, or isolated.'}


def run_pair(cases:Path,reference_argv:Path,candidate_argv:Path,
             reference_cwd:Path,candidate_cwd:Path,output_dir:Path,
             *,execute_authorized=False,timeout=3.0,max_cases=100,shrink_trials=0,memory_mb=512,
             shrink_preserve_signature=True,capture_fs=False):
    if capture_fs and shrink_trials:
        raise DataError("capture_fs with shrinking requires a resettable oracle and is not supported")
    if capture_fs and reference_cwd.resolve()==candidate_cwd.resolve():
        raise DataError("capture_fs requires separate reference/candidate working directories")
    if not execute_authorized:raise DataError('execution not authorized: trusted local programs only')
    if not 0.1<=timeout<=30.0 or not 1<=max_cases<=300 or not 0<=shrink_trials<=100 or not 0<=memory_mb<=8192:
        raise DataError('execution budget out of range')
    ref_cmd=check_command(reference_argv);cand_cmd=check_command(candidate_argv)
    for cwd in (reference_cwd,candidate_cwd):
        if cwd.is_symlink() or not cwd.is_dir():raise DataError('cwd must exist and not be a symlink')
    if output_dir.exists():
        raise DataError('output directory must not already exist; preserve previous evidence')
    inputs=json_lines(cases,max_cases)
    for p in (cases,reference_argv,candidate_argv,reference_cwd,candidate_cwd):
        if output_dir.resolve()==p.resolve():raise DataError('output aliases a protected input')
    output_dir.mkdir(parents=True,exist_ok=False)
    reference=[];candidate=[];counterexamples=[]
    for case in inputs:
        ast,obs_a=run_one(ref_cmd,case['input'],reference_cwd,timeout,256*1024,memory_mb,capture_fs=capture_fs)
        bst,obs_b=run_one(cand_cmd,case['input'],candidate_cwd,timeout,256*1024,memory_mb,capture_fs=capture_fs)
        reference.append({**case,'observation':obs_a,'runner_status':ast})
        candidate.append({**case,'observation':obs_b,'runner_status':bst})
        if equivalent(ast,obs_a,bst,obs_b) is False and shrink_trials:
            reduced=shrink_one(case['input'],ref_cmd,cand_cmd,reference_cwd,candidate_cwd,
                               timeout,256*1024,memory_mb,max_trials=shrink_trials,
                               preserve_signature=shrink_preserve_signature,
                               baseline_reference=(ast,obs_a),baseline_candidate=(bst,obs_b))
            counterexamples.append({'id':case['id'],**reduced})
    for name,records in (('reference.jsonl',reference),('candidate.jsonl',candidate)):
        target=output_dir/name
        target.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in records),encoding='utf-8')
    result=compare(output_dir/'reference.jsonl',output_dir/'candidate.jsonl')
    result['reconstruction_oracles']={
        'reference_command_sha256':hashlib.sha256(reference_argv.read_bytes()).hexdigest(),
        'candidate_command_sha256':hashlib.sha256(candidate_argv.read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256(cases.read_bytes()).hexdigest(),
        'authorized_trusted_execution':True,
        'timeout_seconds_per_process':timeout,
        'separate_cwds':reference_cwd.resolve()!=candidate_cwd.resolve(),
        'side_effect_capture':'cwd-regular-file-hashes-only' if capture_fs else 'not provided',
        'shrink_preserve_signature':shrink_preserve_signature,
        'runtime_platform':sys.platform,
        'python_runtime':sys.version.split()[0],
        'security_note':'No OS/network sandbox: program side effects may escape cwd; do not use for untrusted uploads',
    }
    result['counterexamples']=counterexamples
    (output_dir/'comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',required=True,type=Path)
    p.add_argument('--reference-argv',required=True,type=Path)
    p.add_argument('--candidate-argv',required=True,type=Path)
    p.add_argument('--reference-cwd',required=True,type=Path)
    p.add_argument('--candidate-cwd',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--timeout',type=float,default=3.0)
    p.add_argument('--memory-mb',type=int,default=512)
    p.add_argument('--max-cases',type=int,default=100)
    p.add_argument('--shrink-trials',type=int,default=0)
    p.add_argument('--shrink-allow-different-mismatch', action='store_true',
                   help='Opt-in: shrinking may change first failure pointer/kind')
    p.add_argument('--execute-authorized',action='store_true')
    p.add_argument('--capture-fs',action='store_true',help='Opt-in cwd file diff, trusted programs only; no OS isolation')
    a=p.parse_args(argv)
    try:
        result=run_pair(a.cases,a.reference_argv,a.candidate_argv,a.reference_cwd,a.candidate_cwd,
                        a.output_dir,execute_authorized=a.execute_authorized,
                        timeout=a.timeout,memory_mb=a.memory_mb,max_cases=a.max_cases,shrink_trials=a.shrink_trials,
                        shrink_preserve_signature=not a.shrink_allow_different_mismatch,capture_fs=a.capture_fs)
        print(json.dumps({'verdict':result['verdict'],'counts':result['counts'],
                          'comparison':str(a.output_dir/'comparison.json')},ensure_ascii=False))
        return 0 if result['verdict']=='PASS_OBSERVED_CASES' else 1
    except (DataError,OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
