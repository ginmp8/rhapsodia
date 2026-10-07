"""Bounded local source adapters. Never execute source code or fetch links."""
from __future__ import annotations
import ast
import hashlib
import json
import re
import sqlite3
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import quote,unquote,urlparse
import xml.etree.ElementTree as ET
from graph_common import MAX_BYTES,canonical,digest,read_json,finite_tree
from graph_data import evidence,structural_json,scrub

EXCLUDED={'.git','.hg','.svn','node_modules','.venv','venv','__pycache__','.local-graph','dist','build'}
SECRET_EXT={'.pem','.key','.p12','.pfx','.kdbx'}
TEXT_EXT={'.md','.markdown','.txt','.rst','.adoc','.log','.csv','.tsv','.json','.jsonl','.ndjson','.yaml','.yml','.xml','.html','.htm','.sql','.toml','.ini','.conf'}
CODE_LANG={'.py':'python','.cs':'csharp','.js':'javascript','.mjs':'javascript','.cjs':'javascript','.jsx':'jsx','.ts':'typescript','.tsx':'tsx','.java':'java','.go':'go','.rs':'rust','.c':'c','.h':'c','.cpp':'cpp','.hpp':'cpp','.rb':'ruby','.php':'php','.swift':'swift','.kt':'kotlin','.ex':'elixir','.exs':'elixir','.sh':'bash','.scala':'scala'}

def file_id(namespace,relative):return 'file:'+digest([namespace,relative])[:32]

