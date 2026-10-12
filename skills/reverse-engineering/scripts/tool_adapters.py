#!/usr/bin/env python3
"""Explicit opt-in integrations with installed ILSpyCmd, JADX, Ghidra and Kaitai.

No downloads, installation, target execution or unsupervised network operations.
Third-party parsers/decompilers have their own attack surfaces; run only when
operator authorizes the selected tool and isolated parsing environment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from behavior_lab import DataError, strict_json
from json_writer import write_exclusive

TOOLS={'ilspy':('ilspycmd',), 'jadx':('jadx',), 'ghidra':('analyzeHeadless',),
       'kaitai':('ksc','kaitai-struct-compiler'), 'roslyn':('roslyn-export',)}
MAX_INPUT=128*1024*1024
MAX_OUTPUT=64*1024*1024


def tool_path(provider:str,tool_override:Path|None=None)->str|None:
    if provider not in TOOLS:raise DataError('unknown provider')
    if tool_override:
        if not tool_override.is_absolute() or tool_override.is_symlink() or not tool_override.is_file():
            raise DataError('tool override must be a regular absolute executable')
        return str(tool_override.resolve())
    for name in TOOLS[provider]:
        if value:=shutil.which(name):return str(Path(value).resolve())
    return None


def detect()->dict:
    return {'schema_version':'1.0','available':{k:{'path':tool_path(k),
                'status':'installed-not-executed' if tool_path(k) else 'unavailable'} for k in TOOLS},
            'notice':'Detection is PATH-only; do not infer tool functionality or permissions.'}


def build_command(provider:str,tool:str,target:Path,out:Path,*,schema:Path|None=None)->list[str]:
    if provider=='ilspy':return [tool,'-p','-o',str(out),str(target)]
    if provider=='roslyn':return [tool,str(target),'--output',str(out/'roslyn.json')]
    if provider=='jadx':return [tool,'-j','1','-r','-d',str(out),str(target)]
    if provider=='kaitai':
        if not schema:raise DataError('kaitai requires explicit trusted --schema .ksy')
        return [tool,'-t','python','-d',str(out),str(schema)]
    if provider=='ghidra':
        script=Path(__file__).resolve().parent.parent/'tools'/'ghidra'/'export_functions.py'
        project=out/'project'
        return [tool,str(project),'StaticReview','-import',str(target),'-scriptPath',str(script.parent),
                '-postScript',script.name,str(out/'ghidra-symbols.json'),'-deleteProject']
    raise DataError('unsupported provider')


def manifest(root:Path)->list[dict]:
    entries=[];total=0
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=sorted(dirs)
        for d in dirs:
            if (Path(base)/d).is_symlink():raise DataError('tool produced symlink directory')
        for name in sorted(files):
            f=Path(base)/name
            st=f.lstat()
            if not stat.S_ISREG(st.st_mode):raise DataError('tool produced symlink/special file')
            total+=st.st_size
            if len(entries)>=2000 or total>MAX_OUTPUT:raise DataError('tool output budget exceeded')
            h=hashlib.sha256()
            with f.open('rb') as stream:
                for chunk in iter(lambda:stream.read(128*1024),b''):h.update(chunk)
            entries.append({'path':f.relative_to(root).as_posix(),'sha256':h.hexdigest(),'bytes':st.st_size})
    return entries


def bounded_process(command:list[str],cwd:str,environment:dict,timeout:int,stdout_path:Path,stderr_path:Path)->int:
    """Consume both subprocess pipes with strict caps, without unbounded PIPE buffers."""
    try:
        process=subprocess.Popen(command,cwd=cwd,env=environment,stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except OSError as exc:
        raise DataError('optional tool failed to start: '+type(exc).__name__) from exc
    over=threading.Event()
    def copy(source,destination):
        written=0
        with destination.open('wb') as sink:
            while chunk:=source.read(65536):
                written+=len(chunk)
                if written>2*1024*1024:
                    over.set();process.kill();break
                sink.write(chunk)
        source.close()
    threads=[threading.Thread(target=copy,args=(process.stdout,stdout_path),daemon=True),
             threading.Thread(target=copy,args=(process.stderr,stderr_path),daemon=True)]
    for thread in threads:thread.start()
    try:
        code=process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        process.kill();process.wait(timeout=5)
        raise DataError('optional tool timed out; child process cleanup requires host supervision') from exc
    finally:
        for thread in threads:thread.join(timeout=3)
    if any(t.is_alive() for t in threads):
        raise DataError('tool inherited output pipes remained open after exit')
    if over.is_set():raise DataError('tool diagnostic stream exceeds 2MiB budget')
    return code


def run(provider:str,target:Path,output_dir:Path,*,authorized:bool=False,
        environment_approved:bool=False,tool_override:Path|None=None,
        schema:Path|None=None,timeout:int=120)->dict:
    if not authorized or not environment_approved:
        raise DataError('external tool execution requires explicit authorization and assessed parsing environment')
    exe=tool_path(provider,tool_override)
    if not exe:raise DataError('provider unavailable; install externally before authorizing, never auto-download')
    if target.is_symlink() or not target.is_file() or target.stat().st_size>MAX_INPUT:
        raise DataError('input must be bounded regular nonsymlink file')
    if schema and (schema.is_symlink() or not schema.is_file() or schema.suffix!='.ksy' or schema.stat().st_size>1024*1024):
        raise DataError('schema must be bounded regular .ksy')
    if provider=='kaitai' and not schema:raise DataError('kaitai requires schema')
    if output_dir.exists():raise DataError('output directory must not exist; no overwrite allowed')
    if not 1<=timeout<=900:raise DataError('timeout must be 1..900 seconds')
    # Tools may create arbitrary files, so require external host isolation; no claim of sandboxing.
    with tempfile.TemporaryDirectory(prefix='re-adapter-') as scratch:
        working=Path(scratch)/'output';working.mkdir()
        cmd=build_command(provider,exe,target.resolve(),working,schema=schema.resolve() if schema else None)
        env={'PATH':os.environ.get('PATH',''),'HOME':scratch,'LANG':'C.UTF-8','LC_ALL':'C.UTF-8'}
        for key in ('JAVA_HOME','DOTNET_ROOT'):
            if key in os.environ:env[key]=os.environ[key]
        stdout_path=Path(scratch)/'stdout.log';stderr_path=Path(scratch)/'stderr.log'
        code=bounded_process(cmd,scratch,env,timeout,stdout_path,stderr_path)
        if code!=0:
            raise DataError(f'provider exited nonzero: {code}; diagnostic hashes only')
        files=manifest(working)
        if not files:raise DataError('provider produced no inspected files')
        output_dir.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.re-stage-',dir=output_dir.parent) as destination_stage:
            stage=Path(destination_stage)/'deliver';stage.mkdir()
            for entry in files:
                source=working/entry['path'];destination=stage/entry['path']
                destination.parent.mkdir(parents=True,exist_ok=True)
                if source.is_symlink():raise DataError('tool output symlink changed after manifest')
                fd=os.open(source,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
                actual=hashlib.sha256()
                try:
                    with os.fdopen(fd,'rb') as inp,destination.open('xb') as dest:
                        for block in iter(lambda:inp.read(131072),b''):
                            actual.update(block);dest.write(block)
                finally:
                    # fd is owned by fdopen and closed on exit; no separate close.
                    pass
                if actual.hexdigest()!=entry['sha256'] or destination.stat().st_size!=entry['bytes']:
                    raise DataError('tool output changed after manifest')
            # Additional report is constructed while still staged; final directory never partial.
            report={'schema_version':'1.0','provider':provider,'format':'external-static-analysis',
                    'source_path':target.name,'input_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                    'tool_path':exe,'tool_sha256':hashlib.sha256(Path(exe).read_bytes()).hexdigest() if Path(exe).stat().st_size<=256*1024*1024 else None,'returncode':code,
                    'stdout_sha256':hashlib.sha256(stdout_path.read_bytes()).hexdigest(),
                    'stderr_sha256':hashlib.sha256(stderr_path.read_bytes()).hexdigest(),
                    'files':files,'evidence':'optional external tool, output not run as code',
                    'limits':'parsed/decompiled constructs only; no runtime equivalence proved'}
            if provider in ('ghidra','roslyn'):
                p=stage/('ghidra-symbols.json' if provider=='ghidra' else 'roslyn.json')
                if p.exists():
                    data=strict_json(p.read_text('utf-8'))
                    if isinstance(data,dict) and isinstance(data.get('symbols'),list):
                        report['symbols']=data['symbols'][:25000]
            (stage/'adapter-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            if output_dir.exists():raise DataError('output directory appeared during analysis')
            os.rename(stage,output_dir)
            return report


def import_roslyn(path:Path)->dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_OUTPUT:
        raise DataError('Roslyn export must be a bounded regular JSON file')
    data=strict_json(path.read_text('utf-8'))
    if not isinstance(data,dict) or not isinstance(data.get('symbols'),list):
        raise DataError('Roslyn semantic export must contain symbols array')
    # A supplied report is *claimed* semantic evidence until compilation identity is verified.
    verified=bool(isinstance(data.get('compilation'),dict) and data['compilation'].get('project_sha256') and data['compilation'].get('compiler_version'))
    symbols=[]
    for item in data['symbols'][:25000]:
        if not isinstance(item,dict) or not isinstance(item.get('name'),str):
            raise DataError('malformed Roslyn symbol')
        symbols.append({'name':item['name'][:512], 'kind':str(item.get('kind','unknown'))[:80],
                        'references':[str(x)[:512] for x in item.get('references',[])[:100]] if isinstance(item.get('references',[]),list) else [],
                        'evidence_level':'claimed_semantic_resolution' if verified else 'unverified_semantic_export'})
    return {'schema_version':'1.0','format':'roslyn-semantic-import','source_path':path.name,
            'report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'symbols':symbols,
            'compilation_identity_supplied':verified,'runtime_compilation_verified':False,
            'evidence':'imported external report; source compiler was not run by this skill'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['detect','run','import-roslyn'])
    p.add_argument('--provider',choices=list(TOOLS))
    p.add_argument('--input',type=Path)
    p.add_argument('--schema',type=Path)
    p.add_argument('--tool-path',type=Path)
    p.add_argument('--output-dir',type=Path)
    p.add_argument('--timeout',type=int,default=120)
    p.add_argument('--execute-authorized',action='store_true')
    p.add_argument('--environment-approved',action='store_true')
    p.add_argument('-o','--output',type=Path)
    a=p.parse_args(argv)
    try:
        if a.operation=='detect':res=detect()
        elif a.operation=='import-roslyn':
            if not a.input:raise DataError('--input required')
            res=import_roslyn(a.input)
        else:
            if not (a.provider and a.input and a.output_dir):raise DataError('--provider/--input/--output-dir required')
            res=run(a.provider,a.input,a.output_dir,authorized=a.execute_authorized,
                    environment_approved=a.environment_approved,tool_override=a.tool_path,
                    schema=a.schema,timeout=a.timeout)
        if a.output:
            if a.input and a.output.resolve()==a.input.resolve():raise DataError('output aliases input')
            write_exclusive(a.output,json.dumps(res,ensure_ascii=False,indent=2)+'\n',[a.input] if a.input else [])
        else:print(json.dumps(res,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
