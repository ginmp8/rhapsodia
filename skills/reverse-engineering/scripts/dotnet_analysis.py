#!/usr/bin/env python3
"""Independent read-only .NET CLI metadata and CIL call-site reader.

Uses ECMA-335 physical metadata tables and PE/COFF section mapping.
No .NET runtime required. Does not reconstruct C# source, resolve reflection,
proxies, generics dispatch, or dynamic binding. Unsupported tables fail closed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from json_writer import write_exclusive

MAX_FILE=64*1024*1024
MAX_TABLE_ROWS=200000
MAX_METHOD_BYTES=2*1024*1024

class CLRParseError(ValueError):pass

class Buffer:
    def __init__(self,data:bytes):self.b=data
    def slice(self,p,n):
        if p<0 or n<0 or p+n>len(self.b):raise CLRParseError(f'out of bounds at {p}, size {n}')
        return self.b[p:p+n]
    def u1(self,p):return self.slice(p,1)[0]
    def u2(self,p):return int.from_bytes(self.slice(p,2),'little')
    def u4(self,p):return int.from_bytes(self.slice(p,4),'little')
    def u8(self,p):return int.from_bytes(self.slice(p,8),'little')
    def cstr(self,p,stop=4096):
        val=self.slice(p,min(stop,len(self.b)-p))
        end=val.find(b'\x00')
        if end<0:raise CLRParseError('unterminated CLR string')
        return val[:end].decode('utf-8','replace')

# Physical ECMA-335 table layouts (0..44). Tokens start at row 1.
# Format: u2, u4, str, guid, blob, table index Tnn, coded index Cname.
TABLES={
 0:'u2 str guid guid guid', 1:'CResolutionScope str str',
 2:'u4 str str CTypeDefOrRef T4 T6', 3:'T4',
 4:'u2 str blob', 5:'T6', 6:'u4 u2 u2 str blob T8', 7:'T8',
 8:'u2 u2 str', 9:'T2 CTypeDefOrRef', 10:'CMemberRefParent str blob',
 11:'u2 CHasConstant blob', 12:'CHasCustomAttribute CCustomAttributeType blob',
 13:'CHasFieldMarshal blob', 14:'u2 CHasDeclSecurity blob',
 15:'u2 u4 T2',16:'u4 T4',17:'blob',18:'T2 T20',19:'T20',
 20:'u2 str CTypeDefOrRef',21:'T2 T23',22:'T23',23:'u2 str blob',
 24:'u2 T6 CHasSemantics',25:'T2 CMethodDefOrRef CMethodDefOrRef',
 26:'str',27:'blob',28:'u2 CMemberForwarded str T26',29:'u4 T4',
 30:'u4 u4',31:'u4',32:'u4 u2 u2 u2 u2 u4 blob str str',
 33:'u4',34:'u4 u4 u4',35:'u2 u2 u2 u2 u4 blob str str blob',
 36:'u4 T35',37:'u4 u4 u4 T35',38:'u4 str blob',
 39:'u4 u4 str str CImplementation',40:'u4 u4 str CImplementation',
 41:'T2 T2',42:'u2 u2 CTypeOrMethodDef str',
 43:'CMethodDefOrRef blob',44:'T42 CTypeDefOrRef'
}
CODED={
 'TypeDefOrRef':(2,[2,1,27]),'ResolutionScope':(2,[0,26,35,1]),
 'MemberRefParent':(3,[2,1,26,6,27]),
 'HasConstant':(2,[4,8,23]),
 'HasCustomAttribute':(5,[6,4,1,2,8,9,10,0,14,23,20,17,26,27,32,35,38,39,40,42,43,44]),
 'CustomAttributeType':(3,[None,None,6,10]),
 'HasFieldMarshal':(1,[4,8]),'HasDeclSecurity':(2,[2,6,32]),
 'HasSemantics':(1,[20,23]), 'MethodDefOrRef':(1,[6,10]),
 'MemberForwarded':(1,[4,6]),'Implementation':(2,[38,35,39]),
 'TypeOrMethodDef':(1,[2,6])
}

def pe_metadata_location(data:bytes)->tuple[int,int,callable,list]:
    b=Buffer(data)
    if b.slice(0,2)!=b'MZ':raise CLRParseError('not a PE file')
    peoff=b.u4(0x3c)
    if b.slice(peoff,4)!=b'PE\x00\x00':raise CLRParseError('invalid PE signature')
    nsect=b.u2(peoff+6); optsize=b.u2(peoff+20)
    if nsect>192:raise CLRParseError('section budget exceeded')
    optional=peoff+24; magic=b.u2(optional)
    if magic not in (0x10b,0x20b):raise CLRParseError('unsupported PE optional header')
    if optsize < (240 if magic == 0x20b else 224):raise CLRParseError('optional header too short')
    dirs=optional+(112 if magic==0x20b else 96)
    count=b.u4(dirs-4)
    if count<15:raise CLRParseError('no CLI data directory')
    rva=b.u4(dirs+14*8)
    if rva==0:raise CLRParseError('PE has no CLR descriptor')
    sections=[]
    for i in range(nsect):
        p=optional+optsize+i*40
        name=b.slice(p,8).split(b'\0')[0].decode('ascii','replace')
        vs,va,rawsize,rawptr=struct.unpack('<IIII',b.slice(p+8,16))
        sections.append({'name':name,'rva':va,'virtual_size':vs,'raw_size':rawsize,'raw_pointer':rawptr})
    def at_rva(r:int,n:int=1)->int:
        if r<0:return -1
        for s in sections:
            if s['rva']<=r and r+n<=s['rva']+s['raw_size'] and r<s['rva']+max(s['virtual_size'],s['raw_size']):
                off=s['raw_pointer']+r-s['rva'];b.slice(off,n);return off
        raise CLRParseError(f'RVA {r:#x} lacks fully file-backed section')
    hdr=at_rva(rva,24)
    metarva=b.u4(hdr+8);metasize=b.u4(hdr+12)
    if metasize==0 or metasize>MAX_FILE:raise CLRParseError('invalid metadata size')
    base=at_rva(metarva,metasize)
    if b.slice(base,4)!=b'BSJB':raise CLRParseError('invalid CLR metadata signature')
    return base, metasize, at_rva,sections

class Metadata:
    def __init__(self,data:bytes,base:int,size:int):
        self.b=Buffer(data);self.base=base;self.size=size
        self.tables={};self.row_counts={};self.heap_sizes=0;self.streams={}
        b=self.b
        length=b.u4(base+12)
        if length>2048:raise CLRParseError('oversized runtime version')
        self.version=b.slice(base+16,length).split(b'\x00',1)[0].decode('ascii','replace')
        p=base+16+((length+3)&~3)
        count=b.u2(p+2);p+=4
        if count>32:raise CLRParseError('stream count limit exceeded')
        for _ in range(count):
            off=b.u4(p);sz=b.u4(p+4);name=b.cstr(p+8,128)
            self.streams[name]=(base+off,sz)
            if off+sz>size:raise CLRParseError('stream outside metadata root')
            p+=8+((len(name.encode())+1+3)&~3)
        self.strings=self._stream('#Strings', optional=True)
        self.blobs=self._stream('#Blob',optional=True)
        tables=self._stream('#~',optional=True) or self._stream('#-',optional=True)
        if not tables:raise CLRParseError('no supported metadata tables stream')
        self._parse_tables(tables)

    def _stream(self,name,optional=False):
        if name not in self.streams:
            if optional:return b''
            raise CLRParseError(f'missing stream {name}')
        p,n=self.streams[name];return self.b.slice(p,n)

    def idx_width(self,desc:str)->int:
        if desc in ('str','guid','blob'):
            return 4 if self.heap_sizes & {'str':1,'guid':2,'blob':4}[desc] else 2
        if desc.startswith('T'):
            return 4 if self.row_counts.get(int(desc[1:]),0)>=65536 else 2
        if desc.startswith('C'):
            bits,targets=CODED[desc[1:]]
            return 4 if any(self.row_counts.get(t,0)>=1<<(16-bits) for t in targets if t is not None) else 2
        return {'u2':2,'u4':4}[desc]

    def _parse_tables(self, data:bytes):
        b=Buffer(data)
        self.heap_sizes=b.u1(6)
        valid=b.u8(8)
        pos=24
        for index in range(64):
            if valid>>index&1:
                count=b.u4(pos);pos+=4
                if count>MAX_TABLE_ROWS:raise CLRParseError(f'table {index} has too many rows')
                self.row_counts[index]=count
        for index,count in self.row_counts.items():
            if count==0:continue
            if index not in TABLES:raise CLRParseError(f'unsupported metadata table {index} with {count} rows')
            fields=TABLES[index].split();widths=[self.idx_width(x) for x in fields]
            total=sum(widths)
            if count*total>len(data)-pos:raise CLRParseError('truncated metadata table')
            rows=[]
            for row in range(count):
                values=[]
                for w in widths:
                    values.append(int.from_bytes(b.slice(pos,w),'little'));pos+=w
                rows.append(values)
            self.tables[index]=rows
        if pos>len(data):raise CLRParseError('table cursor overflow')

    def string(self,offset:int)->str:
        if offset==0:return ''
        if offset>=len(self.strings):raise CLRParseError('string index outside heap')
        end=self.strings.find(b'\x00',offset)
        if end<0:raise CLRParseError('unterminated metadata string')
        return self.strings[offset:end].decode('utf-8','replace')

    def blob(self,offset:int,maxsize=32768)->bytes:
        if offset==0:return b''
        b=self.blobs
        if offset>=len(b):raise CLRParseError('blob heap index outside heap')
        first=b[offset]
        if first&128==0:sz=first;p=offset+1
        elif first&192==128:
            if offset+2>len(b):raise CLRParseError('truncated compressed blob')
            sz=((first&63)<<8)|b[offset+1];p=offset+2
        elif first&224==192:
            if offset+4>len(b):raise CLRParseError('truncated compressed blob')
            sz=((first&31)<<24)|(b[offset+1]<<16)|(b[offset+2]<<8)|b[offset+3];p=offset+4
        else:raise CLRParseError('invalid blob length prefix')
        if sz>maxsize or p+sz>len(b):raise CLRParseError('blob length exceeds budget or data')
        return b[p:p+sz]

    def decode_index(self,name:str,value:int)->tuple[int,int]|None:
        bits,tables=CODED[name]
        tag=value&((1<<bits)-1);rid=value>>bits
        if tag>=len(tables) or tables[tag] is None or rid==0:return None
        return tables[tag],rid

    def resolve_type(self,tagged_index:int):
        v=self.decode_index('TypeDefOrRef',tagged_index)
        if v is None:return ''
        table,row=v
        values=self.tables.get(table,[])
        if row>len(values):return f'unresolved:{table}:{row}'
        meta=values[row-1]
        if table==2:return (self.string(meta[2])+'.' if self.string(meta[2]) else '')+self.string(meta[1])
        if table==1:return (self.string(meta[2])+'.' if self.string(meta[2]) else '')+self.string(meta[1])
        return f'TypeSpec:{row}'

# CIL operand layout for parsed call/branch/signature instructions.
OP_SHORT={0x0e,0x0f,0x10,0x11,0x12,0x13,0x1f,0xde,0xfe12,0xfe19} | set(range(0x2b,0x38))
OP_WORD={0xfe09,0xfe0a,0xfe0b,0xfe0c,0xfe0d,0xfe0e}
OP_DWORD=set(range(0x38,0x45)) | {0x20,0x22,0x27,0x28,0x29,0x6f,0x72,0x73,
 0x74,0x75,0x79,0x7b,0x7c,0x7d,0x7e,0x7f,0x80,0x81,0x8c,0x8d,0x8f,
 0xa3,0xa4,0xa5,0xc2,0xc6,0xd0,0xdd,0xfe06,0xfe07,0xfe15,0xfe16,0xfe1c}
OP_EIGHT={0x21,0x23}
OP_CALL={0x27:'jmp',0x28:'call',0x6f:'callvirt',0x73:'newobj',0x29:'calli',0xfe06:'ldftn',0xfe07:'ldvirtftn'}
OP_DEFAULT=(set(range(0x00,0x0e))|set(range(0x14,0x1f))|{0x25,0x26,0x2a}|
  set(range(0x46,0x6f))|set(range(0x76,0x79))|set(range(0x82,0x8c))|set(range(0x90,0xa3))|
  set(range(0xb3,0xbb))|{0xc3}|set(range(0xd1,0xdd))|set(range(0xdf,0xe1))|
  {0xfe00,0xfe01,0xfe02,0xfe03,0xfe04,0xfe05,0xfe0f,0xfe11,0xfe13,0xfe14,0xfe17,0xfe18,0xfe1a,0xfe1d})


def il_calls(data:bytes,resolve,*,instruction_limit:int=100000)->dict:
    b=Buffer(data);i=0;steps=0;calls=[];branches=[]
    try:
        while i<len(data):
            if steps>=instruction_limit:raise CLRParseError('instruction budget reached')
            steps+=1;start=i;op=b.u1(i);i+=1
            if op==0xfe:
                op=(op<<8)|b.u1(i);i+=1
            size=0
            if op in OP_SHORT:size=1
            elif op in OP_WORD:size=2
            elif op in OP_DWORD:size=4
            elif op in OP_EIGHT:size=8
            elif op==0x45:
                casecount=b.u4(i)
                if casecount>20000:raise CLRParseError('switch case budget exceeded')
                size=4+casecount*4
            elif op not in OP_DEFAULT:
                raise CLRParseError(f'unknown CIL opcode {op:#x} at {start}')
            operand=b.slice(i,size)
            if op in OP_CALL:
                token=int.from_bytes(operand,'little')
                calls.append({'il_offset':start,'opcode':OP_CALL[op], 'token':f'0x{token:08x}',
                              'callee':resolve(token),
                              'dispatch':'potentially dynamic' if op in (0x6f,0xfe07,0x29) else 'static reference only'})
            if op in set(range(0x2b,0x46))|{0xdd,0xde}:
                branches.append({'il_offset':start,'opcode':f'{op:02x}','operand_hex':operand.hex()})
            i+=size
        return {'bytes':len(data),'instruction_count':steps,'calls':calls,'branch_instructions':branches,
                'walk_complete':True}
    except CLRParseError as exc:
        return {'bytes':len(data),'instruction_count':steps,'calls':calls,'branch_instructions':branches,
                'walk_complete':False,'warning':str(exc)}


def parse_method_body(b:Buffer,at_rva,rva:int,resolve):
    if rva==0:return {'has_body':False,'reason':'abstract/pinvoke/runtime/extern or no RVA'}
    try:
        pos=at_rva(rva,1)
        first=b.u1(pos)
        if first&3==2:
            code_size=first>>2;headersize=1;more_sects=False
        elif first&3==3:
            flags=b.u2(pos);headersize=((flags>>12)&15)*4
            if headersize<12 or headersize>64:raise CLRParseError('invalid fat header size')
            code_size=b.u4(pos+4);more_sects=bool(flags&8)
        else:raise CLRParseError('unsupported CIL method body header')
        if code_size>MAX_METHOD_BYTES:raise CLRParseError('CIL method body budget exceeded')
        pos=at_rva(rva,headersize+code_size)
        code=b.slice(pos+headersize,code_size)
        result={'has_body':True,'rva':f'0x{rva:x}','header_bytes':headersize,
                'has_exception_or_extra_sections':more_sects,'cil':il_calls(code,resolve)}
        if more_sects:result['coverage_warning']='extra sections / exception tables not parsed'
        return result
    except CLRParseError as exc:
        return {'has_body':True,'rva':f'0x{rva:x}','parse_error':str(exc)}


def analyze_dotnet(data:bytes)->dict:
    if len(data)>MAX_FILE:raise CLRParseError('file byte budget exceeded')
    base,size,at_rva,sections=pe_metadata_location(data)
    md=Metadata(data,base,size)
    b=Buffer(data)
    typedefs=md.tables.get(2,[])
    methods=md.tables.get(6,[])
    memberrefs=md.tables.get(10,[])
    refs=md.tables.get(1,[])
    assemblyrefs=md.tables.get(35,[])
    namespaces=[]
    owner_by_method={}
    for i,row in enumerate(typedefs):
        # TypeDef.MethodList indexes MethodDef, one-based. Last type extends to end.
        start=row[5]
        finish=typedefs[i+1][5] if i+1<len(typedefs) else len(methods)+1
        typename=(md.string(row[2])+'.' if md.string(row[2]) else '')+md.string(row[1])
        item={'token':f'0x{0x02000000+i+1:08x}','name':typename,
              'flags':row[0],'base_type':md.resolve_type(row[3]),
              'method_count':max(0,finish-start)}
        namespaces.append(item)
        for m in range(max(1,start),min(finish,len(methods)+1)):
            owner_by_method[m]=typename

    def resolve(token):
        table=(token>>24)&255;rid=token&0xffffff
        if rid==0:return {'kind':'invalid','reason':'zero row'}
        if table==6 and rid<=len(methods):
            m=methods[rid-1]
            return {'kind':'methoddef','owner':owner_by_method.get(rid,'unknown'),
                    'name':md.string(m[3]),'signature_hex':md.blob(m[4]).hex()[:128]}
        if table==10 and rid<=len(memberrefs):
            r=memberrefs[rid-1]
            parent=md.decode_index('MemberRefParent',r[0])
            owner=None
            if parent:
                tid,index=parent
                if tid==2 and index<=len(typedefs):owner=namespaces[index-1]['name']
                elif tid==1 and index<=len(refs):
                    typ=refs[index-1]
                    owner=(md.string(typ[2])+'.' if md.string(typ[2]) else '')+md.string(typ[1])
                elif tid==26:
                    modules=md.tables.get(26,[])
                    if index<=len(modules):owner=md.string(modules[index-1][0])
                elif tid==6 and index<=len(methods):owner=owner_by_method.get(index)
            return {'kind':'memberref','owner':owner,'name':md.string(r[1]),'signature_hex':md.blob(r[2]).hex()[:128]}
        if table==43:return {'kind':'methodspec','resolved':False}
        if table==17:return {'kind':'standalone_signature','resolved':False}
        return {'kind':'unknown_token','table':table,'row':rid}

    method_results=[]
    for rid,row in enumerate(methods,1):
        rva,impl_flags,flags,name,sig,params=row
        result={'token':f'0x{0x06000000+rid:08x}', 'owner':owner_by_method.get(rid,'unknown'),
                'name':md.string(name),'flags':flags,'impl_flags':impl_flags,
                'signature_hex':md.blob(sig).hex()[:512],
                'body':parse_method_body(b,at_rva,rva,resolve)}
        method_results.append(result)
    managed_imports=[]
    for row in md.tables.get(28,[]):
        module=md.tables.get(26,[])
        scope=md.string(module[row[3]-1][0]) if row[3] and row[3]<=len(module) else None
        managed_imports.append({'native_library':scope,'import_name':md.string(row[2]),'flags':row[0]})
    return {'format':'dotnet-cli','sha256':hashlib.sha256(data).hexdigest(),
            'metadata_version':md.version,'sections':sections,
            'metadata_row_counts':{str(k):v for k,v in md.row_counts.items()},
            'assemblies_referenced':[md.string(row[6]) for row in assemblyrefs],
            'types':namespaces,'methods':method_results,'native_imports':managed_imports,
            'methods_with_cil':sum(1 for m in method_results if m['body'].get('has_body')),
            'cil_walk_complete':all(not m['body'].get('parse_error') and m['body'].get('cil',{}).get('walk_complete',True) for m in method_results),
            'evidence_level':'ECMA-335 metadata and static CIL call sites only: reflection, runtime dispatch and proxies unresolved'}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('path',type=Path);ap.add_argument('-o','--output',type=Path)
    args=ap.parse_args(argv)
    try:
        if args.path.is_symlink() or not args.path.is_file():raise CLRParseError('regular non-symlink required')
        if args.path.stat().st_size>MAX_FILE:raise CLRParseError('file too large')
        result=analyze_dotnet(args.path.read_bytes())
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            if args.path.resolve()==args.output.resolve():raise CLRParseError('output aliases input')
            write_exclusive(args.output,payload,[args.path])
        else:print(payload,end='')
        return 0 if result['cil_walk_complete'] else 3
    except (CLRParseError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