def file_source(path,root,namespace):
    relative=path.relative_to(root).as_posix()
    return {'uri':'source://'+quote(namespace,safe='')+'/'+quote(relative,safe='/'),'kind':'file','content_hash':'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest(),'metadata':{'namespace':namespace,'path':relative}}

def node(nid,kind,label,locator,properties=None,provenance='EXTRACTED'):
    return {'id':nid,'kind':kind,'label':str(label),'properties':properties or {},'evidence':evidence(locator,provenance)}

def edge(s,t,relation,locator,provenance='EXTRACTED'):
    return {'source':s,'target':t,'relation':relation,'directed':True,'properties':{},'evidence':evidence(locator,provenance)}

def merge_records(patch):
    nodes={};edges={}
    for n in patch['nodes']:
        if n['id'] in nodes:
            prior=nodes[n['id']]
            prior['evidence'].extend(n['evidence'])
            if prior.get('properties',{}).get('history_boundary') and not n.get('properties',{}).get('history_boundary'):
                prior['label']=n['label'];prior['properties']=n['properties']
        else:nodes[n['id']]=n
    for e in patch['edges']:
        if e.get('properties'):
            for ev in e['evidence']:
                ev['details']=dict(ev.get('details',{}),observed_properties=e['properties'])
        key=(e['source'],e['target'],e['relation'],e.get('directed',True))
        if key in edges:edges[key]['evidence'].extend(e['evidence'])
        else:edges[key]=e
    # Duplicate evidence observations do not require duplicate SQLite rows.
    for r in list(nodes.values())+list(edges.values()):r['evidence']=[json.loads(v) for v in sorted({canonical(ev) for ev in r['evidence']})]
    patch['nodes']=sorted(nodes.values(),key=lambda n:n['id']);patch['edges']=sorted(edges.values(),key=canonical)
    return patch

def parse_python(text,patch,fid,relative,namespace):
    tree=ast.parse(text,filename=relative);definitions={};scope=[]
    class Declarations(ast.NodeVisitor):
        def visit_ClassDef(self,n):self.declare(n,'class')
        def visit_FunctionDef(self,n):self.declare(n,'function')
        def visit_AsyncFunctionDef(self,n):self.declare(n,'function')
        def declare(self,n,kind):
            qualified='.'.join(scope+[n.name]);nid='symbol:'+digest([namespace,relative,qualified,kind])[:32]
            parent=definitions.get('.'.join(scope),fid)
            definitions[qualified]=nid
            patch['nodes'].append(node(nid,kind,qualified,f'L{n.lineno}',{'path':relative,'line':n.lineno,'qualified_name':qualified}))
            patch['edges'].append(edge(parent,nid,'defines',f'L{n.lineno}'))
            scope.append(n.name);self.generic_visit(n);scope.pop()
        def visit_Import(self,n):
            for item in n.names:self.add_import(item.name,n.lineno)
        def visit_ImportFrom(self,n):self.add_import('.'*n.level+(n.module or ''),n.lineno)
        def add_import(self,name,line):
            nid='module:'+digest([namespace,name])[:32]
            patch['nodes'].append(node(nid,'module',name,f'L{line}',{'resolution':'import declaration; runtime target not resolved'}))
            patch['edges'].append(edge(fid,nid,'imports',f'L{line}'))
    Declarations().visit(tree)
    class Calls(ast.NodeVisitor):
        def visit_ClassDef(self,n):self.enter(n)
        def visit_FunctionDef(self,n):self.enter(n)
        def visit_AsyncFunctionDef(self,n):self.enter(n)
        def enter(self,n):scope.append(n.name);self.generic_visit(n);scope.pop()
        def visit_Call(self,n):
            if isinstance(n.func,ast.Name):
                name=n.func.id;owner=definitions.get('.'.join(scope),fid)
                candidate=definitions.get('.'.join(scope[:-1]+[name])) or definitions.get(name)
                # Dynamic rebinding is possible even for lexical matches. Keep
                # the call-site syntax distinct from an inferred target binding.
                ref='reference:'+digest([namespace,relative,n.lineno,n.col_offset,name])[:32]
                patch['nodes'].append(node(ref,'symbol_reference',name,f'L{n.lineno}',{'path':relative,'line':n.lineno,'resolution':'syntactic call site'}))
                patch['edges'].append(edge(owner,ref,'calls_reference',f'L{n.lineno}'))
                if candidate:patch['edges'].append(edge(ref,candidate,'may_resolve_to',f'L{n.lineno}','INFERRED'))
            self.generic_visit(n)
    Calls().visit(tree)

def parse_tree_sitter(text,patch,fid,relative,namespace,language):
    try:from tree_sitter_language_pack import get_parser
    except ImportError as exc:raise RuntimeError('Tree-sitter requires the optional tree-sitter-language-pack library') from exc
    parser=get_parser(language);raw=text.encode('utf-8');tree=parser.parse(raw)
    definition_types={'class_declaration','class_definition','interface_declaration','struct_item','struct_specifier','enum_declaration','function_definition','function_declaration','method_declaration','method_definition','function_item','trait_item'}
    stack=[(tree.root_node,fid)];errors=0
    while stack:
        current,parent=stack.pop()
        if current.type=='ERROR' or current.is_missing:errors+=1
        owner=parent
        if current.type in definition_types:
            name=current.child_by_field_name('name')
            if name:
                label=raw[name.start_byte:name.end_byte].decode('utf-8','replace');line=current.start_point[0]+1
                owner='syntax:'+digest([namespace,relative,parent,label,current.type])[:32]
                patch['nodes'].append(node(owner,'symbol',label,f'L{line}',{'path':relative,'line':line,'language':language,'syntax_kind':current.type}))
                patch['edges'].append(edge(parent,owner,'defines',f'L{line}'))
        for child in reversed(current.named_children):stack.append((child,owner))
    patch['source']['metadata']['parse_errors']=errors
    patch['source']['metadata']['coverage']='syntax definitions only; no semantic call resolution'

def document_text(path):
    suffix=path.suffix.lower()
    if suffix=='.pdf':
        try:from pypdf import PdfReader
        except ImportError as exc:raise RuntimeError('PDF requires the optional pypdf library') from exc
        reader=PdfReader(path)
        if reader.is_encrypted:raise ValueError('encrypted PDF requires an explicitly decrypted input')
        pages=[]
        for i,p in enumerate(reader.pages,1):
            if i>1000:raise ValueError('PDF page budget exceeded')
            pages.append(f'\n# Page {i}\n'+(p.extract_text() or ''))
        return '\n'.join(pages)
    if suffix=='.docx':
        with zipfile.ZipFile(path) as z:
            member=z.getinfo('word/document.xml')
            if member.file_size>MAX_BYTES:raise ValueError('DOCX XML exceeds budget')
            raw=z.read(member)
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('DOCX entity declarations are not accepted')
        root=ET.fromstring(raw);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        return '\n'.join(''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in root.findall('.//w:p',ns))
    if suffix in ('.html','.htm'):
        from html.parser import HTMLParser
        class Text(HTMLParser):
            def __init__(self):super().__init__();self.parts=[];self.ignore=0
            def handle_starttag(self,tag,attrs):
                if tag in ('script','style'):self.ignore+=1
            def handle_endtag(self,tag):
                if tag in ('script','style') and self.ignore:self.ignore-=1
            def handle_data(self,data):
                if not self.ignore:self.parts.append(data)
        parser=Text();parser.feed(path.read_text(encoding='utf-8'));return '\n'.join(parser.parts)
    return path.read_text(encoding='utf-8-sig')

def parse_document(text,patch,fid,path,root,namespace):
    if len(text.encode('utf-8'))>MAX_BYTES:raise ValueError('extracted text exceeds budget')
    relative=path.relative_to(root).as_posix();headers=[]
    for index,line in enumerate(text.splitlines(),1):
        match=re.match(r'^(#{1,6})\s+(.+)',line)
        if match:
            level=len(match[1]);label=match[2];sid='section:'+digest([namespace,relative,index,label])[:32]
            while headers and headers[-1][0]>=level:headers.pop()
            parent=headers[-1][1] if headers else fid
            patch['nodes'].append(node(sid,'section',label,f'L{index}',{'path':relative,'line':index}))
            patch['edges'].append(edge(parent,sid,'contains',f'L{index}'));headers.append((level,sid))
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',line):
            parsed=urlparse(link)
            if parsed.scheme in ('http','https'):
                target='url:'+digest(link)[:32];kind='url';props={'uri':link,'fetched':False}
            elif not parsed.scheme and not parsed.netloc and parsed.path:
                resolved=(path.parent/unquote(parsed.path)).resolve()
                try:rel=resolved.relative_to(root).as_posix()
                except ValueError:continue
                target=file_id(namespace,rel);kind='file';props={'path':rel,'exists_in_source_root':resolved.is_file()}
            else:continue
            patch['nodes'].append(node(target,kind,link,f'L{index}',props))
            patch['edges'].append(edge(headers[-1][1] if headers else fid,target,'references',f'L{index}'))
    patch['source']['metadata']['text_characters']=len(text)
    patch['source']['metadata']['coverage']='headings and explicit links only; semantic claims require agent-authored evidence'
    if not text.strip():patch['source']['metadata']['warning']='no extractable text; scan/image interpretation is not automatic'

def parse_file(path:Path,root:Path,namespace:str,code_backend='builtin')->dict:
    path=path.resolve();root=root.resolve()
    if not path.is_relative_to(root):raise ValueError('source escapes root')
    if path.stat().st_size>MAX_BYTES:raise ValueError('file exceeds byte budget')
    source=file_source(path,root,namespace);rel=source['metadata']['path'];fid=file_id(namespace,rel)
    patch={'schema_version':'graph-patch-v1','source':source,'nodes':[node(fid,'file',path.name,'file',{'path':rel,'extension':path.suffix.lower()})],'edges':[]}
    parent=path.parent
    if parent!=root:
        directory=parent.relative_to(root).as_posix();pid='directory:'+digest([namespace,directory])[:32]
        patch['nodes'].append(node(pid,'directory',directory,'file',{'path':directory}))
        patch['edges'].append(edge(pid,fid,'contains','file'))
    suffix=path.suffix.lower()
    if suffix in CODE_LANG:
        text=path.read_text(encoding='utf-8-sig')
        if suffix=='.py' and code_backend=='builtin':parse_python(text,patch,fid,rel,namespace)
        elif code_backend=='tree-sitter':parse_tree_sitter(text,patch,fid,rel,namespace,CODE_LANG[suffix])
        else:source['metadata']['coverage']='file inventory only; select tree-sitter or the Roslyn adapter for definitions'
    elif suffix in ('.md','.markdown','.txt','.rst','.adoc','.html','.htm','.pdf','.docx'):
        parse_document(document_text(path),patch,fid,path,root,namespace)
    else:source['metadata']['coverage']='file inventory; use a structured adapter or explicit mapping to extract records'
    return merge_records(patch)

def scan(root:Path,namespace:str,code_backend='builtin',max_files=2000,extensions=None)->dict:
    root=Path(root).resolve()
    if not root.is_dir():raise ValueError('scan source must be a directory')
    if not 1<=max_files<=100000:raise ValueError('max_files outside 1..100000')
    patches=[];skipped=[];failures=[];candidates=[]
    import os
    for parent,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in EXCLUDED and not (Path(parent)/d).is_symlink())
        for name in sorted(files):
            path=Path(parent)/name;rel=path.relative_to(root).as_posix()
            if path.is_symlink():skipped.append({'path':rel,'reason':'symlink'});continue
            if name=='.env' or name.startswith('.env.') or path.suffix.lower() in SECRET_EXT:
                skipped.append({'path':rel,'reason':'secret-bearing filename'});continue
            if extensions and path.suffix.lower() not in extensions:skipped.append({'path':rel,'reason':'extension filter'});continue
            candidates.append(path)
            if len(candidates)>max_files:raise ValueError('file budget exceeded; narrow the root or raise max_files')
    for path in candidates:
        try:patches.append(parse_file(path,root,namespace,code_backend))
        except (OSError,ValueError,SyntaxError,RuntimeError,UnicodeError,zipfile.BadZipFile,ET.ParseError) as exc:
            failures.append({'path':path.relative_to(root).as_posix(),'reason':str(exc)})
    return {'status':'pass' if not failures else 'fail','patches':patches,'coverage':{'candidates':len(candidates),'parsed':len(patches),'skipped':skipped,'failures':failures},'policy':'atomic import only when every selected source parsed successfully; no automatic deletion of disappeared sources'}

