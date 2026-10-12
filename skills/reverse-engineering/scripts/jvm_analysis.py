#!/usr/bin/env python3
"""Independent, bounded JVM classfile reader (constant pool, member code and calls).

Static data only. Does not execute classes and does not claim behavioral equivalence.
Unknown bytecodes/incomplete attributes produce explicit errors or incomplete flags.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path
from json_writer import write_exclusive

MAX_CLASS = 8 * 1024 * 1024
MAX_ENTRIES = 5000
MAX_CODE = 1024 * 1024


class JVMError(ValueError):
    pass


class Buf:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def raw(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise JVMError(f"truncated at offset {self.pos} requesting {n} bytes")
        val = self.data[self.pos:self.pos + n]
        self.pos += n
        return val

    def u1(self) -> int:
        return self.raw(1)[0]

    def u2(self) -> int:
        return int.from_bytes(self.raw(2), 'big')

    def u4(self) -> int:
        return int.from_bytes(self.raw(4), 'big')


# Bytecode operand counts (most opcodes have zero operands). -1 denotes
# dynamic size and is handled in decode_calls. All unlisted valid opcodes are 0.
OPERAND = {**{x: 1 for x in [16, 18, *range(21, 26), *range(54, 59), 169, 188]},
           **{x: 2 for x in [17, 19, 20, 132, *range(153, 167), 167, 168,
                               178, 179, 180, 181, 182, 183, 184, 187, 189, 192, 193, 198, 199]},
           185: 4, 186: 4, 197: 3, 200: 4, 201: 4}
INVALID_OPS = set(range(203, 254)) | {254, 255}


def decode_calls(code: bytes, cp: list, limit: int = 10000) -> tuple[list[dict], bool, str | None]:
    """Walk JVM instructions to find *static call sites*, not resolved dispatch."""
    pos, calls, instructions = 0, [], 0
    while pos < len(code):
        if instructions >= limit:
            return calls, False, 'instruction budget reached'
        instructions += 1
        start = pos
        op = code[pos]; pos += 1
        if op in INVALID_OPS:
            return calls, False, f'unknown/reserved opcode {op:#x} at {start}'
        if op == 170:  # tableswitch is four-byte aligned relative to method start
            padding = (-pos) % 4
            pos += padding
            if pos + 12 > len(code): return calls, False, 'truncated tableswitch'
            default, low, high = struct.unpack_from('>iii', code, pos)
            count = high - low + 1
            if count < 0 or count > 65536: return calls, False, 'invalid tableswitch range'
            pos += 12 + 4 * count
        elif op == 171:
            pos += (-pos) % 4
            if pos + 8 > len(code): return calls, False, 'truncated lookupswitch'
            count = struct.unpack_from('>i', code, pos + 4)[0]
            if count < 0 or count > 65536: return calls, False, 'invalid lookupswitch count'
            pos += 8 + 8 * count
        elif op == 196:
            if pos >= len(code): return calls, False, 'truncated wide'
            widened = code[pos]; pos += 1
            if widened == 132: pos += 4
            elif widened in (*range(21,26), *range(54,59), 169): pos += 2
            else: return calls, False, f'invalid wide opcode {widened:#x}'
        else:
            pos += OPERAND.get(op, 0)
        if pos > len(code): return calls, False, f'truncated instruction at {start}'
        if op in (182, 183, 184, 185, 186):
            index = int.from_bytes(code[start + 1:start + 3], 'big')
            try:
                kind, details = member_ref(cp, index)
            except JVMError as e:
                return calls, False, f'invalid call reference at {start}: {e}'
            calls.append({'offset':start, 'opcode': {182:'invokevirtual',183:'invokespecial',184:'invokestatic',185:'invokeinterface',186:'invokedynamic'}[op],
                          'reference_index':index, 'kind':kind, **details})
    return calls, True, None


def utf(cp: list, idx: int) -> str:
    if not 0 < idx < len(cp) or cp[idx] is None or cp[idx][0] != 'utf8':
        raise JVMError(f'constant pool string index {idx} is invalid')
    return cp[idx][1]


def class_name(cp: list, idx: int) -> str:
    if idx == 0: return ''
    if not 0 < idx < len(cp) or cp[idx] is None or cp[idx][0] != 'class':
        raise JVMError(f'constant pool class index {idx} is invalid')
    return utf(cp, cp[idx][1])


def member_ref(cp: list, idx: int) -> tuple[str, dict]:
    if not 0 < idx < len(cp) or cp[idx] is None:
        raise JVMError(f'constant pool member index {idx} is invalid')
    row = cp[idx]
    if row[0] in ('field', 'method', 'interface_method'):
        owner = class_name(cp, row[1]); nat = cp[row[2]]
        if nat is None or nat[0] != 'name_type': raise JVMError('invalid NameAndType')
        return row[0], {'owner': owner, 'name': utf(cp,nat[1]), 'descriptor': utf(cp,nat[2])}
    if row[0] == 'invokedynamic':
        nat = cp[row[2]]
        if nat is None or nat[0] != 'name_type': raise JVMError('invalid dynamic name/type')
        return row[0], {'bootstrap_method_index':row[1], 'name':utf(cp,nat[1]), 'descriptor':utf(cp,nat[2]),
                        'note':'bootstrap linkage not resolved'}
    raise JVMError(f'{row[0]} is not a member reference')


def parse_class(data: bytes, *, include_code: bool = False) -> dict:
    if len(data) > MAX_CLASS: raise JVMError('class byte budget exceeded')
    b = Buf(data)
    if b.u4() != 0xcafebabe: raise JVMError('class magic mismatch')
    minor, major = b.u2(), b.u2()
    cpcount = b.u2()
    if cpcount > 25000: raise JVMError('constant-pool budget exceeded')
    cp: list = [None] * cpcount
    i = 1
    while i < cpcount:
        tag = b.u1()
        if tag == 1:
            raw = b.raw(b.u2())
            # JVM modified UTF-8 represents NUL as C0 80. Keep replacements explicit.
            cp[i] = ('utf8', raw.replace(b'\xc0\x80', b'\x00').decode('utf-8','replace'))
        elif tag in (3, 4): cp[i] = ('number', b.raw(4).hex())
        elif tag in (5, 6):
            cp[i] = ('wide_number', b.raw(8).hex()); i += 1
        elif tag in (7, 8, 16, 19, 20):
            cp[i] = ({7:'class', 8:'string',16:'method_type',19:'module',20:'package'}[tag], b.u2())
        elif tag in (9, 10, 11, 12, 17, 18):
            cp[i] = ({9:'field',10:'method',11:'interface_method',12:'name_type',17:'dynamic',18:'invokedynamic'}[tag],b.u2(),b.u2())
        elif tag == 15:
            cp[i] = ('method_handle',b.u1(),b.u2())
        else: raise JVMError(f'unsupported constant-pool tag {tag} at {b.pos - 1}')
        i += 1
    access, this, parent = b.u2(), b.u2(), b.u2()
    interfaces = [class_name(cp,b.u2()) for _ in range(b.u2())]

    def attributes(num: int, is_method: bool = False) -> tuple[list[dict], bytes | None]:
        found, code = [], None
        if num > 2000: raise JVMError('attribute count budget exceeded')
        for _ in range(num):
            name = utf(cp,b.u2()); size = b.u4()
            if size > MAX_CLASS: raise JVMError('attribute byte budget exceeded')
            payload = b.raw(size)
            found.append({'name':name,'bytes':size})
            if is_method and name == 'Code':
                codebuf = Buf(payload)
                stack, locals_count, code_len = codebuf.u2(),codebuf.u2(),codebuf.u4()
                if code_len > MAX_CODE: raise JVMError('code body budget exceeded')
                code = codebuf.raw(code_len)
                found[-1]['max_stack'] = stack
                found[-1]['max_locals'] = locals_count
        return found, code

    def members(is_method: bool) -> list[dict]:
        count = b.u2()
        if count > MAX_ENTRIES: raise JVMError('member count exceeded')
        result = []
        for _ in range(count):
            flags, name, descriptor = b.u2(), b.u2(), b.u2()
            attrs, code = attributes(b.u2(), is_method=is_method)
            item = {'name':utf(cp,name),'descriptor':utf(cp,descriptor),'access_flags':flags,
                    'attributes':attrs}
            if is_method:
                item['has_code'] = code is not None
                if code is not None:
                    item['bytecode_bytes'] = len(code)
                    calls, complete, issue = decode_calls(code, cp)
                    item['calls'] = calls
                    item['bytecode_walk_complete'] = complete
                    if issue: item['bytecode_walk_warning'] = issue
                    if include_code: item['bytecode_hex'] = code.hex()
            result.append(item)
        return result
    fields = members(False)
    methods = members(True)
    attrs,_ = attributes(b.u2())
    return {'format':'jvm-class', 'major_version':major,'minor_version':minor,
            'sha256':hashlib.sha256(data).hexdigest(), 'class_name':class_name(cp,this),
            'super_class':class_name(cp,parent), 'interfaces':interfaces,
            'fields':fields, 'methods':methods,'attributes':attrs,
            'complete':b.pos==len(data), 'remaining_bytes':len(data)-b.pos,
            'evidence_level':'bytecode call sites; virtual targets and invokedynamic linkage not resolved'}


def inspect_file(path: Path, *, include_code: bool = False) -> dict:
    if path.is_symlink(): raise JVMError('symlink input not allowed')
    if path.suffix.lower() not in ('.jar', '.zip'):
        return parse_class(path.read_bytes() if path.stat().st_size <= MAX_CLASS else b'oversized', include_code=include_code)
    classes, errors = [], []
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        if len(members) > 20000: raise JVMError('archive-entry budget exceeded')
        for info in members:
            if not info.filename.endswith('.class'): continue
            if len(classes) >= MAX_ENTRIES: raise JVMError('class-file budget exceeded')
            if (info.external_attr >> 16) & 0o170000 == 0o120000: raise JVMError('archive contains symlink')
            if info.file_size > MAX_CLASS: raise JVMError('class byte budget exceeded')
            if info.compress_size and info.file_size > max(1000,info.compress_size)*200:
                raise JVMError('suspicious archive compression ratio')
            try:
                entry = parse_class(z.read(info), include_code=include_code)
                entry['member'] = info.filename
                classes.append(entry)
            except (ValueError, RuntimeError) as exc:
                errors.append({'member':info.filename, 'error':str(exc)[:200]})
    return {'format':'jvm-archive', 'classes':classes, 'errors':errors,
            'complete':not errors,'class_count':len(classes)}


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path)
    p.add_argument('-o','--output',type=Path)
    p.add_argument('--include-bytecode',action='store_true',help='includes potentially sensitive method bytes')
    args=p.parse_args(argv)
    try:
        result=inspect_file(args.path,include_code=args.include_bytecode)
        encoded=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
        if args.output:
            if args.path.resolve()==args.output.resolve(): raise JVMError('output aliases input')
            write_exclusive(args.output,encoded,[args.path])
        else:print(encoded,end='')
        return 0 if result.get('complete',False) else 3
    except (JVMError,OSError,zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}',file=sys.stderr); return 2

if __name__=='__main__':raise SystemExit(main())
