"""Bounded read-only graph queries shared by CLI, local HTTP and MCP."""
from __future__ import annotations
import heapq
import json
import math
import sqlite3
from collections import Counter, defaultdict, deque
from datetime import datetime
from typing import Any
import graph_engine as ge
from graph_common import canonical, digest, integer
from graph_store import logical_hash

OPERATIONS={'search','find','node','neighbors','path','impact','subgraph','stats','aggregate','timeline','quality'}
FIELDS={'operation','query','node','seed','target','direction','depth','relations','kinds','statuses','provenance','min_confidence','max_nodes','limit','offset','property','group_by','metric','time_property','from','to','weight'}

def validate_request(request: dict) -> dict:
    if not isinstance(request,dict):raise ValueError('query must be an object')
    if set(request)-FIELDS:raise ValueError('unknown query fields: '+', '.join(sorted(set(request)-FIELDS)))
    out=dict(request)
    if out.get('operation','subgraph') not in OPERATIONS:raise ValueError('unsupported operation')
    out.setdefault('operation','subgraph')
    for key,default,low,high in [('depth',2,0,100),('max_nodes',500,1,10000),('limit',100,1,10000),('offset',0,0,1000000)]:
        out.setdefault(key,default);integer(out[key],key,low,high)
    out.setdefault('statuses',['accepted'])
    for key in ['relations','kinds','statuses','provenance']:
        if key in out and (not isinstance(out[key],list) or any(not isinstance(x,str) or not x for x in out[key])):raise ValueError(key+' must be an array of strings')
    if not out['statuses'] or set(out['statuses'])-ge.ACTIVE_EVIDENCE_STATUS:raise ValueError('unsupported/empty statuses')
    if set(out.get('provenance',[]))-ge.PROVENANCE:raise ValueError('unsupported provenance')
    confidence=out.get('min_confidence',0)
    if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or not 0<=confidence<=1:raise ValueError('min_confidence must be in [0,1]')
    if out.get('direction','outgoing') not in ('outgoing','incoming','both','dependents','dependencies'):raise ValueError('invalid direction')
    for k in ['query','node','seed','target','property','group_by','metric','time_property','from','to','weight']:
        if k in out and out[k] is not None and (not isinstance(out[k],str) or len(out[k])>2048):raise ValueError(k+' must be a bounded string')
    return out

def filtered_graph(con,request):
    condition='status IN ('+','.join('?' for _ in request['statuses'])+') AND confidence>=?'
    args=list(request['statuses'])+[request.get('min_confidence',0)]
    if request.get('provenance'):
        condition+=' AND provenance IN ('+','.join('?' for _ in request['provenance'])+')';args+=request['provenance']
    raw=con.execute(f'SELECT * FROM edges WHERE EXISTS(SELECT 1 FROM edge_evidence WHERE edge_id=edges.id AND {condition}) ORDER BY id',args).fetchmany(200001)
    if len(raw)>200000:raise ValueError('edge query budget exceeded; partition the dataset')
    rows=[r for r in raw if not request.get('relations') or r['relation'] in request['relations']]
    own={r[0] for r in con.execute(f'SELECT DISTINCT node_id FROM node_evidence WHERE {condition}',args)}
    endpoints={n for r in rows for n in (r['source_node_id'],r['target_node_id'])}
    ns=con.execute('SELECT id,kind,label,properties_json FROM nodes ORDER BY id').fetchmany(100001)
    if len(ns)>100000:raise ValueError('node query budget exceeded; partition the dataset')
    nodes={r['id']:dict(r) for r in ns if r['id'] in own|endpoints and (not request.get('kinds') or r['kind'] in request['kinds'])}
    rows=[r for r in rows if r['source_node_id'] in nodes and r['target_node_id'] in nodes]
    return nodes,rows

def resolve(nodes,token,con=None):
    if token in nodes:return token
    hits=[k for k,v in nodes.items() if v['label'].casefold()==str(token).casefold()]
    if con:
        hits+= [r['node_id'] for r in con.execute('SELECT alias,node_id FROM node_aliases') if r['alias'].casefold()==str(token).casefold() and r['node_id'] in nodes]
    hits=sorted(set(hits))
    if len(hits)!=1:raise ValueError('ambiguous node: '+canonical(hits) if hits else 'node not found in the selected evidence/filter scope')
    return hits[0]

