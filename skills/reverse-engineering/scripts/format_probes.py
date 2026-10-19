#!/usr/bin/env python3
"""Evidence-oriented, no-execution static format probes with bounded I/O.

Supports PE/CLI headers and imports, ELF section metadata, WASM import/export,
Java class declarations, DEX headers, HAR request summaries, SQLite schema,
and firmware signature candidates. These probes are NOT disassemblers or
substitutes for REA's specialist analyzers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import struct
import sys
import urllib.parse
from pathlib import Path

from recon import emit

MAX_BYTES = 32 * 1024 * 1024
MAX_SECTIONS = 384
MAX_ITEMS = 2000


class ProbeError(ValueError):
    pass


def at(data: bytes, pos: int, size: int) -> bytes:
    if pos < 0 or size < 0 or size > 1 << 20 or pos + size > len(data):
        raise ProbeError(f'Unable to read {size} bytes at offset 0x{pos:x}: truncated or invalid input')
    return data[pos:pos + size]


def unpack(fmt: str, data: bytes, offset: int) -> tuple:
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, at(data, offset, size))


def cstring(data: bytes, pos: int, limit: int = 512) -> str:
    if pos < 0 or pos >= len(data):
        return '<unavailable>'
    raw = data[pos: min(len(data), pos + limit)].split(b'\0', 1)[0]
    return raw.decode('utf-8', 'replace')


def read_varuint(data: bytes, pos: int, end: int, max_bits: int = 32) -> tuple[int, int]:
    value = 0
    for index in range(5 if max_bits == 32 else 10):
        if pos >= end:
            raise ProbeError('Truncated LEB128 field')
        byte = data[pos]; pos += 1
        value |= (byte & 0x7f) << (7 * index)
        if byte & 0x80 == 0:
            if value >= (1 << max_bits): raise ProbeError('LEB128 value outside expected range')
            return value, pos
    raise ProbeError('Overlong LEB128 field')


def read_name(data: bytes, pos: int, end: int) -> tuple[str, int]:
    length, pos = read_varuint(data, pos, end)
    if length > 4096 or pos + length > end: raise ProbeError('Oversized/truncated binary string')
    return data[pos:pos + length].decode('utf-8', 'replace'), pos + length


def scan_wasm(data: bytes) -> dict:
    if not data.startswith(b'\x00asm'):
        raise ProbeError('Not a WebAssembly binary')
    version = unpack('<I', data, 4)[0]
    if version != 1: return {'format': 'wasm', 'version': version, 'supported_version': False}
    pos = 8
    types = {0:'custom',1:'type',2:'import',3:'function',4:'table',5:'memory',6:'global',7:'export',8:'start',9:'element',10:'code',11:'data',12:'data-count'}
    sections = []; imports = []; exports = []; warnings = []
    while pos < len(data):
        if len(sections) >= MAX_SECTIONS:
            warnings.append('Section limit reached'); break
        start = pos; sid = data[pos]; pos += 1
        length, pos = read_varuint(data, pos, len(data))
        if length > len(data) - pos: raise ProbeError(f'Truncated WASM section at {start}')
        end = pos + length
        item = {'offset': start, 'id': sid, 'name': types.get(sid,'unknown'), 'payload_bytes': length}
        if sid == 0:
            item['custom_name'], _ = read_name(data, pos, end)
        if sid in (2, 7):
            count, cur = read_varuint(data, pos, end)
            if count > MAX_ITEMS:
                warnings.append(f'Section {sid} has >{MAX_ITEMS} entries; only a bounded prefix is decoded')
            for _ in range(min(count, MAX_ITEMS)):
                if sid == 2:
                    module, cur = read_name(data, cur, end)
                    name, cur = read_name(data, cur, end)
                    if cur >= end: raise ProbeError('Truncated WASM import')
                    kind = data[cur]; cur += 1
                    if kind == 0: _, cur = read_varuint(data, cur, end)
                    elif kind in (1,2):
                        if kind == 1:
                            # table type: ref element type then limits
                            cur += 1
                        flags, cur = read_varuint(data, cur, end)
                        _, cur = read_varuint(data, cur, end, 64 if flags & 4 else 32)
                        if flags & 1: _, cur = read_varuint(data, cur, end, 64 if flags & 4 else 32)
                    elif kind == 3: cur += 2  # value type and mutability
                    elif kind == 4: _, cur = read_varuint(data, cur, end); _, cur = read_varuint(data, cur, end)
                    else: raise ProbeError('Unsupported WASM import kind')
                    if cur > end: raise ProbeError('Truncated WASM import type')
                    imports.append({'module': module, 'name': name, 'kind': kind})
                else:
                    name, cur = read_name(data, cur, end)
                    if cur >= end: raise ProbeError('Truncated WASM export')
                    kind = data[cur]; cur += 1
                    index, cur = read_varuint(data, cur, end)
                    exports.append({'name': name, 'kind': kind, 'index': index})
        sections.append(item)
        pos = end
    return {'format': 'wasm', 'version': version, 'sections': sections, 'imports': imports,
            'exports': exports, 'warnings': warnings,
            'coverage': 'structural metadata only, no validation/WAT/code reconstruction'}


def scan_elf(data: bytes) -> dict:
    if not data.startswith(b'\x7fELF'): raise ProbeError('Not ELF')
    if len(data) < 52: raise ProbeError('Truncated ELF header')
    bits = {1: 32, 2: 64}.get(data[4])
    endian = {1: '<', 2: '>'}.get(data[5])
    if not bits or not endian: raise ProbeError('Unsupported ELF class or endianness')
    if bits == 32:
        fields = unpack(endian + 'HHIIIIIHHHHHH', data, 16)
        (type_, machine, version, entry, phoff, shoff, flags, ehsize, phentsz,
         phnum, shentsz, shnum, shstrndx) = fields
    else:
        fields = unpack(endian + 'HHIQQQIHHHHHH', data, 16)
        (type_, machine, version, entry, phoff, shoff, flags, ehsize, phentsz,
         phnum, shentsz, shnum, shstrndx) = fields
    fmt = endian + ('IIIIIIIIII' if bits == 32 else 'IIQQQQIIQQ')
    minimum = struct.calcsize(fmt)
    sections = []
    if shnum and shnum <= MAX_SECTIONS and shentsz >= minimum and shoff > 0:
        for idx in range(shnum):
            (name, stype, sflags, addr, offset, size, link, info, align, entsize) = unpack(fmt, data, shoff + idx * shentsz)
            sections.append({'index': idx, 'name_offset': name, 'type': stype, 'offset': offset, 'bytes': size,
                             'address': f'0x{addr:x}', 'flags': sflags, 'entry_bytes': entsize})
        if shstrndx < len(sections):
            strtab = sections[shstrndx]
            if strtab['offset'] + strtab['bytes'] <= len(data):
                blob = data[strtab['offset']:strtab['offset'] + strtab['bytes']]
                for section in sections: section['name'] = cstring(blob, section['name_offset'])
    return {'format': 'elf', 'bits': bits, 'endianness': 'little' if endian == '<' else 'big',
            'type': type_, 'machine': machine, 'entry': f'0x{entry:x}', 'program_header_count': phnum,
            'section_header_count': shnum, 'sections': sections,
            'coverage': 'file-backed header/section structure; no disassembly, dynamic symbols or decompilation',
            'complete_section_table': shnum == len(sections)}


def scan_pe(data: bytes) -> dict:
    if not data.startswith(b'MZ'): raise ProbeError('Not PE')
    peoff = unpack('<I', data, 0x3c)[0]
    if peoff > 1 << 24 or at(data, peoff, 4) != b'PE\0\0': raise ProbeError('Invalid PE signature')
    machine, nsects, timestamp, symbol_ptr, nsyms, opt_size, characteristics = unpack('<HHIIIHH', data, peoff + 4)
    if nsects > MAX_SECTIONS: raise ProbeError('Too many PE sections')
    opt = peoff + 24
    opt_magic = unpack('<H', data, opt)[0]
    if opt_magic not in (0x10b, 0x20b): raise ProbeError('Unsupported PE optional header')
    if opt_size < (120 if opt_magic == 0x10b else 136): raise ProbeError('Optional header too short')
    is64 = opt_magic == 0x20b
    section_offset = opt + opt_size
    sections = []
    for i in range(nsects):
        pos = section_offset + i * 40
        name = at(data, pos, 8).rstrip(b'\0').decode('ascii', 'replace')
        virtual_size, virtual_addr, file_size, file_ptr = unpack('<IIII', data, pos + 8)
        sections.append({'name': name, 'rva': virtual_addr, 'virtual_bytes': virtual_size,
                         'file_offset': file_ptr, 'file_bytes': file_size})
    def rva_offset(rva: int) -> int:
        for sec in sections:
            start = sec['rva']; span = max(sec['virtual_bytes'], sec['file_bytes'])
            if start <= rva < start + span and rva - start < sec['file_bytes']:
                return sec['file_offset'] + rva - start
        raise ProbeError('RVA not present in file-backed section')
    dirbase = opt + (112 if is64 else 96)
    directories = []
    max_dirs = min(16, unpack('<I', data, dirbase - 4)[0], max(0, (opt_size - (dirbase - opt)) // 8))
    for index in range(max_dirs):
        rva, size = unpack('<II', data, dirbase + index * 8)
        directories.append({'index': index, 'rva': rva, 'bytes': size})
    imports = []
    if len(directories) > 1 and directories[1]['rva']:
        try:
            base = rva_offset(directories[1]['rva'])
            for i in range(256):
                original, timestamp, forwarder, name_rva, thunk = unpack('<IIIII', data, base + i * 20)
                if not any((original, timestamp, forwarder, name_rva, thunk)): break
                dllname = cstring(data, rva_offset(name_rva))
                imports.append({'dll': dllname})
        except ProbeError:
            imports.append({'warning': 'Import directory incomplete/unavailable'})
    clr = len(directories) > 14 and directories[14]['rva'] > 0 and directories[14]['bytes'] >= 0x48
    managed = None
    if clr:
        try:
            off = rva_offset(directories[14]['rva'])
            meta_rva, meta_size = unpack('<II', data, off + 8)
            meta_off = rva_offset(meta_rva)
            if at(data, meta_off, 4) == b'BSJB':
                major, minor, reserved, verlen = unpack('<HHII', data, meta_off + 4)
                if verlen > 2048: raise ProbeError('CLR version string too long')
                version = at(data, meta_off + 16, verlen).split(b'\0', 1)[0].decode('ascii','replace')
                streams_base = meta_off + 16 + ((verlen + 3) & ~3)
                _, stream_count = unpack('<HH', data, streams_base)
                stream_pos = streams_base + 4
                streams = []
                for _ in range(min(stream_count, 32)):
                    ofs, sz = unpack('<II', data, stream_pos)
                    n = cstring(data, stream_pos + 8, 128)
                    stream_pos += 8 + ((len(n.encode('utf-8')) + 1 + 3) & ~3)
                    streams.append({'name': n, 'bytes': sz, 'offset_in_metadata': ofs})
                managed = {'metadata_version': version, 'streams': streams,
                           'metadata_offset': meta_off, 'metadata_bytes': meta_size}
            else: managed = {'warning': 'CLR directory present but metadata signature unavailable'}
        except ProbeError as ex: managed = {'warning': f'CLR metadata truncated: {ex}'}
    return {'format': 'pe', 'machine': machine, 'pe_kind': 'PE32+' if is64 else 'PE32',
            'sections': sections, 'imports': imports, 'has_cli_descriptor': bool(clr),
            'managed_metadata': managed, 'coverage': 'PE file-backed structure and CLR root only; not CIL decompilation'}


def scan_dex(data: bytes) -> dict:
    if len(data) < 112 or not re.match(rb'dex\n0\d\d\x00', data[:8]): raise ProbeError('Invalid DEX header')
    size, header_size, endian = unpack('<III', data, 32)
    if header_size != 112 or endian not in (0x12345678, 0x78563412):
        raise ProbeError('Unsupported DEX header/endian')
    strs = unpack('<I', data, 56)[0]; types = unpack('<I', data, 64)[0]
    methods = unpack('<I', data, 88)[0]; classes = unpack('<I', data, 96)[0]
    return {'format': 'dex', 'version': data[4:7].decode('ascii','replace'), 'declared_bytes': size,
            'string_ids': strs, 'type_ids': types, 'method_ids': methods, 'class_defs': classes,
            'coverage': 'DEX header counts only; no class or method decompilation'}


def scan_java_class(data: bytes) -> dict:
    if not data.startswith(b'\xca\xfe\xba\xbe'): raise ProbeError('Not a Java classfile')
    minor, major, pool_count = unpack('>HHH', data, 4)
    if pool_count > 20000: raise ProbeError('Unreasonable constant pool count')
    p = 10; cp: list[tuple | None] = [None] * pool_count
    i = 1
    while i < pool_count:
        tag = at(data, p, 1)[0]; p += 1
        if tag == 1:
            n = unpack('>H', data, p)[0]; p += 2
            if n > 1 << 16: raise ProbeError('Oversized Java UTF8')
            cp[i] = ('utf8', at(data, p, n).decode('utf-8','replace')); p += n
        elif tag in (3, 4): p += 4
        elif tag in (5, 6): p += 8; i += 1
        elif tag in (7, 8, 16, 19, 20): cp[i] = ('idx', unpack('>H', data, p)[0]); p += 2
        elif tag in (9, 10, 11, 12, 17, 18): p += 4
        elif tag == 15: p += 3
        else: raise ProbeError(f'Unsupported Java constant pool tag {tag}')
        if p > len(data): raise ProbeError('Truncated Java constant pool')
        i += 1
    def utf8(index: int) -> str:
        if 0 < index < len(cp) and cp[index] and cp[index][0] == 'utf8': return cp[index][1]
        return '<unavailable>'
    def class_name(index: int) -> str:
        if 0 < index < len(cp) and cp[index] and cp[index][0] == 'idx': return utf8(cp[index][1])
        return '<unavailable>'
    flags, this_idx, super_idx, interface_count = unpack('>HHHH', data, p); p += 8
    interfaces = []
    for _ in range(min(interface_count, MAX_ITEMS)):
        interfaces.append(class_name(unpack('>H', data, p)[0])); p += 2
    if interface_count > MAX_ITEMS: raise ProbeError('Class interface limit exceeded')
    def member_block(p: int) -> tuple[list[dict], int]:
        count = unpack('>H', data, p)[0]; p += 2
        if count > MAX_ITEMS: raise ProbeError('Java member count over budget')
        members = []
        for _ in range(count):
            member_flags, nameidx, descidx, attr_count = unpack('>HHHH', data, p); p += 8
            members.append({'name': utf8(nameidx), 'descriptor': utf8(descidx), 'flags': member_flags})
            for __ in range(attr_count):
                attrname, n = unpack('>HI', data, p); p += 6
                p += n
                if p > len(data): raise ProbeError('Truncated Java attribute')
        return members, p
    fields, p = member_block(p)
    methods, p = member_block(p)
    return {'format': 'java-class', 'major': major, 'minor': minor, 'class_name': class_name(this_idx),
            'super_class': class_name(super_idx), 'interfaces': interfaces, 'fields': fields,
            'methods': methods, 'coverage': 'Declared class/member names and descriptors; bytecode not decompiled'}


def scan_firmware(data: bytes) -> dict:
    signatures = {'gzip': b'\x1f\x8b\x08', 'zip': b'PK\x03\x04', 'squashfs_le': b'hsqs',
                  'squashfs_be': b'sqsh', 'u-boot': b'\x27\x05\x19\x56',
                  'elf': b'\x7fELF', 'xz': b'\xfd7zXZ\x00'}
    hits = []
    for name, signature in signatures.items():
        off = 0
        while len(hits) < MAX_ITEMS:
            pos = data.find(signature, off)
            if pos < 0: break
            hits.append({'kind': name, 'offset': pos})
            off = pos + 1
    hits.sort(key=lambda v: v['offset'])
    return {'format':'unknown-firmware-or-blob', 'candidate_regions':hits,
            'coverage':'magic-byte signature candidates only; no validation/extraction or proof of nested type'}


def mask_route(path: str) -> str:
    segments = path.split('/')
    def mask(segment: str) -> str:
        if re.fullmatch(r'\d{3,}|[a-fA-F0-9]{24,}|[a-fA-F0-9]{8}-[a-fA-F0-9-]{27,}', segment):
            return '{id}'
        return segment[:160]
    return '/'.join(mask(x) for x in segments)[:512]


def scan_har(data: bytes) -> dict:
    try: obj = json.loads(data.decode('utf-8'))
    except (ValueError, UnicodeError) as e: raise ProbeError(f'Invalid UTF-8 HAR: {e}')
    if not isinstance(obj, dict) or not isinstance(obj.get('log'), dict) or not isinstance(obj['log'].get('entries'), list):
        raise ProbeError('Missing HAR log.entries array')
    entries = obj['log']['entries']; records = []
    for i, item in enumerate(entries[:MAX_ITEMS]):
        if not isinstance(item, dict): continue
        request = item.get('request') or {}; response = item.get('response') or {}
        url = request.get('url', '')
        parsed = urllib.parse.urlsplit(url) if isinstance(url,str) else urllib.parse.urlsplit('')
        try: host = parsed.hostname or ''
        except ValueError: host = '<invalid-host>'
        records.append({'ordinal': i, 'method': str(request.get('method',''))[:16],
                        'scheme': parsed.scheme[:16], 'host': host[:256],
                        'route': mask_route(parsed.path), 'status': response.get('status'),
                        'mime_type': str((response.get('content') or {}).get('mimeType',''))[:100]})
    return {'format':'har', 'producer_entries':len(entries), 'requests':records,
            'complete': len(entries) <= MAX_ITEMS,
            'redaction': 'omitted auth, headers, query, bodies, cookies and request/response content; route segments partially masked',
            'coverage': 'captured historical traffic, not a live network observation'}


def scan_sqlite(path: Path) -> dict:
    uri = path.absolute().as_uri() + '?mode=ro&immutable=1'
    try:
        con = sqlite3.connect(uri, uri=True, timeout=2)
        if hasattr(con, 'enable_load_extension'):
            con.enable_load_extension(False)
        con.execute('PRAGMA query_only=ON')
        con.execute('PRAGMA trusted_schema=OFF')
        rows = con.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('table','view','index','trigger') ORDER BY type,name LIMIT ?",(MAX_ITEMS,)).fetchall()
        count = con.execute("SELECT count(*) FROM sqlite_master WHERE type IN ('table','view','index','trigger')").fetchone()[0]
    except sqlite3.DatabaseError as e:
        raise ProbeError(f'Cannot inspect SQLite schema: {e}')
    finally:
        if 'con' in locals(): con.close()
    return {'format': 'sqlite', 'schema_objects': [{'type': r[0], 'name': r[1], 'parent': r[2],
               'declaration': str(r[3] or '')[:2000]} for r in rows], 'total_objects': count,
            'complete': count <= MAX_ITEMS,
            'coverage': 'read-only schema declarations; no table-row contents or arbitrary SQL evaluated'}


def inspect(path: Path, max_bytes: int) -> dict:
    if not path.is_file() or path.is_symlink(): raise ProbeError('Only a regular non-symlink file is supported')
    size = path.stat().st_size
    if max_bytes < 1024 or max_bytes > 256 * 1024 * 1024:
        raise ProbeError('max-bytes must be between 1024 and 268435456')
    # Never automatically read or hash an unbounded artifact.
    with path.open('rb') as stream: data = stream.read(max_bytes + 1)
    complete = len(data) <= max_bytes
    if not complete: data = data[:max_bytes]
    sha = hashlib.sha256(data).hexdigest() if complete else None
    if data.startswith(b'\x00asm'): details = scan_wasm(data)
    elif data.startswith(b'\x7fELF'): details = scan_elf(data)
    elif data.startswith(b'MZ'): details = scan_pe(data)
    elif data.startswith(b'dex\n'): details = scan_dex(data)
    elif data.startswith(b'\xca\xfe\xba\xbe'): details = scan_java_class(data)
    elif data.startswith(b'SQLite format 3\x00'): details = scan_sqlite(path) if complete else {'format':'sqlite','coverage':'too large for schema probe'}
    elif data.lstrip().startswith(b'{') and (path.suffix.lower() == '.har' or b'"entries"' in data[:1024 * 1024]):
        details = scan_har(data) if complete else {'format':'har-candidate','coverage':'truncated; not parsed'}
    else: details = scan_firmware(data)
    return {'operation':'probe', 'input':{'path':str(path.absolute()),'size_bytes':size,
            'sha256':sha,'sha256_scope':'whole file' if complete else 'not computed because byte limit was reached'},
            'read_bytes':len(data), 'complete_read':complete, 'details':details,
            'execution':'none', 'network':'none'}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path)
    parser.add_argument('--max-mib',type=int,default=32)
    parser.add_argument('-o','--output')
    a=parser.parse_args(argv)
    try:
        if not 1 <= a.max_mib <= 256: raise ProbeError('--max-mib must be 1..256')
        result=inspect(a.path,a.max_mib*1048576)
        emit(result,a.output,[a.path])
    except (ProbeError, OSError, sqlite3.DatabaseError) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
