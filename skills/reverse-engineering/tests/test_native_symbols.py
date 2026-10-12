import shutil
import struct
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from native_symbols import analyze_native,NativeError,parse_macho,parse_elf,parse_fat_macho

class NativeTests(unittest.TestCase):
    def test_native_linux_binary(self):
        p=Path('/usr/bin/ls')
        if not p.exists():self.skipTest('ELF binary unavailable')
        data=analyze_native(p.read_bytes())
        self.assertEqual(data['format'],'elf')
        self.assertGreater(len(data['symbols']),10)
        self.assertIn('libc.so.6',data['needed_libraries'])
        self.assertTrue(data['relocations'])
    def test_bad_elf_bounded(self):
        with self.assertRaises(NativeError):parse_elf(b'\x7fELF\2\1\0')
    def test_mach_o_load_dylib(self):
        name=b'/usr/lib/libSystem.B.dylib\0'
        length=(24+len(name)+3)&~3
        header=b'\xcf\xfa\xed\xfe'+struct.pack('<IIIIIII',0x1000007,3,2,1,length,0,0)
        command=struct.pack('<IIIIII',0xc,length,24,0,0,0)+name+b'\0'*(length-24-len(name))
        out=parse_macho(header+command)
        self.assertIn('/usr/lib/libSystem.B.dylib',out['linked_libraries'])
    def test_mach_o_fat_slices(self):
        name=b'/usr/lib/libSystem.B.dylib\0'
        length=(24+len(name)+3)&~3
        thin=b'\xcf\xfa\xed\xfe'+struct.pack('<IIIIIII',0x1000007,3,2,1,length,0,0)
        thin+=struct.pack('<IIIIII',0xc,length,24,0,0,0)+name+b'\0'*(length-24-len(name))
        fat=struct.pack('>II',0xcafebabe,1)+struct.pack('>IIIII',0x1000007,3,28,len(thin),2)+thin
        out=parse_fat_macho(fat)
        self.assertEqual(len(out['architectures']),1)
        self.assertEqual(out['architectures'][0]['slice']['linked_libraries'],['/usr/lib/libSystem.B.dylib'])
        with self.assertRaises(NativeError):parse_fat_macho(fat[:-1])
    def test_not_a_macho(self):
        with self.assertRaises(NativeError):parse_macho(b'ABCD')
if __name__=='__main__':unittest.main()
