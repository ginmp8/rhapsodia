#!/usr/bin/env python3
"""Fail-closed execution routing for analysis of supplied software.

The portable safe default is static-only. OCI policy *prepares* restricted local
container argv; it neither downloads images nor proves sandbox escape resistance.
Actual execution remains an explicitly authorized operator action.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from behavior_lab import DataError
from json_writer import write_exclusive

PINNED_IMAGE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:/-]*@sha256:[a-f0-9]{64}$')


def preflight(mode:str,*,authorized:bool=False,isolated_approved:bool=False,engine:str='docker',
              image:str='',entrypoint:str='/app/oracle')->dict:
    if mode not in ('static','trusted-local','oci-pinned'):
        raise DataError('unknown execution mode')
    if mode=='static':
        return {'mode':mode,'allowed':True,'executable_argv':None,
                'warning':'Static inspection only; never runs uploaded code.'}
    if not authorized:
        raise DataError('explicit execution approval is required')
    if mode=='trusted-local':
        return {'mode':mode,'allowed':True,'executable_argv':None,
                'warning':'For already trusted programs only. No OS/network isolation.'}
    if not isolated_approved:
        raise DataError('OCI requires independently assessed container isolation/daemon and operator authorization')
    if engine not in ('docker','podman'):
        raise DataError('OCI engine must be docker or podman')
    exe=shutil.which(engine)
    if not exe:
        raise DataError(f'{engine} not installed; static analysis remains available')
    if not PINNED_IMAGE.fullmatch(image):
        raise DataError('OCI image must include immutable sha256 digest; tags alone are not accepted')
    if not entrypoint.startswith('/') or len(entrypoint)>512 or any(x in entrypoint for x in ('\x00','\n')):
        raise DataError('entrypoint must be a bounded absolute in-image path')
    # The image carries the program: do not mount the host filesystem or credentials.
    args=[str(Path(exe).resolve()),'run','--rm','--pull=never','-i',
          '--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges',
          '--pids-limit=64','--memory=512m','--cpus=1',
          '--user=65534:65534','--tmpfs=/tmp:rw,noexec,nosuid,size=32m',
          '--entrypoint',entrypoint,image]
    return {'mode':mode,'allowed':True,'executable_argv':args,
            'warning':'Restricted OCI configuration is defense in depth, not a proven security boundary; validate host daemon and isolation externally.'}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['static','trusted-local','oci-pinned'])
    ap.add_argument('--execute-authorized',action='store_true')
    ap.add_argument('--isolation-approved',action='store_true')
    ap.add_argument('--engine',choices=['docker','podman'],default='docker')
    ap.add_argument('--image',default='')
    ap.add_argument('--entrypoint',default='/app/oracle')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(argv)
    try:
        report=preflight(a.mode,authorized=a.execute_authorized,isolated_approved=a.isolation_approved,
                         engine=a.engine,image=a.image,entrypoint=a.entrypoint)
        if a.output:
            write_exclusive(a.output,json.dumps(report,indent=2)+'\n',[])
        else: print(json.dumps(report,indent=2))
        return 0
    except (DataError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
