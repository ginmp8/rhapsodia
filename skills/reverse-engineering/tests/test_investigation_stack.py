"""Independent acceptance/adversarial tests for new portable investigation core."""
import contextlib
import hashlib
import io
import json
import os
import sqlite3
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from artifact_index import VirtualArtifact,ArtifactError,resolve_scoped,digest
from artifact_reports import inspect_binary,inspect_pe_resources,inspect_elf_notes,inspect_apple_bundle
from application_graph import analyze_application,trace_feature,compare_applications
from investigation_store import EvidenceStore,canonical
from reconstruction_contract import compare_partial_order,generate_obligations,assess_obligations
from investigation_api import InvestigationAPI,mcp_tools
from mcp_server import Server,MODERN,LEGACY


class ArchiveTests(unittest.TestCase):
    def test_zip_malicious_paths_duplicates_and_symlinks(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'archive.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('app/main.js','import x from "./lib"')
                z.writestr('../secret.txt','private')
                z.writestr('app/MAIN.js','duplicate-on-casefold')
                s=zipfile.ZipInfo('app/link.js')
                s.create_system=3
                s.external_attr=(stat.S_IFLNK|0o777)<<16
                z.writestr(s,'/etc/passwd')
            view=VirtualArtifact(p)
            self.assertIn('app/main.js',view.entries)
            self.assertNotIn('../secret.txt',view.entries)
            self.assertNotIn('app/link.js',view.entries)
            self.assertEqual(view.read('app/main.js'),b'import x from "./lib"')
            self.assertTrue(view.skips)

    def test_targz_is_never_extracted_and_links_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'app.tar.gz'
            with tarfile.open(p,'w:gz') as tf:
                content=b'export class A {}'
                m=tarfile.TarInfo('src/a.ts');m.size=len(content);tf.addfile(m,io.BytesIO(content))
                s=tarfile.TarInfo('src/link.ts');s.type=tarfile.SYMTYPE;s.linkname='../../etc/passwd';tf.addfile(s)
            a=VirtualArtifact(p)
            self.assertEqual(a.kind,'tar')
            self.assertEqual(a.read('src/a.ts'),content)
            self.assertNotIn('src/link.ts',a.entries)

    def test_asar_reads_bounded_integrity_verified_entries(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'src.asar';content=b'export const answer = 42;'
            doc={'files':{'src':{'files':{'main.js':{
                'offset':'0','size':len(content),'integrity':{'algorithm':'SHA256','hash':digest(content)}
            }}}}}
            header=json.dumps(doc).encode('utf8')
            payload=struct.pack('<I',len(header))+header
            payload+=b'\x00' * ((-len(payload))%4)
            path.write_bytes(struct.pack('<II',4,len(payload)+4)+struct.pack('<I',len(payload))+payload+content)
            a=VirtualArtifact(path)
            self.assertEqual(a.read('src/main.js'),content)
            self.assertEqual(a.kind,'asar')
            path.write_bytes(path.read_bytes()[:-1]+b'!')
            b=VirtualArtifact(path)
            with self.assertRaisesRegex(ArtifactError,'integrity'):
                b.read('src/main.js')

    def test_directory_and_boundary(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/'safe.txt').write_text('ok')
            (root/'alias').symlink_to('/etc',target_is_directory=True)
            with self.assertRaises(ArtifactError):resolve_scoped(root,'alias/passwd')
            with self.assertRaises(ArtifactError):resolve_scoped(root,'../bad')
            a=VirtualArtifact(root)
            self.assertIn('safe.txt',a.entries)
            self.assertNotIn('alias/passwd',a.entries)

    def test_fails_closed_for_duplicate_json_fields(self):
        from artifact_index import strict_json
        with self.assertRaises(ArtifactError):strict_json(b'{"a":1,"a":2}')


class ApplicationTests(unittest.TestCase):
    def _source(self,p:Path):
        p.mkdir(parents=True,exist_ok=True)
        (p/'package.json').write_text('{"name":"example","main":"main.js"}')
        (p/'main.js').write_text('''import { greet } from './lib';\n// require('bad');\nipcMain.handle('openDialog',()=>greet());\napp.get('/v1/items',getItems);\n''')
        (p/'lib.ts').write_text('export function greet() { return 2; }')
        (p/'renderer.js').write_text("ipcRenderer.invoke('openDialog')")

    def test_graph_and_bounded_trace(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'src';self._source(path)
            graph=analyze_application(VirtualArtifact(path))
            self.assertTrue(graph['complete'])
            self.assertEqual(graph['js_files_seen'],3)
            self.assertTrue(any(e['kind']=='esm-import' and e.get('resolution')=='file-extension-fallback'
                                for e in graph['edges']))
            self.assertTrue(any(n.get('symbol')=='route:GET:/v1/items' for n in graph['nodes']))
            self.assertFalse(any(e.get('specifier')=='bad' for e in graph['edges']))
            trace=trace_feature(graph,'openDialog',direction='both')
            self.assertTrue(trace['seed_ids'])
            self.assertGreater(len(trace['edges']),0)

    def test_nodenext_js_specifier_maps_to_typescript_source_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'main.ts').write_text('import { service } from "./service.js";')
            (root/'service.ts').write_text('export const service = 1;')
            graph=analyze_application(VirtualArtifact(root))
            edges=[e for e in graph['edges'] if e.get('specifier')=='./service.js']
            self.assertEqual(len(edges),1)
            self.assertEqual(edges[0]['resolution'],'typescript-source-fallback')
            id_to_node={n['node_id']:n for n in graph['nodes']}
            self.assertEqual(id_to_node[edges[0]['to']]['path'],'service.ts')

    def test_diff_does_not_confuse_candidate_edges_with_behavior(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);path=root/'v1';self._source(path)
            before=analyze_application(VirtualArtifact(path))
            (path/'added.ts').write_text('export class Added {}')
            after=analyze_application(VirtualArtifact(path))
            delta=compare_applications(before,after)
            self.assertIn('added.ts',delta['added_modules'])
            self.assertIn('not behavioral equivalence',delta['claim_ceiling'])

    def test_intentional_partial_limit(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for i in range(10):(root/f'{i}.js').write_text('require("other")')
            graph=analyze_application(VirtualArtifact(root),max_files=3)
            self.assertFalse(graph['complete'])
            self.assertEqual(graph['js_files_seen'],3)


class EvidenceTests(unittest.TestCase):
    def test_evidence_content_hash_and_view_paging(self):
        with tempfile.TemporaryDirectory() as t:
            store=EvidenceStore(Path(t)/'e.sqlite')
            result=store.put('application_graph','a'*64,{'nodes':[{'a':1},{'a':2}], 'complete':True},'lexical_candidate')
            same=store.put('application_graph','a'*64,{'nodes':[{'a':1},{'a':2}], 'complete':True},'lexical_candidate')
            self.assertEqual(same['evidence_id'],result['evidence_id'])
            page=store.get(result['evidence_id'],'nodes',offset=0,limit=1)
            self.assertEqual(page['total'],2)
            self.assertEqual(page['next_offset'],1)
            self.assertEqual(store.query()['total'],1)
            blob=canonical(store.export())
            new=EvidenceStore()
            self.assertEqual(new.import_bundle(blob)['imported'],1)
            bad=json.loads(blob);bad['records'][0]['data']['nodes'] = []
            with self.assertRaises(ArtifactError):new.import_bundle(canonical(bad))
            store.close();new.close()

    def test_atomic_validation_on_bundle_import(self):
        store=EvidenceStore()
        doc=store.export()
        doc['records']=[{'evidence_id':'wrong','kind':'inventory','artifact_sha256':'a'*64,'level':'declared','data':{}}]
        from investigation_store import digest as sha
        doc['bundle_sha256']=sha(canonical({k:v for k,v in doc.items() if k!='bundle_sha256'}))
        with self.assertRaises(ArtifactError):store.import_bundle(canonical(doc))
        self.assertEqual(store.query()['total'],0)
        store.close()


class ContractTests(unittest.TestCase):
    def test_partial_order_ignores_independent_interleaving(self):
        reference={'events':[{'id':'A','payload':1},{'id':'B','payload':2},
                             {'id':'C','payload':3,'before':['A','B']}]}
        candidate={'events':[{'id':'B','payload':2},{'id':'A','payload':1},
                             {'id':'C','payload':3,'before':['B','A']}]}
        self.assertEqual(compare_partial_order(reference,candidate)['status'],'finite-match')
        candidate['events'][-1]['before']=['A']
        self.assertEqual(compare_partial_order(reference,candidate)['status'],'mismatch')

    def test_cyclic_trace_and_dangling_references_refused(self):
        with self.assertRaises(ArtifactError):
            compare_partial_order({'events':[{'id':'a','before':['b']},{'id':'b','before':['a']}]},{'events':[]})
        with self.assertRaises(ArtifactError):
            compare_partial_order({'events':[{'id':'a','before':['missing']}]},{'events':[]})

    def test_empty_and_claimed_obligation_cannot_self_attest(self):
        self.assertEqual(assess_obligations([],[],[])['readiness'],'unknown')
        o=[{'obligation_id':'x','title':'Test','required':True,'required_case_kinds':['positive']}]
        receipt={'obligation_id':'x','result':'pass','authority':'trusted_runtime_receipt',
                 'source_sha256':None,'receipt_sha256':'a'*64,'cases':['positive']}
        b=[{'obligation_id':'x','owner':'implementation','contract_type':'scalar',
            'fixtures':{'positive':'test-case-1'}}]
        r=assess_obligations(o,b,[receipt])
        self.assertEqual(r['readiness'],'incomplete')
        self.assertIn('reported-trust-receipt-needs-independent-authentication',r['obligations'][0]['blockers'])


class BinaryTests(unittest.TestCase):
    def test_pe_resource_directory_leaf_hash(self):
        data=bytearray(1024)
        data[:2]=b'MZ';struct.pack_into('<I',data,0x3c,0x80)
        data[0x80:0x84]=b'PE\0\0'
        struct.pack_into('<HHIIIHH',data,0x84,0x14c,1,0,0,0,224,0)
        opt=0x98;struct.pack_into('<H',data,opt,0x10b)
        struct.pack_into('<II',data,opt+96+16,0x1000,0x200)
        section=opt+224
        data[section:section+5]=b'.rsrc'
        struct.pack_into('<IIII',data,section+8,0x300,0x1000,0x300,0x200)
        for offset,ident,child in [(0x200,10,0x80000020),(0x220,1,0x80000040),(0x240,1033,0x60)]:
            struct.pack_into('<HH',data,offset+12,0,1)
            struct.pack_into('<II',data,offset+16,ident,child)
        struct.pack_into('<IIII',data,0x260,0x1100,4,1200,0)
        data[0x300:0x304]=b'ICON'
        report=inspect_pe_resources(bytes(data))
        self.assertTrue(report['complete'])
        self.assertEqual(report['resources'][0]['path'],['10','1','1033'])
        self.assertEqual(report['resources'][0]['sha256'],digest(b'ICON'))

    def test_elf_note_inventory_not_a_full_crash_report(self):
        data=bytearray(300)
        data[:4]=b'\x7fELF';data[4]=2;data[5]=1
        struct.pack_into('<H',data,16,4)
        struct.pack_into('<Q',data,32,64)
        struct.pack_into('<HH',data,54,56,1)
        struct.pack_into('<IIQQQQQQ',data,64,4,0,200,0,0,24,24,4)
        struct.pack_into('<III',data,200,4,8,1)
        data[212:216]=b'CORE';data[216:224]=b'abcdefgh'
        report=inspect_elf_notes(bytes(data))
        self.assertEqual(report['notes'][0]['sha256'],digest(b'abcdefgh'))
        self.assertTrue(report['possible_core'])


class MCPTests(unittest.TestCase):
    def _client(self,server,method,params=None,number=1,modern=False):
        message={'jsonrpc':'2.0','id':number,'method':method,'params':params or {}}
        if modern:message['params']['_meta']={
           'io.modelcontextprotocol/protocolVersion':MODERN,
           'io.modelcontextprotocol/clientInfo':{'name':'test','version':'1'},
           'io.modelcontextprotocol/clientCapabilities':{}}
        return server.respond(message)

    def test_modern_mcp_discovery_tools_resources_and_errors(self):
        with tempfile.TemporaryDirectory() as t:
            api=InvestigationAPI(Path(t))
            server=Server(api)
            try:
                self.assertIn(MODERN,self._client(server,'server/discover',modern=True)['result']['supportedVersions'])
                tools=self._client(server,'tools/list',modern=True)['result']['tools']
                self.assertEqual(len(tools),len(mcp_tools()))
                self.assertEqual(len(set(t['name'] for t in tools)),len(tools))
                cap=self._client(server,'tools/call',{'name':'detect_capabilities','arguments':{}},modern=True)
                self.assertFalse(cap['result']['isError'])
                self.assertEqual(cap['result']['resultType'],'complete')
                self.assertTrue(self._client(server,'resources/list',modern=True)['result']['resources'])
                self.assertTrue(self._client(server,'prompts/list',modern=True)['result']['prompts'])
                invalid=self._client(server,'tools/call',{'name':'inventory_source','arguments':{'path':'../escapes'}} ,modern=True)
                self.assertTrue(invalid['result']['isError'])
                bad={'jsonrpc':'2.0','id':6,'method':'tools/list','params':{'_meta':{
                    'io.modelcontextprotocol/protocolVersion':'1999-01-01'}}}
                self.assertEqual(server.respond(bad)['error']['code'],-32022)
                missing_meta={'jsonrpc':'2.0','id':7,'method':'tools/list','params':{'_meta':{
                    'io.modelcontextprotocol/protocolVersion':MODERN}}}
                self.assertEqual(server.respond(missing_meta)['error']['code'],-32600)
            finally:
                server.executor.shutdown(wait=True);api.close()

    def test_legacy_init_and_static_tool(self):
        with tempfile.TemporaryDirectory() as t:
            api=InvestigationAPI(Path(t));server=Server(api)
            try:
                init=self._client(server,'initialize',{'protocolVersion':'2025-11-25'})
                self.assertEqual(init['result']['protocolVersion'],'2025-11-25')
                result=self._client(server,'tools/list')
                self.assertNotIn('resultType',result['result'])
            finally:
                server.executor.shutdown(wait=True);api.close()

    def test_cli_and_mcp_stdio_transcript(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'f.js').write_text('export const x = 2;')
            script=str(Path(__file__).resolve().parents[1]/'scripts'/'mcp_server.py')
            cli=subprocess.run([sys.executable,'-B',script,'--root',str(root),'--tool','inventory_source',
                                '--args-json','{"path":"f.js"}'],capture_output=True,text=True,timeout=12)
            self.assertEqual(cli.returncode,0,cli.stderr)
            self.assertEqual(json.loads(cli.stdout)['result']['count'],1)
            request={'jsonrpc':'2.0','id':1,'method':'initialize',
                     'params':{'protocolVersion':'2025-06-18'}}
            request2={'jsonrpc':'2.0','id':2,'method':'tools/call',
                      'params':{'name':'inventory_source','arguments':{'path':'f.js'}}}
            rpc=subprocess.run([sys.executable,'-B',script,'--root',str(root)],
                               input='\n'.join(json.dumps(x) for x in (request,request2))+'\n',
                               capture_output=True,text=True,timeout=12)
            self.assertEqual(rpc.returncode,0,rpc.stderr)
            responses={x['id']:x for x in map(json.loads,rpc.stdout.splitlines())}
            self.assertEqual(responses[2]['result']['structuredContent']['result']['count'],1)

class ReceiptTrustTests(unittest.TestCase):
    def _obligation(self):
        src='a'*64;dst='b'*64
        obligation={'obligation_id':'checkout','title':'Checkout','required':True,
                    'required_case_kinds':['positive','negative'],'authority_sha256':src}
        binding={'obligation_id':'checkout','owner':'candidate/checkout','contract_type':'json',
                 'candidate_sha256':dst,'fixtures':{'positive':'p','negative':'n'}}
        record={'obligation_id':'checkout','authority':'trusted_runtime_receipt','result':'pass',
                'source_sha256':src,'candidate_sha256':dst,'corpus_sha256':'c'*64,
                'cases':['positive','negative'],'recorder':'independent-test-runner-v1'}
        return obligation,binding,record

    def test_signed_finite_receipt_only_with_private_operator_key(self):
        import hmac
        obligation,binding,receipt=self._obligation()
        key=b'operator-verified-outside-runtime-012345'
        raw=canonical(receipt)
        receipt['receipt_sha256']=digest(raw)
        receipt['attestation_hmac_sha256']=hmac.new(key,raw,hashlib.sha256).hexdigest()
        denied=assess_obligations([obligation],[binding],[receipt],None)
        self.assertEqual(denied['readiness'],'incomplete')
        signed=assess_obligations([obligation],[binding],[receipt],None,key)
        self.assertEqual(signed['readiness'],'ready')
        self.assertEqual(signed['closed_required_count'],1)
        self.assertEqual(assess_obligations([obligation],[binding],[receipt],None,b'd'*40)['readiness'],'incomplete')
        altered=dict(receipt);altered['cases']=['positive']
        self.assertEqual(assess_obligations([obligation],[binding],[altered],None,key)['readiness'],'incomplete')
        with_unknown=assess_obligations([obligation],[binding],[receipt],['unresolved dispatch'],key)
        self.assertEqual(with_unknown['readiness'],'incomplete')
        failed=dict(receipt);failed['result']='fail'
        self.assertEqual(assess_obligations([obligation],[binding],[receipt,failed],None,key)['readiness'],'incomplete')

    def test_secret_key_not_a_public_tool_argument(self):
        self.assertNotIn('trusted_verifier_key',mcp_tools()[0]['inputSchema']['properties'])
        self.assertTrue(all('key' not in str(t['inputSchema']['properties']) for t in mcp_tools()))

    def test_refuses_unpaired_surrogates(self):
        from artifact_index import strict_json
        with self.assertRaisesRegex(ArtifactError,'surrogate'):
            strict_json(b'{"description":"\\ud800"}')

    def test_runtime_symlink_replacement_blocked(self):
        if os.name=='nt':self.skipTest('POSIX nofollow behavior')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'file.txt').write_text('safe')
            a=VirtualArtifact(root)
            (root/'file.txt').unlink()
            (root/'file.txt').symlink_to('/etc/passwd')
            with self.assertRaises((ArtifactError,OSError)):
                a.read('file.txt')

if __name__=='__main__':unittest.main()
