"""Executable regression cases for independent semantic readers."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from dotnet_analysis import analyze_dotnet, CLRParseError, il_calls
from jvm_analysis import parse_class, JVMError, inspect_file, decode_calls
from wasm_semantics import analyze_wasm, WasmError


def cli_pe_fixture():
    """Small file-backed PE with valid CLI metadata layout and two method bodies."""
    data=bytearray(4096)
    def write(pos,bytes_):data[pos:pos+len(bytes_)]=bytes_
    def u16(pos,v):struct.pack_into('<H',data,pos,v)
    def u32(pos,v):struct.pack_into('<I',data,pos,v)
    write(0,b'MZ');u32(0x3c,0x80)
    write(0x80,b'PE\0\0')
    write(0x84,struct.pack('<HHIIIHH',0x14c,1,0,0,0,0xe0,0x210e))
    opt=0x98;u16(opt,0x10b);u32(opt+92,16)
    u32(opt+96+14*8,0x2000);u32(opt+96+14*8+4,0x48)
    sec=opt+0xe0
    write(sec,b'.text\0\0\0')
    write(sec+8,struct.pack('<IIII',0x800,0x2000,0x800,0x200))
    u32(0x200,0x48);u32(0x208,0x2100)
    # streams are relative to metadata base = 0x300
    h=bytearray()
    st=b'\0Demo\0Run\0Helper\0'
    run=st.index(b'Run');helper=st.index(b'Helper')
    tables=bytearray()
    tables+=b'\0'*4+bytes([2,0,0,1])
    tables+=struct.pack('<QQ', (1<<2)|(1<<6), 0)
    tables+=struct.pack('<II',1,2)
    tables+=struct.pack('<IHHHHH',0,1,0,0,1,1)
    tables+=struct.pack('<IHHHHH',0x2200,0,0,run,0,1)
    tables+=struct.pack('<IHHHHH',0x2210,0,0,helper,0,1)
    # BSJB + root header + version + stream headers
    h+=b'BSJB'+struct.pack('<HHII',1,1,0,12)+b'v4.0.30319\0\0'
    h+=struct.pack('<HH',0,2)
    table_off=64
    string_off=table_off+len(tables)
    h+=struct.pack('<II',table_off,len(tables))+b'#~\0\0'
    h+=struct.pack('<II',string_off,len(st))+b'#Strings\0'
    h+=b'\0'*(table_off-len(h))
    h+=tables+st
    write(0x300,h)
    u32(0x20c,len(h))
    # body 1: ldc.i4.0 ; call Demo.Helper ; ret
    body=b'\x16\x28\x02\x00\x00\x06\x2a'
    write(0x400,bytes([(len(body)<<2)|2])+body)
    write(0x410,b'\x0a\x17\x2a')
    return bytes(data)


def vlq(x):
    out=b''
    while 1:
        val=x&127;x>>=7
        out+=bytes([val|128 if x else val]);
        if not x: return out

def name(x):
    raw=x.encode();return vlq(len(raw))+raw

def section(i,payload):return bytes([i])+vlq(len(payload))+payload


def wasm_fixture():
    # Type ()->i32, import env.inc type 0, function type 0, export it
    ty=section(1,b'\x01\x60\x00\x01\x7f')
    imp=section(2,b'\x01'+name('env')+name('inc')+b'\x00\x00')
    funcs=section(3,b'\x01\x00')
    exp=section(7,b'\x01'+name('test')+b'\x00\x01')
    code=b'\x00\x41\x01\x10\x00\x0b' # zero locals; const 1; call import 0; end
    body=section(10,b'\x01'+vlq(len(code))+code)
    return b'\x00asm\x01\0\0\0'+ty+imp+funcs+exp+body

class ManagedTests(unittest.TestCase):
    def test_resolves_type_method_cil_call(self):
        j=analyze_dotnet(cli_pe_fixture())
        self.assertEqual(j['types'][0]['name'],'Demo')
        self.assertEqual([x['name'] for x in j['methods']],['Run','Helper'])
        self.assertEqual(j['methods'][0]['body']['cil']['calls'][0]['callee']['name'],'Helper')
        self.assertTrue(j['cil_walk_complete'])
    def test_rejects_invalid_rva(self):
        a=bytearray(cli_pe_fixture());struct.pack_into('<I',a,0x208,0xffffffff)
        with self.assertRaises(CLRParseError):analyze_dotnet(bytes(a))
    def test_detects_unknown_il(self):
        j=il_calls(b'\xff',lambda token:{'name':'x'})
        self.assertFalse(j['walk_complete'])
    def test_pe_header_no_metadata(self):
        with self.assertRaises(CLRParseError):analyze_dotnet(b'MZ'+b'\0'*90)

class WASMTests(unittest.TestCase):
    def test_call_export_and_type(self):
        j=analyze_wasm(wasm_fixture())
        self.assertTrue(j['code_walk_complete'])
        self.assertEqual(j['exports'][0]['name'],'test')
        self.assertEqual(j['functions'][0]['body']['calls'][0]['target']['name'],'inc')
    def test_unsupported_opcode_marks_partial(self):
        a=bytearray(wasm_fixture())
        a[-1]=0xff
        j=analyze_wasm(bytes(a));self.assertFalse(j['code_walk_complete'])
    def test_bad_section_length(self):
        a=wasm_fixture()+b'\x00\xff\xff\xff\xff\x0f'
        with self.assertRaises(WasmError):analyze_wasm(a)
    def test_real_wasm_when_available(self):
        p=Path('/opt/pyvenv/lib/python3.13/site-packages/artifact_tool/bin/embedded_font_decoder.wasm')
        if not p.exists():self.skipTest('real WASM fixture not installed')
        j=analyze_wasm(p.read_bytes())
        self.assertTrue(j['code_walk_complete'])
        self.assertGreater(len(j['functions']),5)

class JVMTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('javac'),'Java compiler not installed')
    def test_compile_and_inspect_real_class(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)
            (path/'Sample.java').write_text('public class Sample { public static int a(int x) { return Math.abs(x); } }')
            subprocess.run(['javac','Sample.java'],cwd=path,check=True,timeout=10,capture_output=True)
            data=parse_class((path/'Sample.class').read_bytes())
            self.assertEqual(data['class_name'],'Sample')
            m=next(m for m in data['methods'] if m['name']=='a')
            self.assertTrue(m['bytecode_walk_complete'])
            self.assertEqual(m['calls'][0]['name'],'abs')
            with zipfile.ZipFile(path/'demo.jar','w') as z:z.write(path/'Sample.class','Sample.class')
            self.assertEqual(inspect_file(path/'demo.jar')['class_count'],1)
    def test_bad_magic(self):
        with self.assertRaises(JVMError):parse_class(b'\x00'*18)
    def test_unknown_instruction_incomplete(self):
        _, ok, detail=decode_calls(b'\xff',[])
        self.assertFalse(ok);self.assertIn('opcode',detail)

if __name__=='__main__':unittest.main()
