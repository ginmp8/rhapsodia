#!/usr/bin/env python3
"""Offline metadata for PE resources, macOS bundles and recorded ELF notes.

Opaque evidence only: no executable parsing plugins or target execution.
"""
from __future__ import annotations

import hashlib
import plistlib
import struct
from pathlib import Path
from artifact_index import ArtifactError,digest,VirtualArtifact

MAX_BINARY = 64 * 1024 * 1024


def _unpack(data:bytes,fmt:str,offset:int):
    length=struct.calcsize(fmt)
    if offset<0 or offset+length>len(data):
        raise ArtifactError('truncated binary structure')
    return struct.unpack_from(fmt,data,offset)


def inspect_pe_resources(raw:bytes,max_resources:int=900) -> dict:
    """Enumerate PE resource directory entries and hash bounded opaque leaves."""
    if len(raw)<256 or raw[:2]!=b'MZ':
        raise ArtifactError('not a PE file')
    pe=_unpack(raw,'<I',0x3c)[0]
    if raw[pe:pe+4]!=b'PE\0\0':raise ArtifactError('invalid PE signature')
    machine,sec_count,_,_,_,opt_size,_=_unpack(raw,'<HHIIIHH',pe+4)
    opt=pe+24
    magic=_unpack(raw,'<H',opt)[0]
    if magic==0x10b:directory=opt+96
    elif magic==0x20b:directory=opt+112
    else:raise ArtifactError('unsupported PE optional header')
    if directory+24>opt+opt_size:raise ArtifactError('missing PE resource data directory')
    rva,size=_unpack(raw,'<II',directory+16)
    sections=[]
    sh=opt+opt_size
    for i in range(min(sec_count,96)):
        at=sh+i*40
        section_name=raw[at:at+8].split(b'\0',1)[0].decode('ascii','replace')
        vsize,virt,rawsize,foff=_unpack(raw,'<IIII',at+8)
        sections.append({'name':section_name,'rva':virt,'virtual_size':vsize,
                         'raw_size':rawsize,'file_offset':foff})
    def locate(addr:int,need:int=1):
        for s in sections:
            span=max(s['virtual_size'],s['raw_size'])
            if s['rva']<=addr and addr+need<=s['rva']+span:
                offset=s['file_offset']+addr-s['rva']
                if addr-s['rva']+need<=s['raw_size'] and offset+need<=len(raw):return offset
        raise ArtifactError('PE RVA outside mapped file data')
    outcome={'format':'pe-resources','machine':machine,'sections':sections,'resource_rva':rva,
             'resource_size':size,'resources':[],'unknowns':[],'complete':True}
    if not rva or not size:return outcome
    base=locate(rva,16)
    seen=set()
    def name_of(raw_name):
        if raw_name & 0x80000000:
            off=base+(raw_name&0x7fffffff)
            chars=_unpack(raw,'<H',off)[0]
            if chars>400:raise ArtifactError('resource name size limit')
            start=off+2
            if start+2*chars>len(raw):raise ArtifactError('truncated resource name')
            return raw[start:start+2*chars].decode('utf-16-le','replace')
        return str(raw_name)
    def walk(offset,labels,depth):
        if depth>3:raise ArtifactError('PE resources deeper than supported directory tree')
        if offset in seen:raise ArtifactError('cyclic PE resource directory')
        seen.add(offset)
        at=base+offset
        count_name,count_id=_unpack(raw,'<HH',at+12)
        if count_name+count_id>MAX_BINARY//16 or count_name+count_id>max_resources*8:
            raise ArtifactError('PE resource directory size bound')
        for i in range(count_name+count_id):
            if len(outcome['resources'])>=max_resources:
                outcome['complete']=False
                outcome['unknowns'].append('resource count limit reached')
                return
            ref,child=_unpack(raw,'<II',at+16+i*8)
            label=name_of(ref)
            if child & 0x80000000:
                walk(child&0x7fffffff,labels+[label],depth+1)
            else:
                data_rva,data_size,codepage,_=_unpack(raw,'<IIII',base+child)
                if data_size>MAX_BINARY:
                    outcome['unknowns'].append('resource leaf too large:'+label)
                    outcome['complete']=False
                    continue
                raw_off=locate(data_rva,data_size)
                blob=raw[raw_off:raw_off+data_size]
                outcome['resources'].append({'path':labels+[label],'rva':data_rva,'file_offset':raw_off,
                                             'size':data_size,'codepage':codepage,'sha256':digest(blob)})
    try:
        walk(0,[],0)
    except ArtifactError as exc:
        outcome['complete']=False
        outcome['unknowns'].append(str(exc))
    return outcome


