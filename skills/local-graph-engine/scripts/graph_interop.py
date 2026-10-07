"""Interchange, federation, history, usage memory and human-readable exports."""
from __future__ import annotations
import csv
import html
import io
import json
import shutil
import tempfile
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET
import graph_engine as ge
from graph_common import atomic_write,canonical,digest,read_json,write_json,safe_output
from graph_store import readonly,reconstruct_sources,ensure_extensions,apply_patches,logical_hash
from graph_query import query


def bundle(db:Path)->dict:
    con=readonly(db)
    try:
        con.execute('BEGIN')
        return {'schema_version':'graph-bundle-v1','graph_hash':logical_hash(con),'patches':reconstruct_sources(con),'metadata':{'scope':'current source assertions, not history or usage memory','producer_version':ge.PACKAGE_VERSION}}
    finally:con.close()

def import_bundle(db:Path,value:dict,namespace:str)->dict:
    if value.get('schema_version')!='graph-bundle-v1' or not isinstance(value.get('patches'),list):raise ValueError('unsupported graph bundle')
    if not namespace or '/' in namespace:raise ValueError('use a nonempty single-segment namespace')
    prefix='federation:'+quote(namespace,safe='')+':'
    patches=json.loads(canonical(value['patches']))
    for p in patches:
        original=p['source']['uri'];p['source']['uri']=prefix+original
        p['source']['metadata']=dict(p['source'].get('metadata',{}),federation_namespace=namespace,original_source_uri=original)
        for node in p['nodes']:
            node['id']=prefix+node['id']
        for edge in p['edges']:
            edge.pop('id',None);edge['source']=prefix+edge['source'];edge['target']=prefix+edge['target']
    if not patches:return {'status':'pass','mutated':False,'sources_changed':[]}
    return apply_patches(db,patches)

def diff(before:dict,after:dict)->dict:
    if before.get('schema_version')!='graph-view-v1' or after.get('schema_version')!='graph-view-v1':raise ValueError('diff expects two GraphView files')
    result={}
    for key in ['nodes','edges']:
        a={x['id']:x for x in before[key]};b={x['id']:x for x in after[key]}
        result[key]={'added':sorted(set(b)-set(a)),'removed':sorted(set(a)-set(b)),'changed':sorted(x for x in set(a)&set(b) if canonical(a[x])!=canonical(b[x]))}
    return {'status':'pass','diff':result,'scope':'differences in the supplied projections; not necessarily the entire databases'}

def history(db:Path,source_uri:str|None=None)->dict:
    con=readonly(db)
    try:
        if not con.execute("SELECT 1 FROM sqlite_master WHERE name='graph_changes'").fetchone():return {'status':'pass','changes':[],'limitation':'no revision history was captured before version 2'}
        sql='SELECT c.*,s.uri FROM graph_changes c LEFT JOIN sources s ON c.source_id=s.id'
        args=[]
        if source_uri:sql+=' WHERE s.uri=?';args=[source_uri]
        rows=[dict(r) for r in con.execute(sql+' ORDER BY sequence',args)]
        return {'status':'pass','changes':rows}
    finally:con.close()

def source_revision(db:Path,uri:str,revision:str|None=None)->dict:
    con=readonly(db)
    try:
        sid=ge.source_id(uri)
        if revision is None:
            row=con.execute('SELECT revision FROM current_revisions WHERE source_id=?',(sid,)).fetchone()
            if not row:raise ValueError('source revision unavailable')
            revision=row[0]
        row=con.execute('SELECT patch_json FROM source_revisions WHERE source_id=? AND revision=?',(sid,revision)).fetchone()
        if not row:raise ValueError('revision not found')
        return json.loads(row[0])
    finally:con.close()

def drop_source(db:Path,uri:str)->dict:
    patch=source_revision(db,uri)
    patch['nodes']=[];patch['edges']=[];patch['source']['metadata']=dict(patch['source'].get('metadata',{}),tombstone=True)
    return apply_patches(db,[patch])

def remember(db:Path,question:str,node_ids:list[str],outcome:str,note:str='')->dict:
    if outcome not in ('useful','dead_end','corrected'):raise ValueError('invalid outcome')
    if not question or len(question)>4000 or len(note)>8000:raise ValueError('memory text exceeds bounds or is empty')
    con=ge.connect(db)
    try:
        con.execute('BEGIN IMMEDIATE');ensure_extensions(con)
        existing={r[0] for r in con.execute('SELECT id FROM active_nodes')}
        if set(node_ids)-existing:raise ValueError('memory references unknown nodes')
        graph_hash=logical_hash(con);identifier='memory:'+digest([question,sorted(node_ids),outcome,note,graph_hash])[:32]
        con.execute('INSERT OR IGNORE INTO graph_memory VALUES(?,?,?,?,?,?)',(identifier,question,canonical(sorted(set(node_ids))),outcome,note,graph_hash));con.commit()
        return {'status':'pass','id':identifier,'graph_hash':graph_hash}
    except Exception:con.rollback();raise
    finally:con.close()