def sqlite_schema(path:Path,namespace:str)->dict:
    con=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        con.row_factory=sqlite3.Row;con.execute('PRAGMA query_only=ON');con.execute('PRAGMA trusted_schema=OFF')
        names=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND sql NOT LIKE 'CREATE VIRTUAL%' ORDER BY name")]
        if len(names)>10000:raise ValueError('schema table budget exceeded')
        schema={}
        for name in names:
            q='"'+name.replace('"','""')+'"'
            schema[name]={'columns':[dict(r) for r in con.execute(f'PRAGMA table_info({q})')],'foreign_keys':[dict(r) for r in con.execute(f'PRAGMA foreign_key_list({q})')]}
        uri='schema://'+quote(namespace,safe='')+'/'+quote(path.name,safe='')
        p={'schema_version':'graph-patch-v1','source':{'uri':uri,'kind':'database_schema','content_hash':'sha256:'+digest(schema),'metadata':{'namespace':namespace}},'nodes':[],'edges':[]}
        ids={name:'table:'+digest([namespace,name])[:32] for name in names}
        for name,meta in schema.items():
            p['nodes'].append(node(ids[name],'table',name,'table:'+name))
            for col in meta['columns']:
                cid='column:'+digest([namespace,name,col['name']])[:32]
                p['nodes'].append(node(cid,'column',col['name'],name+'.'+col['name'],{'sql_type':col['type'],'primary_key_position':col['pk'],'not_null':bool(col['notnull'])}))
                p['edges'].append(edge(ids[name],cid,'has_column',name+'.'+col['name']))
            for fk in meta['foreign_keys']:
                target=ids.get(fk['table'])
                if not target:
                    target='table:'+digest([namespace,fk['table']])[:32]
                    p['nodes'].append(node(target,'unresolved_table',fk['table'],name+':FK',{'resolution':'target table missing'}))
                e=edge(ids[name],target,'foreign_key',name+':FK'+str(fk['id']))
                e['properties']={'from_column':fk['from'],'to_column':fk['to'],'on_delete':fk['on_delete']};p['edges'].append(e)
        return merge_records(p)
    finally:con.close()

