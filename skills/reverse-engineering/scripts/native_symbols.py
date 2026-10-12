#!/usr/bin/env python3
"""Bounded, offline native symbol and import/export inspection: ELF/PE/Mach-O.

No process execution, native decompilation or resolved control-flow graph.
Unknown layouts fail explicitly rather than emit complete-looking results.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from json_writer import write_exclusive

MAX_FILE=128*1024*1024
MAX_SECTIONS=4096
MAX_SYMBOLS=40000

class NativeError(ValueError):pass

class Binary:
    def __init__(self,data:bytes,endian='<'):
        self.data=data;self.endian=endian
    def get(self,fmt,p):
        sz=struct.calcsize(fmt)
        if p<0 or p+sz>len(self.data):raise NativeError(f'truncated at {p}')
        return struct.unpack_from(fmt,self.data,p)
    def read(self,p,size):
        if p<0 or size<0 or p+size>len(self.data):raise NativeError(f'bad extent at {p}')
        return self.data[p:p+size]
    def str(self,p,cap=4096):
        if p<0 or p>=len(self.data):return '<invalid-offset>'
        raw=self.data[p:min(len(self.data),p+cap)].split(b'\0',1)[0]
        return raw.decode('utf-8','replace')


def parse_elf(data:bytes):
    b=Binary(data)
    if data[:4]!=b'\x7fELF':raise NativeError('not ELF')
    bits={1:32,2:64}.get(data[4]);endian={1:'<',2:'>'}.get(data[5])
    if not bits or not endian:raise NativeError('unknown ELF class or endian')
    fmt=endian+('HHIIIIIHHHHHH' if bits==32 else 'HHIQQQIHHHHHH')
    head=b.get(fmt,16)
    _type,machine,_ver,entry,phoff,shoff,_flags,ehsize,phsize,phnum,shsize,shnum,shstrndx=head
    s_fmt=endian+('IIIIIIIIII' if bits==32 else 'IIQQQQIIQQ')
    entrysize=struct.calcsize(s_fmt)
    if shnum>MAX_SECTIONS or shnum and (shsize<entrysize or not shoff):raise NativeError('unsupported section count or layout')
    sections=[]
    for i in range(shnum):
        name,typ,flags,addr,offset,size,link,info,align,entsize=b.get(s_fmt,shoff+i*shsize)
        sections.append({'id':i,'type':typ,'name_offset':name,'offset':offset,'size':size,'link':link,
                         'info':info,'entsize':entsize,'virtual_address':addr})
    if shstrndx<len(sections):
        sec=sections[shstrndx];names=Binary(b.read(sec['offset'],sec['size']))
        for s in sections:s['name']=names.str(s['name_offset'],512)
    symbols=[];needed=[];relocations=[];warnings=[];symbols_by_section={}
    for section in sections:
        typ=section['type']
        if typ in (2,11):
            if section['link']>=len(sections):raise NativeError('invalid ELF symtab link')
            st=sections[section['link']]
            names=Binary(b.read(st['offset'],st['size']))
            sz=section['entsize']
            minimum=16 if bits==32 else 24
            if sz<minimum:raise NativeError('ELF symtab entry too small')
            count=section['size']//sz
            if count>MAX_SYMBOLS:raise NativeError('symbol budget exceeded')
            entries=[]
            for i in range(count):
                p=section['offset']+i*sz
                if bits==64:
                    st_name,info,other,shindex,value,size=b.get(endian+'IBBHQQ',p)
                else:
                    st_name,value,size,info,other,shindex=b.get(endian+'IIIBBH',p)
                name=names.str(st_name)
                obj={'table':section.get('name',section['id']),'index':i,'name':name,
                     'address':f'0x{value:x}','size':size,'binding':info>>4,'type':info&0x0f,
                     'defined':bool(shindex),'visibility':other&3}
                entries.append(obj)
                if name and len(symbols)<MAX_SYMBOLS:symbols.append(obj)
            symbols_by_section[section['id']]=entries
        if typ==6:
            if section['link']>=len(sections):raise NativeError('invalid ELF dynamic string link')
            st=sections[section['link']];strings=Binary(b.read(st['offset'],st['size']))
            fmt_dyn=endian+('iI' if bits==32 else 'qQ')
            dyn_size=struct.calcsize(fmt_dyn)
            if section['size']//dyn_size>MAX_SYMBOLS:raise NativeError('dynamic table budget exceeded')
            for i in range(section['size']//dyn_size):
                tag,value=b.get(fmt_dyn,section['offset']+i*dyn_size)
                if tag==1:needed.append(strings.str(value))
                if tag==0:break
    for section in sections:
        if section['type'] not in (4,9):continue
        entsz=section['entsize']
        base_fmt=endian+('IIi' if bits==32 and section['type']==4 else
                         'II' if bits==32 else 'QQq' if section['type']==4 else 'QQ')
        minimum=struct.calcsize(base_fmt)
        if entsz<minimum:raise NativeError('invalid relocation entry size')
        count=section['size']//entsz
        if count>MAX_SYMBOLS:raise NativeError('relocation budget exceeded')
        symtab=symbols_by_section.get(section['link'])
        for i in range(min(count,5000)):
            values=b.get(base_fmt,section['offset']+i*entsz)
            rva,info=values[:2]
            ref=info>>32 if bits==64 else info>>8
            kind=info&0xffffffff if bits==64 else info&0xff
            name=symtab[ref]['name'] if symtab and ref<len(symtab) else None
            relocations.append({'section':section.get('name'),'offset':f'0x{rva:x}',
                                'relocation_type':kind,'symbol':name})
        if count>5000:warnings.append(f"relocations truncated for section {section['id']}")
    return {'format':'elf','machine':machine,'bits':bits,'endianness':'little' if endian=='<' else 'big',
            'entry':f'0x{entry:x}','section_count':len(sections), 'needed_libraries':needed,
            'symbols':symbols,'relocations':relocations,'warnings':warnings,
            'coverage':'symbol table and relocations only; no disassembly or dynamic linker resolution'}


def parse_pe(data:bytes):
    b=Binary(data)
    if data[:2]!=b'MZ':raise NativeError('not PE')
    pe=b.get('<I',0x3c)[0]
    if b.read(pe,4)!=b'PE\0\0':raise NativeError('bad PE signature')
    nsect=b.get('<H',pe+6)[0];optlen=b.get('<H',pe+20)[0]
    if nsect>MAX_SECTIONS:raise NativeError('PE section count exceeded')
    optional=pe+24;magic=b.get('<H',optional)[0]
    if magic not in (0x10b,0x20b):raise NativeError('unsupported PE optional header')
    is64=magic==0x20b
    base=optional+(112 if is64 else 96)
    count=b.get('<I',base-4)[0]
    if count>16:count=16
    if base+count*8>optional+optlen:raise NativeError('bad PE directory')
    directories=[b.get('<II',base+i*8) for i in range(count)]
    sections=[]
    for i in range(nsect):
        p=optional+optlen+40*i
        vsize,addr,rsize,raw=b.get('<IIII',p+8)
        sections.append({'name':b.read(p,8).rstrip(b'\0').decode('ascii','replace'),
                         'rva':addr,'virtual_size':vsize,'raw_size':rsize,'raw':raw})
    def rva_offset(rva,n=1):
        if rva==0:raise NativeError('null RVA')
        for s in sections:
            if s['rva']<=rva and rva+n<=s['rva']+s['raw_size']:
                p=s['raw']+rva-s['rva'];b.read(p,n);return p
        raise NativeError(f'RVA not backed by file: {rva:#x}')
    imports=[];exports=[];warnings=[]
    if len(directories)>1 and directories[1][0]:
        p=rva_offset(directories[1][0],20)
        for i in range(2048):
            origin,time,forwarder,name,thunk=b.get('<IIIII',p+i*20)
            if not any((origin,time,forwarder,name,thunk)):break
            dll=b.str(rva_offset(name))
            entries=[];thunk_rva=origin or thunk
            thunksize=8 if is64 else 4
            for j in range(4000):
                entry=b.get('<Q' if is64 else '<I',rva_offset(thunk_rva+j*thunksize,thunksize))[0]
                if entry==0:break
                isordinal=bool(entry&(1<<(63 if is64 else 31)))
                if isordinal:entries.append({'ordinal':entry&65535})
                else:
                    nameoff=rva_offset(entry+2)
                    entries.append({'name':b.str(nameoff)})
            imports.append({'library':dll,'symbols':entries})
    if directories and directories[0][0]:
        p=rva_offset(directories[0][0],40)
        flags,timestamp,ver_major,ver_minor,name,ordinalbase,numfunc,numnames,func_rva,names_rva,ord_rva=b.get('<IIHHIIIIIII',p)
        if numnames>MAX_SYMBOLS or numfunc>MAX_SYMBOLS:raise NativeError('PE export entry budget exceeded')
        for i in range(numnames):
            nrva=b.get('<I',rva_offset(names_rva+4*i,4))[0]
            ordinal=b.get('<H',rva_offset(ord_rva+2*i,2))[0]
            funcrva=b.get('<I',rva_offset(func_rva+4*ordinal,4))[0] if ordinal<numfunc else 0
            exports.append({'name':b.str(rva_offset(nrva)),'ordinal':ordinalbase+ordinal,
                            'rva':f'0x{funcrva:x}'})
    return {'format':'pe','is_pe32_plus':is64,'sections':sections,'imports':imports,'exports':exports,
            'warnings':warnings, 'coverage':'file-backed native imports/exports; no disassembly, API-set forwarding resolution or runtime effects'}


def parse_macho(data:bytes):
    magic=data[:4]
    formats={b'\xfe\xed\xfa\xce':('>',32),b'\xce\xfa\xed\xfe':('<',32),
             b'\xfe\xed\xfa\xcf':('>',64),b'\xcf\xfa\xed\xfe':('<',64)}
    if magic not in formats:raise NativeError('not a supported thin Mach-O (fat binaries need slice extraction)')
    endian,bits=formats[magic];b=Binary(data)
    if bits==32:
        cputype,subtype,filetype,ncmds,bytes_,flags=b.get(endian+'IIIIII',4)
        pos=28
    else:
        cputype,subtype,filetype,ncmds,bytes_,flags,reserved=b.get(endian+'IIIIIII',4)
        pos=32
    if ncmds>MAX_SECTIONS or bytes_>len(data)-pos:raise NativeError('bad Mach-O command area')
    end=pos+bytes_;libraries=[];segments=[]
    for i in range(ncmds):
        if pos+8>end:raise NativeError('truncated load command')
        command,size=b.get(endian+'II',pos)
        if size<8 or pos+size>end:raise NativeError('invalid Mach-O command length')
        kind=command&0x7fffffff
        if kind in (0xc,0x18,0x1f,0x23,0x20):
            off=b.get(endian+'I',pos+8)[0]
            if off<size:libraries.append(b.str(pos+off,512))
        elif kind in (1,0x19):
            segments.append(b.read(pos+8,16).rstrip(b'\0').decode('ascii','replace'))
        pos+=size
    return {'format':'mach-o','bits':bits,'endianness':'little' if endian=='<' else 'big',
            'cpu_type':cputype,'file_type':filetype,'linked_libraries':libraries,'segments':segments,
            'coverage':'Mach-O load commands; no dyld resolution, symbols, disassembly, fat slices or runtime proof'}



def parse_fat_macho(data:bytes):
    """Inspect fat Mach-O architecture table and bounded thin slices in-place."""
    if len(data)>MAX_FILE:raise NativeError('fat Mach-O byte budget exceeded')
    if data[:4] not in (b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf',
                        b'\xbe\xba\xfe\xca', b'\xbf\xba\xfe\xca'):
        raise NativeError('not a fat Mach-O binary')
    endian='>' if data[0] == 0xca else '<'
    wide=data[3] in (0xbf,0xca) and data[:4] in (b'\xca\xfe\xba\xbf',b'\xbf\xba\xfe\xca')
    if len(data)<8:raise NativeError('truncated fat header')
    number=struct.unpack_from(endian+'I',data,4)[0]
    if not 1<=number<=32:raise NativeError('fat architecture count out of bounds')
    width=32 if wide else 20
    if 8+number*width>len(data):raise NativeError('truncated fat architecture table')
    parsed=[];seen=[]
    for i in range(number):
        p=8+i*width
        if wide:
            cpu,subtype,offset,size,align,reserved=struct.unpack_from(endian+'IIQQII',data,p)
        else:
            cpu,subtype,offset,size,align=struct.unpack_from(endian+'IIIII',data,p)
        if not size or offset<8+number*width or size>len(data)-offset or align>32:
            raise NativeError('fat slice boundaries invalid')
        if any(offset<high and offset+size>low for low,high in seen):
            raise NativeError('overlapping fat architecture slices')
        seen.append((offset,offset+size))
        child=parse_macho(data[offset:offset+size]);child['slice_sha256']=hashlib.sha256(data[offset:offset+size]).hexdigest()
        parsed.append({'cpu_type':cpu,'cpu_subtype':subtype,'offset':offset,'size':size,'slice':child})
    return {'format':'fat-mach-o','architectures':parsed,
            'coverage':'Fat header and thin slice load commands; not disassembly, imports resolution or behavior'}


def analyze_native(data):
    if len(data)>MAX_FILE:raise NativeError('byte budget exceeded')
    if data.startswith(b'\x7fELF'):out=parse_elf(data)
    elif data.startswith(b'MZ'):out=parse_pe(data)
    elif data[:4] in (b'\xca\xfe\xba\xbe',b'\xca\xfe\xba\xbf',
                       b'\xbe\xba\xfe\xca',b'\xbf\xba\xfe\xca'):out=parse_fat_macho(data)
    else:out=parse_macho(data)
    out['sha256']=hashlib.sha256(data).hexdigest()
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path);p.add_argument('-o','--output',type=Path)
    a=p.parse_args(argv)
    try:
        if not a.path.is_file() or a.path.is_symlink():raise NativeError('regular input required')
        if a.path.stat().st_size>MAX_FILE:raise NativeError('byte budget exceeded')
        obj=analyze_native(a.path.read_bytes())
        content=json.dumps(obj,indent=2,ensure_ascii=False)+'\n'
        if a.output:
            if a.path.resolve()==a.output.resolve():raise NativeError('output aliases input')
            write_exclusive(a.output,content,[a.path])
        else:print(content,end='')
        return 0
    except (NativeError,OSError) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
