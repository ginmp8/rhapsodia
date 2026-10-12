"""Deterministic cases for web evidence and Android DEX parser."""
from pathlib import Path
import io
import json
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from web_analysis import map_segments, vlq_decode, analyze_sourcemap, analyze_js, analyze_har, analyze_openapi, WebError
from dex_analysis import analyze_dex, DexError, analyze_path, decode_invokes


def android_fixture():
    buf=bytearray(400)
    def u16(p,v):struct.pack_into('<H',buf,p,v)
    def u32(p,v):struct.pack_into('<I',buf,p,v)
    buf[:8]=b'dex\n035\x00'
    u32(32,len(buf));u32(36,112);u32(40,0x12345678)
    for off,num,idx in [(56,3,112),(64,2,124),(72,1,132),(88,1,144),(96,1,152)]:
        u32(off,num);u32(off+4,idx)
    strings=[(184,b'\x09LExample;\0'),(200,b'\x01V\0'),(208,b'\x06method\0')]
    for i,(pos,data) in enumerate(strings):
        u32(112+i*4,pos);buf[pos:pos+len(data)]=data
    u32(124,0);u32(128,1)
    u32(132,1);u32(136,1);u32(140,0)
    u16(144,0);u16(146,0);u32(148,2)
    u32(152,0);u32(160,0xffffffff);u32(176,0x100)
    buf[0x100:0x108]=b'\x00\x00\x01\x00\x00\x01\xa0\x02'
    u16(0x120,1);u16(0x122,1);u16(0x124,0);u16(0x126,0)
    u32(0x128,0);u32(0x12c,5)
    for k,v in enumerate([0x0012,0x1071,0x0000,0x0000,0x000e]):u16(0x130+2*k,v)
    return bytes(buf)

class DexTests(unittest.TestCase):
    def test_class_method_invocation(self):
        value=analyze_dex(android_fixture())
        self.assertTrue(value['code_walk_complete'])
        self.assertEqual(value['classes'][0]['name'],'LExample;')
        calls=value['classes'][0]['methods'][0]['invokes']
        self.assertEqual(calls[0]['callee']['name'],'method')
    def test_truncated(self):
        with self.assertRaises(DexError):analyze_dex(android_fixture()[:148])
    def test_partial_decoder(self):
        calls,complete,reason=decode_invokes([0x00ff],[])
        self.assertFalse(complete);self.assertIn('truncated',reason)
    def test_apk_member(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'example.apk'
            with zipfile.ZipFile(p,'w') as z:z.writestr('classes.dex',android_fixture())
            out=analyze_path(p)
            self.assertEqual(out['dex_files'][0]['classes'][0]['methods'][0]['invokes'][0]['callee_index'],0)

class WebTests(unittest.TestCase):
    def test_sourcemap_vlq(self):
        out=map_segments({'version':3,'sources':['src/main.ts'],'names':[], 'mappings':'AAAA,CAAC;AACA'})
        self.assertEqual(out[0]['source'],'src/main.ts')
        self.assertEqual(out[-1]['generated_line'],2)
        self.assertEqual(out[-1]['original_line'],2)
    def test_source_map_lookup(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'app.js.map';p.write_text(json.dumps({'version':3,'sources':['a.ts'],'sourcesContent':['let a=1;'], 'names':[], 'mappings':'AAAA'}))
            out=analyze_sourcemap(p,1,1)
            self.assertEqual(out['lookup']['closest_segment']['source'],'a.ts')
            self.assertEqual(out['sources'][0]['sha256'],__import__('hashlib').sha256(b'let a=1;').hexdigest())
    def test_rejects_invalid_sourcemap(self):
        with self.assertRaises(WebError):map_segments({'version':3,'sources':['a'],'mappings':'X'})
    def test_js_ipc_and_route(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'index.js'
            p.write_text("import x from './x'; ipcRenderer.invoke('do-it', x); app.post('/api/v1/items', () => x);")
            v=analyze_js(p)
            self.assertEqual([x['kind'] for x in v['references']],['esm_import','electron_ipc_send','express_route'])
    def test_har_contract_redacts_values(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'capture.har'
            url='https://api.example.com/items/123456?token=secret&limit=3'
            p.write_text(json.dumps({'log':{'entries':[{'request':{'method':'GET','url':url,'headers':[{'name':'Authorization','value':'secret'}]},'response':{'status':200,'content':{'mimeType':'application/json','text':'{"id":123,"token":"secret"}'}}}]}}))
            v=analyze_har(p,include_shape=True)
            j=json.dumps(v)
            self.assertNotIn('secret',j)
            self.assertIn('{id}',j)
            self.assertEqual(v['routes'][0]['query_parameters'],['limit'])
    def test_openapi_contract(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'api.json'
            p.write_text(json.dumps({'openapi':'3.0.2','paths':{'/things':{'post':{'operationId':'createThing','responses':{'201':{}}}}}}))
            self.assertEqual(analyze_openapi(p)['operations'][0]['operation_id'],'createThing')

if __name__=='__main__':unittest.main()

class EVMTests(unittest.TestCase):
    def test_push4_and_effect(self):
        from evm_analysis import analyze_evm
        result=analyze_evm(bytes.fromhex('63deadbeef146005575b60006000f1'))
        self.assertEqual(result['candidate_selectors'][0]['selector'],'0xdeadbeef')
        self.assertEqual(result['potential_side_effects'][0]['operation'],'CALL')
        self.assertTrue(result['complete_decode'])
    def test_does_not_treat_push_data_as_opcode(self):
        from evm_analysis import analyze_evm
        result=analyze_evm(bytes.fromhex('60f1ff'))
        self.assertEqual(len(result['potential_side_effects']),1)
        self.assertEqual(result['potential_side_effects'][0]['operation'],'SELFDESTRUCT')
    def test_malformed_hex(self):
        from evm_analysis import parse_hex,EVMError
        with self.assertRaises(EVMError):parse_hex('0x0xz')
