#!/usr/bin/env python3
"""Evaluate bounded recorded web traces against independently frozen expectations.

This is a deterministic trace assertions engine, not a full vulnerability scanner,
performance benchmark, regulatory audit or truth oracle for undefined requirements.
Missing fields -> incomplete, never silently pass. No scripts from policies execute.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from behavior_lab import DataError, strict_json
from json_writer import write_exclusive

MAX_INPUT=16*1024*1024
OPS={'eq','ne','lt','lte','gt','gte','contains'}


def load(path:Path,max_size:int=MAX_INPUT):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>max_size:
        raise DataError('bounded regular JSON input required')
    raw=path.read_bytes()
    return strict_json(raw.decode('utf-8')),hashlib.sha256(raw).hexdigest()


def read_pointer(obj,ptr):
    if not isinstance(ptr,str) or not ptr.startswith('/') or len(ptr)>512:
        raise DataError('expected nonempty bounded RFC6901 JSON pointer')
    current=obj
    for key in ptr.lstrip('/').split('/'):
        if '~' in key:
            import re
            if re.search(r'~(?![01])',key):
                raise DataError('malformed JSON pointer escape')
        key=key.replace('~1','/').replace('~0','~')
        if isinstance(current,list):
            if not key.isascii() or not key.isdigit() or (key.startswith('0') and key!='0'):
                return None,False
            index=int(key)
            if index>=len(current):
                return None,False
            current=current[index]
        elif isinstance(current,dict):
            if key not in current:
                return None,False
            current=current[key]
        else:
            return None,False
    return current,True


def matches(actual,op,expected)->bool:
    if op in ('eq','ne'):
        same=type(actual) is type(expected) and actual==expected
        return same if op=='eq' else not same
    if op=='contains':
        if isinstance(actual,str) and isinstance(expected,str):
            return expected in actual
        if isinstance(actual,(list,dict)):
            return expected in actual
        return False
    if (type(actual) not in (float,int) or type(expected) not in (float,int)):
        raise DataError('ordering comparisons require finite numeric values')
    return {'lt':lambda:actual<expected,'lte':lambda:actual<=expected,
            'gt':lambda:actual>expected,'gte':lambda:actual>=expected}[op]()


def audit(trace:dict,policy:dict,trace_sha:str='',policy_sha:str='')->dict:
    if trace.get('mode')!='web-investigation' or trace.get('schema_version')!='1.0':
        raise DataError('expected web-investigation trace v1.0')
    if policy.get('schema_version')!='1.0' or not isinstance(policy.get('rules'),list) or not 1<=len(policy['rules'])<=200:
        raise DataError('policy v1.0 requires between 1 and 200 rules')
    findings=[]
    ids=set()
    for rule in policy['rules']:
        if (not isinstance(rule,dict) or set(rule)!={'id','path','op','expected'}
                or not isinstance(rule['id'],str) or not 1<=len(rule['id'])<=100
                or rule['id'] in ids or rule['op'] not in OPS):
            raise DataError('rules require unique id, path, op, expected')
        ids.add(rule['id'])
        actual,found=read_pointer(trace,rule['path'])
        if not found:
            findings.append({'id':rule['id'],'path':rule['path'],'status':'incomplete',
                             'reason':'field not captured; absence is not evidence of compliance'})
            continue
        passed=matches(actual,rule['op'],rule['expected'])
        # Avoid sensitive actual/expected values in reports; persist only their hashes.
        findings.append({'id':rule['id'],'path':rule['path'], 'status':'pass' if passed else 'fail',
                         'comparison':rule['op'],
                         'actual_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
    counts={k:sum(x['status']==k for x in findings) for k in ('pass','fail','incomplete')}
    result='failed' if counts['fail'] else 'incomplete' if counts['incomplete'] else 'passed'
    return {'schema_version':'1.0','mode':'web-audit','result':result,'trace_sha256':trace_sha,
            'policy_sha256':policy_sha,'trace_type':trace.get('evidence_type'),
            'counts':counts,'findings':findings,
            'coverage':'Only explicit policy rules evaluated against captured finite trace fields',
            'security':'No general vulnerability/security clearance or browser/backend safety guarantee',
            'limits':'Policy expectations must be independently sourced; missing observations are incomplete'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--policy',type=Path,required=True)
    p.add_argument('-o','--output',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        if a.trace.resolve()==a.policy.resolve():
            raise DataError('trace and policy must be distinct independently sourced inputs')
        t,ts=load(a.trace)
        policy,ps=load(a.policy,256*1024)
        if not isinstance(t,dict) or not isinstance(policy,dict):
            raise DataError('trace and policy require JSON object')
        result=audit(t,policy,ts,ps)
        write_exclusive(a.output,json.dumps(result,sort_keys=True,indent=2)+'\n',[a.trace,a.policy])
        return 0 if result['result']=='passed' else 3
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