def adjacency(rows,direction='outgoing'):
    out=defaultdict(list)
    for r in rows:
        s,t,e=r['source_node_id'],r['target_node_id'],r['id']
        if direction in ('outgoing','both','dependencies') or not r['directed']:out[s].append((t,e))
        if direction in ('incoming','both','dependents') or not r['directed']:out[t].append((s,e))
    return {k:sorted(set(v)) for k,v in out.items()}

def details(con,kind,entity_id,limit=100):
    claim_table=kind+'_claims';column=kind+'_id'
    if con.execute("SELECT 1 FROM sqlite_master WHERE name=?",(claim_table,)).fetchone():
        stored=con.execute(f'SELECT c.payload_json,s.uri FROM {claim_table} c JOIN sources s ON s.id=c.source_id WHERE {column}=? ORDER BY s.uri',(entity_id,)).fetchall()
        observations=[]
        for r in stored:
            for ev in json.loads(r['payload_json']).get('evidence',[]):observations.append(dict(ev,source_uri=r['uri']))
        if observations:
            observations=sorted({canonical(x):x for x in observations}.values(),key=canonical)
            return observations[:limit],len(observations)>limit
    table,column=('node_evidence','node_id') if kind=='node' else ('edge_evidence','edge_id')
    rows=con.execute(f'SELECT e.*,s.uri FROM {table} e JOIN sources s ON s.id=e.source_id WHERE {column}=? ORDER BY s.uri,e.locator,e.id',(entity_id,)).fetchmany(limit+1)
    evidence=[{'source_uri':r['uri'],'locator':r['locator'],'provenance':r['provenance'],'confidence':r['confidence'],'status':r['status'],'details':json.loads(r['details_json'])} for r in rows[:limit]]
    return evidence,len(rows)>limit

def node_view(con,nid):
    value=ge.node_record(con,nid)
    value['evidence'],value['evidence_truncated']=details(con,'node',nid)
    value['claims']=claims(con,'node',nid)
    return value

def edge_view(con,row):
    value=ge.edge_record(con,row)
    value['evidence'],value['evidence_truncated']=details(con,'edge',row['id'])
    value['claims']=claims(con,'edge',row['id'])
    return value

def project(con,request,nodes,rows,ids=None,truncated=False):
    ids=sorted(nodes if ids is None else ids);selected=set(ids)
    recs=[node_view(con,x) for x in ids]
    edges=[edge_view(con,r) for r in rows if r['source_node_id'] in selected and r['target_node_id'] in selected]
    run,cmap,communities=ge.latest_community_map(con,selected)
    for n in recs:n['community']=cmap.get(n['id'])
    return {'schema_version':ge.VIEW_VERSION,'graph':{'contract':'local-graph-sqlite-v1','node_count':len(recs),'edge_count':len(edges)},'nodes':recs,'edges':edges,'communities':communities,'query':request,'metadata':{'truncated':truncated,'source_graph_sha256':logical_hash(con),'eligible_nodes':len(nodes),'eligible_edges':len(rows),'complete_database':not truncated and len(ids)==con.execute('SELECT COUNT(*) FROM active_nodes').fetchone()[0] and request['statuses']==sorted(ge.ACTIVE_EVIDENCE_STATUS),'community_run_id':run,'evidence_policy':request['statuses'],'producer_version':ge.PACKAGE_VERSION}}

def subgraph(con,request,nodes,rows):
    token=request.get('seed') or request.get('node')
    if not token:
        if len(nodes)>request['max_nodes']:raise ValueError('graph exceeds max_nodes; specify seed, kinds, or aggregate')
        return project(con,request,nodes,rows)
    seed=resolve(nodes,token,con);adj=adjacency(rows,request.get('direction','both'))
    q=deque([(seed,0)]);seen={seed};truncated=False
    while q:
        node,depth=q.popleft()
        if depth>=request['depth']:continue
        for other,_ in adj.get(node,[]):
            if other in seen:continue
            if len(seen)>=request['max_nodes']:truncated=True;continue
            seen.add(other);q.append((other,depth+1))
    return project(con,dict(request,seed=seed),nodes,rows,seen,truncated)