def openapi(path:Path,namespace:str)->dict:
    value=read_json(path)
    if not isinstance(value,dict) or not ('openapi' in value or 'swagger' in value):raise ValueError('expected OpenAPI JSON')
    uri='openapi://'+quote(namespace,safe='')+'/'+quote(path.name,safe='');p={'schema_version':'graph-patch-v1','source':{'uri':uri,'kind':'openapi','content_hash':'sha256:'+digest(value)},'nodes':[],'edges':[]}
    components=value.get('components',{}).get('schemas',value.get('definitions',{}))
    schemas={name:'schema:'+digest([namespace,name])[:32] for name in components}
    for name,definition in sorted(components.items()):p['nodes'].append(node(schemas[name],'schema',name,'#/components/schemas/'+name,{'type':definition.get('type')}))
    for route,methods in sorted(value.get('paths',{}).items()):
        for method,operation in sorted(methods.items()):
            if method.lower() not in ('get','post','put','patch','delete','options','head','trace'):continue
            eid='endpoint:'+digest([namespace,method,route])[:32];loc='#/paths/'+route+'/'+method
            p['nodes'].append(node(eid,'endpoint',method.upper()+' '+route,loc,{'method':method,'route':route,'operation_id':operation.get('operationId')}))
            stack=[operation]
            while stack:
                item=stack.pop()
                if isinstance(item,dict):
                    ref=item.get('$ref')
                    if isinstance(ref,str):
                        name=ref.rsplit('/',1)[-1]
                        if ref.startswith('#/') and name in schemas:p['edges'].append(edge(eid,schemas[name],'references_schema',loc))
                    stack.extend(item.values())
                elif isinstance(item,list):stack.extend(item)
    return merge_records(p)

