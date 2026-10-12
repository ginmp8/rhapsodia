#!/usr/bin/env python3
"""Offline WASM MVP function/type/import/export/call graph decoder.

Never executes WebAssembly. Decodes supported MVP instruction operands and
marks new/unknown instructions as incomplete rather than inventing call edges.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from json_writer import write_exclusive

MAX_BYTES = 64*1024*1024
MAX_RECORDS = 100000

class WasmError(ValueError):pass

class Reader:
    def __init__(self, data: bytes, start=0, end=None):
        self.data=data; self.p=start; self.end=len(data) if end is None else end
        if not 0<=start<=self.end<=len(data):raise WasmError('invalid section extent')
    def take(self,n):
        if n<0 or n>self.end-self.p:raise WasmError(f'truncated at {self.p}')
        p=self.p;self.p+=n;return self.data[p:self.p]
    def u8(self):return self.take(1)[0]
    def uleb(self,maxbits=32):
        result=0
        for shift in range(0,maxbits+6,7):
            byte=self.u8()
            result|=(byte&127)<<shift
            if byte&128==0:
                if result>=(1<<maxbits):raise WasmError('integer overflow')
                return result
        raise WasmError('invalid uleb128')
    def sleb(self,maxbits=33):
        result=0;shift=0
        for _ in range(10):
            byte=self.u8();result|=(byte&127)<<shift;shift+=7
            if byte&128==0:
                if (byte&64):result-=1<<shift
                if not -(1<<(maxbits-1))<=result<1<<(maxbits-1):raise WasmError('sleb128 overflow')
                return result
        raise WasmError('invalid sleb128')
    def name(self):
        size=self.uleb()
        if size>65536:raise WasmError('oversized WASM name')
        return self.take(size).decode('utf-8','replace')
    def sub(self,n):
        out=Reader(self.data,self.p,self.p+n)
        self.take(n)
        return out
    def vec(self,method):
        count=self.uleb()
        if count>MAX_RECORDS:raise WasmError('vector entry budget exceeded')
        return [method(self) for _ in range(count)]

VALTYPE = {0x7f:'i32',0x7e:'i64',0x7d:'f32',0x7c:'f64',0x70:'funcref',0x6f:'externref',0x7b:'v128'}

def valtype(r):return VALTYPE.get(r.u8(),'unknown')
def limits(r):
    flags=r.uleb(); minimum=r.uleb(64 if flags&4 else 32)
    maximum=r.uleb(64 if flags&4 else 32) if flags&1 else None
    if flags&~7:raise WasmError('unsupported WASM memory/table limits flags')
    return {'min':minimum,'max':maximum,'shared':bool(flags&2)}

def extern_desc(r,kind):
    if kind==0:return {'type_index':r.uleb()}
    if kind==1:return {'element_type':valtype(r),'limits':limits(r)}
    if kind==2:return {'limits':limits(r)}
    if kind==3:return {'value_type':valtype(r),'mutable':bool(r.u8())}
    if kind==4:return {'attribute':r.uleb(),'tag_type':r.uleb()}
    raise WasmError(f'unsupported external kind {kind}')

# WASM numeric opcodes 0x45..0xbf have no immediate fields; therefore they
# are safe to skip in MVP modules. Typed references and extensions are gated.
NUMERIC_NOARGS=set(range(0x45,0xc5)) | {0x00,0x01,0x05,0x0b,0x0f,0x1a,0x1b}
MEMARG=set(range(0x28,0x3f))

def scan_instructions(code:Reader, src:int, max_inst=100000):
    calls=[]; locals_used=[]; steps=0; complete=True; message=None
    while code.p<code.end:
        if steps>=max_inst:complete=False;message='instruction budget reached';break
        steps+=1;off=code.p;op=code.u8()
        try:
            if op in (0x02,0x03,0x04): code.sleb(33)
            elif op in (0x0c,0x0d):code.uleb()
            elif op==0x0e:
                count=code.uleb()
                if count>65536:raise WasmError('branch table too large')
                for _ in range(count+1):code.uleb()
            elif op in (0x10,0x12):
                dest=code.uleb();calls.append({'offset':off-src,'index':dest,'opcode':'call' if op==0x10 else 'return_call'})
            elif op in (0x11,0x13):
                t=code.uleb();tab=code.uleb()
                calls.append({'offset':off-src,'opcode':'call_indirect' if op==0x11 else 'return_call_indirect', 'type_index':t,'table_index':tab,
                              'resolved':False})
            elif op in (0x14,0x15):
                typ=code.uleb(); calls.append({'offset':off-src,'opcode':'call_ref','type_index':typ,'resolved':False})
            elif op in (0x20,0x21,0x22,0x23,0x24,0x25,0x26,0xd2):
                idx=code.uleb()
                if op in (0x20,0x21,0x22):locals_used.append(idx)
            elif op==0x1c:
                code.vec(lambda x:valtype(x))
            elif op in MEMARG:
                code.uleb();code.uleb()
            elif op in (0x3f,0x40):code.uleb() # memory index
            elif op==0x41:code.sleb(32)
            elif op==0x42:code.sleb(64)
            elif op==0x43:code.take(4)
            elif op==0x44:code.take(8)
            elif op==0xd0:code.u8() # ref.null heap type MVP only
            elif op==0xd1:pass
            elif op==0xfc:
                sub=code.uleb()
                if sub in range(8):pass
                elif sub==8:code.uleb();code.uleb()
                elif sub==9:code.uleb()
                elif sub==10:code.uleb();code.uleb()
                elif sub==11:code.uleb()
                elif sub==12:code.uleb();code.uleb()
                elif sub==13:code.uleb()
                elif sub==14:code.uleb();code.uleb()
                elif sub in (15,16,17):code.uleb()
                else:raise WasmError(f'unsupported 0xfc opcode {sub}')
            elif op in NUMERIC_NOARGS:pass
            else:raise WasmError(f'unsupported opcode 0x{op:02x}')
        except WasmError as e:
            complete=False;message=f'{e} at {off-src}';break
    return {'calls':calls,'locals_referenced':sorted(set(locals_used))[:1024],
            'instruction_count':steps,'complete':complete,'warning':message}


def analyze_wasm(data:bytes)->dict:
    if len(data)>MAX_BYTES:raise WasmError('file exceeds byte budget')
    if not data.startswith(b'\x00asm\x01\x00\x00\x00'):raise WasmError('unsupported WASM magic/version')
    r=Reader(data,8);types=[];imports=[];defined_types=[];exports=[];bodies=[];sections=[];warnings=[];seen=set()
    while r.p<r.end:
        if len(sections)>200:raise WasmError('section budget exceeded')
        sid=r.u8();size=r.uleb();start=r.p;sec=r.sub(size)
        section={'id':sid,'offset':start,'bytes':size};sections.append(section)
        if sid!=0:
            if sid in seen: warnings.append(f'duplicate section id {sid}')
            seen.add(sid)
        if sid==0:
            section['custom_name']=sec.name()
            continue
        if sid==1:
            def t(x):
                tag=x.u8()
                if tag!=0x60:raise WasmError(f'unsupported WASM type kind 0x{tag:x}')
                return {'parameters':x.vec(valtype),'returns':x.vec(valtype)}
            types=sec.vec(t)
        elif sid==2:
            def imp(x):
                module=x.name();name=x.name();kind=x.u8()
                return {'module':module,'name':name,'kind':kind,**extern_desc(x,kind)}
            imports=sec.vec(imp)
        elif sid==3:
            defined_types=sec.vec(lambda x:x.uleb())
        elif sid==7:
            exports=sec.vec(lambda x:{'name':x.name(),'kind':x.u8(),'index':x.uleb()})
        elif sid==8:section['start_function_index']=sec.uleb()
        elif sid==10:
            count=sec.uleb()
            if count>MAX_RECORDS:raise WasmError('code body budget exceeded')
            for _ in range(count):
                size=sec.uleb()
                if size>8*1024*1024:raise WasmError('single function too large')
                body=sec.sub(size)
                declarations=body.uleb()
                if declarations>65536:raise WasmError('local declarations budget exceeded')
                locals_count=0
                for i in range(declarations):
                    locals_count+=body.uleb();valtype(body)
                startcode=body.p
                info=scan_instructions(body,startcode)
                info['locals_count']=locals_count
                info['code_bytes']=body.end-startcode
                bodies.append(info)
        else:
            continue
        if sec.p!=sec.end:
            warnings.append(f'section {sid} contains {sec.end-sec.p} unparsed bytes')
    imported_functions=[x for x in imports if x['kind']==0]
    imported_count=len(imported_functions)
    funcs=[]
    for i,index in enumerate(defined_types):
        symbol=imported_count+i
        t=types[index] if index<len(types) else None
        item={'index':symbol,'type_index':index,'type':t,'body':bodies[i] if i<len(bodies) else None}
        if item['body']:
            for call in item['body']['calls']:
                if 'index' in call:
                    dest=call['index']
                    if dest<imported_count:
                        target=imported_functions[dest]
                        call['target']={'module':target['module'],'name':target['name'],'type':'import'}
                    elif dest<imported_count+len(defined_types):
                        call['target']={'function_index':dest,'type':'defined'}
                    else: call['target']={'function_index':dest,'type':'unresolved'}
        funcs.append(item)
    if len(defined_types)!=len(bodies):warnings.append('function/code section count mismatch')
    return {'format':'wasm','sha256':hashlib.sha256(data).hexdigest(), 'sections':sections,
            'types':types,'imports':imports,'exports':exports,'functions':funcs,
            'imported_function_count':imported_count,'warnings':warnings,
            'code_walk_complete':all(x['complete'] for x in bodies) and len(bodies)==len(defined_types),
            'evidence_level':'MVP-compatible bytecode call sites, not semantic decompilation or validation'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path);p.add_argument('-o','--output',type=Path)
    a=p.parse_args(argv)
    try:
        if a.path.is_symlink():raise WasmError('symlink input forbidden')
        if a.path.stat().st_size>MAX_BYTES:raise WasmError('byte budget exceeded')
        data=analyze_wasm(a.path.read_bytes())
        text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
        if a.output:
            if a.path.resolve()==a.output.resolve():raise WasmError('output aliases input')
            write_exclusive(a.output,text,[a.path])
        else:print(text,end='')
        return 0 if data['code_walk_complete'] else 3
    except (WasmError,OSError,RecursionError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