def shortest(nodes,rows,start,goal,request):
    adjacency_map=adjacency(rows,request.get('direction','outgoing'))
    if start==goal:return {'nodes':[start],'edges':[],'hops':0,'cost':0.0,'search_complete':True}
    byid={r['id']:r for r in rows}; weight=request.get('weight')
    # State includes hop count: cheapest arrival is not necessarily usable under
    # a hop ceiling. A deterministic tuple breaks ties without global randomness.
    queue=[(0.0,0,(start,),())];best={(start,0):0.0};explored=0;depth_bound=False
    while queue:
        cost,hops,path,edges=heapq.heappop(queue);node=path[-1]
        if node==goal:return {'nodes':list(path),'edges':list(edges),'hops':hops,'cost':cost,'search_complete':True}
        if hops>=request['depth']:depth_bound=True;continue
        explored+=1
        if explored>200000:raise ValueError('path exploration budget exceeded')
        for nxt,eid in adjacency_map.get(node,[]):
            if nxt in path:continue
            step=json.loads(byid[eid]['properties_json']).get(weight,1.0) if weight else 1.0
            if isinstance(step,bool) or not isinstance(step,(int,float)) or not math.isfinite(step) or step<0:raise ValueError('path weights must be finite nonnegative numbers')
            newcost=cost+step;state=(nxt,hops+1)
            if newcost>=best.get(state,float('inf')):continue
            best[state]=newcost;heapq.heappush(queue,(newcost,hops+1,path+(nxt,),edges+(eid,)))
    return {'nodes':[],'edges':[],'hops':None,'cost':None,'search_complete':not depth_bound,'bound':request['depth']}

def timestamp(value):
    if not isinstance(value,str):return None
    try:
        dt=datetime.fromisoformat(value.replace('Z','+00:00'))
        if dt.tzinfo is None:return None
        return dt.timestamp()
    except ValueError:return None