def git_history(root:Path,namespace:str,max_commits=100)->dict:
    if not 1<=max_commits<=1000:raise ValueError('commit budget outside 1..1000')
    def git(*args):
        p=subprocess.run(['git','-c','core.fsmonitor=false','-c','core.pager=cat','-C',str(root),*args],capture_output=True,timeout=30)
        if p.returncode:raise ValueError('Git read command failed; verify repository and local Git availability')
        if len(p.stdout)>MAX_BYTES:raise ValueError('Git output budget exceeded')
        return p.stdout
    raw=git('log',f'--max-count={max_commits}','--format=%H%x00%P%x00%aI%x00%s%x00','-z')
    fields=raw.decode('utf-8','replace').split('\x00')
    if fields and fields[-1]=='':fields.pop()
    if len(fields)%5:raise ValueError('unexpected Git log record framing')
    chunks=[fields[i:i+5] for i in range(0,len(fields),5)]
    patches={'schema_version':'graph-patch-v1','source':{'uri':'git://'+quote(namespace,safe='')+'/history','kind':'git_history','content_hash':'sha256:'+hashlib.sha256(raw).hexdigest(),'metadata':{'limit':max_commits,'authors_stored':False}},'nodes':[],'edges':[]}
    for chunk in chunks:
        sha,parents,time,subject,terminator=chunk
        if terminator:raise ValueError('unexpected Git record terminator')
        cid='commit:'+namespace+':'+sha
        patches['nodes'].append(node(cid,'commit',subject or sha[:12],sha,{'sha':sha,'timestamp':time}))
        for parent in parents.split():
            pid='commit:'+namespace+':'+parent
            patches['nodes'].append(node(pid,'commit',parent[:12],sha,{'sha':parent,'history_boundary':True}));patches['edges'].append(edge(cid,pid,'parent_commit',sha))
        entries=git('diff-tree','--root','--no-commit-id','--name-status','--no-ext-diff','--no-renames','-r','-z',sha).decode('utf-8','replace').split('\x00')
        entries=[x for x in entries if x]
        if len(entries)%2:raise ValueError('unexpected Git name-status framing')
        for i in range(0,len(entries),2):
            status,path=entries[i:i+2];fid=file_id(namespace,path)
            patches['nodes'].append(node(fid,'file',path,sha,{'path':path}));e=edge(cid,fid,'changes',sha);e['properties']={'change_status':status};patches['edges'].append(e)
    return merge_records(patches)

def transcribe(path:Path,model_dir:Path,namespace:str)->dict:
    if not model_dir.is_dir():raise ValueError('provide a local Whisper model directory; automatic downloads are disabled')
    try:from faster_whisper import WhisperModel
    except ImportError as exc:raise RuntimeError('transcription requires optional faster-whisper and a local model') from exc
    model=WhisperModel(str(model_dir),device='cpu',compute_type='int8',local_files_only=True)
    segments,info=model.transcribe(str(path),beam_size=1)
    source={'uri':'media://'+quote(namespace,safe='')+'/'+quote(path.name,safe=''),'kind':'transcript','content_hash':'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest(),'metadata':{'language':info.language,'model_path_name':model_dir.name,'method':'local speech model; transcript is inferred'}}
    patch={'schema_version':'graph-patch-v1','source':source,'nodes':[],'edges':[]};previous=None
    for i,segment in enumerate(segments):
        if i>=100000:raise ValueError('transcript segment budget exceeded')
        nid='segment:'+digest([source['uri'],i])[:32]
        patch['nodes'].append(node(nid,'transcript_segment',segment.text.strip(),f'{segment.start:.3f}-{segment.end:.3f}',{'start_seconds':segment.start,'end_seconds':segment.end},'INFERRED'))
        if previous:patch['edges'].append(edge(previous,nid,'next_segment',str(i),'DERIVED'))
        previous=nid
    return patch