def inspect_apple_bundle(artifact:VirtualArtifact)->dict:
    plists=sorted(x for x in artifact.entries if x.endswith('Info.plist'))
    items=[];unknowns=[]
    for name in plists[:50]:
        try:
            data=artifact.read(name,1_000_000)
            details=plistlib.loads(data)
            if not isinstance(details,dict):
                raise ArtifactError('plist root is not a dictionary')
            allow=('CFBundleIdentifier','CFBundleName','CFBundleExecutable','CFBundlePackageType',
                   'CFBundleShortVersionString','CFBundleVersion','NSPrincipalClass','LSMinimumSystemVersion')
            items.append({'path':name,'sha256':digest(data),'fields':{
                k:str(details[k])[:300] for k in allow if isinstance(details.get(k),(str,int))},
                'keys':sorted(k for k in details if isinstance(k,str))[:250]})
        except (ArtifactError,UnicodeError,ValueError,TypeError,OverflowError,plistlib.InvalidFileException) as exc:
            unknowns.append({'path':name,'reason':type(exc).__name__})
    if len(plists)>50:unknowns.append({'reason':'plist entry bound'})
    return {'format':'apple-bundle-metadata','source_sha256':artifact.source_sha(),'items':items,
            'unknowns':unknowns,'complete':not unknowns,
            'evidence_level':'declared bundle metadata only; runtime loading and code signatures unverified'}


def inspect_elf_notes(data:bytes,max_notes:int=500) -> dict:
    if data[:4]!=b'\x7fELF' or len(data)<64:
        raise ArtifactError('not an ELF binary')
    ident=data[4];endian=data[5]
    if ident not in (1,2) or endian not in (1,2):
        raise ArtifactError('unsupported ELF bitness or byte order')
    byte_order='<' if endian==1 else '>'
    if ident==2:
        e_type=_unpack(data,byte_order+'H',16)[0]
        phoff=_unpack(data,byte_order+'Q',32)[0]
        entry_size,phnum=_unpack(data,byte_order+'HH',54)
    else:
        e_type=_unpack(data,byte_order+'H',16)[0]
        phoff=_unpack(data,byte_order+'I',28)[0]
        entry_size,phnum=_unpack(data,byte_order+'HH',42)
    if phnum>1024:raise ArtifactError('ELF program header count limit')
    notes=[];errors=[]
    for i in range(phnum):
        at=phoff+i*entry_size
        if ident==2:
            typ,flags,p_offset,p_vaddr,p_phys,p_filesz,memsz,align=_unpack(data,byte_order+'IIQQQQQQ',at)
        else:
            typ,p_offset,p_vaddr,p_phys,p_filesz,memsz,flags,align=_unpack(data,byte_order+'IIIIIIII',at)
        if typ!=4:continue
        pos=p_offset;end=min(p_offset+p_filesz,len(data))
        while pos<end:
            try:
                if len(notes)>=max_notes:
                    errors.append('note count limit reached');break
                namesz,descsz,notetype=_unpack(data,byte_order+'III',pos)
                pos+=12
                if namesz>4096 or descsz>MAX_BINARY or pos+namesz>end:
                    raise ArtifactError('note bounds exceeded')
                label=data[pos:pos+namesz].rstrip(b'\x00').decode('ascii','replace')
                pos+=(namesz+3)&~3
                if pos+descsz>end:raise ArtifactError('note payload truncated')
                body=data[pos:pos+descsz]
                notes.append({'program_index':i,'kind':notetype,'owner':label[:100],
                              'size':descsz,'file_offset':pos,'sha256':digest(body)})
                pos+=(descsz+3)&~3
            except ArtifactError as exc:
                errors.append(str(exc));break
    return {'format':'elf-note-inventory','elf_type':e_type,'possible_core':e_type==4,
            'notes':notes,'unknowns':errors,'complete':not errors,
            'evidence_level':'ELF recorded notes only; CPU registers/core memory require ABI-specific decoders'}


def inspect_binary(raw:bytes,kind:str='auto')->dict:
    if len(raw)>MAX_BINARY:raise ArtifactError('binary budget exceeded')
    if kind=='pe-resources' or (kind=='auto' and raw[:2]==b'MZ'):
        return inspect_pe_resources(raw)
    if kind=='elf-notes' or (kind=='auto' and raw[:4]==b'\x7fELF'):
        return inspect_elf_notes(raw)
    if kind=='auto':
        from format_probes import scan_firmware
        return {'format':'signature-candidates','report':scan_firmware(raw),
                'evidence_level':'byte signatures only; no auto extraction or firmware execution'}
    raise ArtifactError('unsupported binary inspection mode')