def query(con:sqlite3.Connection,request:dict)->dict:
    request=validate_request(request);op=request['operation'];nodes,rows=filtered_graph(con,request)
    if op=='subgraph':return {'status':'pass','view':subgraph(con,request,nodes,rows)}
    if op=='stats':return {'status':'pass','nodes':len(nodes),'edges':len(rows),'kinds':dict(sorted(Counter(n['kind'] for n in nodes.values()).items())),'relations':dict(sorted(Counter(r['relation'] for r in rows).items())),'graph_hash':logical_hash(con)}
    if op=='search':
        term=request.get('query') or ''
        if not term:raise ValueError('search query required')
        available=con.execute("SELECT 1 FROM sqlite_master WHERE name='node_search'").fetchone()
        if available:
            matches=con.execute('SELECT node_id,bm25(node_search) AS rank FROM node_search WHERE node_search MATCH ? ORDER BY rank,node_id LIMIT 10001',(term,)).fetchall()
            found=[dict(nodes[r['node_id']],rank=r['rank']) for r in matches if r['node_id'] in nodes]
            offset=request['offset'];limit=request['limit']
            return {'status':'pass','backend':'fts5','results':found[offset:offset+limit],'truncated':len(matches)>10000 or len(found)>offset+limit}
        fallback=query(con,dict(request,operation='find'))
        return dict(fallback,backend='substring-fallback',limitation='FTS5 unavailable; advanced MATCH syntax is not evaluated')
    if op=='find':
        text=(request.get('query') or '').casefold()
        aliases=defaultdict(list)
        for r in con.execute('SELECT alias,node_id FROM node_aliases'):aliases[r['node_id']].append(r['alias'])
        found=[{'id':n['id'],'kind':n['kind'],'label':n['label']} for n in nodes.values() if text in n['label'].casefold() or text in n['id'].casefold() or any(text in a.casefold() for a in aliases[n['id']])]
        found.sort(key=lambda n:(n['label'].casefold()!=text,n['label'].casefold(),n['id']))
        offset=request['offset'];limit=request['limit']
        return {'status':'pass','total':len(found),'results':found[offset:offset+limit],'next_offset':offset+limit if offset+limit<len(found) else None}
    if op in ('node','neighbors','path','impact'):
        start=resolve(nodes,request.get('node') or request.get('seed'),con)
        if op=='node':return {'status':'pass','node':node_view(con,start)}
        if op=='path':
            goal=resolve(nodes,request.get('target'),con)
            return {'status':'pass','path':shortest(nodes,rows,start,goal,request)}
        if op=='neighbors':
            ids=sorted({n for n,_ in adjacency(rows,request.get('direction','both')).get(start,[])})
            return {'status':'pass','node':start,'total':len(ids),'neighbors':[node_view(con,n) for n in ids[request['offset']:request['offset']+request['limit']]],'truncated':len(ids)>request['offset']+request['limit']}
        view=subgraph(con,dict(request,seed=start,direction=request.get('direction','incoming')),nodes,rows)
        return {'status':'pass','node':start,'view':view,'interpretation':'reachable relationships, not proof of business impact or causality'}
    if op=='aggregate':
        field=request.get('group_by','kind');metric=request.get('metric','count');prop=request.get('property')
        if metric not in ('count','sum','mean','min','max'):raise ValueError('invalid metric')
        if metric!='count' and not prop:raise ValueError('numeric property is required')
        groups=defaultdict(list);skipped=0
        for n in nodes.values():
            properties=json.loads(n['properties_json']);key=n.get(field,properties.get(field))
            key=scalar_group(key)
            val=1 if metric=='count' else properties.get(prop)
            if isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val):skipped+=1;continue
            groups[key].append(val)
        result=[]
        for key,values in sorted(groups.items()):
            v=len(values) if metric=='count' else sum(values) if metric=='sum' else sum(values)/len(values) if metric=='mean' else min(values) if metric=='min' else max(values)
            result.append({'group':key,'value':v,'records':len(values)})
        return {'status':'pass','group_by':field,'metric':metric,'property':prop,'groups':result,'excluded_non_numeric':skipped,'warning':'Verify units before aggregating different entities' if metric!='count' else None}
    if op=='timeline':
        field=request.get('time_property','timestamp');items=[];missing=0
        lower=timestamp(request.get('from'));upper=timestamp(request.get('to'))
        if request.get('from') and lower is None or request.get('to') and upper is None:raise ValueError('time bounds must be ISO-8601 with timezone')
        for n in nodes.values():
            v=json.loads(n['properties_json']).get(field);t=timestamp(v)
            if t is None:missing+=1;continue
            if lower is not None and t<lower or upper is not None and t>upper:continue
            items.append({'id':n['id'],'label':n['label'],'kind':n['kind'],'timestamp':v,'_sort':t})
        items.sort(key=lambda x:(x['_sort'],x['id']))
        for item in items:item.pop('_sort')
        return {'status':'pass','items':items[request['offset']:request['offset']+request['limit']],'eligible':len(items),'missing_or_ambiguous_time':missing,'time_property':field}
    if op=='quality':
        labels=defaultdict(list)
        for n in nodes.values():labels[n['label'].casefold()].append(n['id'])
        endpoints={n for r in rows for n in (r['source_node_id'],r['target_node_id'])}
        conflicts=[]
        if con.execute("SELECT 1 FROM sqlite_master WHERE name='node_claims'").fetchone():
            for n in nodes:
                claims=con.execute('SELECT payload_json,source_id FROM node_claims WHERE node_id=? ORDER BY source_id',(n,)).fetchall()
                variants={canonical({k:json.loads(c['payload_json']).get(k) for k in ['label','kind','properties']}) for c in claims}
                if len(variants)>1:conflicts.append({'node':n,'sources':[c['source_id'] for c in claims],'variants':len(variants)})
        return {'status':'pass','isolates':sorted(set(nodes)-endpoints),'duplicate_labels':[{'label':k,'ids':sorted(v),'decision':'review; not automatic merge'} for k,v in sorted(labels.items()) if len(v)>1],'attribute_conflicts':conflicts,'coverage':{'nodes':len(nodes),'edges':len(rows),'statuses':request['statuses']}}
    raise ValueError('unsupported operation')

def scalar_group(value):
    return '(missing)' if value is None else value if isinstance(value,str) else canonical(value)


def claims(con,kind,identifier):
    table=kind+'_claims';key=kind+'_id'
    if not con.execute("SELECT 1 FROM sqlite_master WHERE name=?",(table,)).fetchone():return []
    rows=con.execute(f'SELECT c.payload_json,s.uri FROM {table} c JOIN sources s ON s.id=c.source_id WHERE {key}=? ORDER BY s.uri LIMIT 100',(identifier,)).fetchall()
    return [{'source_uri':r['uri'],'assertion':{k:v for k,v in json.loads(r['payload_json']).items() if k!='evidence'}} for r in rows]