def reflect(db:Path)->dict:
    con=readonly(db)
    try:
        if not con.execute("SELECT 1 FROM sqlite_master WHERE name='graph_memory'").fetchone():return {'status':'pass','nodes':[]}
        current=logical_hash(con);counts=defaultdict(Counter)
        for row in con.execute('SELECT * FROM graph_memory ORDER BY id'):
            for node in json.loads(row['node_ids_json']):
                counts[node][row['outcome']]+=1
                if row['graph_hash']!=current:counts[node]['needs_revalidation']+=1
        return {'status':'pass','nodes':[{'id':n,**dict(sorted(v.items()))} for n,v in sorted(counts.items())],'interpretation':'usage observations only; do not alter source facts, confidence or ranking without an explicit policy'}
    finally:con.close()

def export_view(db:Path,request:dict|None=None)->dict:
    con=readonly(db)
    try:
        con.execute('BEGIN');return query(con,dict(request or {},operation='subgraph'))['view']
    finally:con.close()

def serialize_view(view:dict,format:str)->str:
    nodes=view['nodes'];edges=view['edges']
    if format=='json':return json.dumps(view,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if format=='dot':
        # A mixed graph is exported as a digraph; undirected edges disable arrows.
        lines=['digraph LocalGraph {']
        for n in nodes:lines.append('  '+json.dumps(n['id'])+' [label='+json.dumps(n['label'])+'];')
        for e in edges:lines.append('  '+json.dumps(e['source'])+' -> '+json.dumps(e['target'])+' [label='+json.dumps(e['relation'])+(', dir=none' if not e.get('directed',True) else '')+'];')
        return '\n'.join(lines+['}'])+'\n'
    if format=='mermaid':
        ids={n['id']:'n'+str(i) for i,n in enumerate(nodes)}
        def label(s):return html.escape(s,quote=True).replace('\n',' ').replace('[','&#91;').replace(']','&#93;').replace('|','&#124;')
        lines=['flowchart LR']+[f'  {ids[n["id"]]}["{label(n["label"])}"]' for n in nodes]
        for e in edges:lines.append(f'  {ids[e["source"]]} '+('-->' if e.get('directed',True) else '---')+f'|"{label(e["relation"])}"| {ids[e["target"]]}')
        return '\n'.join(lines)+'\n'
    if format=='graphml':
        ns='http://graphml.graphdrawing.org/xmlns';ET.register_namespace('',ns)
        root=ET.Element('{'+ns+'}graphml')
        for key in ['label','kind','relation','properties']:
            ET.SubElement(root,'{'+ns+'}key',{'id':key,'for':'all','attr.name':key,'attr.type':'string'})
        graph=ET.SubElement(root,'{'+ns+'}graph',{'id':'G','edgedefault':'directed'})
        for n in nodes:
            item=ET.SubElement(graph,'{'+ns+'}node',{'id':n['id']})
            for k in ['label','kind','properties']:ET.SubElement(item,'{'+ns+'}data',{'key':k}).text=canonical(n.get(k,{})) if k=='properties' else n.get(k,'')
        for e in edges:
            item=ET.SubElement(graph,'{'+ns+'}edge',{'id':e['id'],'source':e['source'],'target':e['target'],'directed':str(e.get('directed',True)).lower()})
            ET.SubElement(item,'{'+ns+'}data',{'key':'relation'}).text=e['relation']
            ET.SubElement(item,'{'+ns+'}data',{'key':'properties'}).text=canonical(e.get('properties',{}))
        return ET.tostring(root,encoding='unicode',xml_declaration=True)+'\n'
    if format=='csv':
        buff=io.StringIO();writer=csv.writer(buff);writer.writerow(['id','kind','label','properties_json'])
        def safe(value):
            s=str(value)
            return "'"+s if s and s.lstrip().startswith(('=','+','-','@')) else s
        for n in nodes:writer.writerow([safe(n['id']),safe(n['kind']),safe(n['label']),safe(canonical(n.get('properties',{})))])
        return buff.getvalue()
    raise ValueError('unsupported export format')

def export_wiki(view:dict,destination:Path)->dict:
    destination=Path(destination).resolve()
    if destination.exists():raise FileExistsError('wiki destination must be new; never overwrite user notes')
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.graph-wiki-',dir=destination.parent))
    try:
        filenames={n['id']:digest(n['id'])[:24]+'.md' for n in view['nodes']}
        for n in view['nodes']:
            lines=['# '+html.escape(n['label']),'','Kind: '+html.escape(n['kind']),'','## Properties','','```json',json.dumps(n.get('properties',{}),ensure_ascii=False,sort_keys=True,indent=2),'```','','## Relationships','']
            for e in view['edges']:
                if e['source']==n['id']:lines.append('- '+html.escape(e['relation'])+' -> ['+html.escape(e['target'])+']('+filenames[e['target']]+')')
                elif e['target']==n['id']:lines.append('- ['+html.escape(e['source'])+']('+filenames[e['source']]+') -> '+html.escape(e['relation']))
            lines+=['','## Evidence','','```json',json.dumps(n.get('evidence',[]),ensure_ascii=False,indent=2),'```']
            (stage/filenames[n['id']]).write_text('\n'.join(lines)+'\n',encoding='utf-8')
        index=['# Local Graph Wiki','','Generated projection; original data remains authoritative.','']+['- ['+html.escape(n['label']).replace('[','&#91;').replace(']','&#93;')+']('+filenames[n['id']]+')' for n in view['nodes']]
        (stage/'index.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
        stage.rename(destination)
        return {'status':'pass','output':str(destination),'pages':len(filenames)+1}
    finally:
        if stage.exists():shutil.rmtree(stage)


def graphml_patch(path:Path,namespace:str)->dict:
    """Import ordinary GraphML with explicit source evidence, never inferred edges."""
    from graph_data import evidence,file_info
    from graph_common import MAX_BYTES,parse_json
    if path.stat().st_size>MAX_BYTES:raise ValueError('GraphML exceeds input byte budget')
    raw=path.read_bytes()
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('GraphML DTD/entities are not accepted')
    root=ET.fromstring(raw);ns={'g':'http://graphml.graphdrawing.org/xmlns'}
    if root.tag!='{'+ns['g']+'}graphml':raise ValueError('expected standard GraphML namespace')
    graphs=root.findall('g:graph',ns)
    if len(graphs)!=1:raise ValueError('exactly one top-level GraphML graph is required')
    graph=graphs[0]
    if graph.get('edgedefault') not in ('directed','undirected'):raise ValueError('GraphML requires an explicit directed or undirected default')
    if graph.findall('.//g:graph',ns) or graph.findall('.//g:hyperedge',ns):raise ValueError('nested graphs/hyperedges need an explicit relationship-node mapping')
    definitions={k.get('id'):k.get('attr.name',k.get('id')) for k in root.findall('g:key',ns)}
    prefix='graphml:'+quote(namespace,safe='')+':'
    def values(item):
        result={}
        for d in item.findall('g:data',ns):
            name=definitions.get(d.get('key'),d.get('key'));value=d.text or ''
            if name in result:raise ValueError('duplicate GraphML data field')
            result[name]=value
        props={k:v for k,v in result.items() if k not in ('label','kind','relation','properties')}
        if 'properties' in result:
            supplied=parse_json(result['properties'])
            if not isinstance(supplied,dict):raise ValueError('properties must encode a JSON object')
            props.update(supplied)
        return result,props
    nodes=[];edges=[];ids=set()
    for n in graph.findall('g:node',ns):
        identifier=n.get('id')
        if not identifier or identifier in ids:raise ValueError('missing or duplicate GraphML node ID')
        ids.add(identifier);fields,props=values(n)
        nodes.append({'id':prefix+identifier,'kind':fields.get('kind') or 'entity','label':fields.get('label') or identifier,'properties':props,'evidence':evidence('node:'+identifier)})
    for i,e in enumerate(graph.findall('g:edge',ns)):
        if e.get('source') not in ids or e.get('target') not in ids:raise ValueError('GraphML edge references unknown endpoint')
        fields,props=values(e);direction=e.get('directed',str(graph.get('edgedefault')=='directed').lower())
        if direction not in ('true','false'):raise ValueError('invalid GraphML direction')
        edges.append({'source':prefix+e.get('source'),'target':prefix+e.get('target'),'relation':fields.get('relation') or 'related_to','directed':direction=='true','properties':props,'evidence':evidence('edge:'+str(i),details={'imported_relation':True})})
    # GraphPatch edge identity is (source,target,relation,direction). Preserve any
    # repeated GraphML occurrences as observations instead of silently dropping.
    from graph_adapters import merge_records
    return merge_records({'schema_version':'graph-patch-v1','source':file_info(path,namespace),'nodes':nodes,'edges':edges})


def save_query(db:Path,name:str,request:dict)->dict:
    from graph_query import validate_request
    if not name or len(name)>120:raise ValueError('query name must contain 1..120 characters')
    request=validate_request(request);con=ge.connect(db)
    try:
        con.execute('BEGIN IMMEDIATE');ensure_extensions(con)
        con.execute('INSERT INTO saved_queries VALUES(?,?) ON CONFLICT(name) DO UPDATE SET request_json=excluded.request_json',(name,canonical(request)))
        con.commit();return {'status':'pass','name':name,'request':request}
    except Exception:con.rollback();raise
    finally:con.close()


def saved_queries(db:Path,name:str|None=None)->dict:
    con=readonly(db)
    try:
        if not con.execute("SELECT 1 FROM sqlite_master WHERE name='saved_queries'").fetchone():return {'status':'pass','queries':[]}
        rows=[{'name':r['name'],'request':json.loads(r['request_json'])} for r in con.execute('SELECT * FROM saved_queries ORDER BY name')]
        if name:
            found=[r for r in rows if r['name']==name]
            if not found:raise ValueError('saved query not found')
            return query(con,found[0]['request'])
        return {'status':'pass','queries':rows}
    finally:con.close()
