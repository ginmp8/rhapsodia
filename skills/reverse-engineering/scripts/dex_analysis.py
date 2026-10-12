#!/usr/bin/env python3
"""Independent Dalvik DEX declarations and static invoke reference decoder.

No smali/decompilation. Operates on non-executed .dex/.apk (ZIP) with limits.
Only supported opcode widths are decoded; malformed instructions fail closed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path
from json_writer import write_exclusive

MAX_DEX=48*1024*1024
MAX_ITEMS=100000
MAX_CLASSES=10000

class DexError(ValueError):pass

class R:
    def __init__(self,buf:bytes):self.b=buf
    def chunk(self,p,n):
        if p<0 or n<0 or p+n>len(self.b):raise DexError(f'out of bounds at {p} size {n}')
        return self.b[p:p+n]
    def u2(self,p):return int.from_bytes(self.chunk(p,2),'little')
    def u4(self,p):return int.from_bytes(self.chunk(p,4),'little')
    def uleb(self,p):
        val=0
        for step in range(5):
            byte=self.chunk(p,1)[0];p+=1;val|=(byte&127)<<(7*step)
            if byte&128==0:return val,p
        raise DexError('invalid uleb128')
    def s(self,p):
        _,p=self.uleb(p)  # declared UTF-16 length; do not trust it for buffer bounds
        end=self.b.find(b'\x00',p,min(len(self.b),p+65536))
        if end<0:raise DexError('unterminated DEX string')
        return self.b[p:end].replace(b'\xc0\x80',b'\0').decode('utf-8','replace')

# Instruction sizes in 16-bit code units for the explicitly decoded subset.
# Unknown opcodes are reported as incomplete, never guessed to be one unit.
WIDTH = {0: 1}
for opcode in (0x01,0x04,0x07,*range(0x0a,0x0f),0x0f,0x10,0x11,0x12,
               0x1d,0x1e,0x21,0x27,0x28,*range(0x7b,0x90),*range(0xb0,0xd0)):
    WIDTH[opcode] = 1
for opcode in (0x02,0x05,0x08,0x13,0x15,0x16,0x19,0x1a,0x1c,
               0x1f,0x20,0x22,0x23,0x29,*range(0x2d,0x3e),
               *range(0x44,0x6e),*range(0x90,0xb0),*range(0xd0,0xe3),0xfe,0xff):
    WIDTH[opcode] = 2
for opcode in (0x03,0x06,0x09,0x14,0x17,0x1b,0x24,0x25,0x26,
               0x2a,0x2b,0x2c,*range(0x6e,0x73),*range(0x74,0x79),0xfc,0xfd):
    WIDTH[opcode] = 3
for opcode in (0xfa,0xfb):
    WIDTH[opcode] = 4
WIDTH[0x18] = 5

def decode_invokes(words:list[int],method_names:list[dict]):
    p=0;calls=[];steps=0
    while p<len(words):
        steps+=1
        if steps>500000:return calls,False,'instruction limit exceeded'
        raw=words[p];op=raw&255
        if raw in (0x0100,0x0200,0x0300):
            return calls,False,'DEX payload format not decoded'
        width=WIDTH.get(op)
        if width is None:return calls,False,f'unsupported or reserved DEX opcode 0x{op:02x} at code unit {p}'
        if p+width>len(words):return calls,False,f'truncated DEX opcode at code unit {p}'
        if op in (*range(0x6e,0x73),*range(0x74,0x79),0xfa,0xfb):
            ref=words[p+1]
            calls.append({'code_unit_offset':p,'opcode':f'0x{op:02x}',
                          'callee_index':ref,'callee':method_names[ref] if ref<len(method_names) else None,
                          'dispatch':'dynamic/unresolved' if op in (0x6e,0x72,0x74,0x78,0xfa,0xfb) else 'static call site'})
        p+=width
    return calls,True,None


def analyze_dex(data:bytes)->dict:
    if len(data)>MAX_DEX:raise DexError('DEX byte budget exceeded')
    b=R(data)
    if len(data)<112 or not re.fullmatch(rb'dex\n0[0-9]{2}\x00',data[:8]):raise DexError('unsupported DEX magic')
    declared=b.u4(32);header=b.u4(36);endian=b.u4(40)
    if header!=112 or endian!=0x12345678:raise DexError('unsupported DEX header/endian')
    if declared>len(data):raise DexError('truncated DEX declared size')
    sizes={}
    for name,off in [('strings',56),('types',64),('protos',72),('fields',80),('methods',88),('classes',96)]:
        count=b.u4(off);start=b.u4(off+4)
        width={'strings':4,'types':4,'protos':12,'fields':8,'methods':8,'classes':32}[name]
        if count>MAX_ITEMS or count and (start<112 or start+count*width>len(data)):
            raise DexError(f'{name} index bounds invalid')
        sizes[name]=(count,start)
    n,off=sizes['strings'];strings=[b.s(b.u4(off+i*4)) for i in range(n)]
    n,off=sizes['types']
    types=[strings[b.u4(off+i*4)] if b.u4(off+i*4)<len(strings) else f'<invalid:{i}>' for i in range(n)]
    n,off=sizes['protos'];protos=[]
    for i in range(n):
        p=off+i*12;rt=b.u4(p+4);args_off=b.u4(p+8)
        args=[]
        if args_off:
            count=b.u4(args_off)
            if count>1000:raise DexError('proto argument budget exceeded')
            args=[types[b.u2(args_off+4+2*k)] for k in range(count) if b.u2(args_off+4+2*k)<len(types)]
        protos.append({'parameters':args,'return':types[rt] if rt<len(types) else '<invalid>'})
    n,off=sizes['methods'];method_names=[]
    for i in range(n):
        p=off+i*8;clazz=b.u2(p);proto=b.u2(p+2);name=b.u4(p+4)
        method_names.append({'owner':types[clazz] if clazz<len(types) else '<invalid>',
                             'name':strings[name] if name<len(strings) else '<invalid>',
                             'signature':protos[proto] if proto<len(protos) else None})
    n,off=sizes['classes'];classes=[]
    if n>MAX_CLASSES:raise DexError('class count budget exceeded')
    for i in range(n):
        p=off+i*32;idx=b.u4(p);superidx=b.u4(p+8);classdata=b.u4(p+24)
        entry={'name':types[idx] if idx<len(types) else '<invalid>',
               'superclass':types[superidx] if superidx<len(types) else None,
               'access_flags':b.u4(p+4),'methods':[]}
        if classdata:
            counts=[];cursor=classdata
            for _ in range(4):
                count,cursor=b.uleb(cursor)
                if count>MAX_ITEMS:raise DexError('class-data method/field budget exceeded')
                counts.append(count)
            for count in counts[:2]:
                for _ in range(count):
                    _,cursor=b.uleb(cursor);_,cursor=b.uleb(cursor)
            for count in counts[2:]:
                previous=0
                for _ in range(count):
                    delta,cursor=b.uleb(cursor);previous+=delta
                    flags,cursor=b.uleb(cursor);codeoff,cursor=b.uleb(cursor)
                    if previous>=len(method_names):raise DexError('method index out of range')
                    m={**method_names[previous],'method_id':previous,'access_flags':flags,'code_offset':codeoff}
                    if codeoff:
                        insns_size=b.u4(codeoff+12)
                        if insns_size>1000000:raise DexError('method code budget exceeded')
                        insns=struct.unpack('<'+'H'*insns_size,b.chunk(codeoff+16,insns_size*2))
                        calls,complete,warning=decode_invokes(list(insns),method_names)
                        m['invokes']=calls;m['code_walk_complete']=complete
                        if warning:m['warning']=warning
                    entry['methods'].append(m)
        classes.append(entry)
    return {'format':'dex','version':data[4:7].decode('ascii'),
            'sha256':hashlib.sha256(data).hexdigest(),
            'declarations':{'strings':sizes['strings'][0],'types':len(types),'protos':len(protos),
                            'methods':len(method_names),'classes':len(classes)},
            'classes':classes, 'code_walk_complete':all(m.get('code_walk_complete',True) for c in classes for m in c['methods']),
            'evidence_level':'DEX declared class/methods and parsed supported invoke sites; no Java source reconstruction'}


def analyze_path(path:Path):
    if path.is_symlink():raise DexError('symlink not allowed')
    if path.suffix.lower() not in ('.apk','.aab','.zip'):
        if path.stat().st_size>MAX_DEX:raise DexError('byte budget exceeded')
        return analyze_dex(path.read_bytes())
    results=[]
    with zipfile.ZipFile(path) as z:
        entries=z.infolist()
        if len(entries)>MAX_ITEMS:raise DexError('archive entry budget exceeded')
        for entry in entries:
            if not re.fullmatch(r'classes\d*\.dex',entry.filename):continue
            if entry.file_size>MAX_DEX or entry.file_size>max(entry.compress_size,1024)*200:
                raise DexError('untrusted archive expansion budget exceeded')
            if (entry.external_attr>>16)&0o170000==0o120000:raise DexError('symlink entry forbidden')
            out=analyze_dex(z.read(entry));out['archive_member']=entry.filename
            results.append(out)
    return {'format':'android-archive', 'dex_files':results,'complete':bool(results) and all(r['code_walk_complete'] for r in results)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path);p.add_argument('-o','--output',type=Path)
    a=p.parse_args(argv)
    try:
        out=analyze_path(a.path)
        text=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
        if a.output:
            if a.output.resolve()==a.path.resolve():raise DexError('output aliases input')
            write_exclusive(a.output,text,[a.path])
        else:print(text,end='')
        return 0 if out.get('code_walk_complete',out.get('complete',False)) else 3
    except (DexError,OSError,zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
